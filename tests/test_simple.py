#!/usr/bin/env python3
"""
Простой тестовый скрипт для проверки Manus и OpenRouter API
Simple test script to verify Manus and OpenRouter API connectivity
"""

import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

print("=" * 60)
print("🧪 ПРОСТОЙ ТЕСТ API")
print("=" * 60)
print()

# Шаг 1: Проверить что ключи загружены
print("📋 Шаг 1: Проверка переменных окружения")
print("-" * 60)

manus_key = os.getenv("MANUS_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if manus_key:
    print(f"✅ MANUS_API_KEY: {manus_key[:15]}...{manus_key[-10:]}")
else:
    print("❌ MANUS_API_KEY не найден!")

if openrouter_key:
    print(f"✅ OPENROUTER_API_KEY: {openrouter_key[:15]}...{openrouter_key[-10:]}")
else:
    print("❌ OPENROUTER_API_KEY не найден!")

print()

# Шаг 2: Проверить импорты
print("📋 Шаг 2: Проверка импортов")
print("-" * 60)

try:
    from src.manus import ManusClient
    print("✅ ManusClient импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта ManusClient: {e}")
    exit(1)

try:
    from src.openrouter import OpenRouterClient
    print("✅ OpenRouterClient импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта OpenRouterClient: {e}")
    # Не критично для этого теста

print()

# Шаг 3: Тест OpenRouter API (бесплатная модель)
print("📋 Шаг 3: Тест OpenRouter API")
print("-" * 60)

try:
    from src.openrouter import OpenRouterClient, Message

    client = OpenRouterClient()
    print("✅ OpenRouter клиент создан")

    messages = [Message(role="user", content="Say 'Hello from OpenRouter!' in one sentence.")]
    print("📤 Отправка запроса к OpenRouter...")

    response = client.chat_completion(
        messages=messages,
        model="xiaomi/mimo-v2-flash:free"
    )

    answer = response.choices[0].message.content
    print(f"✅ Ответ получен: {answer}")

    # Проверить метрики
    metrics = client.get_metrics_summary()
    print(f"📊 Метрики: {metrics['total_calls']} запросов, cost: {metrics['total_cost_usd']}")

except Exception as e:
    print(f"❌ Ошибка OpenRouter API: {e}")
    import traceback
    traceback.print_exc()

print()

# Шаг 4: Тест Manus API (создание задачи)
print("📋 Шаг 4: Тест Manus API")
print("-" * 60)

try:
    client = ManusClient()
    print("✅ Manus клиент создан")

    # Создать простую тестовую задачу
    print("📤 Создание тестовой задачи в Manus...")

    task_response = client.create_task(
        prompt="Hello! This is a test. Please respond with 'Test successful!'",
        context="This is a simple connectivity test."
    )

    if "error" in task_response:
        print(f"❌ Ошибка создания задачи: {task_response['error']}")
        print(f"   Сообщение: {task_response.get('message', 'No details')}")
    elif "id" in task_response or "task_id" in task_response:
        task_id = task_response.get("id") or task_response.get("task_id")
        print(f"✅ Задача создана успешно!")
        print(f"   Task ID: {task_id}")
        print(f"   Status: {task_response.get('status', 'unknown')}")
    else:
        print(f"⚠️  Неожиданный ответ: {task_response}")

    # Получить метрики
    metrics = client.get_metrics()
    print(f"📊 Метрики Manus: {metrics['request_count']} запросов")

except Exception as e:
    print(f"❌ Ошибка Manus API: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✅ ТЕСТ ЗАВЕРШЕН!")
print("=" * 60)
print()
print("📝 Следующие шаги:")
print("   1. Если OpenRouter работает - API ключ правильный ✅")
print("   2. Если Manus возвращает ошибку - проверьте:")
print("      - Правильность API ключа")
print("      - Доступность API (https://api.manus.ai/v1)")
print("      - Формат запроса")
print()
