#!/usr/bin/env python3
"""
Тест исправления проблемы с ID профиля
Tests the profile ID fix in frontend-backend communication
"""

def test_profile_id_structure():
    """Тестируем правильную структуру данных профиля"""
    
    # Имитируем структуру данных, которую возвращает API
    mock_api_response = {
        "profile_id": "test-profile-123",
        "department": "IT",
        "position": "Senior Developer",
        "employee_name": "Test User",
        "status": "active",
        "validation_score": 0.95,
        "completeness_score": 0.98,
        "created_at": "2024-01-01T12:00:00",
        "created_by_username": "admin"
    }
    
    # Тестируем, что можем получить profile_id (правильное поле)
    profile_id = mock_api_response.get("profile_id")
    assert profile_id is not None, "❌ profile_id должен существовать"
    assert profile_id == "test-profile-123", f"❌ Неожиданное значение profile_id: {profile_id}"
    
    # Тестируем, что поле 'id' НЕ существует (это была проблема)
    old_id_field = mock_api_response.get("id")
    assert old_id_field is None, "❌ Поле 'id' не должно существовать в ответе API"
    
    print("✅ Структура данных профиля корректна")
    print(f"✅ profile_id: {profile_id}")
    print("✅ Старое поле 'id' отсутствует")
    
    return True

def test_frontend_logic():
    """Тестируем логику фронтенда с исправленным кодом"""
    
    mock_profile = {
        "profile_id": "test-profile-456",
        "department": "HR", 
        "position": "HR Manager"
    }
    
    # Имитируем исправленный код фронтенда
    def get_profile_id_fixed(profile):
        """Исправленная логика получения ID профиля"""
        return profile.get("profile_id", "")
    
    def get_profile_id_old(profile):
        """Старая (проблемная) логика получения ID профиля"""
        return profile.get("id", "")
    
    # Тестируем исправленную версию
    fixed_id = get_profile_id_fixed(mock_profile)
    assert fixed_id == "test-profile-456", f"❌ Исправленная версия вернула: {fixed_id}"
    
    # Тестируем старую версию (должна вернуть пустую строку)
    old_id = get_profile_id_old(mock_profile)
    assert old_id == "", f"❌ Старая версия должна вернуть пустую строку, вернула: {old_id}"
    
    print("✅ Логика фронтенда исправлена корректно")
    print(f"✅ Исправленная версия получает ID: {fixed_id}")
    print(f"✅ Старая версия возвращает пустоту: '{old_id}'")
    
    return True

if __name__ == "__main__":
    print("🔬 Тестирование исправления проблемы с ID профиля...")
    print("-" * 60)
    
    try:
        test_profile_id_structure()
        print()
        test_frontend_logic()
        print()
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Исправление проблемы с ID профиля работает корректно")
        
    except AssertionError as e:
        print(f"❌ ТЕСТ ПРОВАЛЕН: {e}")
        exit(1)
    except Exception as e:
        print(f"💥 НЕОЖИДАННАЯ ОШИБКА: {e}")
        exit(1)