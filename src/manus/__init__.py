"""
Manus AI Integration Package
Интеграция с Manus AI для автоматизации задач

Этот пакет предоставляет:
- ManusClient: Клиент для работы с Manus AI API
- ManusWebhookHandler: Обработчик webhooks от Manus
- Pydantic модели для типизированных запросов/ответов
- Кастомные исключения для обработки ошибок

Example:
    >>> from src.manus import ManusClient, ManusWebhookHandler
    >>>
    >>> # Создание клиента
    >>> client = ManusClient(api_key="sk-manus-xxx")
    >>>
    >>> # Создание задачи
    >>> task = client.create_task(
    ...     prompt="Проанализируй код",
    ...     context="https://github.com/user/repo/file.py"
    ... )
    >>>
    >>> # Ожидание результата
    >>> result = client.wait_for_completion(task["task_id"])
    >>>
    >>> # Создание webhook handler
    >>> handler = ManusWebhookHandler(secret="your-secret")
    >>>
    >>> # Регистрация обработчика
    >>> @handler.on("task.completed")
    >>> def handle_completed(event_data):
    ...     print(f"Task {event_data['task_id']} completed!")
"""

from .client import ManusClient
from .webhook import ManusWebhookHandler
from .models import (
    ManusTaskRequest,
    ManusTaskStatus,
    ManusTaskResult,
    ManusWebhookEvent,
    ManusCodeAnalysisRequest,
    ManusTestRequest,
    ManusConfig,
)
from .exceptions import (
    ManusException,
    ManusAPIError,
    ManusAuthenticationError,
    ManusRateLimitError,
    ManusTaskNotFoundError,
    ManusTaskTimeoutError,
    ManusTaskFailedError,
    ManusWebhookVerificationError,
    ManusConfigurationError,
    ManusNetworkError,
)

__version__ = "1.0.0"

__all__ = [
    # Main classes
    "ManusClient",
    "ManusWebhookHandler",
    # Models
    "ManusTaskRequest",
    "ManusTaskStatus",
    "ManusTaskResult",
    "ManusWebhookEvent",
    "ManusCodeAnalysisRequest",
    "ManusTestRequest",
    "ManusConfig",
    # Exceptions
    "ManusException",
    "ManusAPIError",
    "ManusAuthenticationError",
    "ManusRateLimitError",
    "ManusTaskNotFoundError",
    "ManusTaskTimeoutError",
    "ManusTaskFailedError",
    "ManusWebhookVerificationError",
    "ManusConfigurationError",
    "ManusNetworkError",
]
