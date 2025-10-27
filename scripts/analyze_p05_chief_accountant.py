#!/usr/bin/env python3
"""
Analyze P0.5 Chief Accountant profile for key quality metrics.
"""

import json
from pathlib import Path

def analyze_p01_task_concreteness(profile_data: dict) -> dict:
    """
    P0.1: Task Concreteness Analysis
    Target: 95%+ tasks should be concrete and actionable
    """
    all_tasks = []
    for area in profile_data.get("responsibility_areas", []):
        all_tasks.extend(area.get("tasks", []))

    total_tasks = len(all_tasks)

    # Check for concrete action verbs and measurable outcomes
    concrete_verbs = [
        "организовывать", "контролировать", "готовить", "обеспечивать",
        "представлять", "анализировать", "разрабатывать", "проводить",
        "взаимодействовать", "согласовывать", "утверждать", "вести"
    ]

    concrete_count = 0
    task_analysis = []

    for task in all_tasks:
        task_lower = task.lower()
        is_concrete = any(verb in task_lower for verb in concrete_verbs)

        # Check for specificity (mentions of systems, timeframes, metrics)
        has_specifics = any(x in task for x in [
            "1С", "ERP", "РСБУ", "МСФО", "BI", "Power BI", "ELMA",
            "3-й рабочий день", "день", "период", "КС", "налог"
        ])

        if is_concrete and has_specifics:
            concrete_count += 1
            task_analysis.append({"task": task[:80], "concrete": True, "specific": True})
        else:
            task_analysis.append({"task": task[:80], "concrete": is_concrete, "specific": has_specifics})

    concreteness_score = (concrete_count / total_tasks * 100) if total_tasks > 0 else 0

    return {
        "metric": "P0.1: Task Concreteness",
        "total_tasks": total_tasks,
        "concrete_tasks": concrete_count,
        "score_percent": round(concreteness_score, 1),
        "target": "95%+",
        "status": "PASS" if concreteness_score >= 95 else "NEEDS_IMPROVEMENT",
        "sample_tasks": task_analysis[:5]
    }


def analyze_p03_regulatory_frameworks(profile_data: dict) -> dict:
    """
    P0.3: Regulatory Frameworks Analysis
    Target: МСФО, РСБУ, НК РФ should be present
    """
    # Convert entire profile to string for searching
    profile_str = json.dumps(profile_data, ensure_ascii=False)

    frameworks = {
        "МСФО": profile_str.count("МСФО"),
        "IFRS": profile_str.count("IFRS"),
        "РСБУ": profile_str.count("РСБУ"),
        "НК РФ": profile_str.count("НК РФ") + profile_str.count("налог"),
        "1С": profile_str.count("1С") + profile_str.count("1C"),
    }

    all_present = all(count > 0 for framework, count in frameworks.items() if framework in ["МСФО", "РСБУ"])

    return {
        "metric": "P0.3: Regulatory Frameworks Presence",
        "frameworks_mentioned": frameworks,
        "all_required_present": all_present,
        "target": "МСФО, РСБУ, Налоговое законодательство",
        "status": "PASS" if all_present else "FAIL",
        "details": "All critical accounting frameworks are mentioned" if all_present else "Some frameworks missing"
    }


def analyze_p04_proficiency_levels(profile_data: dict) -> dict:
    """
    P0.4: Proficiency Levels Uniqueness Analysis
    Target: Diverse proficiency levels (not all the same)
    """
    skills = profile_data.get("professional_skills", [])

    all_proficiency_levels = []
    for category in skills:
        for skill in category.get("specific_skills", []):
            level = skill.get("proficiency_level")
            all_proficiency_levels.append(level)

    from collections import Counter
    level_distribution = Counter(all_proficiency_levels)

    total_skills = len(all_proficiency_levels)
    unique_levels = len(level_distribution)

    # Calculate diversity score (entropy-based)
    max_diversity = min(total_skills, 4)  # Max 4 levels
    diversity_score = (unique_levels / max_diversity * 100) if max_diversity > 0 else 0

    # Check if all levels are the same (bad)
    all_same = unique_levels == 1

    return {
        "metric": "P0.4: Proficiency Levels Diversity",
        "total_skills": total_skills,
        "unique_levels": unique_levels,
        "level_distribution": dict(level_distribution),
        "diversity_score_percent": round(diversity_score, 1),
        "all_same_level": all_same,
        "target": "Diverse levels (2-4 unique levels)",
        "status": "FAIL" if all_same else ("GOOD" if unique_levels >= 2 else "NEEDS_IMPROVEMENT"),
        "warning": "All skills have same proficiency level!" if all_same else None
    }


def calculate_overall_quality(profile_data: dict) -> dict:
    """
    Calculate overall quality score based on multiple factors
    """
    validation = profile_data.get("metadata", {}).get("validation", {})

    # Check reasoning presence
    has_reasoning = all(key in profile_data for key in [
        "reasoning_context_analysis",
        "responsibility_areas_reasoning",
        "professional_skills_reasoning"
    ])

    # Check completeness
    completeness = validation.get("completeness_score", 0.0)

    # Check required fields
    required_fields = [
        "position_title", "department_specific", "responsibility_areas",
        "professional_skills", "experience_and_education", "performance_metrics"
    ]

    fields_present = sum(1 for field in required_fields if field in profile_data and profile_data[field])
    field_completeness = (fields_present / len(required_fields)) * 100

    return {
        "metric": "Overall Quality Score",
        "has_reasoning_blocks": has_reasoning,
        "completeness_score": completeness * 100,
        "field_completeness_percent": round(field_completeness, 1),
        "validation_errors": len(validation.get("errors", [])),
        "validation_warnings": len(validation.get("warnings", [])),
        "overall_status": "EXCELLENT" if field_completeness >= 95 and has_reasoning else "GOOD"
    }


def main():
    """Main analysis function"""
    profile_path = Path("/home/yan/A101/HR/output/profile_chief_accountant_p05.json")

    print("=" * 80)
    print("P0.5 CHIEF ACCOUNTANT PROFILE QUALITY ANALYSIS")
    print("=" * 80)
    print()

    # Load profile
    with open(profile_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    profile = data.get("profile", {})

    # Run analyses
    p01_result = analyze_p01_task_concreteness(profile)
    p03_result = analyze_p03_regulatory_frameworks(profile)
    p04_result = analyze_p04_proficiency_levels(profile)
    overall_result = calculate_overall_quality(profile)

    # Print results
    print("📊 P0.1: TASK CONCRETENESS")
    print("-" * 80)
    print(f"Total Tasks: {p01_result['total_tasks']}")
    print(f"Concrete Tasks: {p01_result['concrete_tasks']}")
    print(f"Score: {p01_result['score_percent']}% (Target: {p01_result['target']})")
    print(f"Status: {p01_result['status']}")
    print()
    print("Sample Tasks:")
    for task in p01_result['sample_tasks']:
        status = "✓" if task['concrete'] and task['specific'] else "✗"
        print(f"  {status} {task['task']}...")
    print()

    print("📊 P0.3: REGULATORY FRAMEWORKS")
    print("-" * 80)
    print(f"Frameworks Mentioned:")
    for framework, count in p03_result['frameworks_mentioned'].items():
        print(f"  - {framework}: {count} times")
    print(f"All Required Present: {p03_result['all_required_present']}")
    print(f"Status: {p03_result['status']}")
    print()

    print("📊 P0.4: PROFICIENCY LEVELS DIVERSITY")
    print("-" * 80)
    print(f"Total Skills: {p04_result['total_skills']}")
    print(f"Unique Levels: {p04_result['unique_levels']}")
    print(f"Level Distribution: {p04_result['level_distribution']}")
    print(f"Diversity Score: {p04_result['diversity_score_percent']}%")
    print(f"Status: {p04_result['status']}")
    if p04_result['warning']:
        print(f"⚠️  WARNING: {p04_result['warning']}")
    print()

    print("📊 OVERALL QUALITY SCORE")
    print("-" * 80)
    print(f"Has Reasoning Blocks: {overall_result['has_reasoning_blocks']}")
    print(f"Completeness Score: {overall_result['completeness_score']}%")
    print(f"Field Completeness: {overall_result['field_completeness_percent']}%")
    print(f"Validation Errors: {overall_result['validation_errors']}")
    print(f"Validation Warnings: {overall_result['validation_warnings']}")
    print(f"Overall Status: {overall_result['overall_status']}")
    print()

    # Final summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_pass = (
        p01_result['status'] == "PASS" and
        p03_result['status'] == "PASS" and
        p04_result['status'] in ["GOOD", "NEEDS_IMPROVEMENT"]
    )

    print(f"P0.1 Task Concreteness: {p01_result['status']} ({p01_result['score_percent']}%)")
    print(f"P0.3 Regulatory Frameworks: {p03_result['status']}")
    print(f"P0.4 Proficiency Diversity: {p04_result['status']}")
    print(f"Overall Quality: {overall_result['overall_status']}")
    print()

    if all_pass:
        print("✅ Profile meets P0.5 quality standards!")
    else:
        print("⚠️  Profile has some quality issues that need attention.")

    print()
    print("=" * 80)

    # Save results to JSON
    results = {
        "p01_task_concreteness": p01_result,
        "p03_regulatory_frameworks": p03_result,
        "p04_proficiency_levels": p04_result,
        "overall_quality": overall_result,
        "summary": {
            "all_tests_pass": all_pass,
            "profile_path": str(profile_path),
            "analysis_timestamp": data.get("metadata", {}).get("generation", {}).get("timestamp")
        }
    }

    results_path = profile_path.parent / "profile_chief_accountant_p05_analysis.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📁 Full analysis saved to: {results_path}")
    print()


if __name__ == '__main__':
    main()
