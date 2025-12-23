"""
Integration tests for OpenRouter API client.
Tests real API calls (requires valid API key).
"""

import pytest
import os
from src.openrouter import OpenRouterClient, Message
from src.openrouter.exceptions import (
    InvalidRequestError,
    AuthenticationError
)


@pytest.fixture
def client():
    """Create client for testing."""
    return OpenRouterClient()


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API key not available."""
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")


class TestBasicFunctionality:
    """Test basic API functionality."""
    
    def test_simple_completion(self, client, skip_if_no_api_key):
        """Test simple chat completion."""
        messages = [Message(role="user", content="Say 'test successful'")]
        
        response = client.chat_completion(messages)
        
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message.content
        assert "test" in response.choices[0].message.content.lower()
    
    def test_token_usage_tracking(self, client, skip_if_no_api_key):
        """Test that token usage is tracked."""
        messages = [Message(role="user", content="Hello")]
        
        response = client.chat_completion(messages)
        
        if response.usage:
            assert response.usage.prompt_tokens > 0
            assert response.usage.completion_tokens > 0
            assert response.usage.total_tokens > 0
    
    def test_streaming(self, client, skip_if_no_api_key):
        """Test streaming responses."""
        messages = [Message(role="user", content="Count to 3")]
        
        chunks = []
        for chunk in client.stream_chat_completion(messages):
            chunks.append(chunk)
        
        full_response = "".join(chunks)
        assert len(chunks) > 0
        assert len(full_response) > 0


class TestConversationContext:
    """Test multi-turn conversations."""
    
    def test_multi_turn_conversation(self, client, skip_if_no_api_key):
        """Test that context is maintained."""
        messages = [
            Message(role="user", content="My favorite color is blue.")
        ]
        
        response1 = client.chat_completion(messages)
        messages.append(Message(
            role="assistant",
            content=response1.choices[0].message.content
        ))
        
        messages.append(Message(
            role="user",
            content="What is my favorite color?"
        ))
        
        response2 = client.chat_completion(messages)
        answer = response2.choices[0].message.content.lower()
        
        assert "blue" in answer


class TestErrorHandling:
    """Test error handling."""
    
    def test_empty_messages_validation(self, client):
        """Test that empty messages are rejected."""
        with pytest.raises((ValueError, InvalidRequestError)):
            client.chat_completion([])
    
    def test_invalid_model(self, client, skip_if_no_api_key):
        """Test handling of invalid model."""
        messages = [Message(role="user", content="Hello")]
        
        with pytest.raises((InvalidRequestError, Exception)):
            client.chat_completion(messages, model="invalid/model:free")


class TestCostTracking:
    """Test cost tracking functionality."""
    
    def test_cost_estimation_free_model(self, client):
        """Test cost estimation for free models."""
        cost = client.estimate_cost(
            model="xiaomi/mimo-v2-flash:free",
            input_tokens=100,
            output_tokens=50
        )
        
        assert cost.total_cost == 0.0
        assert "Free" in cost.format_cost()
    
    def test_metrics_tracking(self, client, skip_if_no_api_key):
        """Test that metrics are collected."""
        messages = [Message(role="user", content="Hello")]
        
        # Clear metrics
        client.metrics = []
        
        # Make request
        client.chat_completion(messages)
        
        # Check metrics
        assert len(client.metrics) > 0
        metric = client.metrics[0]
        assert metric.success
        assert metric.model
        assert metric.duration_ms > 0


class TestClientConfiguration:
    """Test client configuration."""
    
    def test_custom_timeout(self, skip_if_no_api_key):
        """Test custom timeout configuration."""
        os.environ["REQUEST_TIMEOUT"] = "60"
        from config.settings import reset_settings
        reset_settings()
        
        client = OpenRouterClient()
        assert client.settings.request_timeout == 60
        
        # Reset
        os.environ["REQUEST_TIMEOUT"] = "30"
        reset_settings()
    
    def test_context_manager(self, skip_if_no_api_key):
        """Test client as context manager."""
        with OpenRouterClient() as client:
            messages = [Message(role="user", content="Hello")]
            response = client.chat_completion(messages)
            assert response is not None


class TestMetricsSummary:
    """Test metrics summary generation."""
    
    def test_metrics_summary(self, client, skip_if_no_api_key):
        """Test metrics summary generation."""
        client.metrics = []
        
        messages = [Message(role="user", content="Hello")]
        client.chat_completion(messages)
        
        summary = client.get_metrics_summary()
        
        assert "total_calls" in summary
        assert "successful_calls" in summary
        assert "success_rate" in summary
        assert summary["total_calls"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
