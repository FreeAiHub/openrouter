"""
Configuration management for OpenRouter API integration.
Uses Pydantic for type safety and validation.
"""

from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os
from pathlib import Path


class OpenRouterSettings(BaseSettings):
    """OpenRouter API configuration with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    openrouter_api_key: str = Field(
        ...,
        description="OpenRouter API key",
        min_length=20
    )
    api_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    
    # Application Settings
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Model Configuration
    default_model: str = Field(
        default="xiaomi/mimo-v2-flash:free",
        description="Default model to use"
    )
    fallback_model: str = Field(
        default="kwaipilot/kat-coder-pro-v1:free",
        description="Fallback model if primary fails"
    )
    
    # Rate Limiting & Retry
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )
    retry_delay: int = Field(
        default=2,
        ge=1,
        le=60,
        description="Base delay between retries (seconds)"
    )
    request_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout (seconds)"
    )
    
    # Cost Controls
    max_tokens_per_request: int = Field(
        default=2000,
        ge=1,
        le=200000,
        description="Maximum tokens per request"
    )
    enable_cost_tracking: bool = Field(
        default=True,
        description="Enable cost tracking"
    )
    
    # Monitoring
    enable_prometheus: bool = Field(
        default=False,
        description="Enable Prometheus metrics"
    )
    enable_structured_logging: bool = Field(
        default=True,
        description="Enable structured logging"
    )
    
    # Security
    http_referer: Optional[str] = Field(
        default="https://github.com/enterprise-ai",
        description="HTTP Referer header"
    )
    x_title: Optional[str] = Field(
        default="Enterprise AI Platform",
        description="X-Title header"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_envs = {"development", "staging", "production"}
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    def get_headers(self) -> Dict[str, str]:
        """Get standard API headers."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        
        if self.x_title:
            headers["X-Title"] = self.x_title
        
        return headers
    
    def get_model_config(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "model": model or self.default_model,
            "max_tokens": self.max_tokens_per_request,
        }


# Singleton instance
_settings: Optional[OpenRouterSettings] = None


def get_settings() -> OpenRouterSettings:
    """Get settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = OpenRouterSettings()
    return _settings


def reset_settings():
    """Reset settings (for testing)."""
    global _settings
    _settings = None


# Example usage
if __name__ == "__main__":
    settings = get_settings()
    print(f"Environment: {settings.environment}")
    print(f"Default Model: {settings.default_model}")
    print(f"API Base URL: {settings.api_base_url}")
    print(f"Is Production: {settings.is_production}")
