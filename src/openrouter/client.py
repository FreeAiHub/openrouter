"""
Enterprise-grade OpenRouter API Client.

Features:
- Automatic retries with exponential backoff
- Circuit breaker pattern
- Request/response logging
- Cost tracking
- Type safety with Pydantic
- Comprehensive error handling
"""

import time
import json
import logging
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import get_settings
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
    StreamChunk,
    CostEstimate,
    APIMetrics
)
from .exceptions import (
    OpenRouterException,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    ModelNotFoundError,
    ServerError,
    TimeoutError as CustomTimeoutError,
    NetworkError
)


logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise OpenRouterException(
                    "Circuit breaker is OPEN - service temporarily unavailable"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker CLOSED")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )


class OpenRouterClient:
    """Enterprise-grade OpenRouter API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: Optional API key (uses environment if not provided)
        """
        self.settings = get_settings()
        
        if api_key:
            self.settings.openrouter_api_key = api_key
        
        # Configure session with connection pooling
        self.session = requests.Session()
        
        # Configure retries for transient errors
        retry_strategy = Retry(
            total=self.settings.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Circuit breaker for fault tolerance
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=OpenRouterException
        )
        
        # Metrics tracking
        self.metrics: List[APIMetrics] = []
        
        logger.info(
            f"OpenRouter client initialized (env={self.settings.environment})"
        )
    
    def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        stream: bool = False
    ) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            stream: Enable streaming
            
        Returns:
            Response object
            
        Raises:
            Various OpenRouterException subclasses
        """
        url = f"{self.settings.api_base_url}/{endpoint}"
        headers = self.settings.get_headers()
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.settings.request_timeout,
                stream=stream
            )
            
            # Handle error status codes
            if response.status_code != 200:
                self._handle_error_response(response)
            
            return response
            
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise CustomTimeoutError(
                f"Request timeout after {self.settings.request_timeout}s"
            )
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError("Network connection failed")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OpenRouterException(f"Unexpected error: {str(e)}")
    
    def _handle_error_response(self, response: requests.Response):
        """Handle HTTP error responses."""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", str(error_data))
        except:
            error_msg = response.text
        
        if response.status_code == 400:
            raise InvalidRequestError(
                error_msg,
                status_code=400,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                "Invalid API key",
                status_code=401
            )
        elif response.status_code == 404:
            raise ModelNotFoundError(
                error_msg,
                status_code=404
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded",
                status_code=429,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: {error_msg}",
                status_code=response.status_code
            )
        else:
            raise OpenRouterException(
                f"HTTP {response.status_code}: {error_msg}",
                status_code=response.status_code
            )
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> ChatCompletionResponse:
        """
        Create a chat completion.
        
        Args:
            messages: List of conversation messages
            model: Model to use (default from settings)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            ChatCompletionResponse
            
        Example:
            >>> client = OpenRouterClient()
            >>> messages = [Message(role="user", content="Hello!")]
            >>> response = client.chat_completion(messages)
            >>> print(response.choices[0].message.content)
        """
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Build request
        request = ChatCompletionRequest(
            model=model or self.settings.default_model,
            messages=messages,
            max_tokens=max_tokens or self.settings.max_tokens_per_request,
            temperature=temperature,
            **kwargs
        )
        
        logger.info(
            f"Chat completion request: model={request.model}, "
            f"messages={len(messages)}, max_tokens={request.max_tokens}"
        )
        
        try:
            # Use circuit breaker
            response = self.circuit_breaker.call(
                self._make_request,
                "chat/completions",
                request.model_dump(exclude_none=True)
            )
            
            response_data = response.json()
            completion = ChatCompletionResponse(**response_data)
            
            # Track metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metrics(
                request_id=request_id,
                model=request.model,
                duration_ms=duration_ms,
                input_tokens=completion.usage.prompt_tokens if completion.usage else 0,
                output_tokens=completion.usage.completion_tokens if completion.usage else 0,
                success=True
            )
            
            logger.info(
                f"Chat completion success: tokens={completion.usage.total_tokens if completion.usage else 0}, "
                f"duration={duration_ms:.2f}ms"
            )
            
            return completion
            
        except OpenRouterException as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metrics(
                request_id=request_id,
                model=request.model,
                duration_ms=duration_ms,
                input_tokens=0,
                output_tokens=0,
                success=False,
                error=str(e)
            )
            raise
    
    def stream_chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat completion.
        
        Args:
            messages: List of conversation messages
            model: Model to use
            **kwargs: Additional parameters
            
        Yields:
            Content chunks
            
        Example:
            >>> for chunk in client.stream_chat_completion(messages):
            ...     print(chunk, end="", flush=True)
        """
        request = ChatCompletionRequest(
            model=model or self.settings.default_model,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        logger.info(f"Streaming chat completion: model={request.model}")
        
        try:
            response = self._make_request(
                "chat/completions",
                request.model_dump(exclude_none=True),
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str != "[DONE]":
                            try:
                                data = json.loads(data_str)
                                chunk = StreamChunk(**data)
                                
                                delta = chunk.choices[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.warning(f"Error parsing chunk: {e}")
                                continue
        
        except OpenRouterException:
            raise
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise OpenRouterException(f"Streaming error: {str(e)}")
    
    def _record_metrics(
        self,
        request_id: str,
        model: str,
        duration_ms: float,
        input_tokens: int,
        output_tokens: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Record API call metrics."""
        cost = None
        if success and self.settings.enable_cost_tracking:
            cost = self.estimate_cost(model, input_tokens, output_tokens)
        
        metric = APIMetrics(
            request_id=request_id,
            model=model,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success=success,
            error=error,
            cost=cost
        )
        
        self.metrics.append(metric)
        
        # Keep only last 1000 metrics in memory
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> CostEstimate:
        """
        Estimate cost for API call.
        
        Args:
            model: Model ID
            input_tokens: Input token count
            output_tokens: Output token count
            
        Returns:
            CostEstimate
        """
        # Free models
        if ":free" in model:
            return CostEstimate(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost=0.0,
                output_cost=0.0,
                total_cost=0.0
            )
        
        # Pricing per 1M tokens (update from openrouter.ai/models)
        pricing = {
            "deepseek/deepseek-chat": {"input": 0.14, "output": 0.14},
            "qwen/qwen-2.5-7b-instruct": {"input": 0.07, "output": 0.07},
            "meta-llama/llama-3.2-3b-instruct": {"input": 0.06, "output": 0.06},
        }
        
        rates = pricing.get(model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        
        return CostEstimate(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of API metrics."""
        if not self.metrics:
            return {"total_calls": 0}
        
        total_calls = len(self.metrics)
        successful_calls = sum(1 for m in self.metrics if m.success)
        failed_calls = total_calls - successful_calls
        
        total_input_tokens = sum(m.input_tokens for m in self.metrics)
        total_output_tokens = sum(m.output_tokens for m in self.metrics)
        
        total_cost = sum(
            m.cost.total_cost for m in self.metrics 
            if m.cost and m.success
        )
        
        avg_duration = sum(m.duration_ms for m in self.metrics) / total_calls
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": f"{(successful_calls/total_calls)*100:.2f}%",
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost_usd": f"${total_cost:.6f}",
            "average_duration_ms": f"{avg_duration:.2f}",
        }
    
    def close(self):
        """Close client session."""
        self.session.close()
        logger.info("OpenRouter client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
