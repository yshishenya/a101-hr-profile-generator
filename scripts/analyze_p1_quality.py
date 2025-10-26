#!/usr/bin/env python3
"""
Analysis script for P1 quality improvements in generated profiles.

Checks:
1. Skill category naming compliance with P1.1 enhanced rules
2. Proficiency level/description mapping accuracy with P1.2 rules
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Expected P1.1 skill category patterns
EXPECTED_PATTERNS = [
    "Знания и умения в области",
    "Знания и умения",
    "Технические",
    "Методологические",
    "Управленческие",
]

# P1.2 Proficiency level mapping (from prompt lines 113-181)
PROFICIENCY_MAPPING = {
    1: "Базовые знания",
    2: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях",
    3: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях",
    4: "Экспертные знания и практика",
    5: "Лидерство в отрасли"
}


def analyze_skill_naming(profile: dict) -> Tuple[int, int, List[str]]:
    """
    Analyze skill category naming compliance.

    Returns:
        (compliant_count, total_count, issues)
    """
    professional_skills = profile.get("profile", {}).get("professional_skills", [])
    total = len(professional_skills)
    compliant = 0
    issues = []

    for idx, skill_group in enumerate(professional_skills):
        category = skill_group.get("skill_category", "")

        # Check if matches expected patterns
        is_compliant = any(pattern in category for pattern in EXPECTED_PATTERNS)

        if is_compliant:
            compliant += 1
        else:
            issues.append(f"Category {idx+1}: '{category}' doesn't match expected patterns")

    return compliant, total, issues


def analyze_proficiency_mapping(profile: dict) -> Tuple[int, int, List[str]]:
    """
    Analyze proficiency level/description mapping accuracy.

    Returns:
        (accurate_count, total_count, issues)
    """
    professional_skills = profile.get("profile", {}).get("professional_skills", [])
    total_skills = 0
    accurate = 0
    issues = []

    for skill_group in professional_skills:
        category = skill_group.get("skill_category", "")
        specific_skills = skill_group.get("specific_skills", [])

        for skill in specific_skills:
            total_skills += 1
            level = skill.get("proficiency_level")
            description = skill.get("proficiency_description", "")
            skill_name = skill.get("skill_name", "")[:50]  # First 50 chars

            # Check if level and description match
            expected_desc = PROFICIENCY_MAPPING.get(level)

            if expected_desc:
                # For levels 2 and 3, they have the same description
                # Check if description matches expected
                if description == expected_desc:
                    accurate += 1
                else:
                    issues.append(
                        f"Skill '{skill_name}...' in '{category}': "
                        f"Level {level} has description '{description[:60]}...' "
                        f"but expected '{expected_desc[:60]}...'"
                    )
            else:
                issues.append(
                    f"Skill '{skill_name}...' in '{category}': "
                    f"Invalid level {level} (expected 1-5)"
                )

    return accurate, total_skills, issues


def generate_report(profile_path: str) -> None:
    """Generate quality analysis report for a profile."""

    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    print("=" * 80)
    print("P1 QUALITY ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nProfile: {profile_path}")
    print(f"Position: {profile.get('profile', {}).get('position_title', 'N/A')}")
    print(f"Department: {profile.get('profile', {}).get('department_specific', 'N/A')}")
    print()

    # Analyze skill naming (P1.1)
    print("-" * 80)
    print("P1.1 - SKILL CATEGORY NAMING COMPLIANCE")
    print("-" * 80)

    compliant, total_cats, naming_issues = analyze_skill_naming(profile)
    compliance_pct = (compliant / total_cats * 100) if total_cats > 0 else 0

    print(f"Compliant categories: {compliant}/{total_cats} ({compliance_pct:.1f}%)")
    print(f"Target: ≥90%")
    print(f"Status: {'✅ PASS' if compliance_pct >= 90 else '❌ FAIL'}")

    if naming_issues:
        print("\nIssues found:")
        for issue in naming_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No naming issues found!")

    # Analyze proficiency mapping (P1.2)
    print("\n" + "-" * 80)
    print("P1.2 - PROFICIENCY LEVEL/DESCRIPTION MAPPING")
    print("-" * 80)

    accurate, total_skills, mapping_issues = analyze_proficiency_mapping(profile)
    accuracy_pct = (accurate / total_skills * 100) if total_skills > 0 else 0

    print(f"Accurate mappings: {accurate}/{total_skills} ({accuracy_pct:.1f}%)")
    print(f"Target: ≥90%")
    print(f"Status: {'✅ PASS' if accuracy_pct >= 90 else '❌ FAIL'}")

    if mapping_issues:
        print("\nIssues found:")
        for issue in mapping_issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(mapping_issues) > 10:
            print(f"  ... and {len(mapping_issues) - 10} more issues")
    else:
        print("\n✅ No mapping issues found!")

    # Overall summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Skill categories: {total_cats}")
    print(f"Total skills: {total_skills}")
    print(f"Naming compliance: {compliance_pct:.1f}% (target: ≥90%)")
    print(f"Mapping accuracy: {accuracy_pct:.1f}% (target: ≥90%)")

    overall_pass = compliance_pct >= 90 and accuracy_pct >= 90
    print(f"\nOverall: {'✅ PASS' if overall_pass else '❌ NEEDS IMPROVEMENT'}")
    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_p1_quality.py <profile.json>")
        sys.exit(1)

    profile_path = sys.argv[1]

    if not Path(profile_path).exists():
        print(f"Error: File not found: {profile_path}")
        sys.exit(1)

    generate_report(profile_path)


if __name__ == '__main__':
    main()
