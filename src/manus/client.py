"""
Manus AI Integration Client
Enterprise-grade клиент для работы с Manus AI API
"""

import os
import time
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import (
    ManusTaskRequest,
    ManusTaskStatus,
    ManusTaskResult,
    ManusCodeAnalysisRequest,
    ManusTestRequest,
    ManusConfig,
)
from .exceptions import (
    ManusAPIError,
    ManusAuthenticationError,
    ManusRateLimitError,
    ManusTaskNotFoundError,
    ManusTaskTimeoutError,
    ManusTaskFailedError,
    ManusConfigurationError,
    ManusNetworkError,
)


class ManusClient:
    """
    Enterprise-grade клиент для работы с Manus AI API

    Предоставляет высокоуровневый интерфейс для:
    - Создания и управления задачами
    - Анализа кода
    - Автоматического тестирования
    - Интеграции с GitHub

    Example:
        >>> from src.manus import ManusClient
        >>> client = ManusClient(api_key="sk-manus-xxx")
        >>> task = client.create_task(
        ...     prompt="Проанализируй код",
        ...     context="https://github.com/user/repo/file.py"
        ... )
        >>> result = client.wait_for_completion(task["task_id"])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Инициализация Manus клиента

        Args:
            api_key: API ключ Manus (по умолчанию из MANUS_API_KEY env)
            base_url: Базовый URL API (по умолчанию https://api.manus.ai/v1)
            timeout: Timeout для запросов в секундах
            max_retries: Максимальное количество retry попыток

        Raises:
            ManusConfigurationError: Если API ключ не предоставлен
        """
        self.api_key = api_key or os.getenv("MANUS_API_KEY")
        if not self.api_key:
            raise ManusConfigurationError(
                "MANUS_API_KEY не найден. Укажите api_key или установите переменную окружения."
            )

        self.base_url = base_url or os.getenv("MANUS_BASE_URL", "https://api.manus.ai/v1")
        self.timeout = timeout
        self.max_retries = max_retries

        self.headers = {
            "API_KEY": self.api_key,  # Manus использует API_KEY вместо Bearer
            "Content-Type": "application/json",
        }

        # Счетчики для метрик
        self._request_count = 0
        self._error_count = 0

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос с retry логикой

        Args:
            method: HTTP метод (GET, POST, etc.)
            endpoint: API endpoint (без base_url)
            **kwargs: Дополнительные параметры для requests

        Returns:
            Ответ API в виде dict

        Raises:
            ManusAPIError: При ошибках API
            ManusNetworkError: При сетевых ошибках
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                self._request_count += 1
                response = requests.request(method, url, **kwargs)

                # Обработка различных HTTP статусов
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise ManusAuthenticationError("Invalid API key")
                elif response.status_code == 404:
                    raise ManusAPIError(
                        "Resource not found",
                        status_code=404,
                        response_text=response.text
                    )
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise ManusRateLimitError(retry_after=retry_after)
                else:
                    raise ManusAPIError(
                        f"API request failed",
                        status_code=response.status_code,
                        response_text=response.text
                    )

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                self._error_count += 1
                raise ManusNetworkError(
                    f"Network error after {self.max_retries} attempts",
                    original_error=e
                )

        # Если дошли сюда - все retry попытки исчерпаны
        self._error_count += 1
        raise ManusNetworkError(
            f"Request failed after {self.max_retries} attempts",
            original_error=last_exception
        )

    def create_task(
        self,
        prompt: str,
        context: Optional[str] = None,
        tools: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Создать задачу для Manus

        Args:
            prompt: Описание задачи
            context: Дополнительный контекст (URL, текст)
            tools: Список инструментов для использования

        Returns:
            Информация о созданной задаче с task_id

        Example:
            >>> task = client.create_task(
            ...     prompt="Протестируй функцию chat_completion",
            ...     context="https://github.com/FreeAiHub/openrouter/blob/main/src/openrouter/client.py",
            ...     tools=["code_analysis", "testing"]
            ... )
            >>> print(task["task_id"])
        """
        task_request = ManusTaskRequest(
            prompt=prompt,
            context=context or "",
            tools=tools or [],
        )

        return self._make_request(
            "POST",
            "/tasks",
            json=task_request.model_dump()
        )

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи

        Args:
            task_id: ID задачи

        Returns:
            Информация о задаче (статус, прогресс, результат)

        Raises:
            ManusTaskNotFoundError: Если задача не найдена
        """
        try:
            return self._make_request("GET", f"/tasks/{task_id}")
        except ManusAPIError as e:
            if e.details.get("status_code") == 404:
                raise ManusTaskNotFoundError(task_id)
            raise

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Ждать завершения задачи с polling

        Args:
            task_id: ID задачи
            timeout: Максимальное время ожидания (секунды)
            poll_interval: Интервал проверки (секунды)

        Returns:
            Результат выполненной задачи

        Raises:
            ManusTaskTimeoutError: Если задача не завершилась за timeout
            ManusTaskFailedError: Если задача завершилась с ошибкой

        Example:
            >>> task = client.create_task(prompt="Analyze code")
            >>> result = client.wait_for_completion(task["task_id"], timeout=120)
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            task = self.get_task(task_id)
            status = task.get("status")

            if status == "completed":
                return task
            elif status == "failed":
                error_msg = task.get("error", "Unknown error")
                raise ManusTaskFailedError(task_id, error_msg)

            time.sleep(poll_interval)

        raise ManusTaskTimeoutError(task_id, timeout)

    def analyze_code(
        self,
        code_url: str,
        task: str = "Проанализируй код и найди возможные проблемы",
        check_security: bool = True,
        check_performance: bool = True,
        check_style: bool = False
    ) -> Dict[str, Any]:
        """
        Анализ кода через Manus

        Args:
            code_url: URL файла на GitHub
            task: Описание задачи анализа
            check_security: Проверять безопасность
            check_performance: Проверять производительность
            check_style: Проверять стиль кода

        Returns:
            Информация о созданной задаче анализа

        Example:
            >>> analysis = client.analyze_code(
            ...     code_url="https://github.com/user/repo/file.py",
            ...     task="Найди уязвимости безопасности",
            ...     check_security=True
            ... )
        """
        analysis_request = ManusCodeAnalysisRequest(
            code_url=code_url,
            task=task,
            check_security=check_security,
            check_performance=check_performance,
            check_style=check_style
        )

        tools = ["code_analysis", "github"]
        if check_security:
            tools.append("security_scan")
        if check_performance:
            tools.append("performance_analysis")

        return self.create_task(
            prompt=analysis_request.task,
            context=analysis_request.code_url,
            tools=tools
        )

    def test_function(
        self,
        function_url: str,
        test_cases: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Тестирование функции через Manus

        Args:
            function_url: URL функции на GitHub
            test_cases: Тестовые случаи для проверки

        Returns:
            Информация о созданной задаче тестирования

        Example:
            >>> tests = client.test_function(
            ...     function_url="https://github.com/user/repo/utils.py#L10-L20",
            ...     test_cases=[
            ...         {"input": {"x": 1, "y": 2}, "expected": 3},
            ...         {"input": {"x": 0, "y": 0}, "expected": 0}
            ...     ]
            ... )
        """
        test_request = ManusTestRequest(
            function_url=function_url,
            test_cases=test_cases
        )

        context = f"URL: {test_request.function_url}"
        if test_request.test_cases:
            context += f"\nТесты: {test_request.test_cases}"

        return self.create_task(
            prompt="Протестируй эту функцию с предоставленными тестами",
            context=context,
            tools=["testing", "code_execution"]
        )

    def get_metrics(self) -> Dict[str, int]:
        """
        Получить метрики использования клиента

        Returns:
            Словарь с метриками (request_count, error_count)
        """
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "success_rate": (
                (self._request_count - self._error_count) / self._request_count * 100
                if self._request_count > 0
                else 0
            )
        }

    def __repr__(self) -> str:
        return f"ManusClient(base_url='{self.base_url}', timeout={self.timeout})"
