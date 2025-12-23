"""
Manus AI Integration Client
Интеграция с Manus AI для автоматизации задач
"""

import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime


class ManusClient:
    """Клиент для работы с Manus AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация Manus клиента
        
        Args:
            api_key: API ключ Manus (по умолчанию из env)
        """
        self.api_key = api_key or os.getenv("MANUS_API_KEY")
        self.base_url = "https://api.manus.ai/v1"  # Базовый URL Manus API
        
        if not self.api_key:
            raise ValueError("MANUS_API_KEY не найден!")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
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
            context: Дополнительный контекст
            tools: Список инструментов для использования
            
        Returns:
            Информация о созданной задаче
            
        Example:
            >>> client = ManusClient()
            >>> task = client.create_task(
            ...     prompt="Протестируй функцию chat_completion",
            ...     context="https://github.com/FreeAiHub/openrouter/blob/main/src/openrouter/client.py"
            ... )
        """
        payload = {
            "prompt": prompt,
            "context": context or "",
            "tools": tools or [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "error": "Exception",
                "message": str(e)
            }
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Информация о задаче
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "error": "Exception",
                "message": str(e)
            }
    
    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Ждать завершения задачи
        
        Args:
            task_id: ID задачи
            timeout: Максимальное время ожидания (секунды)
            poll_interval: Интервал проверки (секунды)
            
        Returns:
            Результат задачи
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task(task_id)
            
            if task.get("status") == "completed":
                return task
            elif task.get("status") == "failed":
                return task
            
            time.sleep(poll_interval)
        
        return {
            "error": "Timeout",
            "message": f"Задача не завершилась за {timeout} секунд"
        }
    
    def analyze_code(
        self,
        code_url: str,
        task: str = "Проанализируй код и найди возможные проблемы"
    ) -> Dict[str, Any]:
        """
        Анализ кода через Manus
        
        Args:
            code_url: URL файла на GitHub
            task: Описание задачи анализа
            
        Returns:
            Результат анализа
        """
        return self.create_task(
            prompt=task,
            context=code_url,
            tools=["code_analysis", "github"]
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
            test_cases: Тестовые случаи
            
        Returns:
            Результаты тестирования
        """
        context = f"URL: {function_url}"
        if test_cases:
            context += f"\nТесты: {test_cases}"
        
        return self.create_task(
            prompt="Протестируй эту функцию с предоставленными тестами",
            context=context,
            tools=["testing", "code_execution"]
        )


class ManusWebhookHandler:
    """Обработчик webhooks от Manus"""
    
    def __init__(self, secret: Optional[str] = None):
        """
        Инициализация обработчика webhooks
        
        Args:
            secret: Секретный ключ для верификации webhooks
        """
        self.secret = secret or os.getenv("MANUS_WEBHOOK_SECRET")
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Проверка подписи webhook
        
        Args:
            payload: Тело запроса
            signature: Подпись из заголовка
            
        Returns:
            True если подпись валидна
        """
        import hmac
        import hashlib
        
        if not self.secret:
            return False
        
        expected = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def handle_task_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка события завершения задачи
        
        Args:
            event_data: Данные события
            
        Returns:
            Ответ для webhook
        """
        task_id = event_data.get("task_id")
        result = event_data.get("result")
        
        # Здесь можно добавить логику:
        # - Создать комментарий в GitHub Issue
        # - Отправить уведомление
        # - Обновить статус в базе данных
        
        return {
            "status": "processed",
            "task_id": task_id,
            "action": "github_comment_created"
        }
    
    def handle_webhook(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главный обработчик webhooks
        
        Args:
            event_type: Тип события
            event_data: Данные события
            
        Returns:
            Ответ для webhook
        """
        handlers = {
            "task.completed": self.handle_task_completed,
            "task.failed": lambda d: {"status": "error_logged"},
            "task.started": lambda d: {"status": "acknowledged"},
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        
        return {"status": "unknown_event", "event_type": event_type}


# Пример использования
if __name__ == "__main__":
    # Создание клиента
    client = ManusClient(api_key="sk-Ng1s0QVjeZXa1DjQjJw8qZbB7xL96AdiKAYdhgu-mMzn5tvwd8XlJRfe-ZxSMQ8mb40OP4nrRyxjsAlobevlHUWZ8Pkt")
    
    # Создание задачи
    task = client.create_task(
        prompt="Протестируй базовый пример OpenRouter",
        context="https://github.com/FreeAiHub/openrouter/blob/main/examples/basic_usage.py"
    )
    
    print("Задача создана:", task)
    
    # Анализ кода
    analysis = client.analyze_code(
        code_url="https://github.com/FreeAiHub/openrouter/blob/main/src/openrouter/client.py",
        task="Проверь на наличие багов и проблем безопасности"
    )
    
    print("Анализ запущен:", analysis)
