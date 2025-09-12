#!/usr/bin/env python3
"""
Преобразование организационной структуры из Excel в структурированный JSON
с интеграцией данных о численности штата из листа "Сводная"
"""

import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List, Any


def extract_hierarchy(row: pd.Series) -> List[str]:
    """Извлекает реальную иерархию, убирая повторы."""
    levels = []
    prev_level = None

    for level_col in [
        "Уровень 2",
        "Уровень 3",
        "Уровень 4",
        "Уровень 5",
        "Уровень 6",
        "Уровень 7",
    ]:
        current_level = row[level_col]
        if pd.isna(current_level):
            break
        if current_level != prev_level:
            levels.append(current_level)
            prev_level = current_level

    return levels


def load_headcount_data(file_path: str) -> Dict[str, int]:
    """
    Загружает данные о численности из листа "Сводная".
    
    Args:
        file_path: Путь к Excel файлу
        
    Returns:
        Словарь {название_подразделения: численность}
    """
    try:
        # Читаем лист "Сводная"
        summary_df = pd.read_excel(file_path, sheet_name="Сводная", header=None)
        
        headcount_dict = {}
        
        # Обрабатываем каждую строку сводной таблицы
        for _, row in summary_df.iterrows():
            # Столбец 2 - название подразделения, столбец 3 - численность
            if (len(row) > 3 and 
                pd.notna(row[2]) and pd.notna(row[3]) and 
                str(row[2]).strip() != "Общий итог"):
                
                dept_name = str(row[2]).strip()
                try:
                    headcount = int(row[3])
                    # Агрегируем численность для подразделений с дублирующими записями
                    headcount_dict[dept_name] = headcount_dict.get(dept_name, 0) + headcount
                except (ValueError, TypeError):
                    continue
        
        print(f"📊 Загружено данных о численности: {len(headcount_dict)} подразделений")
        print(f"📈 Общая численность: {sum(headcount_dict.values())} человек")
        
        return headcount_dict
        
    except Exception as e:
        print(f"⚠️ Ошибка загрузки данных о численности: {e}")
        print(f"📋 Продолжаем без данных о численности")
        return {}


def match_headcount_to_hierarchy(hierarchy: List[str], headcount_dict: Dict[str, int]) -> tuple:
    """
    Находит данные о численности для иерархии подразделения.
    Ищет совпадения от самого детального уровня к общему.
    
    Args:
        hierarchy: Иерархия подразделения ["Блок", "Департамент", "Управление", ...]
        headcount_dict: Словарь с данными о численности
        
    Returns:
        Tuple (численность, источник_уровня, название_подразделения) или (None, None, None)
    """
    # Ищем совпадения от самого детального к общему уровню
    for i in range(len(hierarchy) - 1, -1, -1):
        dept_name = hierarchy[i]
        if dept_name in headcount_dict:
            level_source = f"Уровень {i + 2}"  # Уровень 2 = индекс 0
            return headcount_dict[dept_name], level_source, dept_name
    
    return None, None, None


def build_hierarchy_tree(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Строит иерархическое дерево из плоских данных с данными о численности."""
    tree = {}

    for item in data:
        hierarchy = item["hierarchy"]
        positions = item["positions"]
        number = item["number"]
        headcount = item.get("headcount")
        headcount_source = item.get("headcount_source")
        headcount_department = item.get("headcount_department")

        current_node = tree

        # Проходим по иерархии, создавая узлы
        for i, level in enumerate(hierarchy):
            if level not in current_node:
                current_node[level] = {
                    "positions": [], 
                    "children": {}, 
                    "number": None,
                    "headcount": None,
                    "headcount_source": None,
                    "headcount_department": None
                }

            # На последнем уровне добавляем все данные
            if i == len(hierarchy) - 1:
                current_node[level]["positions"].extend(positions)
                current_node[level]["number"] = number
                current_node[level]["headcount"] = headcount
                current_node[level]["headcount_source"] = headcount_source
                current_node[level]["headcount_department"] = headcount_department

            current_node = current_node[level]["children"]

    return tree


def clean_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Очищает дерево от пустых узлов и оптимизирует структуру."""
    cleaned = {}

    for key, value in tree.items():
        cleaned_value = {
            "number": value["number"],
            "positions": value["positions"] if value["positions"] else [],
            "headcount": value.get("headcount"),
            "headcount_source": value.get("headcount_source"),
            "headcount_department": value.get("headcount_department")
        }

        # Рекурсивно очищаем детей
        if value["children"]:
            cleaned_children = clean_tree(value["children"])
            if cleaned_children:
                cleaned_value["children"] = cleaned_children

        cleaned[key] = cleaned_value

    return cleaned


def excel_to_json(file_path: str, output_path: str = None) -> Dict[str, Any]:
    """
    Преобразует Excel файл организационной структуры в структурированный JSON
    с интеграцией данных о численности штата.

    Args:
        file_path: Путь к Excel файлу
        output_path: Путь для сохранения JSON (опционально)

    Returns:
        Словарь с организационной структурой и данными о численности
    """
    
    print("📁 Читаем основную структуру из листа 'выгрузка'...")
    # Читаем Excel файл
    df = pd.read_excel(file_path, sheet_name="выгрузка")
    
    print("📊 Загружаем данные о численности из листа 'Сводная'...")
    # Загружаем данные о численности
    headcount_dict = load_headcount_data(file_path)

    # Группируем данные по номерам
    grouped_data = defaultdict(lambda: {"hierarchy": None, "positions": []})
    headcount_stats = {"matched": 0, "total": 0}

    for _, row in df.iterrows():
        number = row["Номер"]
        hierarchy = extract_hierarchy(row)
        position = row["Должность"]
        
        headcount_stats["total"] += 1

        # Устанавливаем иерархию (она одинакова для всех записей с одним номером)
        if grouped_data[number]["hierarchy"] is None:
            grouped_data[number]["hierarchy"] = hierarchy
            
            # Находим данные о численности для этой иерархии
            headcount, headcount_source, headcount_dept = match_headcount_to_hierarchy(hierarchy, headcount_dict)
            grouped_data[number]["headcount"] = headcount
            grouped_data[number]["headcount_source"] = headcount_source
            grouped_data[number]["headcount_department"] = headcount_dept
            
            if headcount is not None:
                headcount_stats["matched"] += 1

        # Добавляем позицию, избегая дубликатов
        if position not in grouped_data[number]["positions"]:
            grouped_data[number]["positions"].append(position)

    # Преобразуем в список для построения дерева
    tree_data = []
    for number, data in grouped_data.items():
        tree_data.append(
            {
                "number": number,
                "hierarchy": data["hierarchy"],
                "positions": data["positions"],
                "headcount": data.get("headcount"),
                "headcount_source": data.get("headcount_source"),
                "headcount_department": data.get("headcount_department")
            }
        )

    # Строим иерархическое дерево
    hierarchy_tree = build_hierarchy_tree(tree_data)

    # Очищаем и оптимизируем структуру
    cleaned_tree = clean_tree(hierarchy_tree)

    # Подсчет подразделений с данными о численности
    units_with_headcount = sum(1 for data in grouped_data.values() if data.get("headcount") is not None)

    # Создаем финальную структуру
    result = {
        "organization": cleaned_tree,
        "metadata": {
            "total_records": len(df),
            "unique_units": len(grouped_data),
            "top_level_blocks": len(cleaned_tree),
            "headcount_data": {
                "total_headcount_records": len(headcount_dict),
                "units_with_headcount": units_with_headcount,
                "headcount_coverage_percent": round((units_with_headcount / len(grouped_data)) * 100, 1),
                "total_employees": sum(headcount_dict.values())
            }
        },
    }

    print(f"\n✅ Интеграция данных о численности:")
    print(f"   📋 Подразделений с численностью: {units_with_headcount}/{len(grouped_data)} ({result['metadata']['headcount_data']['headcount_coverage_percent']}%)")
    print(f"   👥 Общая численность: {result['metadata']['headcount_data']['total_employees']} человек")

    # Сохраняем в файл, если указан путь
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def main():
    """Основная функция для запуска скрипта."""
    input_file = "/home/yan/A101/HR/docs/org_structure/Structure.xlsx"
    output_file = "/home/yan/A101/HR/data/structure.json"

    try:
        print("🚀 Преобразование Excel в JSON с интеграцией данных о численности...")
        result = excel_to_json(input_file, output_file)

        print(f"\n✅ Успешно преобразовано:")
        print(f"   📊 Всего записей: {result['metadata']['total_records']}")
        print(f"   🏢 Уникальных единиц: {result['metadata']['unique_units']}")
        print(f"   🔝 Блоков верхнего уровня: {result['metadata']['top_level_blocks']}")
        print(f"   👥 Общая численность: {result['metadata']['headcount_data']['total_employees']} человек")
        print(f"   📈 Покрытие данными о численности: {result['metadata']['headcount_data']['headcount_coverage_percent']}%")
        print(f"   💾 JSON сохранен в: {output_file}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
