"""
@doc
Core service для генерации красивых Markdown документов из JSON профилей должностей.

Перемещен из services в core как domain service - генерация markdown
является частью бизнес-логики, не внешним сервисом.

Конвертирует структурированные JSON профили в читаемые MD документы
с правильным форматированием, таблицами и разделами.

Examples:
  python> generator = ProfileMarkdownService()
  python> md_content = generator.generate_from_json(profile_data)
  python> generator.save_md_file("profile.md", md_content)
"""

import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ProfileMarkdownService:
    """
    @doc
    Core service для генерации Markdown документов из JSON профилей должностей.

    Создает красиво отформатированные MD файлы с:
    - Структурированными разделами
    - Таблицами навыков
    - Списками задач и требований
    - Метаинформацией

    Examples:
      python> service = ProfileMarkdownService()
      python> md_text = service.generate_from_json(json_profile)
    """

    def __init__(self):
        # Больше не создаем отдельную папку для MD файлов
        # MD файлы теперь сохраняются рядом с JSON в иерархической структуре
        self.output_dir = None

    def generate_from_json(self, profile_data: Dict[str, Any]) -> str:
        """
        @doc
        Генерирует MD документ из JSON профиля.

        Args:
          profile_data: Словарь с данными профиля должности

        Returns:
          str: Готовый Markdown документ

        Examples:
          python> md = service.generate_from_json({"position_title": "Аналитик BI"})
        """
        try:
            # Если передана полная структура с "profile", извлекаем его
            # Если передан прямой профиль, используем его как есть
            if "profile" in profile_data:
                profile = profile_data.get("profile", {})
            else:
                profile = profile_data
            

            md_content = []

            # Заголовок документа
            # Generating header...")
            md_content.append(self._generate_header(profile))

            # Основная информация
            # Generating basic_info...")
            md_content.append(self._generate_basic_info(profile))

            # Области ответственности
            # Generating responsibilities...")
            md_content.append(self._generate_responsibilities(profile))

            # Профессиональные навыки
            # Generating skills...")
            md_content.append(self._generate_skills(profile))

            # Личностные качества
            # Generating personal_qualities...")
            md_content.append(self._generate_personal_qualities(profile))

            # Корпоративные компетенции
            # Generating corporate_competencies...")
            md_content.append(self._generate_corporate_competencies(profile))

            # Образование и опыт
            # Generating education...")
            md_content.append(self._generate_education(profile))

            # Карьерное развитие (карьерограмма)
            # Generating career_development...")
            md_content.append(self._generate_career_development(profile))

            # Обеспечение рабочего места
            # Generating workplace_provisioning...")
            md_content.append(self._generate_workplace_provisioning(profile))

            # Метрики эффективности
            # Generating performance_metrics...")
            md_content.append(self._generate_performance_metrics(profile))

            # Дополнительная информация
            # Generating additional_info...")
            md_content.append(self._generate_additional_info(profile))

            # Метаданные
            # Generating metadata...")
            md_content.append(self._generate_metadata(profile_data))

            return "\n\n".join(md_content)

        except Exception as e:
            logger.error(f"Error generating MD from JSON: {e}")
            return f"# Ошибка генерации профиля\n\n**Ошибка:** {str(e)}"

    def _generate_header(self, profile: Dict[str, Any]) -> str:
        """Генерирует заголовок документа"""
        title = profile.get("position_title", "Должность не указана")
        department = profile.get("department_specific", "")

        header = f"# 📋 {title}\n\n"
        if department:
            header += f"**Подразделение:** {department}\n\n"

        header += "---\n*Профиль должности создан системой A101 HR Profile Generator*"
        return header

    def _generate_basic_info(self, profile: Dict[str, Any]) -> str:
        """Генерирует базовую информацию о должности"""
        content = ["## 📊 Основная информация"]

        basic_info = [
            ("Название должности", profile.get("position_title", "Не указано")),
            ("Блок", profile.get("department_broad", "Не указано")),
            ("Департамент/Отдел", profile.get("department_specific", "Не указано")),
            (
                "Категория должности",
                profile.get("position_category", profile.get("category", "Не указано")),
            ),
            (
                "Непосредственный руководитель",
                profile.get("direct_manager", "Не указано"),
            ),
            (
                "Тип деятельности",
                profile.get(
                    "primary_activity_type",
                    profile.get("primary_activity", "Не указано"),
                ),
            ),
        ]

        # Подчиненные
        subordinates = profile.get("subordinates", {})
        if isinstance(subordinates, dict):
            departments = subordinates.get("departments", 0)
            people = subordinates.get("direct_reports", subordinates.get("people", 0))
            subordinates_text = f"Департаментов: {departments}, Человек: {people}"
        else:
            subordinates_text = str(subordinates)

        basic_info.append(("Подчиненные", subordinates_text))

        # Создаем таблицу
        content.append("\n| Параметр | Значение |")
        content.append("|----------|----------|")
        for param, value in basic_info:
            content.append(f"| **{param}** | {value} |")

        return "\n".join(content)

    def _generate_responsibilities(self, profile: Dict[str, Any]) -> str:
        """Генерирует области ответственности"""
        content = ["## 🎯 Области ответственности"]

        responsibilities = profile.get("responsibility_areas", [])
        if not responsibilities:
            return "\n".join(content + ["\n*Области ответственности не определены*"])

        for i, area in enumerate(responsibilities, 1):
            # Название области
            if isinstance(area, dict):
                area_name = area.get("area")
                if area_name is None:
                    area_name = area.get("title", f"Область {i}")
                elif isinstance(area_name, list):
                    area_name = area_name[0] if area_name else f"Область {i}"

                content.append(f"\n### {i}. {area_name}")

                # Задачи
                tasks = area.get("tasks", [])
                if tasks:
                    for task in tasks:
                        content.append(f"- {task}")
            elif isinstance(area, list):
                # Если area это список, обрабатываем как список строк
                content.append(f"\n### {i}. Область {i}")
                for task in area:
                    content.append(f"- {task}")
            else:
                content.append(f"\n### {i}. {str(area)}")

        return "\n".join(content)

    def _generate_skills(self, profile: Dict[str, Any]) -> str:
        """Генерирует профессиональные навыки"""
        content = ["## 🛠️ Профессиональные навыки"]

        skills = profile.get("professional_skills", [])
        if not skills:
            return "\n".join(content + ["\n*Профессиональные навыки не определены*"])

        for skill_category in skills:
            if isinstance(skill_category, dict):
                category_name = skill_category.get(
                    "skill_category",
                    skill_category.get("category", "Неизвестная категория"),
                )
                content.append(f"\n### {category_name}")

                # Конкретные навыки
                specific_skills = skill_category.get(
                    "specific_skills", skill_category.get("skills", [])
                )
            elif isinstance(skill_category, list):
                # Если skill_category это список, обрабатываем как список навыков
                content.append(f"\n### Навыки")
                specific_skills = skill_category
            else:
                # Если это строка или другой тип
                content.append(f"\n### {str(skill_category)}")
                specific_skills = []

            if specific_skills and len(specific_skills) > 0 and isinstance(specific_skills[0], dict):
                # Детальные навыки с уровнями
                content.append("\n| Навык | Уровень | Описание |")
                content.append("|-------|---------|----------|")

                for skill in specific_skills:
                    name = skill.get("skill_name", "Неизвестный навык")
                    level = skill.get(
                        "proficiency_level", skill.get("target_level", "Не указан")
                    )
                    description = skill.get(
                        "proficiency_description", "Описание отсутствует"
                    )

                    # Конвертируем числовой уровень в текст
                    if isinstance(level, int):
                        level_map = {
                            1: "Базовый",
                            2: "Средний",
                            3: "Продвинутый",
                            4: "Экспертный",
                        }
                        level_text = level_map.get(level, f"Уровень {level}")
                    else:
                        level_text = str(level)

                    content.append(f"| **{name}** | {level_text} | {description} |")
            else:
                # Простой список навыков
                for skill in specific_skills:
                    content.append(f"- {skill}")

        return "\n".join(content)

    def _generate_personal_qualities(self, profile: Dict[str, Any]) -> str:
        """Генерирует личностные качества"""
        content = ["## 👤 Личностные качества"]

        qualities = profile.get("personal_qualities", [])
        if not qualities:
            return "\n".join(content + ["\n*Личностные качества не определены*"])

        # Группируем качества по 3 в строку для компактности
        content.append("")
        for i in range(0, len(qualities), 3):
            row_qualities = qualities[i : i + 3]
            quality_badges = []
            for q in row_qualities:
                if isinstance(q, dict):
                    quality_name = q.get("quality", q.get("name", "Качество"))
                    quality_badges.append(f"🔹 **{quality_name.capitalize()}**")
                else:
                    quality_badges.append(f"🔹 **{str(q).capitalize()}**")
            content.append(" | ".join(quality_badges))

        return "\n".join(content)

    def _generate_corporate_competencies(self, profile: Dict[str, Any]) -> str:
        """Генерирует корпоративные компетенции"""
        content = ["## 🏢 Корпоративные компетенции"]

        competencies = profile.get("corporate_competencies", [])
        if not competencies:
            return "\n".join(content + ["\n*Корпоративные компетенции не определены*"])

        # Группируем компетенции по 2 в строку для лучшего отображения
        content.append("")
        for i in range(0, len(competencies), 2):
            row_competencies = competencies[i : i + 2]
            competency_badges = []
            for comp in row_competencies:
                if isinstance(comp, dict):
                    comp_name = comp.get("competency", comp.get("name", "Компетенция"))
                    competency_badges.append(f"🎯 **{comp_name}**")
                else:
                    competency_badges.append(f"🎯 **{str(comp)}**")
            content.append(" | ".join(competency_badges))

        return "\n".join(content)

    def _generate_education(self, profile: Dict[str, Any]) -> str:
        """Генерирует требования к образованию"""
        content = ["## 🎓 Образование и опыт работы"]

        education = profile.get(
            "experience_and_education",
            profile.get("education_requirements", profile.get("education", {})),
        )
        if not education:
            return "\n".join(content + ["\n*Требования к образованию не определены*"])

        edu_info = []

        # Уровень образования
        if "education_level" in education:
            edu_info.append(("Уровень образования", education["education_level"]))

        # Область обучения (новое поле)
        field_of_study = education.get("field_of_study")
        if field_of_study:
            edu_info.append(("Область обучения", field_of_study))

        # Опыт работы (новые поля в новой схеме)
        total_work_experience = education.get(
            "total_work_experience", education.get("total_experience")
        )
        if total_work_experience:
            edu_info.append(("Общий опыт работы", total_work_experience))

        previous_position_experience = education.get("previous_position_experience")
        if previous_position_experience:
            edu_info.append(("Опыт на аналогичной позиции", previous_position_experience))

        # Релевантный опыт (старое поле)
        if "relevant_experience" in education:
            edu_info.append(("Релевантный опыт", education["relevant_experience"]))

        # Специальности (старое поле для совместимости)
        specializations = education.get(
            "preferred_specializations", education.get("specialties")
        )
        if specializations:
            if isinstance(specializations, list):
                spec_text = ", ".join(specializations)
            else:
                spec_text = str(specializations)
            edu_info.append(("Предпочтительные специальности", spec_text))

        # Дополнительные сертификаты и образование
        certs = education.get(
            "additional_certifications", education.get("additional_education")
        )
        if certs:
            if isinstance(certs, list):
                content.append("\n**Дополнительные сертификаты и курсы:**")
                for cert in certs:
                    content.append(f"- {cert}")
            else:
                edu_info.append(("Дополнительное образование", str(certs)))

        # Таблица основной информации
        if edu_info:
            content.append("\n| Требование | Описание |")
            content.append("|------------|----------|")
            for req, desc in edu_info:
                content.append(f"| **{req}** | {desc} |")

        return "\n".join(content)

    def _generate_career_development(self, profile: Dict[str, Any]) -> str:
        """Генерирует карьерограмму (карьерное развитие)"""
        content = ["## 📈 Карьерограмма"]

        # Поддерживаем новую структуру careerogram и старую
        # career_development/career_path
        careerogram = profile.get("careerogram", {})
        career_legacy = profile.get(
            "career_development", profile.get("career_path", {})
        )

        # Объединяем данные
        career_data = {**career_legacy, **careerogram}

        if not career_data:
            return "\n".join(
                content + ["\n*Информация о карьерном развитии не определена*"]
            )

        # Новая структура careerogram: source_positions и target_pathways
        source_positions = career_data.get("source_positions", {})
        target_pathways = career_data.get("target_pathways", {})
        
        if source_positions:
            content.append("\n### 🚪 Входные позиции")
            
            # Проверяем, какая структура у source_positions
            if isinstance(source_positions, list):
                # Новый формат: простой список позиций
                content.append("\n**Предшествующие позиции:**")
                for pos in source_positions:
                    content.append(f"- {pos}")
            elif isinstance(source_positions, dict):
                # Старый формат: словарь с детализацией
                # Прямые предшественники
                direct_predecessors = source_positions.get("direct_predecessors", [])
                if direct_predecessors:
                    content.append("\n**Прямые предшественники:**")
                    for pos in direct_predecessors:
                        content.append(f"- {pos}")
                
                # Смежные входы
                cross_functional = source_positions.get("cross_functional_entrants", [])
                content.append("\n**Смежные переходы:**")
                for pos in cross_functional:
                    content.append(f"- {pos}")

        if target_pathways:
            content.append("\n### 🚀 Карьерные пути")
            
            # Вертикальный рост
            vertical_growth = target_pathways.get("vertical_growth", [])
            if vertical_growth:
                content.append("\n#### ⬆️ Вертикальный рост")
                for position in vertical_growth:
                    if isinstance(position, dict):
                        target = position.get("target_position", "Не указано")
                        department = position.get("target_department", "")
                        rationale = position.get("rationale", "")
                        
                        content.append(f"\n**{target}**")
                        if department:
                            content.append(f"*Департамент:* {department}")
                        if rationale:
                            content.append(f"*Обоснование:* {rationale}")
                        
                        # Развитие компетенций
                        competency_bridge = position.get("competency_bridge", {})
                        if competency_bridge:
                            strengthen = competency_bridge.get("strengthen_skills", [])
                            if strengthen:
                                content.append("*Навыки для развития:*")
                                for skill in strengthen:
                                    content.append(f"- {skill}")
                            
                            acquire = competency_bridge.get("acquire_skills", [])
                            if acquire:
                                content.append("*Новые навыки:*")
                                for skill in acquire:
                                    content.append(f"- {skill}")
                    else:
                        content.append(f"- {position}")

            # Горизонтальный рост
            horizontal_growth = target_pathways.get("horizontal_growth", [])
            if horizontal_growth:
                content.append("\n#### ↔️ Горизонтальный рост")
                for position in horizontal_growth:
                    if isinstance(position, dict):
                        target = position.get("target_position", "Не указано")
                        department = position.get("target_department", "")
                        rationale = position.get("rationale", "")
                        
                        content.append(f"\n**{target}**")
                        if department:
                            content.append(f"*Департамент:* {department}")
                        if rationale:
                            content.append(f"*Обоснование:* {rationale}")
                        
                        # Развитие компетенций
                        competency_bridge = position.get("competency_bridge", {})
                        if competency_bridge:
                            strengthen = competency_bridge.get("strengthen_skills", [])
                            if strengthen:
                                content.append("*Навыки для развития:*")
                                for skill in strengthen:
                                    content.append(f"- {skill}")
                            
                            acquire = competency_bridge.get("acquire_skills", [])
                            if acquire:
                                content.append("*Новые навыки:*")
                                for skill in acquire:
                                    content.append(f"- {skill}")
                    else:
                        content.append(f"- {position}")

            # Экспертный рост
            expert_growth = target_pathways.get("expert_growth", [])
            if expert_growth:
                content.append("\n#### 🎯 Экспертный рост")
                for position in expert_growth:
                    if isinstance(position, dict):
                        target = position.get("target_position", "Не указано")
                        department = position.get("target_department", "")
                        rationale = position.get("rationale", "")
                        
                        content.append(f"\n**{target}**")
                        if department:
                            content.append(f"*Департамент:* {department}")
                        if rationale:
                            content.append(f"*Обоснование:* {rationale}")
                        
                        # Развитие компетенций
                        competency_bridge = position.get("competency_bridge", {})
                        if competency_bridge:
                            strengthen = competency_bridge.get("strengthen_skills", [])
                            if strengthen:
                                content.append("*Навыки для развития:*")
                                for skill in strengthen:
                                    content.append(f"- {skill}")
                            
                            acquire = competency_bridge.get("acquire_skills", [])
                            if acquire:
                                content.append("*Новые навыки:*")
                                for skill in acquire:
                                    content.append(f"- {skill}")
                    else:
                        content.append(f"- {position}")

        # Если новая структура отсутствует, используем старую (обратная совместимость)
        if not source_positions and not target_pathways:
            # Старая структура: career_pathways
            career_pathways = career_data.get("career_pathways", [])
            if career_pathways:
                for pathway in career_pathways:
                    pathway_type = pathway.get("pathway_type", "Карьерный путь")
                    content.append(f"\n### 🛤️ {pathway_type}")

                    # Входные позиции для этого пути
                    entry_positions = pathway.get("entry_positions", [])
                    if entry_positions:
                        content.append("\n**Входные позиции:**")
                        for pos in entry_positions:
                            content.append(f"- {pos}")

                    # Позиции продвижения для этого пути
                    advancement_positions = pathway.get("advancement_positions", [])
                    if advancement_positions:
                        content.append("\n**Позиции продвижения:**")
                        for pos in advancement_positions:
                            content.append(f"- {pos}")
            else:
                # Старая структура (для обратной совместимости)
                entry_positions = career_data.get(
                    "career_entry_positions", career_data.get("donor_positions", [])
                )
                if entry_positions:
                    content.append("\n### 🚪 Входные позиции")
                    for pos in entry_positions:
                        content.append(f"- {pos}")

                # Позиции роста
                growth_positions = career_data.get(
                    "career_growth_positions", career_data.get("target_positions", [])
                )
                if growth_positions:
                    content.append("\n### 🚀 Карьерный рост")
                    for pos in growth_positions:
                        content.append(f"- {pos}")

        # Приоритеты развития (может быть в любой структуре)
        dev_priorities = career_data.get("development_priorities", [])
        if dev_priorities:
            content.append("\n### 🎯 Приоритеты развития")
            for priority in dev_priorities:
                content.append(f"- {priority}")

        # Менторство
        mentoring = career_data.get("mentoring_opportunities")
        if mentoring:
            content.append(f"\n### 👥 Возможности менторства\n{mentoring}")

        return "\n".join(content)

    def _generate_workplace_provisioning(self, profile: Dict[str, Any]) -> str:
        """Генерирует обеспечение рабочего места"""
        content = ["## 💻 Обеспечение рабочего места"]

        # Новая структура workplace_provisioning и старая
        # technical_requirements для обратной совместимости
        workplace = profile.get("workplace_provisioning", {})
        tech_req_legacy = profile.get("technical_requirements", {})

        # Объединяем данные
        provisioning_data = {**tech_req_legacy, **workplace}

        if not provisioning_data:
            return "\n".join(
                content + ["\n*Требования к обеспечению рабочего места не определены*"]
            )

        # Новая структура: прямые software и hardware секции
        software_info = provisioning_data.get("software", {})
        hardware_info = provisioning_data.get("hardware", {})
        
        if software_info:
            content.append("\n### 📱 Программное обеспечение")
            
            # Стандартный пакет
            standard_package = software_info.get("standard_package", [])
            if standard_package:
                content.append("\n**Стандартный пакет:**")
                for sw in standard_package:
                    content.append(f"- {sw}")
            
            # Специализированные инструменты
            specialized_tools = software_info.get("specialized_tools", [])
            if specialized_tools:
                content.append("\n**Специализированные инструменты:**")
                for tool in specialized_tools:
                    content.append(f"- {tool}")

        if hardware_info:
            content.append("\n### 🖥️ Аппаратное обеспечение")
            
            # Стандартное рабочее место
            standard_workstation = hardware_info.get("standard_workstation", "")
            if standard_workstation:
                content.append(f"\n**Стандартное рабочее место:** {standard_workstation}")
            
            # Специализированное оборудование
            specialized_equipment = hardware_info.get("specialized_equipment", [])
            if specialized_equipment:
                content.append("\n**Специализированное оборудование:**")
                for eq in specialized_equipment:
                    # Проверяем, что это не "не требуется"
                    if eq.lower() != "не требуется":
                        content.append(f"- {eq}")
                    else:
                        content.append(f"- {eq}")

        # Обратная совместимость со старой структурой
        if not software_info and not hardware_info:
            # Программное и аппаратное обеспечение (старая структура)
            software_hardware = provisioning_data.get("software_hardware", {})
            if software_hardware:
                # Программное обеспечение
                software = software_hardware.get("software_systems", [])
                if software:
                    content.append("\n### 📱 Программное обеспечение")
                    for sw in software:
                        content.append(f"- {sw}")

                # Аппаратное обеспечение
                hardware = software_hardware.get("hardware_equipment", [])
                if hardware:
                    content.append("\n### 🖥️ Аппаратное обеспечение")
                    for hw in hardware:
                        content.append(f"- {hw}")
            else:
                # Еще более старая структура
                # Программное обеспечение
                software = provisioning_data.get(
                    "software_systems", provisioning_data.get("software", [])
                )
                if software:
                    content.append("\n### 📱 Программное обеспечение")
                    for sw in software:
                        content.append(f"- {sw}")

                # Оборудование
                equipment = provisioning_data.get(
                    "equipment_tools", provisioning_data.get("equipment", [])
                )
                if equipment:
                    content.append("\n### 🖥️ Оборудование")
                    for eq in equipment:
                        content.append(f"- {eq}")

        # Права доступа (и в новой, и в старой структуре)
        permissions = provisioning_data.get("access_permissions", [])
        if permissions:
            content.append("\n### 🔐 Права доступа")
            for perm in permissions:
                content.append(f"- {perm}")

        return "\n".join(content)

    def _generate_performance_metrics(self, profile: Dict[str, Any]) -> str:
        """Генерирует показатели эффективности"""
        content = ["## 📊 Показатели эффективности"]

        metrics = profile.get("performance_metrics", {})
        if not metrics:
            return "\n".join(content + ["\n*Показатели эффективности не определены*"])

        # Методология оценки (новое поле)
        methodology = metrics.get("evaluation_methodology")
        if methodology:
            content.append(f"\n**Методология оценки:** {methodology}")

        # Частота оценки (старое поле, сохраняем для совместимости)
        frequency = metrics.get("evaluation_frequency")
        if frequency:
            content.append(f"\n**Частота оценки:** {frequency}")

        # Показатели успеха (новое поле)
        success_indicators = metrics.get("success_indicators", [])
        if success_indicators:
            content.append("\n### 🎯 Показатели успеха")
            for indicator in success_indicators:
                content.append(f"- {indicator}")

        # Количественные KPI (старое поле, сохраняем для совместимости)
        quantitative = metrics.get("quantitative_kpis", [])
        if quantitative:
            content.append("\n### 📈 Количественные показатели")
            for kpi in quantitative:
                content.append(f"- {kpi}")

        # Качественные показатели (старое поле, сохраняем для совместимости)
        qualitative = metrics.get("qualitative_indicators", [])
        if qualitative:
            content.append("\n### 📋 Качественные показатели")
            for indicator in qualitative:
                content.append(f"- {indicator}")

        # Планы развития (новое поле)
        development_plans = metrics.get("development_plans", [])
        if development_plans:
            content.append("\n### 🚀 Планы развития")
            for plan in development_plans:
                content.append(f"- {plan}")

        return "\n".join(content)

    def _generate_additional_info(self, profile: Dict[str, Any]) -> str:
        """Генерирует дополнительную информацию"""
        content = ["## ℹ️ Дополнительная информация"]

        additional = profile.get("additional_information", {})
        if not additional:
            return "\n".join(content + ["\n*Дополнительная информация отсутствует*"])

        # Условия работы
        working_conditions = additional.get("working_conditions", {})
        if working_conditions:
            content.append("\n### 🏢 Условия работы")

            schedule = working_conditions.get("work_schedule")
            if schedule:
                content.append(f"**График работы:** {schedule}")

            remote = working_conditions.get("remote_work_options")
            if remote:
                content.append(f"**Удаленная работа:** {remote}")

            travel = working_conditions.get("business_travel")
            if travel:
                content.append(f"**Командировки:** {travel}")

        # Факторы риска
        risks = additional.get("risk_factors", [])
        if risks:
            content.append("\n### ⚠️ Факторы риска")
            for risk in risks:
                content.append(f"- {risk}")

        # Специальные требования
        special_req = additional.get("special_requirements", [])
        if special_req:
            content.append("\n### 📋 Специальные требования")
            for req in special_req:
                content.append(f"- {req}")

        return "\n".join(content)

    def _generate_metadata(self, profile_data: Dict[str, Any]) -> str:
        """Генерирует метаданные"""
        content = ["## 📋 Метаданные"]

        profile_meta = profile_data.get("profile", {}).get("metadata", {})
        generation_meta = profile_data.get("metadata", {})

        metadata_info = []

        # Информация о создании
        if "creation_date" in profile_meta:
            metadata_info.append(
                ("Дата создания профиля", profile_meta["creation_date"])
            )

        if "version" in profile_meta:
            metadata_info.append(("Версия профиля", profile_meta["version"]))

        if "profile_author" in profile_meta:
            metadata_info.append(("Автор профиля", profile_meta["profile_author"]))

        # Информация о генерации
        generation_info = generation_meta.get("generation", {})
        if generation_info:
            if "timestamp" in generation_info:
                metadata_info.append(("Дата генерации", generation_info["timestamp"]))

            if "duration" in generation_info:
                duration = generation_info["duration"]
                metadata_info.append(("Время генерации", f"{duration:.2f} сек"))

        # LLM информация
        llm_info = generation_meta.get("llm", {})
        if llm_info:
            if "model" in llm_info:
                metadata_info.append(("Модель LLM", llm_info["model"]))

            if "tokens" in llm_info:
                tokens = llm_info["tokens"]
                total_tokens = tokens.get("total", 0)
                metadata_info.append(("Токены", f"{total_tokens:,}"))

        # Статус валидации
        validation = generation_meta.get("validation", {})
        if validation:
            is_valid = validation.get("is_valid", False)
            status = "✅ Валиден" if is_valid else "❌ Есть ошибки"
            metadata_info.append(("Статус валидации", status))

            if "completeness_score" in validation:
                score = validation["completeness_score"]
                metadata_info.append(("Полнота профиля", f"{score:.0%}"))

        # Создаем таблицу метаданных
        if metadata_info:
            content.append("\n| Параметр | Значение |")
            content.append("|----------|----------|")
            for param, value in metadata_info:
                content.append(f"| **{param}** | {value} |")

        # Дата генерации MD
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content.append(f"\n---\n*MD документ сгенерирован: {current_time}*")

        return "\n".join(content)

    def save_md_file(self, filename: str, content: str) -> str:
        """
        @doc
        Сохраняет MD контент в файл.

        Args:
          filename: Имя файла (без пути)
          content: MD контент для сохранения

        Returns:
          str: Полный путь к сохраненному файлу

        Examples:
          python> path = service.save_md_file("profile.md", md_content)
        """
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"MD file saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving MD file: {e}")
            raise

    def generate_filename(self, profile_data: Dict[str, Any]) -> str:
        """
        @doc
        Генерирует имя файла на основе данных профиля.

        Args:
          profile_data: Данные профиля

        Returns:
          str: Имя файла в формате Department_Position_YYYYMMDD_HHMMSS.md

        Examples:
          python> filename = service.generate_filename(profile_json)
        """
        try:
            # Если передана полная структура с "profile", извлекаем его
            # Если передан прямой профиль, используем его как есть  
            if "profile" in profile_data:
                profile = profile_data.get("profile", {})
            else:
                profile = profile_data

            # Извлекаем данные
            position = profile.get("position_title", "Unknown_Position")
            department_specific = profile.get("department_specific", "")

            # Извлекаем последнюю часть департамента (группа)
            if department_specific:
                dept_parts = department_specific.split(", ")
                department = dept_parts[-1] if dept_parts else "Unknown_Department"
            else:
                department = "Unknown_Department"

            # Очищаем от спецсимволов
            position = "".join(
                c for c in position if c.isalnum() or c in " _-"
            ).replace(" ", "_")
            department = "".join(
                c for c in department if c.isalnum() or c in " _-"
            ).replace(" ", "_")

            # Добавляем timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            return f"{department}_{position}_{timestamp}.md"

        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            return f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


if __name__ == "__main__":
    print(
        "✅ ProfileMarkdownService - Convert JSON profiles to beautiful MD documents"
    )
    print("📝 Features: Structured sections, skill tables, metadata")
    print("🎨 Output: Clean, readable Markdown files")