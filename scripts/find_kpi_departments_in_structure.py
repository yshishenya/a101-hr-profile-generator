#!/usr/bin/env python3
"""
Находит департаменты из KPI файлов в организационной структуре.

Задача: Определить ТОЧНОЕ соответствие KPI файлов к департаментам,
без произвольного маппинга.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.organization_cache import organization_cache


# Маппинг KPI файлов к их РЕАЛЬНЫМ департаментам (из headers файлов)
KPI_TO_REAL_DEPARTMENT = {
    'KPI_ДИТ.md': [
        'Департамент информационных технологий',
        'ДИТ',
    ],
    'KPI_ДРР.md': [
        'Департамент регионального развития',
        'ДРР',
    ],
    'KPI_ДПУ.md': [
        'Дирекция ПУ',
        'ДПУ',
        'производственное управление',
        'производственн',
    ],
    'KPI_УВАиК.md': [
        'Управление внутреннего аудита и контроля',
        'УВАиК',
        'аудит',
        'контроль',
    ],
    'KPI_АС.md': [
        'Отдел бюджетирования и анализа себестоимости',
        'анализа себестоимости',
    ],
    'KPI_ПРП.md': [
        'Управление планирования и контроля реализации проектов',
        'планирования и контроля реализации проектов',
    ],
    'KPI_Цифра.md': [
        'цифровизация',
        'цифровых',
    ],
    'KPI_Закупки.md': [
        'закупк',
        'закупок',
    ],
    'KPI_DIT.md': [
        # Legacy файл, дубликат ДИТ
    ],
}


def find_department_in_structure(keywords: List[str]) -> Optional[tuple]:
    """
    Находит департамент в структуре по ключевым словам.

    Args:
        keywords: Список ключевых слов для поиска

    Returns:
        Tuple (dept_name, dept_info) или None
    """
    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    # Ищем точное совпадение
    for keyword in keywords:
        if keyword in all_depts:
            return (keyword, dept_index.get(keyword))

    # Ищем частичное совпадение
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for dept_name in all_depts:
            if keyword_lower in dept_name.lower():
                return (dept_name, dept_index.get(dept_name))

    return None


def extract_block(path: str) -> Optional[str]:
    """Извлекает блок верхнего уровня из пути."""
    parts = [p.strip() for p in path.split('/') if p.strip()]

    # Ищем первый элемент после "ГК А101"
    for part in parts:
        if part != 'ГК А101':
            return part

    return None


def main():
    """Main entry point."""
    print("=" * 80)
    print("🔍 ТОЧНЫЙ ПОИСК KPI ДЕПАРТАМЕНТОВ В СТРУКТУРЕ")
    print("=" * 80)
    print()

    kpi_to_block_mapping = {}
    kpi_details = {}

    for kpi_file, keywords in KPI_TO_REAL_DEPARTMENT.items():
        print(f"📄 {kpi_file}")

        if not keywords:
            print(f"   ⚠️  Legacy файл, пропускаем")
            print()
            continue

        # Ищем департамент
        result = find_department_in_structure(keywords)

        if result:
            dept_name, dept_info = result
            path = dept_info['path']
            block = extract_block(path)

            print(f"   ✅ Найден: {dept_name}")
            print(f"   📂 Путь: {path}")
            print(f"   🏢 Блок: {block}")

            kpi_details[kpi_file] = {
                'department': dept_name,
                'path': path,
                'block': block,
                'keywords': keywords,
            }

            if block:
                kpi_to_block_mapping[block] = kpi_file
        else:
            print(f"   ❌ НЕ НАЙДЕН в структуре!")
            print(f"   🔍 Искали по: {', '.join(keywords)}")
            kpi_details[kpi_file] = {
                'department': None,
                'path': None,
                'block': None,
                'keywords': keywords,
                'status': 'NOT_FOUND'
            }

        print()

    # Выводим итоговый маппинг
    print("=" * 80)
    print("📊 ИТОГОВЫЙ BLOCK → KPI МАППИНГ (на основе ФАКТИЧЕСКИХ данных)")
    print("=" * 80)
    print()

    if kpi_to_block_mapping:
        print("✅ Найденные соответствия:")
        print()
        for block, kpi_file in sorted(kpi_to_block_mapping.items()):
            dept_name = kpi_details[kpi_file]['department']
            print(f"   🏢 {block}")
            print(f"      └─ {kpi_file}")
            print(f"         (через департамент: {dept_name})")
            print()
    else:
        print("⚠️  Не найдено ни одного соответствия блоков к KPI!")
        print()

    # Проверяем непокрытые блоки
    print("=" * 80)
    print("🔍 ПРОВЕРКА ПОКРЫТИЯ ВСЕХ БЛОКОВ")
    print("=" * 80)
    print()

    # Получаем все блоки из структуры
    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    all_blocks = set()
    for dept_name in all_depts:
        dept_info = dept_index.get(dept_name)
        if dept_info:
            block = extract_block(dept_info['path'])
            if block:
                all_blocks.add(block)

    print(f"📦 Всего блоков в организации: {len(all_blocks)}")
    print()

    covered_blocks = set(kpi_to_block_mapping.keys())
    uncovered_blocks = all_blocks - covered_blocks

    print(f"✅ Блоков с KPI: {len(covered_blocks)} ({len(covered_blocks)/len(all_blocks)*100:.1f}%)")
    for block in sorted(covered_blocks):
        print(f"   • {block}")
    print()

    if uncovered_blocks:
        print(f"⚠️  Блоков БЕЗ KPI: {len(uncovered_blocks)} ({len(uncovered_blocks)/len(all_blocks)*100:.1f}%)")
        for block in sorted(uncovered_blocks):
            # Считаем департаменты в блоке
            dept_count = sum(1 for d in all_depts
                            if dept_index.get(d) and extract_block(dept_index[d]['path']) == block)
            print(f"   • {block} ({dept_count} департаментов)")
        print()

    # Анализ: можно ли использовать иерархическое наследование?
    print("=" * 80)
    print("💡 АНАЛИЗ: HIERARCHICAL INHERITANCE")
    print("=" * 80)
    print()

    # Для каждого непокрытого блока ищем родительские департаменты с KPI
    hierarchy_solutions = {}

    for block in uncovered_blocks:
        # Находим все департаменты в этом блоке
        block_depts = [d for d in all_depts
                      if dept_index.get(d) and extract_block(dept_index[d]['path']) == block]

        # Для каждого департамента проверяем можно ли найти KPI через иерархию
        has_hierarchical = False
        for dept_name in block_depts[:3]:  # Проверяем первые 3 для примера
            dept_info = dept_index[dept_name]
            path = dept_info['path']
            path_parts = [p.strip() for p in path.split('/') if p.strip()]

            # Идем вверх по иерархии
            for i in range(len(path_parts), 0, -1):
                parent = path_parts[i-1]

                # Проверяем есть ли KPI для родителя
                for kpi_file, details in kpi_details.items():
                    if details.get('department') == parent:
                        has_hierarchical = True
                        if block not in hierarchy_solutions:
                            hierarchy_solutions[block] = []
                        hierarchy_solutions[block].append({
                            'example_dept': dept_name,
                            'parent_with_kpi': parent,
                            'kpi_file': kpi_file,
                        })
                        break

                if has_hierarchical:
                    break

            if has_hierarchical:
                break

    if hierarchy_solutions:
        print("✅ Найдены решения через hierarchical inheritance:")
        print()
        for block, solutions in hierarchy_solutions.items():
            print(f"   🏢 {block}")
            for sol in solutions:
                print(f"      Пример: {sol['example_dept']}")
                print(f"      → Наследует от: {sol['parent_with_kpi']}")
                print(f"      → KPI: {sol['kpi_file']}")
            print()

    remaining_uncovered = uncovered_blocks - set(hierarchy_solutions.keys())

    if remaining_uncovered:
        print(f"⚠️  Блоков без решения (нужен fallback или новый KPI): {len(remaining_uncovered)}")
        for block in sorted(remaining_uncovered):
            dept_count = sum(1 for d in all_depts
                            if dept_index.get(d) and extract_block(dept_index[d]['path']) == block)
            print(f"   • {block} ({dept_count} департаментов)")
        print()

    # Итоговая рекомендация
    print("=" * 80)
    print("🎯 РЕКОМЕНДАЦИИ ДЛЯ 100% ПОКРЫТИЯ")
    print("=" * 80)
    print()

    print("✅ TIER 1: Direct block mapping")
    print(f"   Покрытие: {len(covered_blocks)}/{len(all_blocks)} блоков ({len(covered_blocks)/len(all_blocks)*100:.1f}%)")
    print()

    print("✅ TIER 2: Hierarchical inheritance")
    print(f"   Дополнительно: {len(hierarchy_solutions)} блоков")
    print()

    if remaining_uncovered:
        print("⚠️  TIER 3: Требуется решение")
        print(f"   Блоков: {len(remaining_uncovered)}")
        print()
        print("   Варианты:")
        print("   1. Создать новые KPI файлы для этих блоков")
        print("   2. НЕ использовать fallback (возвращать None)")
        print("   3. Уточнить у пользователя какой KPI подходит")
        print()

    # Сохраняем результаты
    output_path = Path("docs/analysis/ACCURATE_KPI_MAPPING.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'kpi_details': kpi_details,
            'block_to_kpi_mapping': kpi_to_block_mapping,
            'all_blocks': sorted(list(all_blocks)),
            'covered_blocks': sorted(list(covered_blocks)),
            'uncovered_blocks': sorted(list(uncovered_blocks)),
            'hierarchy_solutions': hierarchy_solutions,
            'remaining_uncovered': sorted(list(remaining_uncovered)),
        }, f, ensure_ascii=False, indent=2)

    print(f"📊 Детальные результаты сохранены: {output_path}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
