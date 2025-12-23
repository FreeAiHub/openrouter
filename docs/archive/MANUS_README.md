# Инструкция для Manus - OpenRouter Integration

## Контекст проекта (Project Context)

Это enterprise-grade интеграция с OpenRouter API для работы с AI моделями.

**Репозиторий (Repository):** https://github.com/FreeAiHub/openrouter

**API Key работает:** ✅ Подтверждено тестированием с моделью `xiaomi/mimo-v2-flash:free`

## Структура проекта (Project Structure)

```
openrouter-integration/
├── config/settings.py          # Конфигурация (Pydantic settings)
├── src/openrouter/
│   ├── client.py              # Главный клиент с retry/circuit breaker
│   ├── models.py              # Pydantic модели для type safety
│   └── exceptions.py          # Кастомные исключения (exceptions)
├── examples/                   # Примеры использования
│   ├── basic_usage.py         # Начните отсюда
│   ├── original_test.py       # Ваши тесты
│   └── original_examples.py   # Ваши примеры
├── tests/                      # Тесты
├── docs/DEPLOYMENT.md         # Деплой на AWS/K8s
├── .env.example               # Шаблон конфигурации
└── requirements.txt           # Зависимости (dependencies)
```

## Ключевые файлы для работы

### 1. Конфигурация
- **Файл:** `config/settings.py`
- **Что делает:** Управляет настройками через environment variables
- **Редактировать:** `.env` файл (не settings.py)

### 2. Главный клиент
- **Файл:** `src/openrouter/client.py`
- **Что делает:** API клиент с retry логикой и circuit breaker
- **Фичи:** Автоматические повторы, отслеживание стоимости, метрики

### 3. Модели данных
- **Файл:** `src/openrouter/models.py`
- **Что делает:** Pydantic модели для валидации

### 4. Примеры
- **Файл:** `examples/basic_usage.py`
- **Что делает:** 7 практических примеров использования

## Быстрый старт (Quick Start)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/FreeAiHub/openrouter.git
cd openrouter

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env
cp .env.example .env
# Добавить в .env:
# OPENROUTER_API_KEY=sk-or-v1-ваш-ключ

# 4. Тестировать
python examples/basic_usage.py
```

## Использование в коде

### Простой пример
```python
from src.openrouter import OpenRouterClient, Message

# Создать клиент
with OpenRouterClient() as client:
    # Отправить сообщение
    messages = [Message(role="user", content="Привет!")]
    response = client.chat_completion(messages)
    
    # Получить ответ
    print(response.choices[0].message.content)
```

### Со streaming
```python
messages = [Message(role="user", content="Напиши рассказ")]

for chunk in client.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### Отслеживание затрат
```python
# После нескольких запросов
summary = client.get_metrics_summary()
print(f"Стоимость: {summary['total_cost_usd']}")
print(f"Токенов использовано: {summary['total_tokens']}")
```

## Бесплатные модели (Free Models)

Используйте для разработки ($0.00):

1. **xiaomi/mimo-v2-flash:free** - Универсальная модель
2. **kwaipilot/kat-coder-pro-v1:free** - Для кода
3. **z-ai/glm-4.5-air:free** - Лёгкая модель

## Дешёвые модели (Cheap Models)

Для production ($0.14 за 1M токенов):

1. **deepseek/deepseek-chat** - Лучшее соотношение цена/качество
2. **qwen/qwen-2.5-7b-instruct** - Быстрая и дешёвая

## Enterprise фичи

✅ **Automatic Retry** - Автоматические повторы с exponential backoff
✅ **Circuit Breaker** - Защита от каскадных ошибок
✅ **Cost Tracking** - Отслеживание затрат в реальном времени
✅ **Type Safety** - Полная типизация через Pydantic
✅ **Error Handling** - Продвинутая обработка ошибок
✅ **Connection Pool** - Пул соединений для производительности

## Важные параметры (Settings)

В `.env` файле:

```bash
# API ключ (обязательно)
OPENROUTER_API_KEY=sk-or-v1-ваш-ключ

# Модель по умолчанию
DEFAULT_MODEL=xiaomi/mimo-v2-flash:free

# Окружение
ENVIRONMENT=development  # или production

# Retry настройки
MAX_RETRIES=3           # Максимум попыток
REQUEST_TIMEOUT=30      # Таймаут в секундах

# Лимиты
MAX_TOKENS_PER_REQUEST=2000
```

## Когда использовать что

### Для разработки (Development)
- Модель: `xiaomi/mimo-v2-flash:free`
- Стоимость: $0.00
- Лимит: 50 запросов/день

### Для production
- Модель: `deepseek/deepseek-chat`
- Стоимость: $0.14 за 1M токенов
- Лимит: Без ограничений

## Обработка ошибок (Error Handling)

```python
from src.openrouter.exceptions import (
    RateLimitError,        # Превышен лимит запросов
    AuthenticationError,   # Неверный API ключ
    InvalidRequestError,   # Неверный запрос
    ModelNotFoundError     # Модель не найдена
)

try:
    response = client.chat_completion(messages)
except RateLimitError as e:
    print(f"Лимит превышен: {e.message}")
    # Подождать и повторить
except AuthenticationError:
    print("Неверный API ключ")
```

## Тестирование (Testing)

```bash
# Запустить все тесты
pytest tests/ -v

# Интеграционные тесты (нужен API ключ)
export OPENROUTER_API_KEY="ваш-ключ"
pytest tests/test_integration.py -v

# С покрытием кода
pytest --cov=src --cov-report=html
```

## Деплой (Deployment)

См. `docs/DEPLOYMENT.md` для:
- Docker контейнеров
- Kubernetes манифестов
- AWS ECS/Fargate
- Google Cloud Run

## Частые проблемы (Common Issues)

### "API key not found"
**Решение:** Добавьте ключ в `.env` файл

### "Rate limit exceeded"
**Решение:** Бесплатный план = 50 запросов/день. Подождите или обновите план.

### "Model not found"
**Решение:** Проверьте ID модели на openrouter.ai/models

## Мониторинг и метрики

```python
# Получить статистику
summary = client.get_metrics_summary()

# Возвращает:
# {
#   "total_calls": 10,
#   "successful_calls": 9,
#   "success_rate": "90.00%",
#   "total_tokens": 1500,
#   "total_cost_usd": "$0.00",
#   "average_duration_ms": "245.32"
# }
```

## Ссылки (Links)

- **GitHub:** https://github.com/FreeAiHub/openrouter
- **OpenRouter Docs:** https://openrouter.ai/docs
- **Модели:** https://openrouter.ai/models
- **Цены:** https://openrouter.ai/pricing

## Контакты для вопросов

- OpenRouter Support: https://openrouter.ai/support
- GitHub Issues: https://github.com/FreeAiHub/openrouter/issues

---

**Примечание:** Этот проект создан Claude (Anthropic) в сотрудничестве с Manus для enterprise интеграции OpenRouter API.
