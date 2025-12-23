"""Custom exceptions for OpenRouter API client."""

from typing import Optional, Dict, Any


class OpenRouterException(Exception):
    """Base exception for OpenRouter API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(OpenRouterException):
    """Authentication failed (401)."""
    pass


class RateLimitError(OpenRouterException):
    """Rate limit exceeded (429)."""
    pass


class InvalidRequestError(OpenRouterException):
    """Invalid request parameters (400)."""
    pass


class ModelNotFoundError(OpenRouterException):
    """Requested model not found (404)."""
    pass


class ServerError(OpenRouterException):
    """Server error (5xx)."""
    pass


class TimeoutError(OpenRouterException):
    """Request timeout."""
    pass


class NetworkError(OpenRouterException):
    """Network connectivity error."""
    pass


class ValidationError(OpenRouterException):
    """Request validation error."""
    pass
