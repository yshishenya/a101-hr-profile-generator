#!/usr/bin/env python3
"""
Преобразование организационной структуры из Excel в структурированный JSON
"""

import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List, Any


def extract_hierarchy(row: pd.Series) -> List[str]:
    """Извлекает реальную иерархию, убирая повторы."""
    levels = []
    prev_level = None
    
    for level_col in ['Уровень 2', 'Уровень 3', 'Уровень 4', 'Уровень 5', 'Уровень 6', 'Уровень 7']:
        current_level = row[level_col]
        if pd.isna(current_level):
            break
        if current_level != prev_level:
            levels.append(current_level)
            prev_level = current_level
    
    return levels


def build_hierarchy_tree(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Строит иерархическое дерево из плоских данных."""
    tree = {}
    
    for item in data:
        hierarchy = item['hierarchy']
        positions = item['positions']
        number = item['number']
        
        current_node = tree
        
        # Проходим по иерархии, создавая узлы
        for i, level in enumerate(hierarchy):
            if level not in current_node:
                current_node[level] = {
                    'positions': [],
                    'children': {},
                    'number': None
                }
            
            # На последнем уровне добавляем позиции и номер
            if i == len(hierarchy) - 1:
                current_node[level]['positions'].extend(positions)
                current_node[level]['number'] = number
            
            current_node = current_node[level]['children']
    
    return tree


def clean_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Очищает дерево от пустых узлов и оптимизирует структуру."""
    cleaned = {}
    
    for key, value in tree.items():
        cleaned_value = {
            'number': value['number'],
            'positions': value['positions'] if value['positions'] else [],
        }
        
        # Рекурсивно очищаем детей
        if value['children']:
            cleaned_children = clean_tree(value['children'])
            if cleaned_children:
                cleaned_value['children'] = cleaned_children
        
        cleaned[key] = cleaned_value
    
    return cleaned


def excel_to_json(file_path: str, output_path: str = None) -> Dict[str, Any]:
    """
    Преобразует Excel файл организационной структуры в структурированный JSON.
    
    Args:
        file_path: Путь к Excel файлу
        output_path: Путь для сохранения JSON (опционально)
    
    Returns:
        Словарь с организационной структурой
    """
    
    # Читаем Excel файл
    df = pd.read_excel(file_path, sheet_name='выгрузка')
    
    # Группируем данные по номерам
    grouped_data = defaultdict(lambda: {'hierarchy': None, 'positions': []})
    
    for _, row in df.iterrows():
        number = row['Номер']
        hierarchy = extract_hierarchy(row)
        position = row['Должность']
        
        # Устанавливаем иерархию (она одинакова для всех записей с одним номером)
        if grouped_data[number]['hierarchy'] is None:
            grouped_data[number]['hierarchy'] = hierarchy
        
        # Добавляем позицию, избегая дубликатов
        if position not in grouped_data[number]['positions']:
            grouped_data[number]['positions'].append(position)
    
    # Преобразуем в список для построения дерева
    tree_data = []
    for number, data in grouped_data.items():
        tree_data.append({
            'number': number,
            'hierarchy': data['hierarchy'],
            'positions': data['positions']
        })
    
    # Строим иерархическое дерево
    hierarchy_tree = build_hierarchy_tree(tree_data)
    
    # Очищаем и оптимизируем структуру
    cleaned_tree = clean_tree(hierarchy_tree)
    
    # Создаем финальную структуру
    result = {
        'organization': cleaned_tree,
        'metadata': {
            'total_records': len(df),
            'unique_units': len(grouped_data),
            'top_level_blocks': len(cleaned_tree)
        }
    }
    
    # Сохраняем в файл, если указан путь
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def main():
    """Основная функция для запуска скрипта."""
    input_file = '/home/yan/A101/HR/Структура.xlsx'
    output_file = '/home/yan/A101/HR/structure.json'
    
    try:
        print("Преобразование Excel в JSON...")
        result = excel_to_json(input_file, output_file)
        
        print(f"✅ Успешно преобразовано:")
        print(f"   📊 Всего записей: {result['metadata']['total_records']}")
        print(f"   🏢 Уникальных единиц: {result['metadata']['unique_units']}")
        print(f"   🔝 Блоков верхнего уровня: {result['metadata']['top_level_blocks']}")
        print(f"   💾 JSON сохранен в: {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()