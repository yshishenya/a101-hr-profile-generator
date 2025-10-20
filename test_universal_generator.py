#!/usr/bin/env python3
"""
🧪 ТЕСТ УНИВЕРСАЛЬНОГО ГЕНЕРАТОРА ПРОФИЛЕЙ А101

Тестирует все ключевые компоненты универсального генератора:
1. Загрузку организационной структуры
2. Поиск и выбор бизнес-юнитов
3. Подсчет позиций с рекурсией
4. Извлечение позиций из разных уровней иерархии
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from scripts.universal_profile_generator import (
    BusinessUnitSelector,
    UniversalPositionsExtractor,
    UniversalProgressManager
)

def test_business_unit_selector():
    """Тестирует селектор бизнес-юнитов"""
    print("🧪 ТЕСТ 1: BusinessUnitSelector")
    print("-" * 40)

    selector = BusinessUnitSelector()

    # Загружаем данные
    if not selector.load_organization_data():
        print("❌ Не удалось загрузить организационные данные")
        return False

    print(f"✅ Загружено {len(selector.all_units)} бизнес-юнитов")
    print(f"✅ Создано {len(selector.searchable_items)} элементов для поиска")

    # Проверяем группировку по уровням
    by_levels = selector._group_by_levels()

    print(f"\n📊 Распределение по уровням:")
    for level in sorted(by_levels.keys()):
        count = len(by_levels[level])
        print(f"   Уровень {level + 1}: {count} юнитов")

    # Тестируем подсчет позиций
    test_paths = [
        "Блок безопасности",  # Уровень 1
        "Служба безопасности",  # Уровень 2
        "Группа анализа данных",  # Уровень 4
        "Группа онлайн продаж"  # Уровень 6
    ]

    print(f"\n🔍 Тестируем подсчет позиций:")
    for path in test_paths:
        total = selector._calculate_total_positions(path)
        unit_data = selector.all_units.get(path, {})
        direct = len(unit_data.get('positions', []))
        print(f"   {path}: {direct} прямых + {total - direct} дочерних = {total} всего")

    return True


def test_positions_extractor():
    """Тестирует экстрактор позиций"""
    print("\n🧪 ТЕСТ 2: UniversalPositionsExtractor")
    print("-" * 40)

    extractor = UniversalPositionsExtractor()
    extractor.load_organization_data()

    # Тестируем извлечение позиций разных уровней
    test_units = [
        ("Блок безопасности", "Блок"),
        ("Департамент информационных технологий", "Департамент"),
        ("Группа анализа данных", "Группа"),
        ("Группа онлайн продаж", "Конечная группа")
    ]

    for unit_path, unit_type in test_units:
        print(f"\n🔍 Тестируем {unit_type}: {unit_path}")

        # Получаем информацию о юните
        unit_info = extractor.get_unit_hierarchy_info(unit_path)
        if unit_info:
            print(f"   📊 Уровень: {unit_info.get('level', 'N/A')}")
            print(f"   👥 Позиций в юните: {unit_info.get('positions_count', 0)}")
            print(f"   🏢 Дочерних юнитов: {unit_info.get('children_count', 0)}")
            print(f"   🧑‍💼 Численность: {unit_info.get('headcount', 'N/A')}")

        # Извлекаем позиции
        positions_with_children = extractor.extract_positions_from_unit(unit_path, include_children=True)
        positions_only = extractor.extract_positions_from_unit(unit_path, include_children=False)

        print(f"   📋 Позиций только в юните: {len(positions_only)}")
        print(f"   📈 Позиций с дочерними: {len(positions_with_children)}")

        # Показываем примеры позиций
        if positions_with_children:
            print(f"   📝 Примеры позиций:")
            for dept, pos in positions_with_children[:3]:
                dept_short = dept.split('/')[-1]  # Последний компонент пути
                print(f"      • {pos} ({dept_short})")
            if len(positions_with_children) > 3:
                print(f"      ... и еще {len(positions_with_children) - 3}")

    return True


def test_progress_manager():
    """Тестирует менеджер прогресса"""
    print("\n🧪 ТЕСТ 3: UniversalProgressManager")
    print("-" * 40)

    # Создаем временный файл прогресса
    test_progress_file = "test_progress.json"

    try:
        progress_manager = UniversalProgressManager(test_progress_file)

        # Тестируем установку юнита
        test_unit_path = "Группа анализа данных"
        test_unit_info = {
            "name": "Группа анализа данных",
            "level": 3,
            "positions_count": 3
        }

        progress_manager.set_selected_unit(test_unit_path, test_unit_info)
        progress_manager.reset_progress_for_unit(test_unit_path, 10, test_unit_info)

        print(f"✅ Установлен юнит: {progress_manager.progress['selected_unit']}")
        print(f"✅ Общее количество позиций: {progress_manager.progress['total_positions']}")

        # Симулируем завершение некоторых задач
        progress_manager.progress["completed_positions"].append({
            "department": test_unit_path,
            "position": "Тестовая позиция 1",
            "task_id": "test_task_1",
            "completed_at": "2025-09-25T10:00:00"
        })

        progress_manager.progress["failed_positions"].append({
            "department": test_unit_path,
            "position": "Тестовая позиция 2",
            "task_id": "test_task_2",
            "error": "Test error",
            "failed_at": "2025-09-25T10:01:00"
        })

        # Проверяем сводку
        print("\n📊 Тестовая сводка прогресса:")
        progress_manager.print_progress_summary()

        # Тестируем сохранение/загрузку
        progress_manager.save_progress()

        # Создаем новый менеджер и загружаем прогресс
        new_progress_manager = UniversalProgressManager(test_progress_file)
        loaded_progress = new_progress_manager.load_progress()

        if loaded_progress.get("selected_unit") == test_unit_path:
            print("✅ Прогресс корректно сохранен и загружен")
        else:
            print("❌ Ошибка сохранения/загрузки прогресса")
            return False

    finally:
        # Удаляем тестовый файл
        if os.path.exists(test_progress_file):
            os.remove(test_progress_file)

    return True


def test_integration():
    """Интеграционный тест всех компонентов"""
    print("\n🧪 ТЕСТ 4: Интеграционный тест")
    print("-" * 40)

    # Инициализируем все компоненты
    selector = BusinessUnitSelector()
    extractor = UniversalPositionsExtractor()
    progress_manager = UniversalProgressManager()

    # Загружаем данные
    if not selector.load_organization_data():
        print("❌ Не удалось загрузить данные в selector")
        return False

    extractor.load_organization_data()

    # Выбираем тестовый юнит (средней сложности)
    test_unit = "Блок директора по правовому обеспечению и управлению рисками/Управление по информационной безопасности"  # Уровень 1, 9 позиций

    print(f"🎯 Тестовый юнит: {test_unit}")

    # Получаем информацию о юните
    unit_info = extractor.get_unit_hierarchy_info(test_unit)
    if not unit_info:
        print(f"❌ Не найден тестовый юнит: {test_unit}")
        return False

    print(f"✅ Информация о юните получена:")
    print(f"   📊 Уровень: {unit_info.get('level')}")
    print(f"   👥 Позиций: {unit_info.get('positions_count')}")

    # Извлекаем позиции
    all_positions = extractor.extract_positions_from_unit(test_unit, include_children=True)

    if not all_positions:
        print(f"❌ Не найдено позиций в юните {test_unit}")
        return False

    print(f"✅ Извлечено {len(all_positions)} позиций")

    # Настраиваем прогресс
    progress_manager.set_selected_unit(test_unit, unit_info)
    progress_manager.reset_progress_for_unit(test_unit, len(all_positions), unit_info)

    # Симулируем частичное выполнение
    remaining = progress_manager.get_remaining_positions(all_positions)

    if len(remaining) != len(all_positions):
        print("❌ Ошибка в логике remaining positions")
        return False

    print(f"✅ Логика remaining positions работает корректно")

    # Проверяем подсчет с рекурсией
    calculated_total = selector._calculate_total_positions(test_unit)
    actual_total = len(all_positions)

    if calculated_total == actual_total:
        print(f"✅ Подсчет позиций корректен: {calculated_total}")
    else:
        print(f"❌ Несоответствие в подсчете: {calculated_total} vs {actual_total}")
        return False

    return True


def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 ТЕСТИРОВАНИЕ УНИВЕРСАЛЬНОГО ГЕНЕРАТОРА ПРОФИЛЕЙ А101")
    print("=" * 60)

    tests = [
        ("BusinessUnitSelector", test_business_unit_selector),
        ("UniversalPositionsExtractor", test_positions_extractor),
        ("UniversalProgressManager", test_progress_manager),
        ("Integration Test", test_integration)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: ПРОЙДЕН")
                passed += 1
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"💥 {test_name}: ОШИБКА - {e}")

    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")

    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Универсальный генератор готов к использованию")
        return True
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ. Требуется исправление ошибок")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)