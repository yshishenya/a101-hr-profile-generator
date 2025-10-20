#!/usr/bin/env python3
"""
Тест системы поддержки 6-уровневой иерархии
Проверяет корректность работы на подразделениях разной глубины
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from backend.core.data_loader import DataLoader
from backend.core.organization_cache import organization_cache
import json


def test_hierarchy_extraction():
    """Тестирует извлечение иерархической информации для разных глубин"""

    data_loader = DataLoader()

    # Тестовые случаи разной глубины (РЕАЛЬНЫЕ ДЕПАРТАМЕНТЫ из structure.json)
    test_cases = [
        # Уровень 1 (только блок)
        {
            "department": "Блок безопасности",
            "position": "Заместитель генерального директора по безопасности",
            "expected_level": 1
        },

        # Уровень 2 (блок + департамент)
        {
            "department": "Служба безопасности",
            "position": "Руководитель службы безопасности",
            "expected_level": 2
        },

        # Уровень 3 (блок + департамент + управление)
        {
            "department": "Управление комплексной безопасности",
            "position": "Руководитель управления",
            "expected_level": 3
        },

        # Уровень 4 (блок + департамент + управление + отдел)
        {
            "department": "Группа анализа данных",
            "position": "Аналитик BI",
            "expected_level": 4
        },

        # Уровень 5 (5 уровней иерархии)
        {
            "department": "Отдел аренды",
            "position": "Специалист",
            "expected_level": 5
        },

        # Уровень 6 (максимальная глубина)
        {
            "department": "Группа онлайн продаж",
            "position": "Специалист",
            "expected_level": 6
        }
    ]

    print("🧪 ТЕСТИРОВАНИЕ 6-УРОВНЕВОЙ ИЕРАРХИИ\n" + "="*50)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        department = test_case["department"]
        position = test_case["position"]
        expected_level = test_case["expected_level"]

        print(f"\n📋 ТЕСТ {i}: {department}")
        print(f"   Должность: {position}")
        print(f"   Ожидаемый уровень: {expected_level}")

        try:
            # Получаем переменные для Langfuse
            variables = data_loader.prepare_langfuse_variables(department, position)

            # Проверяем ключевые переменные
            hierarchy_level = variables.get("hierarchy_level", 0)
            business_block = variables.get("business_block", "")
            department_unit = variables.get("department_unit", "")
            section_unit = variables.get("section_unit", "")
            group_unit = variables.get("group_unit", "")
            sub_section_unit = variables.get("sub_section_unit", "")
            final_group_unit = variables.get("final_group_unit", "")
            full_hierarchy_path = variables.get("full_hierarchy_path", "")

            print(f"   ✅ Фактический уровень: {hierarchy_level}")
            print(f"   📍 Полный путь: {full_hierarchy_path}")
            print(f"   🏢 Блок: '{business_block}'")
            print(f"   🏬 Департамент: '{department_unit}'")
            print(f"   📋 Управление/Отдел: '{section_unit}'")
            print(f"   📂 Отдел: '{group_unit}'")
            print(f"   📁 Под-отдел: '{sub_section_unit}'")
            print(f"   👥 Группа: '{final_group_unit}'")

            # Проверяем соответствие уровня
            if hierarchy_level != expected_level:
                print(f"   ❌ ОШИБКА: Ожидался уровень {expected_level}, получен {hierarchy_level}")
                all_passed = False
            else:
                print(f"   ✅ УСПЕХ: Уровень корректный")

            # Проверяем, что переменные заполнены корректно для данного уровня
            level_checks = [
                (1, business_block, "business_block должен быть заполнен на уровне 1+"),
                (2, department_unit, "department_unit должен быть заполнен на уровне 2+"),
                (3, section_unit, "section_unit должен быть заполнен на уровне 3+"),
                (4, group_unit, "group_unit должен быть заполнен на уровне 4+"),
                (5, sub_section_unit, "sub_section_unit должен быть заполнен на уровне 5+"),
                (6, final_group_unit, "final_group_unit должен быть заполнен на уровне 6+")
            ]

            for level, value, message in level_checks:
                if hierarchy_level >= level and not value:
                    print(f"   ⚠️  ПРЕДУПРЕЖДЕНИЕ: {message}")

        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            all_passed = False

    print(f"\n" + "="*50)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("="*50)

    return all_passed


def test_organization_cache_search():
    """Тестирует поиск в кеше организации"""

    print("\n🔍 ТЕСТИРОВАНИЕ ПОИСКА В ОРГАНИЗАЦИОННОМ КЕШЕ\n" + "="*50)

    # Тестовые запросы разной сложности
    search_queries = [
        "Департамент информационных технологий",
        "Управление архитектуры",
        "Отдел управления данными",
        "Группа анализа данных",
        "Отдел разработки",  # Может быть несколько
        "ДИТ"  # Сокращение
    ]

    for query in search_queries:
        print(f"\n🔎 Поиск: '{query}'")

        # Ищем департамент
        path = organization_cache.find_department_path(query)

        if path:
            print(f"   ✅ Найден путь: {' → '.join(path)}")
            print(f"   📊 Уровень: {len(path)}")
        else:
            print(f"   ❌ Не найдено")


if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ПОДДЕРЖКИ 6-УРОВНЕВОЙ ИЕРАРХИИ")

    # Запуск тестов
    success1 = test_hierarchy_extraction()
    test_organization_cache_search()

    if success1:
        print("\n🎉 ВСЕ ОСНОВНЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        sys.exit(0)
    else:
        print("\n❌ ЕСТЬ ОШИБКИ В ОСНОВНЫХ ТЕСТАХ")
        sys.exit(1)