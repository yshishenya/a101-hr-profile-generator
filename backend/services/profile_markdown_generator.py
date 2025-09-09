"""
@doc
Сервис генерации красивых Markdown документов из JSON профилей должностей.

Конвертирует структурированные JSON профили в читаемые MD документы
с правильным форматированием, таблицами и разделами.

Examples:
  python> generator = ProfileMarkdownGenerator()
  python> md_content = generator.generate_from_json(profile_data)
  python> generator.save_md_file("profile.md", md_content)
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ProfileMarkdownGenerator:
  """
  @doc
  Генератор Markdown документов из JSON профилей должностей.
  
  Создает красиво отформатированные MD файлы с:
  - Структурированными разделами
  - Таблицами навыков
  - Списками задач и требований
  - Метаинформацией
  
  Examples:
    python> generator = ProfileMarkdownGenerator()
    python> md_text = generator.generate_from_json(json_profile)
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
      python> md = generator.generate_from_json({"position_title": "Аналитик BI"})
    """
    try:
      profile = profile_data.get("profile", {})
      
      md_content = []
      
      # Заголовок документа
      md_content.append(self._generate_header(profile))
      
      # Основная информация
      md_content.append(self._generate_basic_info(profile))
      
      # Области ответственности
      md_content.append(self._generate_responsibilities(profile))
      
      # Профессиональные навыки
      md_content.append(self._generate_skills(profile))
      
      # Личностные качества
      md_content.append(self._generate_personal_qualities(profile))
      
      # Образование и опыт
      md_content.append(self._generate_education(profile))
      
      # Карьерное развитие
      md_content.append(self._generate_career_development(profile))
      
      # Технические требования
      md_content.append(self._generate_technical_requirements(profile))
      
      # Метрики эффективности
      md_content.append(self._generate_performance_metrics(profile))
      
      # Дополнительная информация
      md_content.append(self._generate_additional_info(profile))
      
      # Метаданные
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
    
    header += f"---\n*Профиль должности создан системой A101 HR Profile Generator*"
    return header
  
  def _generate_basic_info(self, profile: Dict[str, Any]) -> str:
    """Генерирует базовую информацию о должности"""
    content = ["## 📊 Основная информация"]
    
    basic_info = [
      ("Название должности", profile.get("position_title", "Не указано")),
      ("Блок", profile.get("department_broad", "Не указано")),
      ("Департамент/Отдел", profile.get("department_specific", "Не указано")),
      ("Категория должности", profile.get("position_category", profile.get("category", "Не указано"))),
      ("Непосредственный руководитель", profile.get("direct_manager", "Не указано")),
      ("Тип деятельности", profile.get("primary_activity_type", profile.get("primary_activity", "Не указано")))
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
        area_name = area.get("area", area.get("title", f"Область {i}"))
        if isinstance(area_name, list):
          area_name = area_name[0] if area_name else f"Область {i}"
        
        content.append(f"\n### {i}. {area_name}")
        
        # Задачи
        tasks = area.get("tasks", [])
        if tasks:
          for task in tasks:
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
        category_name = skill_category.get("skill_category", skill_category.get("category", "Неизвестная категория"))
        content.append(f"\n### {category_name}")
        
        # Конкретные навыки
        specific_skills = skill_category.get("specific_skills", skill_category.get("skills", []))
        
        if specific_skills and isinstance(specific_skills[0], dict):
          # Детальные навыки с уровнями
          content.append("\n| Навык | Уровень | Описание |")
          content.append("|-------|---------|----------|")
          
          for skill in specific_skills:
            name = skill.get("skill_name", "Неизвестный навык")
            level = skill.get("proficiency_level", skill.get("target_level", "Не указан"))
            description = skill.get("proficiency_description", "Описание отсутствует")
            
            # Конвертируем числовой уровень в текст
            if isinstance(level, int):
              level_map = {1: "Базовый", 2: "Средний", 3: "Продвинутый", 4: "Экспертный"}
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
      row_qualities = qualities[i:i+3]
      quality_badges = [f"🔹 **{q.capitalize()}**" for q in row_qualities]
      content.append(" | ".join(quality_badges))
    
    return "\n".join(content)
  
  def _generate_education(self, profile: Dict[str, Any]) -> str:
    """Генерирует требования к образованию"""
    content = ["## 🎓 Образование и опыт работы"]
    
    education = profile.get("education_requirements", profile.get("education", {}))
    if not education:
      return "\n".join(content + ["\n*Требования к образованию не определены*"])
    
    edu_info = []
    
    # Уровень образования
    if "education_level" in education:
      edu_info.append(("Уровень образования", education["education_level"]))
    
    # Специальности
    specializations = education.get("preferred_specializations", education.get("specialties"))
    if specializations:
      if isinstance(specializations, list):
        spec_text = ", ".join(specializations)
      else:
        spec_text = str(specializations)
      edu_info.append(("Предпочтительные специальности", spec_text))
    
    # Опыт работы
    if "total_experience" in education:
      edu_info.append(("Общий опыт работы", education["total_experience"]))
    
    if "relevant_experience" in education:
      edu_info.append(("Релевантный опыт", education["relevant_experience"]))
    
    # Дополнительные сертификаты
    certs = education.get("additional_certifications", education.get("additional_education"))
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
    """Генерирует карьерное развитие"""
    content = ["## 📈 Карьерное развитие"]
    
    career = profile.get("career_development", profile.get("career_path", {}))
    if not career:
      return "\n".join(content + ["\n*Информация о карьерном развитии не определена*"])
    
    # Входные позиции
    entry_positions = career.get("career_entry_positions", career.get("donor_positions", []))
    if entry_positions:
      content.append("\n### 🚪 Входные позиции")
      for pos in entry_positions:
        content.append(f"- {pos}")
    
    # Позиции роста
    growth_positions = career.get("career_growth_positions", career.get("target_positions", []))
    if growth_positions:
      content.append("\n### 🚀 Карьерный рост")
      for pos in growth_positions:
        content.append(f"- {pos}")
    
    # Приоритеты развития
    dev_priorities = career.get("development_priorities", [])
    if dev_priorities:
      content.append("\n### 🎯 Приоритеты развития")
      for priority in dev_priorities:
        content.append(f"- {priority}")
    
    # Менторство
    mentoring = career.get("mentoring_opportunities")
    if mentoring:
      content.append(f"\n### 👥 Возможности менторства\n{mentoring}")
    
    return "\n".join(content)
  
  def _generate_technical_requirements(self, profile: Dict[str, Any]) -> str:
    """Генерирует технические требования"""
    content = ["## 💻 Техническое обеспечение"]
    
    tech_req = profile.get("technical_requirements", {})
    if not tech_req:
      return "\n".join(content + ["\n*Технические требования не определены*"])
    
    # Программное обеспечение
    software = tech_req.get("software_systems", tech_req.get("software", []))
    if software:
      content.append("\n### 📱 Программное обеспечение")
      for sw in software:
        content.append(f"- {sw}")
    
    # Оборудование
    equipment = tech_req.get("equipment_tools", tech_req.get("equipment", []))
    if equipment:
      content.append("\n### 🖥️ Оборудование")
      for eq in equipment:
        content.append(f"- {eq}")
    
    # Права доступа
    permissions = tech_req.get("access_permissions", [])
    if permissions:
      content.append("\n### 🔐 Права доступа")
      for perm in permissions:
        content.append(f"- {perm}")
    
    return "\n".join(content)
  
  def _generate_performance_metrics(self, profile: Dict[str, Any]) -> str:
    """Генерирует метрики эффективности"""
    content = ["## 📊 Показатели эффективности"]
    
    metrics = profile.get("performance_metrics", {})
    if not metrics:
      return "\n".join(content + ["\n*Показатели эффективности не определены*"])
    
    # Частота оценки
    frequency = metrics.get("evaluation_frequency")
    if frequency:
      content.append(f"\n**Частота оценки:** {frequency}")
    
    # Количественные KPI
    quantitative = metrics.get("quantitative_kpis", [])
    if quantitative:
      content.append("\n### 📈 Количественные показатели")
      for kpi in quantitative:
        content.append(f"- {kpi}")
    
    # Качественные показатели
    qualitative = metrics.get("qualitative_indicators", [])
    if qualitative:
      content.append("\n### 📋 Качественные показатели")
      for indicator in qualitative:
        content.append(f"- {indicator}")
    
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
      metadata_info.append(("Дата создания профиля", profile_meta["creation_date"]))
    
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
      python> path = generator.save_md_file("profile.md", md_content)
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
      python> filename = generator.generate_filename(profile_json)
    """
    try:
      profile = profile_data.get("profile", {})
      
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
      position = "".join(c for c in position if c.isalnum() or c in " _-").replace(" ", "_")
      department = "".join(c for c in department if c.isalnum() or c in " _-").replace(" ", "_")
      
      # Добавляем timestamp
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      
      return f"{department}_{position}_{timestamp}.md"
      
    except Exception as e:
      logger.error(f"Error generating filename: {e}")
      return f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


if __name__ == "__main__":
  print("✅ ProfileMarkdownGenerator - Convert JSON profiles to beautiful MD documents")
  print("📝 Features: Structured sections, skill tables, metadata")
  print("🎨 Output: Clean, readable Markdown files")