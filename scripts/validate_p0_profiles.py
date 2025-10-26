#!/usr/bin/env python3
"""
Скрипт валидации профилей после внедрения P0.1-P0.4 улучшений.
Использует ProfileValidator для оценки качества сгенерированных профилей.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к backend модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.profile_validator import ProfileValidator


def load_profile(file_path: Path) -> Dict[str, Any]:
    """Загрузить профиль из JSON файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_validation_report(profile_name: str, validation_result: Dict[str, Any]) -> None:
    """Вывести отчёт по валидации профиля."""
    print(f"\n{'='*80}")
    print(f"ПРОФИЛЬ: {profile_name}")
    print(f"{'='*80}")

    print(f"\n📊 OVERALL QUALITY SCORE: {validation_result['quality_score']:.2f}/10")
    print(f"   Validation Status: {'✅ PASSED' if validation_result['valid'] else '❌ FAILED'}")

    metrics = validation_result['metrics']

    # P0.1: Task Concreteness
    print(f"\n🎯 P0.1 TASK CONCRETENESS:")
    p0_1 = metrics['p0_1_tasks']
    print(f"   Valid tasks: {p0_1['valid_tasks']}/{p0_1['total_tasks']}")
    print(f"   Valid ratio: {p0_1['valid_ratio']*100:.1f}%")
    print(f"   Avg concrete elements: {p0_1['avg_concrete_elements']:.1f}")
    print(f"   Avg filler ratio: {p0_1['avg_filler_ratio']*100:.1f}%")

    # P0.2: Soft Skills Methodologies
    print(f"\n💼 P0.2 SOFT SKILLS METHODOLOGIES:")
    p0_2 = metrics['p0_2_soft_skills']
    print(f"   Total skills: {p0_2['total_skills']}")
    print(f"   Soft skills count: {p0_2['soft_skills_count']}")
    print(f"   With methodologies: {p0_2['with_methodology']}")
    print(f"   Valid ratio: {p0_2['valid_ratio']*100:.1f}%")

    # P0.3: Regulatory Frameworks
    print(f"\n📋 P0.3 REGULATORY FRAMEWORKS:")
    p0_3 = metrics['p0_3_regulatory']
    print(f"   Domain: {p0_3.get('domain', 'unknown')}")
    print(f"   Required: {p0_3.get('required', False)}")
    print(f"   Status: {'✅ PASSED' if p0_3['valid'] else '❌ FAILED'}")
    if p0_3.get('issues'):
        for issue in p0_3['issues']:
            print(f"   ⚠️  {issue}")

    # P0.4: Proficiency Levels
    print(f"\n📈 P0.4 PROFICIENCY LEVELS:")
    p0_4 = metrics['p0_4_levels']
    print(f"   Total skills checked: {p0_4.get('total_checked', 0)}")
    print(f"   Status: {'✅ PASSED' if p0_4['valid'] else '❌ FAILED'}")
    if p0_4.get('issues'):
        for issue in p0_4['issues'][:3]:  # показываем первые 3
            print(f"   ⚠️  {issue}")

    # Summary
    summary = validation_result['summary']
    if summary['total_issues'] > 0 or summary['total_warnings'] > 0:
        print(f"\n⚠️  SUMMARY:")
        print(f"   Critical issues: {summary['total_issues']}")
        print(f"   Warnings: {summary['total_warnings']}")


def main():
    """Главная функция валидации."""
    output_dir = Path('/home/yan/A101/HR/output')

    profiles = {
        'Backend Python Developer': output_dir / 'profile_backend_python.json',
        'Главный бухгалтер': output_dir / 'profile_chief_accountant.json',
        'HR Business Partner': output_dir / 'profile_hrbp.json',
        'Менеджер по продажам B2B': output_dir / 'profile_sales_b2b.json'
    }

    validator = ProfileValidator()
    results = {}

    print("="*80)
    print("P0.1-P0.4 PROFILE VALIDATION REPORT")
    print("="*80)

    for profile_name, profile_path in profiles.items():
        if not profile_path.exists():
            print(f"\n❌ ERROR: Profile not found: {profile_path}")
            continue

        try:
            profile_data = load_profile(profile_path)
            # Профиль находится в profile_data['profile']
            profile = profile_data.get('profile', profile_data)
            validation_result = validator.validate_profile(profile)
            results[profile_name] = validation_result

            print_validation_report(profile_name, validation_result)

        except Exception as e:
            print(f"\n❌ ERROR validating {profile_name}: {e}")
            import traceback
            traceback.print_exc()

    # Сводная статистика
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")

    if results:
        avg_quality = sum(r['quality_score'] for r in results.values()) / len(results)
        passed_profiles = sum(1 for r in results.values() if r['valid'])

        print(f"📊 Average Quality Score: {avg_quality:.2f}/10")
        print(f"✅ Profiles Passed: {passed_profiles}/{len(results)}")
        print(f"❌ Profiles Failed: {len(results) - passed_profiles}/{len(results)}")

        # P0 метрики
        print("\nP0 METRICS ACROSS ALL PROFILES:")

        # P0.1
        avg_concreteness = sum(
            r['metrics']['p0_1_tasks']['valid_ratio']
            for r in results.values()
        ) / len(results)
        print(f"  P0.1 Task Concreteness: {avg_concreteness*100:.1f}% valid tasks")

        # P0.2
        avg_methodology = sum(
            r['metrics']['p0_2_soft_skills']['valid_ratio']
            for r in results.values()
        ) / len(results)
        print(f"  P0.2 Soft Skills Methodologies: {avg_methodology*100:.1f}% coverage")

        # P0.3
        regulatory_passed = sum(
            1 for r in results.values() if r['metrics']['p0_3_regulatory']['valid']
        )
        print(f"  P0.3 Regulatory Frameworks: {regulatory_passed}/{len(results)} passed")

        # P0.4
        proficiency_passed = sum(
            1 for r in results.values() if r['metrics']['p0_4_levels']['valid']
        )
        print(f"  P0.4 Proficiency Levels: {proficiency_passed}/{len(results)} passed")

    print(f"\n{'='*80}")
    print("Validation completed!")
    print(f"{'='*80}\n")

    # Сохранить результаты в JSON
    results_file = output_dir / 'validation_results_p0.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📁 Results saved to: {results_file}")


if __name__ == '__main__':
    main()
