"""
@doc
Утилитарные функции для работы с должностями.

Содержит общую логику определения уровней, категорий и характеристик должностей,
используемую в нескольких модулях системы.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def determine_position_level(position_name: str, return_type: str = "string") -> Any:
    """
    @doc
    Определение уровня должности на основе названия.

    Args:
        position_name: Название должности
        return_type: Тип возвращаемого значения ("string" или "number")

    Returns:
        str или int: Уровень должности

    Examples:
        python> level = determine_position_level("Руководитель отдела")
        python> # "senior"
        python> level = determine_position_level("Директор", "number")
        python> # 1
    """
    position_lower = position_name.lower()

    # Определяем уровень по ключевым словам
    if any(
        keyword in position_lower
        for keyword in ["руководитель", "директор", "управляющий", "начальник"]
    ):
        level_str = "senior"
        level_num = 1
    elif any(
        keyword in position_lower
        for keyword in ["заместитель", "зам", "заместитель руководителя"]
    ):
        level_str = "deputy"
        level_num = 2
    elif any(
        keyword in position_lower for keyword in ["ведущий", "главный", "старший"]
    ):
        level_str = "lead"
        level_num = 3
    elif any(
        keyword in position_lower
        for keyword in ["специалист", "аналитик", "консультант", "инженер"]
    ):
        level_str = "middle"
        level_num = 4
    elif any(
        keyword in position_lower for keyword in ["младший", "помощник", "стажер"]
    ):
        level_str = "junior"
        level_num = 5
    else:
        level_str = "middle"  # По умолчанию
        level_num = 4

    if return_type == "number":
        return level_num
    else:
        return level_str


def determine_position_category(position_name: str) -> str:
    """
    @doc
    Определение категории должности на основе названия.

    Args:
        position_name: Название должности

    Returns:
        str: Категория должности

    Examples:
        python> category = determine_position_category("Аналитик данных")
        python> # "analytical"
    """
    position_lower = position_name.lower()

    if any(
        keyword in position_lower
        for keyword in ["руководитель", "директор", "управляющий", "начальник"]
    ):
        return "management"
    elif any(
        keyword in position_lower
        for keyword in ["архитектор", "разработчик", "программист", "техник", "инженер"]
    ):
        return "technical"
    elif any(
        keyword in position_lower for keyword in ["аналитик", "исследователь"]
    ):
        return "analytical"
    elif any(
        keyword in position_lower
        for keyword in ["продаж", "менеджер", "коммерческий"]
    ):
        return "sales"
    elif any(
        keyword in position_lower
        for keyword in ["hr", "кадр", "персонал", "рекрутер"]
    ):
        return "hr"
    elif any(
        keyword in position_lower
        for keyword in ["финанс", "бухгалтер", "экономист"]
    ):
        return "finance"
    elif any(
        keyword in position_lower
        for keyword in ["маркетинг", "реклам", "pr", "brand"]
    ):
        return "marketing"
    elif any(
        keyword in position_lower
        for keyword in ["юрист", "правов", "legal"]
    ):
        return "legal"
    else:
        return "specialist"


def get_position_characteristics(position_name: str) -> Dict[str, Any]:
    """
    @doc
    Получение полных характеристик должности.

    Объединяет определение уровня и категории в одном вызове.

    Args:
        position_name: Название должности

    Returns:
        Dict: Характеристики должности

    Examples:
        python> chars = get_position_characteristics("Ведущий аналитик")
        python> # {"level": "lead", "level_num": 3, "category": "analytical"}
    """
    return {
        "level": determine_position_level(position_name, "string"),
        "level_num": determine_position_level(position_name, "number"),
        "category": determine_position_category(position_name)
    }


# Константы для уровней должностей
POSITION_LEVELS = {
    1: "senior",
    2: "deputy", 
    3: "lead",
    4: "middle",
    5: "junior"
}

# Константы для категорий должностей
POSITION_CATEGORIES = [
    "management",
    "technical", 
    "analytical",
    "sales",
    "hr",
    "finance",
    "marketing",
    "legal",
    "specialist"
]


if __name__ == "__main__":
    # Тестирование утилит
    test_positions = [
        "Руководитель отдела",
        "Ведущий аналитик данных",
        "Специалист по маркетингу", 
        "Младший разработчик",
        "Директор по продажам"
    ]
    
    print("🧪 Тестирование position_utils...")
    for position in test_positions:
        chars = get_position_characteristics(position)
        print(f"📋 {position}:")
        print(f"   Уровень: {chars['level']} ({chars['level_num']})")
        print(f"   Категория: {chars['category']}")
        print()