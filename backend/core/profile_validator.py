"""
Валидация профилей по новым метрикам P0.

Метрики:
- P0.1: Конкретность задач (concrete_elements >= 2, filler_ratio < 15%)
- P0.2: Методики для soft skills (has_methodology if soft_skill)
- P0.3: Regulatory frameworks (has_framework if applicable domain)
- P0.4: Разные уровни владения (unique descriptions per level)
"""

import re
from typing import Dict, List, Any, Tuple
import json


class ProfileValidator:
    """Валидатор качества профилей по метрикам P0."""

    # Служебные фразы (filler phrases)
    FILLER_PHRASES = [
        "в соответствии с",
        "обеспечивать соответствие",
        "осуществление подготовки",
        "выполнение работ по",
        "проведение мероприятий",
        "обеспечение выполнения"
    ]

    # Regulatory frameworks по доменам
    REGULATORY_FRAMEWORKS = {
        'finance': ['МСФО', 'IFRS', 'РСБУ', 'налоговый', 'GAAP'],
        'hr': ['ТК РФ', 'Трудовое право', '152-ФЗ', 'персональные данные'],
        'legal': ['ГК РФ', 'корпоративное право', 'АПК'],
        'construction': ['ГОСТ', 'СНиП', 'СП', 'градостроительный'],
        'it': ['архитектурн', 'паттерн', 'security', 'OWASP']
    }

    # Методики для soft skills
    SOFT_SKILL_METHODOLOGIES = [
        'GROW', 'CLEAR', 'SBI', 'BATNA', 'Kotter', 'ADKAR',
        'RACI', 'SCARF', 'Cialdini', 'Win-Win', 'framework',
        'model', 'method', 'approach', 'technique'
    ]

    def validate_task_concreteness(self, task: str) -> Dict[str, Any]:
        """
        P0.1: Валидация конкретности задачи.

        Returns:
            {
                'valid': bool,
                'concrete_elements': int,
                'filler_ratio': float,
                'issues': List[str]
            }
        """
        issues = []

        # Подсчет конкретных элементов (перечисления через запятую)
        concrete_elements = len([p for p in task.split(',') if len(p.strip()) > 2])

        # Если нет запятых, проверяем списки через союзы
        if concrete_elements <= 1:
            concrete_patterns = [' и ', ' или ', ': ']
            for pattern in concrete_patterns:
                concrete_elements += task.count(pattern)

        # Подсчет filler phrases
        filler_count = sum(1 for phrase in self.FILLER_PHRASES if phrase in task.lower())
        words_count = len(task.split())
        filler_ratio = filler_count / max(words_count, 1) if words_count > 0 else 0

        # Проверки
        if concrete_elements < 2:
            issues.append(f"Недостаточно конкретных элементов: {concrete_elements} < 2")

        if filler_ratio >= 0.15:
            issues.append(f"Слишком много служебных фраз: {filler_ratio:.1%} >= 15%")

        return {
            'valid': len(issues) == 0,
            'concrete_elements': concrete_elements,
            'filler_ratio': filler_ratio,
            'task_length': len(task),
            'issues': issues
        }

    def validate_soft_skill_methodology(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """
        P0.2: Валидация наличия методики для soft skill.

        Returns:
            {
                'valid': bool,
                'is_soft_skill': bool,
                'has_methodology': bool,
                'found_methodologies': List[str],
                'issues': List[str]
            }
        """
        issues = []
        skill_text = f"{skill.get('skill_name', '')} {skill.get('description', '')}".lower()

        # Определяем soft skill по ключевым словам
        soft_skill_keywords = [
            'coaching', 'leadership', 'коммуникац', 'переговор',
            'влияние', 'убеждение', 'изменени', 'stakeholder',
            'команд', 'презентац', 'обучен'
        ]
        is_soft_skill = any(keyword in skill_text for keyword in soft_skill_keywords)

        # Ищем методики
        found_methodologies = [
            method for method in self.SOFT_SKILL_METHODOLOGIES
            if method.lower() in skill_text
        ]
        has_methodology = len(found_methodologies) > 0

        # Валидация: если soft skill, должна быть методика
        if is_soft_skill and not has_methodology:
            issues.append(f"Soft skill без методики: {skill.get('skill_name', 'N/A')}")

        return {
            'valid': len(issues) == 0,
            'is_soft_skill': is_soft_skill,
            'has_methodology': has_methodology,
            'found_methodologies': found_methodologies,
            'issues': issues
        }

    def validate_regulatory_frameworks(
        self,
        profile: Dict[str, Any],
        domain: str = None
    ) -> Dict[str, Any]:
        """
        P0.3: Валидация наличия regulatory frameworks.

        Args:
            profile: Полный профиль
            domain: 'finance', 'hr', 'legal', 'construction', 'it'

        Returns:
            {
                'valid': bool,
                'domain': str,
                'required': bool,
                'has_framework': bool,
                'found_frameworks': List[str],
                'issues': List[str]
            }
        """
        issues = []

        # Автоопределение домена из department
        if not domain:
            department = profile.get('department_specific', '').lower()
            if any(word in department for word in ['финанс', 'бухгалтер', 'finance']):
                domain = 'finance'
            elif any(word in department for word in ['персонал', 'hr', 'кадр']):
                domain = 'hr'
            elif any(word in department for word in ['юридич', 'legal', 'правов']):
                domain = 'legal'
            elif any(word in department for word in ['проектир', 'архитектур', 'строител']):
                domain = 'construction'
            elif any(word in department for word in ['it', 'информац', 'разработ']):
                domain = 'it'
            else:
                domain = 'unknown'

        required_frameworks = self.REGULATORY_FRAMEWORKS.get(domain, [])
        required = len(required_frameworks) > 0

        # Проверяем наличие фреймворков в навыках
        profile_text = json.dumps(profile, ensure_ascii=False).lower()
        found_frameworks = [
            fw for fw in required_frameworks
            if fw.lower() in profile_text
        ]
        has_framework = len(found_frameworks) > 0

        # Валидация
        if required and not has_framework:
            issues.append(
                f"Отсутствуют regulatory frameworks для домена '{domain}'. "
                f"Ожидаются: {', '.join(required_frameworks)}"
            )

        return {
            'valid': len(issues) == 0,
            'domain': domain,
            'required': required,
            'has_framework': has_framework,
            'found_frameworks': found_frameworks,
            'expected_frameworks': required_frameworks,
            'issues': issues
        }

    def validate_proficiency_levels(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        P0.4: Валидация описаний уровней владения.

        Правила (на основе анализа оригинальных XLS):
        1. Все навыки ОДНОГО уровня должны иметь ОДНО описание
        2. РАЗНЫЕ уровни должны иметь РАЗНЫЕ описания

        Стандартные описания из XLS:
        - Уровень 1: "Знание основ, опыт применения знаний и навыков на практике необязателен"
        - Уровень 2: "Существенные знания и регулярный опыт применения знаний на практике"
        - Уровень 3: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
        - Уровень 4: "Экспертные знания, должность подразумевает передачу знаний и опыта другим"

        Returns:
            {
                'valid': bool,
                'levels_found': List[int],
                'unique_descriptions': int,
                'should_be_unique': int,
                'duplicate_descriptions': Dict[str, List[int]],
                'issues': List[str]
            }
        """
        issues = []

        # Собираем все описания по уровням (не только первое, а все)
        all_descriptions_by_level = {}  # level -> [desc1, desc2, ...]

        for skill_cat in profile.get('professional_skills', []):
            for skill in skill_cat.get('specific_skills', []):
                level = skill.get('proficiency_level')
                desc = skill.get('proficiency_description', '')
                if level and desc:
                    if level not in all_descriptions_by_level:
                        all_descriptions_by_level[level] = []
                    all_descriptions_by_level[level].append(desc)

        # Правило 1: Все навыки одного уровня должны иметь одно описание
        level_to_canonical_desc = {}
        for level, descriptions in all_descriptions_by_level.items():
            unique_descs = set(descriptions)
            if len(unique_descs) > 1:
                issues.append(
                    f"Уровень {level} имеет {len(unique_descs)} разных описаний "
                    f"(должно быть 1 описание для всех {len(descriptions)} навыков этого уровня)"
                )
                # Для отчетности берем первое
                level_to_canonical_desc[level] = descriptions[0]
            else:
                # Все описания одинаковые - это норма
                level_to_canonical_desc[level] = list(unique_descs)[0]

        # Правило 2: Разные уровни должны иметь разные описания
        desc_to_levels = {}
        for level, desc in level_to_canonical_desc.items():
            if desc not in desc_to_levels:
                desc_to_levels[desc] = []
            desc_to_levels[desc].append(level)

        duplicate_descriptions = {
            desc: levels for desc, levels in desc_to_levels.items()
            if len(levels) > 1
        }

        if duplicate_descriptions:
            for desc, levels in duplicate_descriptions.items():
                issues.append(
                    f"Одинаковое описание используется для разных уровней {levels}: "
                    f"'{desc[:80]}...'"
                )

        levels_found = sorted(all_descriptions_by_level.keys())
        unique_descriptions = len(set(level_to_canonical_desc.values()))
        should_be_unique = len(level_to_canonical_desc)

        return {
            'valid': len(issues) == 0,
            'levels_found': levels_found,
            'unique_descriptions': unique_descriptions,
            'should_be_unique': should_be_unique,
            'duplicate_descriptions': duplicate_descriptions,
            'issues': issues
        }

    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полная валидация профиля по всем метрикам P0.

        Returns:
            {
                'valid': bool,
                'quality_score': float (0-10),
                'metrics': {
                    'p0_1_tasks': {...},
                    'p0_2_soft_skills': {...},
                    'p0_3_regulatory': {...},
                    'p0_4_levels': {...}
                },
                'summary': {
                    'total_issues': int,
                    'critical_issues': List[str],
                    'warnings': List[str]
                }
            }
        """
        all_issues = []
        all_warnings = []

        # P0.1: Валидация задач
        tasks_results = []
        for area in profile.get('responsibility_areas', []):
            for task in area.get('tasks', []):
                result = self.validate_task_concreteness(task)
                tasks_results.append(result)
                if not result['valid']:
                    all_issues.extend(result['issues'])

        tasks_valid_ratio = (
            sum(1 for r in tasks_results if r['valid']) / len(tasks_results)
            if tasks_results else 0
        )

        # P0.2: Валидация soft skills
        soft_skills_results = []
        for skill_cat in profile.get('professional_skills', []):
            for skill in skill_cat.get('specific_skills', []):
                result = self.validate_soft_skill_methodology(skill)
                soft_skills_results.append(result)
                if not result['valid']:
                    all_warnings.extend(result['issues'])  # Warning, не critical

        soft_skills_valid_ratio = (
            sum(1 for r in soft_skills_results if r['valid']) / len(soft_skills_results)
            if soft_skills_results else 1.0
        )

        # P0.3: Валидация regulatory frameworks
        regulatory_result = self.validate_regulatory_frameworks(profile)
        if not regulatory_result['valid']:
            if regulatory_result['required']:
                all_issues.extend(regulatory_result['issues'])
            else:
                all_warnings.extend(regulatory_result['issues'])

        # P0.4: Валидация уровней владения
        levels_result = self.validate_proficiency_levels(profile)
        if not levels_result['valid']:
            all_issues.extend(levels_result['issues'])

        # Расчет quality score
        quality_score = (
            tasks_valid_ratio * 3 +  # 30% веса
            soft_skills_valid_ratio * 2 +  # 20% веса
            (1 if regulatory_result['valid'] else 0) * 2 +  # 20% веса
            (1 if levels_result['valid'] else 0) * 3  # 30% веса
        )

        return {
            'valid': len(all_issues) == 0,
            'quality_score': quality_score,
            'metrics': {
                'p0_1_tasks': {
                    'total_tasks': len(tasks_results),
                    'valid_tasks': sum(1 for r in tasks_results if r['valid']),
                    'valid_ratio': tasks_valid_ratio,
                    'avg_concrete_elements': (
                        sum(r['concrete_elements'] for r in tasks_results) / len(tasks_results)
                        if tasks_results else 0
                    ),
                    'avg_filler_ratio': (
                        sum(r['filler_ratio'] for r in tasks_results) / len(tasks_results)
                        if tasks_results else 0
                    )
                },
                'p0_2_soft_skills': {
                    'total_skills': len(soft_skills_results),
                    'soft_skills_count': sum(1 for r in soft_skills_results if r['is_soft_skill']),
                    'with_methodology': sum(
                        1 for r in soft_skills_results
                        if r['is_soft_skill'] and r['has_methodology']
                    ),
                    'valid_ratio': soft_skills_valid_ratio
                },
                'p0_3_regulatory': regulatory_result,
                'p0_4_levels': levels_result
            },
            'summary': {
                'total_issues': len(all_issues),
                'total_warnings': len(all_warnings),
                'critical_issues': all_issues,
                'warnings': all_warnings
            }
        }


def main():
    """Пример использования валидатора."""
    validator = ProfileValidator()

    # Пример профиля для валидации
    test_profile = {
        "department_specific": "Департамент персонала",
        "responsibility_areas": [
            {
                "area": ["Подбор и адаптация"],
                "tasks": [
                    "Подбор специалистов: интервьюирование, assessment center, оффер",
                    "Разрабатывать программы адаптации в соответствии с требованиями компании"
                ]
            }
        ],
        "professional_skills": [
            {
                "skill_category": "Подбор персонала",
                "specific_skills": [
                    {
                        "skill_name": "Интервьюирование",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания..."
                    },
                    {
                        "skill_name": "Coaching сотрудников",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания..."
                    }
                ]
            }
        ]
    }

    result = validator.validate_profile(test_profile)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
