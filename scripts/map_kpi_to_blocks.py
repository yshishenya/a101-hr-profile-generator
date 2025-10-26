#!/usr/bin/env python3
"""
Детальный маппинг существующих KPI файлов к блокам организации.

Цель: Понять какие KPI относятся к каким блокам, чтобы создать 100% маппинг.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.organization_cache import organization_cache
from backend.core.data_mapper import KPIMapper


def find_department_block(dept_name: str, dept_index: Dict) -> str:
    """
    Находит блок верхнего уровня для департамента.

    Args:
        dept_name: Название департамента
        dept_index: Индекс департаментов

    Returns:
        Название блока или "Unknown"
    """
    dept_info = dept_index.get(dept_name)
    if not dept_info:
        return "Unknown"

    path = dept_info["path"]
    path_parts = [p.strip() for p in path.split("/") if p.strip() and p.strip() != "ГК А101"]

    if not path_parts:
        return "Unknown"

    # Первый элемент = блок верхнего уровня
    return path_parts[0]


def analyze_current_kpi_distribution():
    """
    Анализирует как текущие KPI файлы распределены по блокам.
    """
    print("=" * 80)
    print("🔍 ANALYZING CURRENT KPI DISTRIBUTION ACROSS BLOCKS")
    print("=" * 80)
    print()

    mapper = KPIMapper()
    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    # Группируем департаменты по блокам и KPI
    block_kpi_map = defaultdict(lambda: defaultdict(list))
    kpi_stats = defaultdict(lambda: {
        'total': 0,
        'blocks': defaultdict(int),
        'departments': []
    })

    for dept_name in all_depts:
        # Очищаем лог
        mapper.mappings_log = []

        # Находим KPI
        kpi_file = mapper.find_kpi_file(dept_name)
        mapping_method = mapper.mappings_log[-1]['method'] if mapper.mappings_log else 'unknown'

        # Находим блок
        block_name = find_department_block(dept_name, dept_index)

        # Собираем статистику
        block_kpi_map[block_name][kpi_file].append({
            'department': dept_name,
            'method': mapping_method
        })

        kpi_stats[kpi_file]['total'] += 1
        kpi_stats[kpi_file]['blocks'][block_name] += 1
        kpi_stats[kpi_file]['departments'].append({
            'name': dept_name,
            'block': block_name,
            'method': mapping_method
        })

    return block_kpi_map, kpi_stats


def print_block_kpi_analysis(block_kpi_map: Dict, kpi_stats: Dict):
    """
    Выводит детальный анализ распределения KPI по блокам.
    """
    print("📊 BLOCK-LEVEL KPI DISTRIBUTION")
    print("=" * 80)
    print()

    # Сортируем блоки по количеству департаментов
    sorted_blocks = sorted(
        block_kpi_map.items(),
        key=lambda x: sum(len(depts) for depts in x[1].values()),
        reverse=True
    )

    for block_name, kpi_depts in sorted_blocks:
        total_in_block = sum(len(depts) for depts in kpi_depts.values())
        print(f"🏢 {block_name}")
        print(f"   Total departments: {total_in_block}")
        print()

        # Сортируем KPI по количеству департаментов
        sorted_kpis = sorted(kpi_depts.items(), key=lambda x: len(x[1]), reverse=True)

        for kpi_file, depts in sorted_kpis:
            # Подсчитываем методы
            smart_count = sum(1 for d in depts if d['method'] == 'smart_mapping')
            hierarchical_count = sum(1 for d in depts if d['method'] == 'hierarchical_inheritance')
            fallback_count = sum(1 for d in depts if 'fallback' in d['method'])

            # Определяем иконку
            if fallback_count == len(depts):
                icon = "⚠️"  # Все fallback
            elif smart_count > 0:
                icon = "✅"  # Есть smart mapping
            elif hierarchical_count > 0:
                icon = "🌳"  # Hierarchical
            else:
                icon = "❓"

            print(f"   {icon} {kpi_file}: {len(depts)} depts", end="")

            # Показываем breakdown
            if smart_count > 0 or hierarchical_count > 0:
                methods = []
                if smart_count > 0:
                    methods.append(f"{smart_count} smart")
                if hierarchical_count > 0:
                    methods.append(f"{hierarchical_count} hierarchical")
                if fallback_count > 0:
                    methods.append(f"{fallback_count} fallback")
                print(f" ({', '.join(methods)})")
            else:
                print(f" (all fallback)")

            # Показываем примеры департаментов с non-fallback маппингом
            non_fallback = [d for d in depts if 'fallback' not in d['method']]
            if non_fallback and len(non_fallback) <= 5:
                for dept_info in non_fallback:
                    method_icon = "🎯" if dept_info['method'] == 'smart_mapping' else "🌳"
                    print(f"      {method_icon} {dept_info['department']}")

        print()

    print("=" * 80)
    print()


def propose_block_kpi_mapping(block_kpi_map: Dict) -> Dict[str, str]:
    """
    Предлагает оптимальный маппинг блоков к KPI файлам.

    Логика:
    1. Если блок имеет доминирующий non-fallback KPI → используем его
    2. Иначе → нужно создать новый KPI файл для блока

    Returns:
        Маппинг блок → KPI файл
    """
    print("💡 PROPOSING OPTIMAL BLOCK → KPI MAPPING")
    print("=" * 80)
    print()

    proposed_mapping = {}
    new_kpi_needed = []

    for block_name, kpi_depts in block_kpi_map.items():
        total_in_block = sum(len(depts) for depts in kpi_depts.values())

        # Ищем доминирующий non-fallback KPI
        non_fallback_kpis = {}
        for kpi_file, depts in kpi_depts.items():
            non_fallback = [d for d in depts if 'fallback' not in d['method']]
            if non_fallback:
                non_fallback_kpis[kpi_file] = len(non_fallback)

        if non_fallback_kpis:
            # Берем KPI с максимальным числом non-fallback маппингов
            dominant_kpi = max(non_fallback_kpis.items(), key=lambda x: x[1])
            kpi_file, count = dominant_kpi

            coverage_pct = count / total_in_block * 100

            proposed_mapping[block_name] = kpi_file
            print(f"✅ {block_name}")
            print(f"   → Use existing: {kpi_file}")
            print(f"   Coverage: {count}/{total_in_block} ({coverage_pct:.1f}%)")
            print()
        else:
            # Нет non-fallback KPI - нужен новый файл
            # Генерируем имя
            words = block_name.split()
            if len(words) >= 2:
                acronym = ''.join(w[0].upper() for w in words if w.lower() not in ['и', 'по', 'для', 'с', 'в', '"'])
            else:
                acronym = block_name[:3].upper()

            new_kpi_file = f"KPI_{acronym}.md"

            proposed_mapping[block_name] = new_kpi_file
            new_kpi_needed.append({
                'block': block_name,
                'kpi_file': new_kpi_file,
                'departments': total_in_block
            })

            print(f"⚠️  {block_name}")
            print(f"   → Need new: {new_kpi_file}")
            print(f"   Impact: {total_in_block} departments")
            print()

    print("=" * 80)
    print()

    if new_kpi_needed:
        print("📝 NEW KPI FILES NEEDED:")
        print()
        for item in sorted(new_kpi_needed, key=lambda x: x['departments'], reverse=True):
            priority = "🔴 HIGH" if item['departments'] > 20 else "🟡 MEDIUM"
            print(f"   {priority}: {item['kpi_file']}")
            print(f"      Block: {item['block']}")
            print(f"      Impact: {item['departments']} departments")
            print()

        print(f"   TOTAL: {len(new_kpi_needed)} new KPI files needed")
        print()

    print("=" * 80)
    print()

    return proposed_mapping, new_kpi_needed


def calculate_100_percent_coverage(proposed_mapping: Dict[str, str]) -> Dict:
    """
    Рассчитывает что произойдет при использовании block-level маппинга.
    """
    print("📊 100% COVERAGE SIMULATION")
    print("=" * 80)
    print()

    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    # Симулируем новый маппинг
    coverage_stats = {
        'existing_kpi': 0,
        'new_kpi': 0,
        'total': len(all_depts)
    }

    existing_kpi_files = [
        'KPI_ДИТ.md', 'KPI_ДРР.md', 'KPI_ДПУ.md', 'KPI_УВАиК.md',
        'KPI_АС.md', 'KPI_ПРП.md', 'KPI_Цифра.md', 'KPI_Закупки.md',
        'KPI_DIT.md'
    ]

    for dept_name in all_depts:
        block_name = find_department_block(dept_name, dept_index)
        kpi_file = proposed_mapping.get(block_name, 'KPI_UNKNOWN.md')

        if kpi_file in existing_kpi_files:
            coverage_stats['existing_kpi'] += 1
        else:
            coverage_stats['new_kpi'] += 1

    print(f"   Total departments: {coverage_stats['total']}")
    print(f"   Using existing KPI: {coverage_stats['existing_kpi']} ({coverage_stats['existing_kpi']/coverage_stats['total']*100:.1f}%)")
    print(f"   Using new KPI: {coverage_stats['new_kpi']} ({coverage_stats['new_kpi']/coverage_stats['total']*100:.1f}%)")
    print()
    print(f"   ✅ COVERAGE: 100% (all departments mapped to block-level KPI)")
    print()

    print("=" * 80)
    print()

    return coverage_stats


def main():
    """Main entry point."""
    # Анализ
    block_kpi_map, kpi_stats = analyze_current_kpi_distribution()

    # Вывод анализа
    print_block_kpi_analysis(block_kpi_map, kpi_stats)

    # Предложение маппинга
    proposed_mapping, new_kpi_needed = propose_block_kpi_mapping(block_kpi_map)

    # Симуляция 100% покрытия
    coverage_stats = calculate_100_percent_coverage(proposed_mapping)

    # Сохраняем результаты
    output_path = Path("docs/analysis/BLOCK_KPI_MAPPING_STRATEGY.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'proposed_mapping': proposed_mapping,
            'new_kpi_needed': new_kpi_needed,
            'coverage_stats': coverage_stats,
            'implementation_steps': [
                "1. Create new KPI files for blocks without existing KPI",
                "2. Implement block-level KPI inheritance in KPIMapper",
                "3. Update find_kpi_file() to use block-level fallback before generic fallback",
                "4. Test with all 510 departments",
                "5. Validate 100% coverage"
            ]
        }, f, ensure_ascii=False, indent=2)

    print(f"📊 Analysis saved to: {output_path}")
    print()

    # Итоговая рекомендация
    print("=" * 80)
    print("🎯 RECOMMENDED IMPLEMENTATION APPROACH")
    print("=" * 80)
    print()
    print(f"1. Create {len(new_kpi_needed)} new KPI files for blocks")
    print()
    print("2. Modify KPIMapper.find_kpi_file() algorithm:")
    print("   TIER 1: Smart mapping (department-level exact match)")
    print("   TIER 2: Hierarchical inheritance (parent department)")
    print("   TIER 3: Block-level mapping (top-level block) ← NEW!")
    print("   TIER 4: Generic fallback (KPI_DIT.md)")
    print()
    print("3. Implementation:")
    print("   - Add _find_kpi_by_block(department) method")
    print("   - Map department → block → KPI file")
    print("   - Use predefined block→KPI mapping")
    print()
    print(f"📊 Expected Result: 100% coverage ({coverage_stats['total']} departments)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
