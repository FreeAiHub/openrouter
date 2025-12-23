"""Pydantic models for OpenRouter API requests and responses."""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Message(BaseModel):
    """Chat message."""
    
    role: Literal["system", "user", "assistant"]
    content: str
    name: Optional[str] = None


class UsageInfo(BaseModel):
    """Token usage information."""
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Choice(BaseModel):
    """Response choice."""
    
    index: int
    message: Message
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Chat completion API response."""
    
    id: str
    model: str
    created: int
    choices: List[Choice]
    usage: Optional[UsageInfo] = None


class ChatCompletionRequest(BaseModel):
    """Chat completion API request."""
    
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=200000
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )
    frequency_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0
    )
    presence_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0
    )
    stop: Optional[List[str]] = None
    stream: bool = False
    
    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[Message]) -> List[Message]:
        """Validate messages list."""
        if not v:
            raise ValueError("Messages list cannot be empty")
        return v


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    
    id: str
    model: str
    created: int
    choices: List[Dict[str, Any]]


class ModelInfo(BaseModel):
    """Model information."""
    
    id: str
    name: str
    description: Optional[str] = None
    context_length: int
    pricing: Dict[str, float]
    created: Optional[datetime] = None


class CostEstimate(BaseModel):
    """Cost estimation for API call."""
    
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"
    
    def format_cost(self) -> str:
        """Format cost as string."""
        if self.total_cost == 0:
            return "$0.00 (Free)"
        return f"${self.total_cost:.6f}"


class APIMetrics(BaseModel):
    """API call metrics."""
    
    request_id: str
    model: str
    timestamp: datetime
    duration_ms: float
    input_tokens: int
    output_tokens: int
    success: bool
    error: Optional[str] = None
    cost: Optional[CostEstimate] = None
