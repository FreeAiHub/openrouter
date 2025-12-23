"""
Pydantic Models for Manus AI Integration
Модели данных для работы с Manus AI API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ManusTaskRequest(BaseModel):
    """Запрос на создание задачи в Manus"""

    prompt: str = Field(..., description="Описание задачи для выполнения")
    context: Optional[str] = Field(None, description="Дополнительный контекст (URL, текст)")
    tools: List[str] = Field(default_factory=list, description="Список инструментов для использования")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Время создания задачи"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Проанализируй код на наличие багов",
                "context": "https://github.com/user/repo/blob/main/file.py",
                "tools": ["code_analysis", "github"],
                "timestamp": "2025-12-23T10:00:00"
            }
        }
    )


class ManusTaskStatus(BaseModel):
    """Статус задачи в Manus"""

    task_id: str = Field(..., description="Уникальный ID задачи")
    status: str = Field(..., description="Статус: pending, running, completed, failed")
    created_at: datetime = Field(..., description="Время создания задачи")
    updated_at: Optional[datetime] = Field(None, description="Время последнего обновления")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Прогресс выполнения (0-100)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "task_abc123",
                "status": "running",
                "created_at": "2025-12-23T10:00:00",
                "updated_at": "2025-12-23T10:01:00",
                "progress": 45.5
            }
        }
    )


class ManusTaskResult(BaseModel):
    """Результат выполнения задачи"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Финальный статус: completed или failed")
    result: Optional[Dict[str, Any]] = Field(None, description="Результаты выполнения")
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если статус failed)")
    execution_time: Optional[float] = Field(None, description="Время выполнения в секундах")
    cost: Optional[float] = Field(None, description="Стоимость выполнения в USD")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "task_abc123",
                "status": "completed",
                "result": {
                    "analysis": "Код выглядит хорошо, проблем не найдено",
                    "suggestions": ["Добавить type hints", "Улучшить docstrings"]
                },
                "execution_time": 12.5,
                "cost": 0.002
            }
        }
    )


class ManusWebhookEvent(BaseModel):
    """Событие webhook от Manus"""

    event_type: str = Field(..., description="Тип события: task.started, task.completed, task.failed")
    task_id: str = Field(..., description="ID задачи")
    timestamp: datetime = Field(..., description="Время события")
    data: Dict[str, Any] = Field(default_factory=dict, description="Данные события")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "task.completed",
                "task_id": "task_abc123",
                "timestamp": "2025-12-23T10:05:00",
                "data": {
                    "result": "Анализ завершен успешно",
                    "cost": 0.002
                }
            }
        }
    )


class ManusCodeAnalysisRequest(BaseModel):
    """Запрос на анализ кода"""

    code_url: str = Field(..., description="URL файла кода на GitHub")
    task: str = Field(
        default="Проанализируй код и найди возможные проблемы",
        description="Описание задачи анализа"
    )
    check_security: bool = Field(default=True, description="Проверять безопасность")
    check_performance: bool = Field(default=True, description="Проверять производительность")
    check_style: bool = Field(default=False, description="Проверять стиль кода")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code_url": "https://github.com/user/repo/blob/main/app.py",
                "task": "Проверь на уязвимости безопасности",
                "check_security": True,
                "check_performance": True,
                "check_style": False
            }
        }
    )


class ManusTestRequest(BaseModel):
    """Запрос на тестирование функции"""

    function_url: str = Field(..., description="URL функции на GitHub")
    test_cases: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Тестовые случаи для проверки"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "function_url": "https://github.com/user/repo/blob/main/utils.py#L10-L20",
                "test_cases": [
                    {"input": {"x": 1, "y": 2}, "expected": 3},
                    {"input": {"x": 0, "y": 0}, "expected": 0}
                ]
            }
        }
    )


class ManusConfig(BaseModel):
    """Конфигурация Manus клиента"""

    api_key: str = Field(..., description="API ключ Manus")
    base_url: str = Field(
        default="https://api.manus.ai/v1",
        description="Базовый URL Manus API"
    )
    timeout: int = Field(default=30, description="Timeout для запросов (секунды)")
    max_retries: int = Field(default=3, description="Максимум попыток retry")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key": "sk-manus-xxx",
                "base_url": "https://api.manus.ai/v1",
                "timeout": 30,
                "max_retries": 3
            }
        }
    )
