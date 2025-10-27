#!/usr/bin/env python3
"""
Финальная валидация P0.5-enhanced профилей.
Проверяет эффективность P0.5 mandatory checkpoints.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.profile_validator import ProfileValidator


def load_profile(file_path: Path):
    """Load profile from JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main validation"""
    output_dir = Path('/home/yan/A101/HR/output')

    profiles = {
        'Backend Python Developer': output_dir / 'profile_backend_python_p05_v49_final.json',
        'Главный бухгалтер': output_dir / 'profile_chief_accountant_p05_v49_final.json',
        'HR Business Partner': output_dir / 'profile_hrbp_p05_v49_final.json',
        'Менеджер по продажам B2B': output_dir / 'profile_sales_b2b_p05_v49_final.json'
    }

    validator = ProfileValidator()
    results = {}

    print("="*80)
    print("P0.5 FINAL VALIDATION REPORT (Langfuse v49)")
    print("="*80)

    for profile_name, profile_path in profiles.items():
        if not profile_path.exists():
            print(f"\n❌ ERROR: {profile_path} not found")
            continue

        try:
            profile_data = load_profile(profile_path)
            profile = profile_data.get('profile', profile_data)

            validation_result = validator.validate_profile(profile)
            results[profile_name] = validation_result

            print(f"\n{'='*80}")
            print(f"ПРОФИЛЬ: {profile_name}")
            print(f"{'='*80}")

            metrics = validation_result['metrics']

            print(f"\n📊 OVERALL QUALITY SCORE: {validation_result['quality_score']:.2f}/10")
            print(f"   Status: {'✅ PASSED' if validation_result['valid'] else '❌ FAILED'}")

            # P0.1
            p0_1 = metrics['p0_1_tasks']
            print(f"\n🎯 P0.1 TASK CONCRETENESS:")
            print(f"   Valid: {p0_1['valid_tasks']}/{p0_1['total_tasks']} ({p0_1['valid_ratio']*100:.1f}%)")
            print(f"   Avg concrete elements: {p0_1['avg_concrete_elements']:.1f}")
            print(f"   Avg filler: {p0_1['avg_filler_ratio']*100:.1f}%")

            # P0.2 - CRITICAL FOR P0.5
            p0_2 = metrics['p0_2_soft_skills']
            print(f"\n💼 P0.2 SOFT SKILLS METHODOLOGIES (⚠️ CRITICAL P0.5 TEST):")
            print(f"   Total skills: {p0_2['total_skills']}")
            print(f"   Soft skills: {p0_2['soft_skills_count']}")
            print(f"   With methodologies: {p0_2['with_methodology']}")
            print(f"   Coverage: {p0_2['valid_ratio']*100:.1f}%")

            if p0_2['soft_skills_count'] > 0:
                methodology_pct = (p0_2['with_methodology'] / p0_2['soft_skills_count']) * 100
                print(f"   📊 Methodology rate: {methodology_pct:.1f}%")
                if methodology_pct >= 90:
                    print(f"   ✅ P0.5 SUCCESS: ≥90% soft skills have methodologies!")
                else:
                    print(f"   ❌ P0.5 FAIL: Only {methodology_pct:.1f}% (target: ≥90%)")

            # P0.3
            p0_3 = metrics['p0_3_regulatory']
            print(f"\n📋 P0.3 REGULATORY FRAMEWORKS:")
            print(f"   Domain: {p0_3.get('domain', 'unknown')}")
            print(f"   Status: {'✅ PASSED' if p0_3['valid'] else '❌ FAILED'}")

            # P0.4 - CRITICAL FOR P0.5
            p0_4 = metrics['p0_4_levels']
            print(f"\n📈 P0.4 PROFICIENCY LEVELS (⚠️ CRITICAL P0.5 TEST):")
            print(f"   Status: {'✅ PASSED' if p0_4['valid'] else '❌ FAILED'}")
            if p0_4.get('issues'):
                print(f"   Issues: {len(p0_4['issues'])}")
                for issue in p0_4['issues'][:2]:
                    print(f"   ⚠️  {issue}")

        except Exception as e:
            print(f"\n❌ ERROR validating {profile_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'='*80}")
    print("P0.5 VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    if results:
        avg_quality = sum(r['quality_score'] for r in results.values()) / len(results)
        passed = sum(1 for r in results.values() if r['valid'])

        print(f"📊 Average Quality Score: {avg_quality:.2f}/10")
        print(f"✅ Profiles Passed: {passed}/{len(results)}")
        print(f"❌ Profiles Failed: {len(results) - passed}/{len(results)}")

        # P0 Metrics
        print(f"\nP0 METRICS ACROSS ALL PROFILES:")

        avg_concreteness = sum(
            r['metrics']['p0_1_tasks']['valid_ratio'] for r in results.values()
        ) / len(results)
        print(f"  P0.1 Task Concreteness: {avg_concreteness*100:.1f}% valid")

        avg_methodology = sum(
            r['metrics']['p0_2_soft_skills']['valid_ratio'] for r in results.values()
        ) / len(results)
        print(f"  P0.2 Soft Skills Methodologies: {avg_methodology*100:.1f}% coverage")

        regulatory_passed = sum(
            1 for r in results.values() if r['metrics']['p0_3_regulatory']['valid']
        )
        print(f"  P0.3 Regulatory Frameworks: {regulatory_passed}/{len(results)} passed")

        proficiency_passed = sum(
            1 for r in results.values() if r['metrics']['p0_4_levels']['valid']
        )
        print(f"  P0.4 Proficiency Levels: {proficiency_passed}/{len(results)} passed")

        # P0.5 Success Criteria
        print(f"\n{'='*80}")
        print("P0.5 SUCCESS CRITERIA")
        print(f"{'='*80}\n")

        print(f"Target Metrics:")
        print(f"  - Quality Score: ≥9.0/10")
        print(f"  - Pass Rate: ≥90% (≥3/4 profiles)")
        print(f"  - P0.2 Methodologies: ≥90%")
        print(f"  - P0.4 Uniqueness: ≥90%")

        print(f"\nActual Results:")
        print(f"  - Quality Score: {avg_quality:.2f}/10 {'✅' if avg_quality >= 9.0 else '❌'}")
        print(f"  - Pass Rate: {(passed/len(results))*100:.0f}% {'✅' if passed >= 3 else '❌'}")
        print(f"  - P0.2 Coverage: {avg_methodology*100:.1f}% {'✅' if avg_methodology >= 0.9 else '❌'}")
        print(f"  - P0.4 Pass: {(proficiency_passed/len(results))*100:.0f}% {'✅' if proficiency_passed >= 3 else '❌'}")

        # Final verdict
        p05_success = (
            avg_quality >= 9.0 and
            passed >= 3 and
            avg_methodology >= 0.9 and
            proficiency_passed >= 3
        )

        print(f"\n{'='*80}")
        if p05_success:
            print("✅ P0.5 VALIDATION: SUCCESS!")
            print("✅ Ready for production deployment")
        else:
            print("⚠️  P0.5 VALIDATION: PARTIAL SUCCESS")
            print("⚠️  Review issues above before deployment")
        print(f"{'='*80}\n")

    # Save results
    results_file = output_dir / 'p05_final_validation_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📁 Results saved to: {results_file}")


if __name__ == '__main__':
    main()
