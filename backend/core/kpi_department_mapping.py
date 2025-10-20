"""
KPI Department Mapping
Maps organization departments to KPI files

This module solves the problem of loading correct KPI file for each department
"""

from typing import Dict, Optional, List
import re


class KPIDepartmentMapper:
    """Maps department names to KPI file codes"""

    # Core mapping: Department name patterns → KPI file code
    DEPARTMENT_TO_KPI_FILE = {
        # IT Department (ДИТ)
        "департамент информационных технологий": "ДИТ",
        "дит": "ДИТ",
        "информационн": "ДИТ",

        # Architecture & Strategy (АС)
        "архитектур": "АС",
        "стратег": "АС",

        # Project Management (ДПУ)
        "управление проект": "ДПУ",
        "дпу": "ДПУ",
        "проектн": "ДПУ",

        # Development (ДРР)
        "департамент развития и реализации": "ДРР",
        "дрр": "ДРР",
        "развити": "ДРР",

        # Procurement (Закупки)
        "закупк": "Закупки",
        "procurement": "Закупки",

        # HR (ПРП)
        "персонал": "ПРП",
        "прп": "ПРП",
        "hr": "ПРП",
        "управление персоналом": "ПРП",

        # Construction Analytics (УВАиК)
        "аналитик": "УВАиК",
        "контрол": "УВАиК",
        "уваик": "УВАиК",

        # Digital/Цифра (Цифра)
        "цифр": "Цифра",
        "цифровизаци": "Цифра",
        "digital": "Цифра",
    }

    @classmethod
    def get_kpi_file_for_department(cls, department: str) -> Optional[str]:
        """
        Find KPI file code for given department name

        Args:
            department: Department name (e.g., "Департамент информационных технологий")

        Returns:
            KPI file code (e.g., "ДИТ") or None if not found

        Examples:
            >>> KPIDepartmentMapper.get_kpi_file_for_department("ДИТ")
            'ДИТ'

            >>> KPIDepartmentMapper.get_kpi_file_for_department("Департамент информационных технологий")
            'ДИТ'
        """
        if not department:
            return None

        dept_lower = department.lower().strip()

        # Direct match first
        if dept_lower in cls.DEPARTMENT_TO_KPI_FILE:
            return cls.DEPARTMENT_TO_KPI_FILE[dept_lower]

        # Partial match
        for pattern, kpi_code in cls.DEPARTMENT_TO_KPI_FILE.items():
            if pattern in dept_lower or dept_lower in pattern:
                return kpi_code

        # No match found
        return None

    @classmethod
    def get_all_available_kpi_codes(cls) -> List[str]:
        """
        Get list of all available KPI file codes

        Returns:
            List of KPI codes (e.g., ["ДИТ", "АС", ...])
        """
        return list(set(cls.DEPARTMENT_TO_KPI_FILE.values()))

    @classmethod
    def get_kpi_filename(cls, department: str) -> Optional[str]:
        """
        Get full KPI filename for department

        Args:
            department: Department name

        Returns:
            Filename (e.g., "KPI_ДИТ.md") or None

        Examples:
            >>> KPIDepartmentMapper.get_kpi_filename("ДИТ")
            'KPI_ДИТ.md'
        """
        kpi_code = cls.get_kpi_file_for_department(department)
        if kpi_code:
            return f"KPI_{kpi_code}.md"
        return None

    @classmethod
    def find_best_match(cls, department: str) -> Optional[Dict[str, str]]:
        """
        Find best match with confidence score

        Args:
            department: Department name

        Returns:
            Dict with 'kpi_code', 'filename', 'confidence' or None
        """
        kpi_code = cls.get_kpi_file_for_department(department)

        if not kpi_code:
            return None

        # Calculate confidence (simple heuristic)
        dept_lower = department.lower().strip()

        # Direct match = high confidence
        if dept_lower in cls.DEPARTMENT_TO_KPI_FILE:
            confidence = "high"
        elif kpi_code.lower() in dept_lower:
            confidence = "high"
        else:
            confidence = "medium"

        return {
            "kpi_code": kpi_code,
            "filename": f"KPI_{kpi_code}.md",
            "confidence": confidence,
            "matched_pattern": department
        }


# Convenience function
def get_kpi_file_for_dept(department: str) -> Optional[str]:
    """Shorthand for getting KPI filename"""
    return KPIDepartmentMapper.get_kpi_filename(department)
