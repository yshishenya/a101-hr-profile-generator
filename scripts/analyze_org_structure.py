#!/usr/bin/env python3
"""
Глубокий анализ организационной структуры для разработки 100% KPI маппинга.

Цель: Понять иерархию и разработать стратегию полного покрытия.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.organization_cache import organization_cache


def analyze_hierarchy_levels() -> Dict[str, Any]:
    """
    Анализирует уровни иерархии организации.

    Returns:
        Статистика по уровням иерархии
    """
    print("🔍 Analyzing organization hierarchy levels...\n")

    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    # Анализ по уровням
    levels_stats = defaultdict(list)
    max_depth = 0

    for dept_name in all_depts:
        dept_info = dept_index.get(dept_name)
        if not dept_info:
            continue

        path = dept_info["path"]
        # Убираем "ГК А101" из подсчета уровней
        path_parts = [p.strip() for p in path.split("/") if p.strip() and p.strip() != "ГК А101"]
        level = len(path_parts)
        max_depth = max(max_depth, level)

        levels_stats[level].append({
            'name': dept_name,
            'path': path,
            'path_parts': path_parts
        })

    return {
        'max_depth': max_depth,
        'levels': levels_stats,
        'total_departments': len(all_depts)
    }


def analyze_top_level_blocks() -> Dict[str, Any]:
    """
    Анализирует блоки верхнего уровня (Level 1).

    Returns:
        Информация о блоках и их поддеревьях
    """
    print("📦 Analyzing top-level blocks...\n")

    all_depts = organization_cache.get_all_departments()
    dept_index = organization_cache.get_department_index()

    # Собираем блоки верхнего уровня
    blocks = defaultdict(lambda: {
        'subdepartments': [],
        'total_count': 0,
        'levels': defaultdict(int)
    })

    for dept_name in all_depts:
        dept_info = dept_index.get(dept_name)
        if not dept_info:
            continue

        path = dept_info["path"]
        path_parts = [p.strip() for p in path.split("/") if p.strip() and p.strip() != "ГК А101"]

        if not path_parts:
            continue

        # Первый элемент = блок верхнего уровня
        block_name = path_parts[0]
        level = len(path_parts)

        blocks[block_name]['subdepartments'].append(dept_name)
        blocks[block_name]['total_count'] += 1
        blocks[block_name]['levels'][level] += 1

    return dict(blocks)


def analyze_kpi_files() -> Dict[str, Any]:
    """
    Анализирует существующие KPI файлы.

    Returns:
        Информация о KPI файлах
    """
    print("📄 Analyzing existing KPI files...\n")

    kpi_dir = Path("data/KPI")
    kpi_files = list(kpi_dir.glob("KPI_*.md"))

    kpi_info = {}
    for kpi_file in kpi_files:
        # Читаем первые строки для понимания содержимого
        with open(kpi_file, 'r', encoding='utf-8') as f:
            first_lines = [f.readline().strip() for _ in range(5)]

        kpi_info[kpi_file.name] = {
            'path': str(kpi_file),
            'size': kpi_file.stat().st_size,
            'preview': first_lines
        }

    return kpi_info


def find_kpi_to_block_mapping(blocks: Dict[str, Any], kpi_files: Dict[str, Any]) -> Dict[str, Any]:
    """
    Определяет соответствие KPI файлов к блокам.

    Args:
        blocks: Информация о блоках
        kpi_files: Информация о KPI файлах

    Returns:
        Маппинг и анализ покрытия
    """
    print("🔗 Mapping KPI files to blocks...\n")

    mapping = {}

    # Известные маппинги из существующих KPI
    known_mappings = {
        'KPI_ДИТ.md': 'Департамент информационных технологий',
        'KPI_ДРР.md': 'Департамент регионального развития',
        'KPI_ДПУ.md': 'производственн',  # частичное совпадение
        'KPI_УВАиК.md': 'аудит',
        'KPI_АС.md': 'архитект',
        'KPI_ПРП.md': 'персонал',
        'KPI_Цифра.md': 'цифров',
        'KPI_Закупки.md': 'закупк',
    }

    for kpi_file in kpi_files:
        mapped_blocks = []
        for block_name in blocks:
            # Проверяем известные маппинги
            for pattern in known_mappings.get(kpi_file, '').lower().split():
                if pattern in block_name.lower():
                    mapped_blocks.append(block_name)
                    break

        mapping[kpi_file] = mapped_blocks

    return mapping


def calculate_coverage_potential(
    blocks: Dict[str, Any],
    kpi_mapping: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Рассчитывает потенциальное покрытие при block-level маппинге.

    Returns:
        Анализ покрытия
    """
    print("📊 Calculating coverage potential...\n")

    covered_depts = set()
    uncovered_blocks = []

    for kpi_file, mapped_blocks in kpi_mapping.items():
        for block_name in mapped_blocks:
            if block_name in blocks:
                covered_depts.update(blocks[block_name]['subdepartments'])

    # Находим непокрытые блоки
    for block_name, block_info in blocks.items():
        is_covered = False
        for mapped_blocks in kpi_mapping.values():
            if block_name in mapped_blocks:
                is_covered = True
                break

        if not is_covered:
            uncovered_blocks.append({
                'name': block_name,
                'departments_count': block_info['total_count']
            })

    return {
        'covered_departments': len(covered_depts),
        'uncovered_blocks': uncovered_blocks,
        'coverage_percentage': len(covered_depts) / 510 * 100 if 510 > 0 else 0
    }


def propose_100_percent_strategy(
    blocks: Dict[str, Any],
    kpi_files: Dict[str, Any],
    uncovered_blocks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Предлагает стратегию для достижения 100% покрытия.

    Returns:
        Рекомендации по созданию новых KPI или маппингу
    """
    print("💡 Proposing 100% coverage strategy...\n")

    strategies = []

    # Стратегия 1: Создать KPI для каждого непокрытого блока
    new_kpi_files_needed = []
    for block_info in uncovered_blocks:
        block_name = block_info['name']
        # Создаем имя KPI файла из названия блока

        # Извлекаем аббревиатуру
        words = block_name.split()
        if len(words) >= 2:
            acronym = ''.join(w[0].upper() for w in words if w.lower() not in ['и', 'по', 'для', 'с', 'в'])
        else:
            acronym = block_name[:3].upper()

        suggested_filename = f"KPI_{acronym}.md"
        new_kpi_files_needed.append({
            'block': block_name,
            'suggested_filename': suggested_filename,
            'departments_count': block_info['departments_count'],
            'priority': 'high' if block_info['departments_count'] > 20 else 'medium'
        })

    strategies.append({
        'name': 'Create new KPI files for uncovered blocks',
        'description': f'Создать {len(new_kpi_files_needed)} новых KPI файлов для непокрытых блоков',
        'new_files': new_kpi_files_needed,
        'coverage_impact': '100%'
    })

    # Стратегия 2: Использовать ближайший родственный KPI
    # (для блоков, которые семантически близки к существующим)

    # Стратегия 3: Универсальный блок-уровневый fallback
    strategies.append({
        'name': 'Universal block-level fallback',
        'description': 'Создать универсальный KPI_UNIVERSAL.md для всех непокрытых блоков',
        'new_files': ['KPI_UNIVERSAL.md'],
        'coverage_impact': '100%'
    })

    return {
        'recommended_strategy': strategies[0],  # Первая стратегия - создать файлы
        'alternative_strategies': strategies[1:],
        'total_new_files_needed': len(new_kpi_files_needed)
    }


def main():
    """Main entry point."""
    print("=" * 80)
    print("🔬 DEEP ORGANIZATION STRUCTURE ANALYSIS")
    print("   Goal: Design 100% KPI coverage strategy")
    print("=" * 80)
    print()

    # 1. Анализ уровней иерархии
    hierarchy = analyze_hierarchy_levels()
    print(f"📊 Hierarchy Depth: {hierarchy['max_depth']} levels")
    print(f"📊 Total Departments: {hierarchy['total_departments']}")
    print()

    for level in sorted(hierarchy['levels'].keys()):
        count = len(hierarchy['levels'][level])
        print(f"   Level {level}: {count} departments")
    print()

    # 2. Анализ блоков верхнего уровня
    blocks = analyze_top_level_blocks()
    print(f"📦 Top-level Blocks: {len(blocks)}")
    print()

    # Сортируем по количеству департаментов
    sorted_blocks = sorted(blocks.items(), key=lambda x: x[1]['total_count'], reverse=True)

    print("   Top 10 blocks by department count:")
    for i, (block_name, block_info) in enumerate(sorted_blocks[:10], 1):
        print(f"   {i:2d}. {block_name}")
        print(f"       └─ {block_info['total_count']} departments")
    print()

    print(f"   All {len(blocks)} blocks:")
    for block_name, block_info in sorted_blocks:
        print(f"   • {block_name}: {block_info['total_count']} depts")
    print()

    # 3. Анализ KPI файлов
    kpi_files = analyze_kpi_files()
    print(f"📄 Existing KPI Files: {len(kpi_files)}")
    for kpi_file in sorted(kpi_files.keys()):
        print(f"   • {kpi_file}")
    print()

    # 4. Маппинг KPI к блокам
    kpi_mapping = find_kpi_to_block_mapping(blocks, kpi_files)
    print("🔗 KPI to Block Mapping:")
    for kpi_file, mapped_blocks in kpi_mapping.items():
        if mapped_blocks:
            print(f"   {kpi_file} → {', '.join(mapped_blocks)}")
        else:
            print(f"   {kpi_file} → ⚠️ No blocks matched")
    print()

    # 5. Расчет покрытия
    coverage = calculate_coverage_potential(blocks, kpi_mapping)
    print(f"📊 Current Block-Level Coverage Potential:")
    print(f"   Covered departments: {coverage['covered_departments']}/510")
    print(f"   Coverage: {coverage['coverage_percentage']:.1f}%")
    print(f"   Uncovered blocks: {len(coverage['uncovered_blocks'])}")
    print()

    if coverage['uncovered_blocks']:
        print("   Uncovered blocks (need KPI files):")
        sorted_uncovered = sorted(
            coverage['uncovered_blocks'],
            key=lambda x: x['departments_count'],
            reverse=True
        )
        for block_info in sorted_uncovered:
            print(f"   ⚠️  {block_info['name']}: {block_info['departments_count']} depts")
        print()

    # 6. Стратегия 100% покрытия
    strategy = propose_100_percent_strategy(blocks, kpi_files, coverage['uncovered_blocks'])

    print("=" * 80)
    print("💡 RECOMMENDED 100% COVERAGE STRATEGY")
    print("=" * 80)
    print()

    rec_strategy = strategy['recommended_strategy']
    print(f"Strategy: {rec_strategy['name']}")
    print(f"Description: {rec_strategy['description']}")
    print(f"Impact: {rec_strategy['coverage_impact']} coverage")
    print()

    if 'new_files' in rec_strategy:
        print(f"📝 New KPI files needed: {len(rec_strategy['new_files'])}")
        print()

        # Группируем по приоритету
        high_priority = [f for f in rec_strategy['new_files'] if f.get('priority') == 'high']
        medium_priority = [f for f in rec_strategy['new_files'] if f.get('priority') == 'medium']

        if high_priority:
            print(f"   🔴 HIGH PRIORITY ({len(high_priority)} files):")
            for file_info in sorted(high_priority, key=lambda x: x['departments_count'], reverse=True):
                print(f"      • {file_info['suggested_filename']}")
                print(f"        Block: {file_info['block']}")
                print(f"        Impact: {file_info['departments_count']} departments")
                print()

        if medium_priority:
            print(f"   🟡 MEDIUM PRIORITY ({len(medium_priority)} files):")
            for file_info in sorted(medium_priority, key=lambda x: x['departments_count'], reverse=True):
                print(f"      • {file_info['suggested_filename']}")
                print(f"        Block: {file_info['block']}")
                print(f"        Impact: {file_info['departments_count']} departments")
                print()

    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print()

    # Save detailed analysis
    output_path = Path("docs/analysis/100_PERCENT_KPI_STRATEGY.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'hierarchy': {
                'max_depth': hierarchy['max_depth'],
                'total_departments': hierarchy['total_departments'],
                'levels_distribution': {
                    str(k): len(v) for k, v in hierarchy['levels'].items()
                }
            },
            'blocks': {
                name: {
                    'total_count': info['total_count'],
                    'levels_distribution': dict(info['levels'])
                }
                for name, info in blocks.items()
            },
            'kpi_files': list(kpi_files.keys()),
            'coverage': coverage,
            'strategy': strategy
        }, f, ensure_ascii=False, indent=2)

    print(f"📊 Detailed analysis saved to: {output_path}")


if __name__ == "__main__":
    main()
