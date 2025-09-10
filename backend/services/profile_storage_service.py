"""
@doc
Сервис для управления файловой структурой и путями профилей должностей.

Создает иерархическую структуру папок на основе организационной структуры:
- Блок/Департамент/Отдел/Группа/Должность/ВремяСоздания/файлы
- Связывает файлы с записями в базе данных через уникальные ID
- Управляет версионностью профилей

Examples:
  python> storage = ProfileStorageService()
  python> path = storage.create_profile_path("Группа анализа данных", "Аналитик BI", "v1.0")
  python> storage.save_profile_files(path, json_data, md_content)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import logging

# Импорт централизованного кеша будет выполнен локально для избежания циркулярной зависимости

logger = logging.getLogger(__name__)


class ProfileStorageService:
    """
    @doc
    Сервис для управления файловой структурой профилей должностей.

    Создает полную иерархию папок согласно организационной структуре
    и управляет хранением JSON/MD файлов с версионностью.

    Examples:
      python> storage = ProfileStorageService("/app/generated_profiles")
      python> path = storage.create_profile_directory("Группа анализа данных", "Аналитик BI")
    """

    def __init__(self, base_path: str = "/app/generated_profiles"):
        self.base_path = Path(base_path)
        # Организационная структура теперь доступна через централизованный кеш

    def find_department_path(self, target_department: str) -> Optional[List[str]]:
        """
        @doc
        Находит полный организационный путь к департаменту через централизованный кеш.

        Args:
          target_department: Название целевого департамента/группы

        Returns:
          List[str]: Полный путь от блока до департамента, или None

        Examples:
          python> path = storage.find_department_path("Группа анализа данных")
          python> # ['Блок операционного директора', 'Департамент информационных технологий', 'Отдел управления данными', 'Группа анализа данных']
        """
        try:
            # Локальный импорт для избежания циркулярной зависимости
            from backend.core.organization_cache import organization_cache

            return organization_cache.find_department_path(target_department)
        except ImportError as e:
            logger.error(f"Failed to import organization_cache: {e}")
            # Fallback: возвращаем простую структуру
            return [target_department]

    def get_profile_paths(
        self, profile_id: str, department: str, position: str, created_at: datetime
    ) -> Tuple[Path, Path]:
        """
        @doc
        Детерминистическое вычисление путей к JSON и MD файлам профиля.

        Вычисляет пути на основе данных из БД без обращения к файловой системе.
        Использует кешированную организационную структуру для построения иерархии.

        Args:
          profile_id: UUID профиля из базы данных
          department: Название департамента/группы
          position: Название должности
          created_at: Время создания профиля

        Returns:
          Tuple[Path, Path]: Пути к JSON и MD файлам

        Examples:
          python> json_path, md_path = storage.get_profile_paths(
          ...   "e874d4ca-b4bf-4d91-b741-2cc4cbcb36b5",
          ...   "Группа анализа данных",
          ...   "Senior Data Analyst",
          ...   datetime(2025, 9, 9, 17, 13, 36)
          ... )
        """
        # Находим полный организационный путь из кеша
        org_path = self.find_department_path(department)
        if not org_path:
            logger.warning(
                f"⚠️ Department path not found for: {department}, using fallback"
            )
            org_path = [department]

        # Создаем путь: base/Блок/Департамент/.../Группа/Должность/Должность_Timestamp/
        path_components = [self.sanitize_path_component(comp) for comp in org_path]

        # Добавляем папку должности
        position_clean = self.sanitize_path_component(position)
        path_components.append(position_clean)

        # Добавляем папку экземпляра профиля
        timestamp_str = created_at.strftime("%Y%m%d_%H%M%S")
        # Используем profile_id для уникальности (первые 8 символов)
        short_id = profile_id[:8] if len(profile_id) > 8 else profile_id
        instance_name = f"{position_clean}_{timestamp_str}_{short_id}"
        path_components.append(instance_name)

        # Создаем полный путь к папке экземпляра
        full_path = self.base_path
        for component in path_components:
            full_path = full_path / component

        # Пути к файлам
        json_path = full_path / f"{instance_name}.json"
        md_path = full_path / f"{instance_name}.md"

        return json_path, md_path

    def sanitize_path_component(self, name: str) -> str:
        """
        @doc
        Очищает имя для использования в файловой системе.

        Args:
          name: Исходное имя департамента/должности

        Returns:
          str: Очищенное имя для папки

        Examples:
          python> clean = storage.sanitize_path_component("Группа анализа данных")
        """
        import re

        # Проверяем на path traversal атаки
        if ".." in name or name.startswith("/") or name.startswith("\\"):
            logger.warning(f"⚠️ Potential path traversal attempt blocked: {name}")
            name = name.replace("..", "_").lstrip("/").lstrip("\\")

        # Заменяем проблемные символы
        sanitized = name.replace(" ", "_")
        sanitized = sanitized.replace("/", "_")
        sanitized = sanitized.replace("\\", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = sanitized.replace("*", "_")
        sanitized = sanitized.replace("?", "_")
        sanitized = sanitized.replace('"', "_")
        sanitized = sanitized.replace("<", "_")
        sanitized = sanitized.replace(">", "_")
        sanitized = sanitized.replace("|", "_")

        # Удаляем любые остаточные опасные последовательности
        sanitized = re.sub(r"\.+", "_", sanitized)  # Множественные точки
        sanitized = re.sub(
            r"[^\w\-_а-яА-Я]", "_", sanitized
        )  # Только безопасные символы

        # Убираем множественные подчеркивания и ведущие/завершающие
        sanitized = re.sub(r"_{2,}", "_", sanitized).strip("_")

        # Ограничиваем длину (файловые системы имеют лимиты)
        if len(sanitized) > 100:
            sanitized = sanitized[:100].rstrip("_")

        # Проверяем, что результат не пустой
        if not sanitized:
            sanitized = "unnamed"

        return sanitized

    def create_profile_directory(
        self,
        department: str,
        position: str,
        timestamp: Optional[datetime] = None,
        profile_id: Optional[str] = None,
    ) -> Path:
        """
        @doc
        Создает полную структуру директорий для профиля должности.

        Args:
          department: Департамент/группа из оргструктуры
          position: Название должности
          timestamp: Время создания (по умолчанию - текущее)
          profile_id: Уникальный ID профиля (для связи с БД)

        Returns:
          Path: Путь к созданной директории профиля

        Examples:
          python> path = storage.create_profile_directory("Группа анализа данных", "Аналитик BI")
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Находим полный организационный путь
        org_path = self.find_department_path(department)
        if not org_path:
            logger.warning(f"⚠️ Department path not found for: {department}")
            org_path = [department]  # Fallback к простому пути

        # Создаем путь: base/Блок/Департамент/.../Группа/Должность/Должность_Timestamp/
        path_components = [self.sanitize_path_component(comp) for comp in org_path]

        # Добавляем папку должности
        position_clean = self.sanitize_path_component(position)
        path_components.append(position_clean)

        # Добавляем папку экземпляра профиля
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        instance_name = f"{position_clean}_{timestamp_str}"
        if profile_id:
            # Добавляем короткий ID для уникальности
            short_id = profile_id[:8] if len(profile_id) > 8 else profile_id
            instance_name = f"{position_clean}_{timestamp_str}_{short_id}"

        path_components.append(instance_name)

        # Создаем полный путь
        full_path = self.base_path
        for component in path_components:
            full_path = full_path / component

        # Создаем директории
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created profile directory: {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"❌ Error creating directory {full_path}: {e}")
            raise

    def save_profile_files(
        self,
        directory: Path,
        json_content: Dict[str, Any],
        md_content: str,
        profile_id: Optional[str] = None,
    ) -> Tuple[Path, Path]:
        """
        @doc
        Сохраняет JSON и MD файлы профиля в указанную директорию.

        Args:
          directory: Путь к директории профиля
          json_content: Содержимое JSON профиля
          md_content: Содержимое MD файла
          profile_id: ID профиля для связи с БД

        Returns:
          Tuple[Path, Path]: Пути к JSON и MD файлам

        Examples:
          python> json_path, md_path = storage.save_profile_files(dir_path, data, md)
        """
        try:
            # Извлекаем имя из папки для файлов
            instance_name = directory.name

            # Пути к файлам
            json_path = directory / f"{instance_name}.json"
            md_path = directory / f"{instance_name}.md"

            # Метаинформация о файловых путях теперь не сохраняется -
            # пути вычисляются детерминистически через get_profile_paths()

            # Сохраняем JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_content, f, ensure_ascii=False, indent=2)

            # Сохраняем MD
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            logger.info(f"✅ Saved profile files: {json_path.name}, {md_path.name}")
            return json_path, md_path

        except Exception as e:
            logger.error(f"❌ Error saving profile files: {e}")
            raise


# Методы find_profile_files() и get_profile_versions() удалены -
# теперь информация о профилях получается из базы данных через API


if __name__ == "__main__":
    print("✅ ProfileStorageService - Hierarchical file storage for job profiles")
    print("📁 Features: Organization-based paths, versioning, JSON+MD storage")
    print("🗂️ Structure: Block/Department/Division/Group/Position/Instance/files")
