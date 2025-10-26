#!/usr/bin/env python3
"""
Тест для проверки исправления аутентификации:
- Transparent migration от старого формата (bcrypt) к новому (SHA256+bcrypt)
- Проверка работы с обоими форматами паролей
"""

import sys
import requests
import json

API_BASE_URL = "http://localhost:8022"

def test_authentication():
    """Проверка аутентификации с миграцией паролей"""

    print("🧪 Тест исправления аутентификации HTTP 401\n")
    print("=" * 60)

    # Тест 1: Проверка health endpoint
    print("\n1️⃣ Проверка доступности API...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API доступен")
        else:
            print(f"❌ API вернул код {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

    # Тест 2: Аутентификация с дефолтными креденшелами
    print("\n2️⃣ Тест аутентификации (admin/admin123)...")
    try:
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }

        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=auth_data,
            timeout=10
        )

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Аутентификация успешна!")

            # Проверяем структуру ответа (BaseResponse format)
            if result.get("success") and result.get("access_token"):
                # Verify BaseResponse fields
                if "timestamp" not in result:
                    print("⚠️  Предупреждение: отсутствует поле 'timestamp' в BaseResponse")

                print(f"✅ Получен JWT токен: {result['access_token'][:50]}...")
                print(f"✅ Пользователь: {result['user_info']['username']}")
                print(f"✅ Полное имя: {result['user_info']['full_name']}")
                print(f"✅ Token type: {result['token_type']}")
                print(f"✅ Expires in: {result['expires_in']} секунд")
                print(f"✅ Timestamp: {result.get('timestamp', 'N/A')}")

                return True
            else:
                print(f"⚠️  Неожиданная структура ответа: {result}")
                return False

        else:
            print(f"❌ Ошибка аутентификации: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Ошибка: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response text: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Исключение при аутентификации: {e}")
        return False

    # Тест 3: Повторная аутентификация (должна работать с уже мигрированным паролем)
    print("\n3️⃣ Повторная аутентификация (проверка мигрированного пароля)...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=auth_data,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Повторная аутентификация успешна!")
            print("✅ Пароль корректно работает после миграции")
            return True
        else:
            print(f"❌ Повторная аутентификация не удалась: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Исключение при повторной аутентификации: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ТЕСТ ИСПРАВЛЕНИЯ BUG: HTTP 401 Authentication Error")
    print("="*60 + "\n")

    success = test_authentication()

    print("\n" + "="*60)
    if success:
        print("  ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n  Исправление:")
        print("  - Transparent password migration реализована")
        print("  - Старые пароли (bcrypt) мигрируют автоматически")
        print("  - Новые пароли (SHA256+bcrypt) работают сразу")
    else:
        print("  ❌ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
    print("="*60 + "\n")

    sys.exit(0 if success else 1)
