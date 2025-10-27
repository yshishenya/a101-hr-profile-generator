#!/usr/bin/env python3
"""
Тест для ProfileContentUpdateRequest схемы
Проверяет валидацию profile_data
"""

import sys
sys.path.insert(0, 'backend')

from models.schemas import ProfileContentUpdateRequest
from pydantic import ValidationError

# Тестовые данные - минимальный валидный профиль
valid_profile_data = {
    "position_title": "Backend Python Developer",
    "department_specific": "Департамент информационных технологий",
    "responsibility_areas": [
        {
            "area": ["Разработка backend-сервисов"],
            "tasks": ["Разработка API", "Интеграции с 1С"]
        }
    ],
    "professional_skills": [
        {
            "skill_category": "Технические",
            "specific_skills": [
                {
                    "skill_name": "Python",
                    "proficiency_level": 3
                }
            ]
        }
    ],
    "corporate_competencies": ["Инновационность", "Результативность"],
    "personal_qualities": ["аналитическое мышление", "ответственность"],
    "experience_and_education": {
        "education_level": "Высшее",
        "total_work_experience": "От 3 лет"
    },
    # Опциональные секции
    "careerogram": {
        "source_positions": ["Junior Developer"],
        "target_positions": ["Senior Developer", "Team Lead"]
    },
    "workplace_provisioning": {
        "software": {
            "standard_package": ["MS Office", "Browser"],
            "specialized_tools": ["PyCharm", "Docker"]
        },
        "hardware": {
            "standard_workstation": "Laptop with 16GB RAM",
            "specialized_equipment": []
        }
    },
    "performance_metrics": {
        "quantitative_kpis": ["SLA 99%", "Code coverage 80%"],
        "qualitative_indicators": ["Code quality", "Team collaboration"],
        "evaluation_frequency": "Quarterly"
    }
}

print("=" * 60)
print("TEST 1: Валидный profile_data")
print("=" * 60)
try:
    request = ProfileContentUpdateRequest(profile_data=valid_profile_data)
    print("✓ PASSED: Валидный profile_data принят")
    print(f"  Position: {request.profile_data['position_title']}")
    print(f"  Department: {request.profile_data['department_specific']}")
    print(f"  Sections: {len(request.profile_data)} полей")
except ValidationError as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print()

# Тест 2: Отсутствует обязательное поле
print("=" * 60)
print("TEST 2: Отсутствует обязательное поле (position_title)")
print("=" * 60)
invalid_data = valid_profile_data.copy()
del invalid_data["position_title"]
try:
    request = ProfileContentUpdateRequest(profile_data=invalid_data)
    print("✗ FAILED: Должна была быть ошибка валидации")
    sys.exit(1)
except ValidationError as e:
    print(f"✓ PASSED: Ошибка валидации поймана")
    print(f"  Error: {str(e)[:100]}...")

print()

# Тест 3: Неправильный тип данных
print("=" * 60)
print("TEST 3: Неправильный тип (responsibility_areas не массив)")
print("=" * 60)
invalid_data2 = valid_profile_data.copy()
invalid_data2["responsibility_areas"] = "not a list"
try:
    request = ProfileContentUpdateRequest(profile_data=invalid_data2)
    print("✗ FAILED: Должна была быть ошибка валидации")
    sys.exit(1)
except ValidationError as e:
    print(f"✓ PASSED: Ошибка валидации поймана")
    print(f"  Error: {str(e)[:100]}...")

print()

# Тест 4: Пустая строка в обязательном поле
print("=" * 60)
print("TEST 4: Пустая строка в position_title")
print("=" * 60)
invalid_data3 = valid_profile_data.copy()
invalid_data3["position_title"] = ""
try:
    request = ProfileContentUpdateRequest(profile_data=invalid_data3)
    print("✗ FAILED: Должна была быть ошибка валидации")
    sys.exit(1)
except ValidationError as e:
    print(f"✓ PASSED: Ошибка валидации поймана")
    print(f"  Error: {str(e)[:100]}...")

print()
print("=" * 60)
print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print()
print("Backend endpoint готов к использованию:")
print("  PUT /api/profiles/{profile_id}/content")
print()
print("Для тестирования через curl после запуска backend:")
print("  1. Запустите backend: cd backend && uvicorn main:app --reload")
print("  2. Получите auth token через /api/auth/login")
print("  3. Используйте curl с примером из docstring")
