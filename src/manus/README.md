# Manus AI Integration Module

Enterprise-grade интеграция с Manus AI для автоматизации задач разработки.

## Структура модуля

```
src/manus/
├── __init__.py          # Экспорты и инициализация модуля
├── client.py            # ManusClient - основной клиент API
├── webhook.py           # ManusWebhookHandler - обработчик webhooks
├── models.py            # Pydantic модели для типизации
├── exceptions.py        # Кастомные исключения
└── README.md           # Эта документация
```

## Быстрый старт

### 1. Установка и настройка

```bash
# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env

# Добавьте ваш API ключ в .env
MANUS_API_KEY=sk-manus-xxxxxx
```

### 2. Базовое использование

```python
from src.manus import ManusClient

# Создание клиента
client = ManusClient()

# Создание задачи
task = client.create_task(
    prompt="Проанализируй код на наличие багов",
    context="https://github.com/user/repo/file.py"
)

print(f"Task ID: {task['task_id']}")

# Ожидание результата
result = client.wait_for_completion(task['task_id'])
print(f"Result: {result['result']}")
```

## Основные компоненты

### ManusClient

Основной клиент для работы с Manus AI API.

**Функции:**
- `create_task()` - Создание задачи
- `get_task()` - Получение статуса задачи
- `wait_for_completion()` - Ожидание результата с polling
- `analyze_code()` - Анализ кода на баги/безопасность
- `test_function()` - Автоматическое тестирование функций
- `get_metrics()` - Получение метрик использования

**Пример - Анализ кода:**

```python
from src.manus import ManusClient

client = ManusClient()

# Детальный анализ с параметрами
analysis = client.analyze_code(
    code_url="https://github.com/user/repo/main.py",
    task="Найди уязвимости безопасности и проблемы производительности",
    check_security=True,
    check_performance=True,
    check_style=False
)

# Дождаться результата
result = client.wait_for_completion(analysis['task_id'], timeout=120)
print(result['result'])
```

**Пример - Тестирование функции:**

```python
# Тестирование с тест-кейсами
test_task = client.test_function(
    function_url="https://github.com/user/repo/utils.py#L10-L20",
    test_cases=[
        {"input": {"x": 1, "y": 2}, "expected": 3},
        {"input": {"x": 0, "y": 0}, "expected": 0}
    ]
)
```

### ManusWebhookHandler

Обработчик webhooks от Manus для асинхронных уведомлений.

**Функции:**
- `verify_signature()` - Верификация подписи webhook
- `on()` - Декоратор для регистрации обработчиков
- `register_handler()` - Программная регистрация обработчиков
- `handle_webhook()` - Главный обработчик входящих webhooks

**Пример - Flask integration:**

```python
from flask import Flask, request, jsonify
from src.manus import ManusWebhookHandler

app = Flask(__name__)
handler = ManusWebhookHandler()

# Регистрация обработчиков через декоратор
@handler.on("task.completed")
def on_task_completed(event_data):
    task_id = event_data['task_id']
    result = event_data['result']

    # Создать комментарий в GitHub
    # Отправить уведомление
    # Обновить базу данных

    return {"status": "processed"}

@handler.on("task.failed")
def on_task_failed(event_data):
    print(f"Task failed: {event_data['error']}")
    return {"status": "error_logged"}

# Webhook endpoint
@app.route('/webhooks/manus', methods=['POST'])
def manus_webhook():
    result = handler.handle_webhook(
        event_type=request.headers.get('X-Manus-Event'),
        payload=request.data.decode(),
        signature=request.headers.get('X-Manus-Signature')
    )
    return jsonify(result)
```

### Pydantic Models

Все запросы и ответы типизированы через Pydantic модели:

- `ManusTaskRequest` - Запрос на создание задачи
- `ManusTaskStatus` - Статус задачи
- `ManusTaskResult` - Результат выполнения
- `ManusWebhookEvent` - Событие webhook
- `ManusCodeAnalysisRequest` - Запрос анализа кода
- `ManusTestRequest` - Запрос тестирования
- `ManusConfig` - Конфигурация клиента

**Пример использования моделей:**

```python
from src.manus.models import ManusTaskRequest, ManusCodeAnalysisRequest

# Создание типизированного запроса
task_req = ManusTaskRequest(
    prompt="Analyze code",
    context="https://github.com/...",
    tools=["code_analysis"]
)

# Валидация автоматическая через Pydantic
analysis_req = ManusCodeAnalysisRequest(
    code_url="https://github.com/...",
    check_security=True
)
```

### Исключения

Все ошибки типизированы через кастомные исключения:

- `ManusException` - Базовое исключение
- `ManusAPIError` - Ошибка API
- `ManusAuthenticationError` - Ошибка аутентификации
- `ManusRateLimitError` - Превышен лимит запросов
- `ManusTaskNotFoundError` - Задача не найдена
- `ManusTaskTimeoutError` - Timeout выполнения
- `ManusTaskFailedError` - Задача провалилась
- `ManusWebhookVerificationError` - Ошибка верификации webhook
- `ManusConfigurationError` - Ошибка конфигурации
- `ManusNetworkError` - Сетевая ошибка

**Пример обработки ошибок:**

```python
from src.manus import ManusClient
from src.manus.exceptions import (
    ManusTaskTimeoutError,
    ManusTaskFailedError,
    ManusAPIError
)

client = ManusClient()

try:
    task = client.create_task(prompt="Test")
    result = client.wait_for_completion(task['task_id'], timeout=60)

except ManusTaskTimeoutError as e:
    print(f"Task timed out after {e.timeout} seconds")

except ManusTaskFailedError as e:
    print(f"Task {e.task_id} failed: {e.error_message}")

except ManusAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.details.get('status_code')}")
```

## Конфигурация

### Environment Variables

Все настройки через переменные окружения в `.env`:

```bash
# Manus API
MANUS_API_KEY=sk-manus-xxxxx
MANUS_BASE_URL=https://api.manus.ai/v1

# Webhook
MANUS_WEBHOOK_SECRET=your-webhook-secret

# Настройки
MANUS_DEFAULT_TIMEOUT=300
MANUS_POLL_INTERVAL=5
MANUS_MAX_RETRIES=3
```

### Программная конфигурация

```python
from src.manus import ManusClient

# Кастомные настройки
client = ManusClient(
    api_key="sk-manus-xxx",
    base_url="https://api.manus.ai/v1",
    timeout=60,
    max_retries=5
)
```

## Метрики и мониторинг

### Метрики клиента

```python
metrics = client.get_metrics()
print(f"Requests: {metrics['request_count']}")
print(f"Errors: {metrics['error_count']}")
print(f"Success rate: {metrics['success_rate']}%")
```

### Метрики webhook handler

```python
metrics = handler.get_metrics()
print(f"Events: {metrics['event_count']}")
print(f"Failures: {metrics['verification_failures']}")
print(f"Handlers: {metrics['registered_handlers']}")
```

## Примеры использования

Полные примеры в `/examples/manus_example.py`:

```bash
python examples/manus_example.py
```

## Интеграция с другими модулями

### С OpenRouter

```python
from src.openrouter import OpenRouterClient
from src.manus import ManusClient

# Manus анализирует код
manus = ManusClient()
analysis = manus.analyze_code("https://github.com/...")

# OpenRouter генерирует фиксы
openrouter = OpenRouterClient()
response = openrouter.chat_completion([
    {"role": "user", "content": f"Создай фикс для: {analysis['result']}"}
])
```

### С GitHub webhooks

См. `/src/webhooks/github_handler.py` для полной интеграции.

## Testing

Запуск тестов:

```bash
# Все тесты
pytest tests/

# Только Manus тесты
pytest tests/ -k manus

# С coverage
pytest tests/ --cov=src/manus
```

## Лучшие практики

1. **Всегда используйте try-except** для обработки ошибок API
2. **Устанавливайте timeout** для `wait_for_completion()`
3. **Проверяйте webhook подписи** в production
4. **Используйте environment variables** для секретов
5. **Логируйте метрики** для мониторинга
6. **Не храните API ключи** в коде

## Troubleshooting

### "MANUS_API_KEY не найден"

Создайте `.env` файл и добавьте ключ:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте MANUS_API_KEY
```

### "Invalid webhook signature"

Убедитесь что `MANUS_WEBHOOK_SECRET` совпадает с настройками в Manus dashboard.

### "Task timeout"

Увеличьте timeout или poll_interval:
```python
result = client.wait_for_completion(
    task_id,
    timeout=600,  # 10 минут
    poll_interval=10
)
```

## Roadmap

- [ ] Batch операции для множественных задач
- [ ] WebSocket поддержка для real-time updates
- [ ] Кэширование результатов
- [ ] Retry с exponential backoff
- [ ] Prometheus метрики
- [ ] Async/await версия клиента

## Поддержка

- GitHub Issues: https://github.com/FreeAiHub/openrouter/issues
- Документация: [CLAUDE.md](../../CLAUDE.md)
- Примеры: [examples/](../../examples/)

## License

MIT License - см. LICENSE файл.
