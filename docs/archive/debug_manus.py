#!/usr/bin/env python3
"""
Debug script для Manus API
Поможет определить правильный формат запроса
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MANUS_API_KEY")

print("=" * 70)
print("🔍 DEBUG: Тестирование Manus API")
print("=" * 70)
print()

# Тест 1: Проверка документации API
print("📋 Вариант 1: POST /v1/tasks (стандартный)")
print("-" * 70)

url = "https://api.manus.ai/v1/tasks"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "prompt": "Test task",
    "context": "Testing API"
}

print(f"URL: {url}")
print(f"Headers: Authorization: Bearer {API_KEY[:20]}...")
print(f"Payload: {payload}")
print()

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:500]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("=" * 70)

# Тест 2: Попробовать без /v1
print("📋 Вариант 2: POST /tasks (без /v1)")
print("-" * 70)

url2 = "https://api.manus.ai/tasks"
print(f"URL: {url2}")

try:
    response = requests.post(url2, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("=" * 70)

# Тест 3: Проверить корневой endpoint
print("📋 Вариант 3: GET / (проверка API)")
print("-" * 70)

url3 = "https://api.manus.ai/"
print(f"URL: {url3}")

try:
    response = requests.get(url3, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("=" * 70)

# Тест 4: Альтернативный формат заголовка
print("📋 Вариант 4: X-API-Key вместо Bearer")
print("-" * 70)

headers_alt = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
url4 = "https://api.manus.ai/v1/tasks"
print(f"URL: {url4}")
print(f"Headers: X-API-Key: {API_KEY[:20]}...")

try:
    response = requests.post(url4, headers=headers_alt, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("=" * 70)
print("✅ Debug завершен")
print("=" * 70)
print()
print("📝 Рекомендации:")
print("   1. Проверьте документацию Manus API: https://open.manus.ai/docs")
print("   2. Убедитесь что API ключ действителен")
print("   3. Проверьте правильный endpoint URL")
print("   4. Проверьте формат заголовков авторизации")
print()
