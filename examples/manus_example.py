#!/usr/bin/env python3
"""
Manus AI Integration - Example Usage
Примеры использования нового Manus клиента

Этот файл демонстрирует:
1. Создание клиента Manus
2. Создание задач
3. Анализ кода
4. Тестирование функций
5. Ожидание результатов
6. Работу с webhooks

Перед запуском:
    1. Скопируйте .env.example в .env
    2. Заполните MANUS_API_KEY в .env
    3. Установите зависимости: pip install -r requirements.txt

Запуск:
    python examples/manus_example.py
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.manus import ManusClient, ManusWebhookHandler
from src.manus.exceptions import (
    ManusAPIError,
    ManusTaskTimeoutError,
    ManusTaskFailedError
)

# Загружаем .env
from dotenv import load_dotenv
load_dotenv()


def example_1_basic_usage():
    """Пример 1: Базовое использование Manus клиента"""
    print("\n" + "="*70)
    print("Пример 1: Базовое использование")
    print("="*70)

    # Создание клиента
    client = ManusClient()
    print(f"✅ Клиент создан: {client}")

    # Создание простой задачи
    task = client.create_task(
        prompt="Проанализируй следующий код на наличие багов",
        context="https://github.com/FreeAiHub/openrouter/blob/main/examples/basic_usage.py"
    )

    print(f"✅ Задача создана: {task.get('task_id')}")
    return task


def example_2_code_analysis():
    """Пример 2: Анализ кода"""
    print("\n" + "="*70)
    print("Пример 2: Анализ кода с проверкой безопасности")
    print("="*70)

    client = ManusClient()

    # Анализ кода с параметрами
    analysis = client.analyze_code(
        code_url="https://github.com/FreeAiHub/openrouter/blob/main/src/openrouter/client.py",
        task="Проверь на уязвимости безопасности и проблемы производительности",
        check_security=True,
        check_performance=True,
        check_style=False
    )

    print(f"✅ Анализ запущен: {analysis.get('task_id')}")
    return analysis


def example_3_function_testing():
    """Пример 3: Тестирование функции"""
    print("\n" + "="*70)
    print("Пример 3: Автоматическое тестирование функции")
    print("="*70)

    client = ManusClient()

    # Тестирование функции с тест-кейсами
    test_task = client.test_function(
        function_url="https://github.com/FreeAiHub/openrouter/blob/main/src/openrouter/utils.py",
        test_cases=[
            {
                "input": {"text": "Hello", "max_length": 10},
                "expected": "Hello"
            },
            {
                "input": {"text": "Very long text", "max_length": 5},
                "expected": "Very "
            }
        ]
    )

    print(f"✅ Тестирование запущено: {test_task.get('task_id')}")
    return test_task


def example_4_wait_for_result():
    """Пример 4: Ожидание результата задачи"""
    print("\n" + "="*70)
    print("Пример 4: Ожидание результата с polling")
    print("="*70)

    client = ManusClient()

    # Создаем задачу
    task = client.create_task(
        prompt="Быстрая проверка синтаксиса",
        context="https://github.com/FreeAiHub/openrouter/blob/main/examples/streaming.py"
    )

    task_id = task.get("task_id")
    print(f"✅ Задача создана: {task_id}")

    # Ждем результата
    try:
        print("⏳ Ожидание результата (max 60 секунд)...")
        result = client.wait_for_completion(
            task_id=task_id,
            timeout=60,
            poll_interval=5
        )

        print("✅ Задача завершена!")
        print(f"   Статус: {result.get('status')}")
        print(f"   Результат: {result.get('result')}")
        return result

    except ManusTaskTimeoutError as e:
        print(f"⏱️  Timeout: {e}")
    except ManusTaskFailedError as e:
        print(f"❌ Задача провалилась: {e}")
    except ManusAPIError as e:
        print(f"❌ API ошибка: {e}")


def example_5_error_handling():
    """Пример 5: Обработка ошибок"""
    print("\n" + "="*70)
    print("Пример 5: Корректная обработка ошибок")
    print("="*70)

    client = ManusClient()

    try:
        # Попытка получить несуществующую задачу
        task = client.get_task("non_existent_task_id")

    except ManusAPIError as e:
        print(f"✅ Корректно обработана ошибка: {e}")
        print(f"   Детали: {e.details}")


def example_6_webhook_handler():
    """Пример 6: Настройка webhook handler"""
    print("\n" + "="*70)
    print("Пример 6: Webhook Handler")
    print("="*70)

    # Создание webhook handler
    handler = ManusWebhookHandler()
    print(f"✅ Webhook handler создан: {handler}")

    # Регистрация обработчиков событий через декоратор
    @handler.on("task.completed")
    def handle_task_completed(event_data):
        print(f"🎉 Задача завершена: {event_data.get('task_id')}")
        return {"status": "processed"}

    @handler.on("task.failed")
    def handle_task_failed(event_data):
        print(f"❌ Задача провалилась: {event_data.get('task_id')}")
        print(f"   Ошибка: {event_data.get('error')}")
        return {"status": "error_logged"}

    # Симуляция webhook события
    import json
    import hmac
    import hashlib

    event_payload = json.dumps({
        "task_id": "task_123",
        "result": "Анализ завершен успешно",
        "cost": 0.002
    })

    # Генерация подписи
    secret = os.getenv("MANUS_WEBHOOK_SECRET", "test-secret")
    signature = hmac.new(
        secret.encode(),
        event_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # Обработка webhook
    result = handler.handle_webhook(
        event_type="task.completed",
        payload=event_payload,
        signature=signature
    )

    print(f"✅ Webhook обработан: {result}")


def example_7_metrics():
    """Пример 7: Метрики клиента"""
    print("\n" + "="*70)
    print("Пример 7: Отслеживание метрик")
    print("="*70)

    client = ManusClient()

    # Выполняем несколько операций
    client.create_task(prompt="Task 1", context="https://example.com")
    client.create_task(prompt="Task 2", context="https://example.com")

    try:
        client.get_task("fake_id")
    except:
        pass  # Игнорируем ошибку для демонстрации

    # Получаем метрики
    metrics = client.get_metrics()
    print("📊 Метрики клиента:")
    print(f"   Всего запросов: {metrics['request_count']}")
    print(f"   Ошибок: {metrics['error_count']}")
    print(f"   Success rate: {metrics['success_rate']:.2f}%")


def main():
    """Главная функция - запускает все примеры"""
    print("\n" + "="*70)
    print("🚀 Manus AI Integration - Примеры Использования")
    print("="*70)

    # Проверка API ключа
    if not os.getenv("MANUS_API_KEY"):
        print("\n⚠️  ПРЕДУПРЕЖДЕНИЕ: MANUS_API_KEY не найден!")
        print("   Установите его в .env файле для полноценной работы")
        print("   Примеры будут работать в режиме демонстрации\n")

    try:
        # Запуск примеров
        example_1_basic_usage()
        example_2_code_analysis()
        example_3_function_testing()
        # example_4_wait_for_result()  # Закомментировано - может занять время
        example_5_error_handling()
        example_6_webhook_handler()
        example_7_metrics()

        print("\n" + "="*70)
        print("✅ Все примеры выполнены успешно!")
        print("="*70)
        print("\nДля реального использования:")
        print("1. Установите MANUS_API_KEY в .env")
        print("2. Раскомментируйте example_4_wait_for_result()")
        print("3. Изучите src/manus/ для более глубокого понимания")
        print("\n")

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении примера: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
