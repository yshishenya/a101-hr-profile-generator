#!/usr/bin/env python3
"""
Validate KPI coverage across all 567 departments with hierarchical inheritance.

This script tests the new hierarchical KPI mapping system and generates
a detailed coverage report showing the improvement from 1.6% to ~12%.
"""

import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.data_mapper import KPIMapper
from backend.core.organization_cache import organization_cache


def validate_kpi_coverage() -> Dict[str, Any]:
    """
    Test KPI mapping for all departments and generate coverage report.

    Returns:
        Coverage statistics and detailed mapping results
    """
    print("🔍 Validating KPI coverage across all departments...\n")

    # Initialize mapper
    mapper = KPIMapper()

    # Get all departments
    all_departments = organization_cache.get_all_departments()
    print(f"📊 Total departments in organization: {len(all_departments)}\n")

    # Coverage tracking
    coverage_stats = {
        'total_departments': len(all_departments),
        'smart_mapping': 0,
        'hierarchical_inheritance': 0,
        'fallback': 0,
        'by_kpi_file': defaultdict(list),
        'by_method': defaultdict(list),
        'unmapped_to_specific_kpi': [],
    }

    # Test each department
    for dept_name in sorted(all_departments):
        # Clear previous mappings
        mapper.mappings_log = []

        # Find KPI file
        kpi_file = mapper.find_kpi_file(dept_name)

        # Get mapping method
        if mapper.mappings_log:
            last_mapping = mapper.mappings_log[-1]
            method = last_mapping.get('method', 'unknown')

            # Update stats
            if method == 'smart_mapping':
                coverage_stats['smart_mapping'] += 1
            elif method == 'hierarchical_inheritance':
                coverage_stats['hierarchical_inheritance'] += 1
            elif method == 'block_level_mapping':
                if 'block_level_mapping' not in coverage_stats:
                    coverage_stats['block_level_mapping'] = 0
                coverage_stats['block_level_mapping'] += 1
            elif method in ('fallback', 'fallback_no_match', 'fallback_no_mapper'):
                coverage_stats['fallback'] += 1
            elif method in ('not_found', 'no_mapper'):
                # KPI не найден - это не fallback, это отсутствие KPI
                if 'not_found' not in coverage_stats:
                    coverage_stats['not_found'] = 0
                coverage_stats['not_found'] += 1

            # Track by KPI file (только если KPI найден)
            if kpi_file:
                coverage_stats['by_kpi_file'][kpi_file].append({
                    'department': dept_name,
                    'method': method,
                })

            # Track by method
            coverage_stats['by_method'][method].append({
                'department': dept_name,
                'kpi_file': kpi_file,
            })

            # Track unmapped (not found or fallback)
            if method in ('fallback', 'fallback_no_match', 'fallback_no_mapper', 'not_found', 'no_mapper'):
                coverage_stats['unmapped_to_specific_kpi'].append(dept_name)

    return coverage_stats


def print_coverage_report(stats: Dict[str, Any]) -> None:
    """Print detailed coverage report."""

    total = stats['total_departments']
    smart = stats['smart_mapping']
    hierarchical = stats['hierarchical_inheritance']
    block_level = stats.get('block_level_mapping', 0)
    fallback = stats['fallback']
    not_found = stats.get('not_found', 0)

    # Calculate coverage
    specific_kpi_coverage = smart + hierarchical + block_level
    coverage_percentage = (specific_kpi_coverage / total * 100) if total > 0 else 0

    print("=" * 80)
    print("📊 KPI COVERAGE VALIDATION REPORT")
    print("=" * 80)
    print()

    print("📈 OVERALL STATISTICS:")
    print(f"   Total departments: {total}")
    print(f"   Mapped to specific KPI: {specific_kpi_coverage} ({coverage_percentage:.1f}%)")
    print(f"   NOT found (no KPI available): {not_found} ({not_found/total*100:.1f}%)")
    print(f"   Using fallback KPI: {fallback} ({fallback/total*100:.1f}%)")
    print()

    print("🎯 MAPPING METHOD BREAKDOWN:")
    print(f"   ✅ Smart mapping (exact/partial match): {smart} ({smart/total*100:.1f}%)")
    print(f"   ✅ Hierarchical inheritance: {hierarchical} ({hierarchical/total*100:.1f}%)")
    if block_level > 0:
        print(f"   ✅ Block-level mapping: {block_level} ({block_level/total*100:.1f}%)")
    print(f"   ❌ NOT FOUND (no KPI file): {not_found} ({not_found/total*100:.1f}%)")
    if fallback > 0:
        print(f"   ⚠️  Fallback (generic KPI): {fallback} ({fallback/total*100:.1f}%)")
    print()

    print("📁 COVERAGE BY KPI FILE:")
    for kpi_file, mappings in sorted(stats['by_kpi_file'].items()):
        count = len(mappings)
        smart_count = sum(1 for m in mappings if m['method'] == 'smart_mapping')
        hierarchical_count = sum(1 for m in mappings if m['method'] == 'hierarchical_inheritance')
        block_level_count = sum(1 for m in mappings if m['method'] == 'block_level_mapping')
        fallback_count = sum(1 for m in mappings if m['method'] in ('fallback', 'fallback_no_match', 'fallback_no_mapper'))

        print(f"\n   {kpi_file}: {count} departments")
        if smart_count > 0:
            print(f"      ├─ Smart mapping: {smart_count}")
        if hierarchical_count > 0:
            print(f"      ├─ Hierarchical: {hierarchical_count}")
        if block_level_count > 0:
            print(f"      ├─ Block-level: {block_level_count}")
        if fallback_count > 0:
            print(f"      └─ Fallback: {fallback_count}")

        # Show sample departments (excluding fallbacks for KPI_DIT.md)
        show_mappings = [m for m in mappings if m['method'] not in ('fallback', 'fallback_no_match', 'fallback_no_mapper')]
        if not show_mappings:
            show_mappings = mappings  # Show fallbacks if that's all we have

        if len(show_mappings) <= 5:
            for mapping in show_mappings[:5]:
                if mapping['method'] == 'smart_mapping':
                    method_icon = "🎯"
                elif mapping['method'] == 'hierarchical_inheritance':
                    method_icon = "🌳"
                elif mapping['method'] == 'block_level_mapping':
                    method_icon = "🏢"
                else:
                    method_icon = "⚠️"
                print(f"         {method_icon} {mapping['department']}")
        else:
            # Show first 3 and last 2
            for mapping in show_mappings[:3]:
                if mapping['method'] == 'smart_mapping':
                    method_icon = "🎯"
                elif mapping['method'] == 'hierarchical_inheritance':
                    method_icon = "🌳"
                elif mapping['method'] == 'block_level_mapping':
                    method_icon = "🏢"
                else:
                    method_icon = "⚠️"
                print(f"         {method_icon} {mapping['department']}")
            print(f"         ... ({len(show_mappings) - 5} more) ...")
            for mapping in show_mappings[-2:]:
                if mapping['method'] == 'smart_mapping':
                    method_icon = "🎯"
                elif mapping['method'] == 'hierarchical_inheritance':
                    method_icon = "🌳"
                elif mapping['method'] == 'block_level_mapping':
                    method_icon = "🏢"
                else:
                    method_icon = "⚠️"
                print(f"         {method_icon} {mapping['department']}")

    print()
    print("=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)
    print()

    # Improvement summary
    old_coverage = 1.6  # 9/567 = 1.6%
    improvement_multiplier = coverage_percentage / old_coverage

    print(f"🚀 IMPROVEMENT SUMMARY:")
    print(f"   Before hierarchical inheritance: 1.6% (9 departments)")
    print(f"   After hierarchical inheritance: {coverage_percentage:.1f}% ({specific_kpi_coverage} departments)")
    print(f"   Improvement: {improvement_multiplier:.1f}x increase in coverage!")
    print()


def main():
    """Main entry point."""
    try:
        stats = validate_kpi_coverage()
        print_coverage_report(stats)

        # Save detailed report
        report_path = Path(__file__).parent.parent / "docs" / "analysis" / "KPI_COVERAGE_VALIDATION.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# KPI Coverage Validation Report\n\n")
            f.write(f"**Generated**: 2025-10-25\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total departments**: {stats['total_departments']}\n")
            f.write(f"- **Mapped to specific KPI**: {stats['smart_mapping'] + stats['hierarchical_inheritance']} ")
            f.write(f"({(stats['smart_mapping'] + stats['hierarchical_inheritance'])/stats['total_departments']*100:.1f}%)\n")
            f.write(f"- **Smart mapping**: {stats['smart_mapping']}\n")
            f.write(f"- **Hierarchical inheritance**: {stats['hierarchical_inheritance']} (NEW!)\n")
            f.write(f"- **Fallback**: {stats['fallback']}\n\n")

            f.write(f"## Mapping Details\n\n")
            for kpi_file, mappings in sorted(stats['by_kpi_file'].items()):
                f.write(f"### {kpi_file}\n\n")
                f.write(f"**Total**: {len(mappings)} departments\n\n")
                for mapping in sorted(mappings, key=lambda x: x['department']):
                    method_label = "🎯 Direct" if mapping['method'] == 'smart_mapping' else "🌳 Inherited"
                    f.write(f"- {method_label} {mapping['department']}\n")
                f.write("\n")

        print(f"📝 Detailed report saved to: {report_path}")

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
