"""
Автоматические тесты для валидации качества профилей.
"""

import pytest
import sys
sys.path.insert(0, '/home/yan/A101/HR')

from backend.core.profile_validator import ProfileValidator


class TestP01TaskConcreteness:
    """Тесты для P0.1: Конкретность задач."""

    def test_good_task_with_list(self):
        """Хорошая задача со списком элементов."""
        validator = ProfileValidator()
        task = "Моделирование перекрытий, колонн, пилонов, стен, окон"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == True
        assert result['concrete_elements'] >= 5
        assert result['filler_ratio'] < 0.15

    def test_bad_task_with_filler(self):
        """Плохая задача с filler phrases."""
        validator = ProfileValidator()
        task = "Разрабатывать проекты в соответствии с техническим заданием и требованиями"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == False
        assert result['concrete_elements'] < 2

    def test_medium_task(self):
        """Средняя задача."""
        validator = ProfileValidator()
        task = "Подготовка отчетности: МСФО, РСБУ, налоговые декларации"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == True
        assert result['concrete_elements'] >= 3


class TestP02SoftSkillMethodologies:
    """Тесты для P0.2: Методики для soft skills."""

    def test_soft_skill_with_methodology(self):
        """Soft skill с методикой."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Coaching (GROW model, structured feedback)",
            "proficiency_level": 3
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == True
        assert result['is_soft_skill'] == True
        assert result['has_methodology'] == True

    def test_soft_skill_without_methodology(self):
        """Soft skill без методики - ошибка."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Coaching сотрудников",
            "proficiency_level": 2
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == False
        assert result['is_soft_skill'] == True
        assert result['has_methodology'] == False

    def test_technical_skill_no_methodology_needed(self):
        """Технический навык - методика не нужна."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Python - разработка backend",
            "proficiency_level": 3
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == True
        assert result['is_soft_skill'] == False


class TestP03RegulatoryFrameworks:
    """Тесты для P0.3: Regulatory frameworks."""

    def test_finance_with_frameworks(self):
        """Финансовый профиль с МСФО."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Финансовый департамент",
            "professional_skills": [{
                "skill_category": "Бухгалтерский учет",
                "specific_skills": [{
                    "skill_name": "МСФО - методики признания выручки"
                }]
            }]
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == True
        assert result['domain'] == 'finance'
        assert result['has_framework'] == True

    def test_hr_with_tk_rf(self):
        """HR профиль с ТК РФ."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "professional_skills": [{
                "skill_category": "HR compliance",
                "specific_skills": [{
                    "skill_name": "Трудовое право РФ (ТК РФ)"
                }]
            }]
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == True
        assert result['domain'] == 'hr'
        assert result['has_framework'] == True

    def test_hr_without_tk_rf(self):
        """HR профиль БЕЗ ТК РФ - ошибка."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "professional_skills": []
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == False
        assert result['domain'] == 'hr'
        assert result['required'] == True
        assert result['has_framework'] == False


class TestP04ProficiencyLevels:
    """Тесты для P0.4: Разные уровни владения."""

    def test_different_descriptions_for_levels(self):
        """Разные описания для каждого уровня - OK."""
        validator = ProfileValidator()
        profile = {
            "professional_skills": [{
                "skill_category": "Technical",
                "specific_skills": [
                    {
                        "skill_name": "Python",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания, опыт в кризисных ситуациях"
                    },
                    {
                        "skill_name": "Docker",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания в сложных ситуациях"
                    },
                    {
                        "skill_name": "K8s",
                        "proficiency_level": 1,
                        "proficiency_description": "Базовые знания в стандартных ситуациях"
                    }
                ]
            }]
        }
        result = validator.validate_proficiency_levels(profile)

        assert result['valid'] == True
        assert result['unique_descriptions'] == 3
        assert result['should_be_unique'] == 3

    def test_same_description_for_different_levels(self):
        """Одинаковое описание для разных уровней - ошибка."""
        validator = ProfileValidator()
        profile = {
            "professional_skills": [{
                "skill_category": "Technical",
                "specific_skills": [
                    {
                        "skill_name": "Python",
                        "proficiency_level": 3,
                        "proficiency_description": "Существенные знания"
                    },
                    {
                        "skill_name": "Docker",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания"
                    }
                ]
            }]
        }
        result = validator.validate_proficiency_levels(profile)

        assert result['valid'] == False
        assert result['unique_descriptions'] < result['should_be_unique']


class TestProfileValidation:
    """Интеграционные тесты полной валидации профиля."""

    def test_good_profile_all_checks_pass(self):
        """Хороший профиль проходит все проверки."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент информационных технологий",
            "responsibility_areas": [{
                "area": ["Разработка"],
                "tasks": [
                    "Разработка REST API, GraphQL endpoints, GRPC сервисов",
                    "Оптимизация SQL: индексы, партиционирование, кэширование"
                ]
            }],
            "professional_skills": [{
                "skill_category": "Backend development",
                "specific_skills": [
                    {
                        "skill_name": "Python - разработка сервисов",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания, опыт в кризисных ситуациях, обучение других"
                    },
                    {
                        "skill_name": "Docker - контейнеризация",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания в сложных ситуациях"
                    }
                ]
            }]
        }
        result = validator.validate_profile(profile)

        assert result['valid'] == True
        assert result['quality_score'] >= 8.0
        assert result['summary']['total_issues'] == 0

    def test_bad_profile_multiple_issues(self):
        """Плохой профиль с несколькими проблемами."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "responsibility_areas": [{
                "area": ["HR"],
                "tasks": [
                    "Разрабатывать программы в соответствии с требованиями"
                ]
            }],
            "professional_skills": [{
                "skill_category": "HR",
                "specific_skills": [
                    {
                        "skill_name": "Coaching",  # Без методики
                        "proficiency_level": 3,
                        "proficiency_description": "Знания"  # Одинаково для всех
                    },
                    {
                        "skill_name": "Recruitment",
                        "proficiency_level": 2,
                        "proficiency_description": "Знания"  # Одинаково
                    }
                ]
            }]
            # Нет ТК РФ!
        }
        result = validator.validate_profile(profile)

        assert result['valid'] == False
        assert result['quality_score'] < 7.0
        assert result['summary']['total_issues'] > 0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
