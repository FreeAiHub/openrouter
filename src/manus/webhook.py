"""
Manus Webhook Handler
Обработчик webhooks от Manus AI
"""

import os
import hmac
import hashlib
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from .models import ManusWebhookEvent
from .exceptions import ManusWebhookVerificationError, ManusConfigurationError


class ManusWebhookHandler:
    """
    Обработчик webhooks от Manus AI

    Предоставляет:
    - Верификацию подписи webhooks
    - Маршрутизацию событий к соответствующим обработчикам
    - Логирование событий

    Example:
        >>> from src.manus import ManusWebhookHandler
        >>> handler = ManusWebhookHandler(secret="your-secret")
        >>>
        >>> @handler.on("task.completed")
        >>> def handle_completed(event_data):
        ...     print(f"Task {event_data['task_id']} completed!")
        >>>
        >>> # В Flask endpoint
        >>> result = handler.handle_webhook(
        ...     event_type=request.headers.get("X-Manus-Event"),
        ...     payload=request.data.decode(),
        ...     signature=request.headers.get("X-Manus-Signature")
        ... )
    """

    def __init__(self, secret: Optional[str] = None):
        """
        Инициализация обработчика webhooks

        Args:
            secret: Секретный ключ для верификации webhooks
                   (по умолчанию из MANUS_WEBHOOK_SECRET env)

        Raises:
            ManusConfigurationError: Если secret не предоставлен
        """
        self.secret = secret or os.getenv("MANUS_WEBHOOK_SECRET")
        if not self.secret:
            raise ManusConfigurationError(
                "MANUS_WEBHOOK_SECRET не найден. "
                "Укажите secret или установите переменную окружения."
            )

        # Регистр обработчиков событий
        self._handlers: Dict[str, Callable] = {}

        # Счетчики для метрик
        self._event_count = 0
        self._verification_failures = 0

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Проверка подписи webhook

        Args:
            payload: Тело запроса (строка)
            signature: Подпись из заголовка X-Manus-Signature

        Returns:
            True если подпись валидна

        Raises:
            ManusWebhookVerificationError: Если подпись невалидна
        """
        expected_signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            self._verification_failures += 1
            raise ManusWebhookVerificationError(
                f"Invalid webhook signature. Expected: {expected_signature[:8]}..."
            )

        return True

    def on(self, event_type: str) -> Callable:
        """
        Декоратор для регистрации обработчиков событий

        Args:
            event_type: Тип события (task.completed, task.failed, etc.)

        Example:
            >>> @handler.on("task.completed")
            >>> def handle_completed(event_data):
            ...     print(f"Task completed: {event_data}")
        """
        def decorator(func: Callable) -> Callable:
            self._handlers[event_type] = func
            return func
        return decorator

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Регистрация обработчика события программно

        Args:
            event_type: Тип события
            handler: Функция-обработчик
        """
        self._handlers[event_type] = handler

    def handle_task_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка события завершения задачи (default handler)

        Args:
            event_data: Данные события

        Returns:
            Ответ для webhook
        """
        task_id = event_data.get("task_id")
        result = event_data.get("result", {})

        # Здесь можно добавить логику:
        # - Создать комментарий в GitHub Issue
        # - Отправить уведомление в Slack/Discord
        # - Обновить статус в базе данных
        # - Отправить email уведомление

        return {
            "status": "processed",
            "task_id": task_id,
            "action": "task_completed_acknowledged",
            "timestamp": datetime.now().isoformat()
        }

    def handle_task_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка события ошибки задачи (default handler)

        Args:
            event_data: Данные события

        Returns:
            Ответ для webhook
        """
        task_id = event_data.get("task_id")
        error = event_data.get("error", "Unknown error")

        # Логирование ошибки, отправка уведомлений
        print(f"[ERROR] Task {task_id} failed: {error}")

        return {
            "status": "error_logged",
            "task_id": task_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

    def handle_task_started(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка события старта задачи (default handler)

        Args:
            event_data: Данные события

        Returns:
            Ответ для webhook
        """
        task_id = event_data.get("task_id")

        return {
            "status": "acknowledged",
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        }

    def handle_webhook(
        self,
        event_type: str,
        payload: str,
        signature: str,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Главный обработчик webhooks

        Args:
            event_type: Тип события из заголовка X-Manus-Event
            payload: Тело запроса (строка)
            signature: Подпись из заголовка X-Manus-Signature
            verify: Проверять подпись (по умолчанию True)

        Returns:
            Ответ для webhook

        Raises:
            ManusWebhookVerificationError: Если подпись невалидна

        Example:
            >>> # В Flask endpoint
            >>> @app.route('/webhooks/manus', methods=['POST'])
            >>> def manus_webhook():
            ...     result = handler.handle_webhook(
            ...         event_type=request.headers.get("X-Manus-Event"),
            ...         payload=request.data.decode(),
            ...         signature=request.headers.get("X-Manus-Signature")
            ...     )
            ...     return jsonify(result)
        """
        # Верификация подписи
        if verify:
            self.verify_signature(payload, signature)

        self._event_count += 1

        # Парсинг payload (предполагаем JSON)
        import json
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON payload"
            }

        # Поиск зарегистрированного обработчика
        handler = self._handlers.get(event_type)
        if handler:
            return handler(event_data)

        # Default обработчики
        default_handlers = {
            "task.completed": self.handle_task_completed,
            "task.failed": self.handle_task_failed,
            "task.started": self.handle_task_started,
        }

        default_handler = default_handlers.get(event_type)
        if default_handler:
            return default_handler(event_data)

        # Неизвестный тип события
        return {
            "status": "unknown_event",
            "event_type": event_type,
            "message": f"No handler registered for event: {event_type}"
        }

    def get_metrics(self) -> Dict[str, int]:
        """
        Получить метрики обработки webhooks

        Returns:
            Словарь с метриками
        """
        return {
            "event_count": self._event_count,
            "verification_failures": self._verification_failures,
            "registered_handlers": len(self._handlers)
        }

    def __repr__(self) -> str:
        return f"ManusWebhookHandler(handlers={list(self._handlers.keys())})"
