"""
Custom Exceptions for Manus AI Integration
Кастомные исключения для работы с Manus AI
"""

from typing import Optional, Dict, Any


class ManusException(Exception):
    """Базовое исключение для Manus AI"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ManusAPIError(ManusException):
    """Ошибка при взаимодействии с Manus API"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_text:
            details["response_text"] = response_text
        super().__init__(message, details)


class ManusAuthenticationError(ManusAPIError):
    """Ошибка аутентификации с Manus API"""

    def __init__(self, message: str = "Invalid Manus API key"):
        super().__init__(message, status_code=401)


class ManusRateLimitError(ManusAPIError):
    """Превышен лимит запросов к Manus API"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ManusTaskNotFoundError(ManusAPIError):
    """Задача не найдена"""

    def __init__(self, task_id: str):
        super().__init__(
            f"Task not found: {task_id}",
            status_code=404
        )
        self.task_id = task_id


class ManusTaskTimeoutError(ManusException):
    """Превышено время ожидания выполнения задачи"""

    def __init__(self, task_id: str, timeout: int):
        super().__init__(
            f"Task {task_id} did not complete within {timeout} seconds",
            details={"task_id": task_id, "timeout": timeout}
        )
        self.task_id = task_id
        self.timeout = timeout


class ManusTaskFailedError(ManusException):
    """Задача завершилась с ошибкой"""

    def __init__(self, task_id: str, error_message: str):
        super().__init__(
            f"Task {task_id} failed: {error_message}",
            details={"task_id": task_id, "error": error_message}
        )
        self.task_id = task_id
        self.error_message = error_message


class ManusWebhookVerificationError(ManusException):
    """Ошибка верификации webhook подписи"""

    def __init__(self, message: str = "Invalid webhook signature"):
        super().__init__(message)


class ManusConfigurationError(ManusException):
    """Ошибка конфигурации Manus клиента"""

    def __init__(self, message: str):
        super().__init__(message)


class ManusNetworkError(ManusException):
    """Ошибка сетевого соединения с Manus API"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {"original_error": str(original_error)} if original_error else {}
        super().__init__(message, details)
        self.original_error = original_error
