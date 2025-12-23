"""OpenRouter API integration package."""

from .client import OpenRouterClient
from .models import Message, ChatCompletionResponse
from .exceptions import (
    OpenRouterException,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError
)

__version__ = "1.0.0"
__all__ = [
    "OpenRouterClient",
    "Message",
    "ChatCompletionResponse",
    "OpenRouterException",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
]
