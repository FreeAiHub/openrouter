"""
Tests for Manus AI Integration Module
Тесты для модуля интеграции с Manus AI
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import hmac
import hashlib
import json

from src.manus import (
    ManusClient,
    ManusWebhookHandler,
    ManusException,
    ManusAPIError,
    ManusAuthenticationError,
    ManusTaskNotFoundError,
    ManusTaskTimeoutError,
    ManusTaskFailedError,
    ManusWebhookVerificationError,
    ManusConfigurationError,
)


class TestManusClient:
    """Тесты для ManusClient"""

    def test_client_initialization_with_api_key(self):
        """Тест: Клиент инициализируется с API ключом"""
        client = ManusClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.manus.ai/v1"

    def test_client_initialization_from_env(self, monkeypatch):
        """Тест: Клиент читает API ключ из environment"""
        monkeypatch.setenv("MANUS_API_KEY", "env-key")
        client = ManusClient()
        assert client.api_key == "env-key"

    def test_client_initialization_without_key_raises_error(self, monkeypatch):
        """Тест: Ошибка если нет API ключа"""
        monkeypatch.delenv("MANUS_API_KEY", raising=False)
        with pytest.raises(ManusConfigurationError):
            ManusClient()

    def test_client_custom_base_url(self):
        """Тест: Можно указать кастомный base URL"""
        client = ManusClient(
            api_key="test-key",
            base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"

    @patch('requests.request')
    def test_create_task_success(self, mock_request):
        """Тест: Успешное создание задачи"""
        # Mock ответ API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "pending"
        }
        mock_request.return_value = mock_response

        # Создаем клиент и задачу
        client = ManusClient(api_key="test-key")
        task = client.create_task(
            prompt="Test prompt",
            context="https://github.com/test"
        )

        # Проверки
        assert task["task_id"] == "task_123"
        assert task["status"] == "pending"
        mock_request.assert_called_once()

    @patch('requests.request')
    def test_create_task_with_tools(self, mock_request):
        """Тест: Создание задачи с инструментами"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "task_456"}
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")
        task = client.create_task(
            prompt="Analyze code",
            context="https://github.com/test",
            tools=["code_analysis", "security_scan"]
        )

        # Проверяем что tools переданы в запрос
        call_args = mock_request.call_args
        assert "json" in call_args.kwargs
        assert call_args.kwargs["json"]["tools"] == ["code_analysis", "security_scan"]

    @patch('requests.request')
    def test_get_task_success(self, mock_request):
        """Тест: Успешное получение статуса задачи"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "completed",
            "result": "Analysis complete"
        }
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")
        task = client.get_task("task_123")

        assert task["status"] == "completed"
        assert task["result"] == "Analysis complete"

    @patch('requests.request')
    def test_get_task_not_found(self, mock_request):
        """Тест: Ошибка если задача не найдена"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")

        with pytest.raises(ManusTaskNotFoundError) as exc_info:
            client.get_task("non_existent")

        assert "non_existent" in str(exc_info.value)

    @patch('requests.request')
    def test_authentication_error(self, mock_request):
        """Тест: Ошибка аутентификации"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        client = ManusClient(api_key="invalid-key")

        with pytest.raises(ManusAuthenticationError):
            client.create_task(prompt="test")

    @patch('requests.request')
    def test_wait_for_completion_success(self, mock_request):
        """Тест: Успешное ожидание результата"""
        # Симулируем последовательность: pending -> running -> completed
        responses = [
            {"task_id": "task_123", "status": "pending"},
            {"task_id": "task_123", "status": "running"},
            {"task_id": "task_123", "status": "completed", "result": "Done"}
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = responses
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")
        result = client.wait_for_completion(
            "task_123",
            timeout=10,
            poll_interval=1
        )

        assert result["status"] == "completed"
        assert result["result"] == "Done"

    @patch('requests.request')
    def test_wait_for_completion_timeout(self, mock_request):
        """Тест: Timeout при ожидании результата"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "running"  # Всегда running - не завершится
        }
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")

        with pytest.raises(ManusTaskTimeoutError) as exc_info:
            client.wait_for_completion(
                "task_123",
                timeout=3,
                poll_interval=1
            )

        assert "task_123" in str(exc_info.value)

    @patch('requests.request')
    def test_wait_for_completion_failed_task(self, mock_request):
        """Тест: Задача провалилась"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "failed",
            "error": "Internal error"
        }
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")

        with pytest.raises(ManusTaskFailedError) as exc_info:
            client.wait_for_completion("task_123")

        assert "Internal error" in str(exc_info.value)

    @patch('requests.request')
    def test_analyze_code(self, mock_request):
        """Тест: Анализ кода"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "analysis_123"}
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")
        task = client.analyze_code(
            code_url="https://github.com/test/file.py",
            check_security=True,
            check_performance=True
        )

        # Проверяем что tools включают security_scan
        call_args = mock_request.call_args
        tools = call_args.kwargs["json"]["tools"]
        assert "security_scan" in tools
        assert "performance_analysis" in tools

    @patch('requests.request')
    def test_test_function(self, mock_request):
        """Тест: Тестирование функции"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "test_123"}
        mock_request.return_value = mock_response

        client = ManusClient(api_key="test-key")
        task = client.test_function(
            function_url="https://github.com/test/utils.py",
            test_cases=[{"input": {"x": 1}, "expected": 2}]
        )

        assert task["task_id"] == "test_123"

    def test_client_metrics(self):
        """Тест: Метрики клиента"""
        client = ManusClient(api_key="test-key")

        # Инициализированный клиент имеет 0 запросов
        metrics = client.get_metrics()
        assert metrics["request_count"] == 0
        assert metrics["error_count"] == 0


class TestManusWebhookHandler:
    """Тесты для ManusWebhookHandler"""

    def test_handler_initialization_with_secret(self):
        """Тест: Инициализация с секретом"""
        handler = ManusWebhookHandler(secret="test-secret")
        assert handler.secret == "test-secret"

    def test_handler_initialization_from_env(self, monkeypatch):
        """Тест: Чтение секрета из environment"""
        monkeypatch.setenv("MANUS_WEBHOOK_SECRET", "env-secret")
        handler = ManusWebhookHandler()
        assert handler.secret == "env-secret"

    def test_handler_initialization_without_secret_raises_error(self, monkeypatch):
        """Тест: Ошибка если нет секрета"""
        monkeypatch.delenv("MANUS_WEBHOOK_SECRET", raising=False)
        with pytest.raises(ManusConfigurationError):
            ManusWebhookHandler()

    def test_verify_signature_valid(self):
        """Тест: Валидация корректной подписи"""
        handler = ManusWebhookHandler(secret="test-secret")
        payload = "test payload"

        # Генерируем корректную подпись
        signature = hmac.new(
            "test-secret".encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Должна пройти верификация
        assert handler.verify_signature(payload, signature) is True

    def test_verify_signature_invalid(self):
        """Тест: Отклонение неверной подписи"""
        handler = ManusWebhookHandler(secret="test-secret")
        payload = "test payload"
        invalid_signature = "invalid_signature_123"

        with pytest.raises(ManusWebhookVerificationError):
            handler.verify_signature(payload, invalid_signature)

    def test_register_handler_via_decorator(self):
        """Тест: Регистрация обработчика через декоратор"""
        handler = ManusWebhookHandler(secret="test-secret")

        @handler.on("task.completed")
        def custom_handler(event_data):
            return {"custom": "response"}

        assert "task.completed" in handler._handlers

    def test_register_handler_programmatically(self):
        """Тест: Программная регистрация обработчика"""
        handler = ManusWebhookHandler(secret="test-secret")

        def custom_handler(event_data):
            return {"result": "ok"}

        handler.register_handler("task.started", custom_handler)
        assert "task.started" in handler._handlers

    def test_handle_webhook_with_custom_handler(self):
        """Тест: Обработка webhook с кастомным обработчиком"""
        handler = ManusWebhookHandler(secret="test-secret")

        # Регистрируем обработчик
        @handler.on("task.completed")
        def custom_handler(event_data):
            return {"processed": event_data["task_id"]}

        # Создаем webhook payload
        event_data = {"task_id": "task_123", "result": "Done"}
        payload = json.dumps(event_data)

        # Генерируем подпись
        signature = hmac.new(
            "test-secret".encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Обрабатываем webhook
        result = handler.handle_webhook(
            event_type="task.completed",
            payload=payload,
            signature=signature
        )

        assert result["processed"] == "task_123"

    def test_handle_webhook_default_handler(self):
        """Тест: Default обработчик для известных событий"""
        handler = ManusWebhookHandler(secret="test-secret")

        event_data = {"task_id": "task_456"}
        payload = json.dumps(event_data)
        signature = hmac.new(
            "test-secret".encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Обрабатываем без кастомного обработчика
        result = handler.handle_webhook(
            event_type="task.started",
            payload=payload,
            signature=signature
        )

        assert result["status"] == "acknowledged"

    def test_handle_webhook_unknown_event(self):
        """Тест: Неизвестный тип события"""
        handler = ManusWebhookHandler(secret="test-secret")

        payload = json.dumps({"data": "test"})
        signature = hmac.new(
            "test-secret".encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        result = handler.handle_webhook(
            event_type="unknown.event",
            payload=payload,
            signature=signature
        )

        assert result["status"] == "unknown_event"

    def test_webhook_metrics(self):
        """Тест: Метрики webhook handler"""
        handler = ManusWebhookHandler(secret="test-secret")

        metrics = handler.get_metrics()
        assert metrics["event_count"] == 0
        assert metrics["verification_failures"] == 0


class TestManusExceptions:
    """Тесты для исключений"""

    def test_manus_exception_with_details(self):
        """Тест: ManusException с деталями"""
        exc = ManusException(
            "Test error",
            details={"code": 123, "extra": "info"}
        )

        assert str(exc) == "Test error | Details: {'code': 123, 'extra': 'info'}"

    def test_manus_api_error(self):
        """Тест: ManusAPIError"""
        exc = ManusAPIError(
            "API failed",
            status_code=500,
            response_text="Internal server error"
        )

        assert exc.details["status_code"] == 500
        assert exc.details["response_text"] == "Internal server error"

    def test_manus_task_timeout_error(self):
        """Тест: ManusTaskTimeoutError"""
        exc = ManusTaskTimeoutError("task_123", 300)

        assert exc.task_id == "task_123"
        assert exc.timeout == 300
        assert "task_123" in str(exc)

    def test_manus_task_failed_error(self):
        """Тест: ManusTaskFailedError"""
        exc = ManusTaskFailedError("task_456", "Out of memory")

        assert exc.task_id == "task_456"
        assert exc.error_message == "Out of memory"


# Integration tests (требуют реального API ключа)
@pytest.mark.integration
class TestManusIntegration:
    """Integration тесты (только если есть API ключ)"""

    @pytest.fixture
    def client(self):
        """Fixture для реального клиента"""
        api_key = os.getenv("MANUS_API_KEY")
        if not api_key:
            pytest.skip("MANUS_API_KEY not set")
        return ManusClient(api_key=api_key)

    def test_real_create_task(self, client):
        """Реальное создание задачи (если есть API ключ)"""
        task = client.create_task(
            prompt="Simple test task",
            context="Testing Manus integration"
        )

        assert "task_id" in task
        assert task["task_id"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
