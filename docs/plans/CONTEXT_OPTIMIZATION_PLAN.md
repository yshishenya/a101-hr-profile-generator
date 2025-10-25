# 🎯 Детальный план оптимизации контекста генерации профилей

**Цель:** Сократить количество токенов контекста с 158K до 27K (83% экономия) при сохранении/улучшении качества генерации

**Дата создания:** 2025-10-25
**Статус:** В разработке
**Ответственный:** Backend Team

---

## 📊 Текущая ситуация

### Анализ токенов контекста (на одну генерацию):

| Компонент | Токены сейчас | Использование | Токены нужно | Экономия |
|-----------|---------------|---------------|--------------|----------|
| **OrgStructure** (полная) | 101,000 | ~5% | 5,000 | 96,000 (95%) |
| **company_map** | 51,000 | ~20% | 12,000 | 39,000 (76%) |
| **it_systems** | 4,500 | зависит | 0-4,500 | 0-4,500 |
| **kpi_data** | 1,000 | 100% | 1,000 | 0 |
| **org_structure** (релевантная) | 500 | 100% | 500 | 0 |
| **json_schema** | 100 | 100% | 100 | 0 |
| **Прочие переменные** | 900 | 100% | 900 | 0 |
| **ИТОГО** | **158,000** | - | **24,000** | **134,000 (85%)** |

### Проблемы:
1. ✅ Передаем ВСЮ оргструктуру (567 департаментов) вместо релевантной ветки
2. ✅ Карта компании не сжата (много дублирующейся информации)
3. ✅ IT системы загружаются всегда, даже если не нужны
4. ✅ Нет кеширования обработанного контекста

---

## 🎯 Стратегия оптимизации (4 направления)

### Направление 1: Умная экстракция оргструктуры
**Цель:** 101K → 5K токенов (95% экономия)

### Направление 2: Сжатие карты компании
**Цель:** 51K → 12K токенов (76% экономия)

### Направление 3: Условная загрузка IT систем
**Цель:** 0-4.5K токенов (динамически)

### Направление 4: Кеширование обработанного контекста
**Цель:** Ускорение повторных генераций на 90%

---

## 📋 НАПРАВЛЕНИЕ 1: Умная экстракция оргструктуры

### Задача 1.1: Создать метод извлечения релевантной ветки

**Файл:** `backend/core/data_loader.py`
**Метод:** `_extract_relevant_org_branch()`
**Приоритет:** 🔥 КРИТИЧЕСКИЙ
**Время:** 4-6 часов

#### Что делает:
Вместо передачи всех 567 департаментов, передаем:
- Целевой департамент с полной информацией
- 2 уровня вверх (родительские департаменты)
- 1 уровень вниз (дочерние подразделения)
- Сводную статистику по остальным

#### Детальный алгоритм:

```python
def _extract_relevant_org_branch(
    self,
    target_path: str,
    levels_up: int = 2,
    levels_down: int = 1
) -> Dict[str, Any]:
    """
    Извлекает только релевантную часть оргструктуры для генерации профиля.

    Args:
        target_path: Полный путь к целевому подразделению (dept/position)
        levels_up: Сколько уровней вверх по иерархии включить (для контекста)
        levels_down: Сколько уровней вниз включить (подчиненные)

    Returns:
        Сжатая структура с релевантными данными

    Example:
        # Было: 567 департаментов, 101K токенов
        # Стало: ~15 единиц, 5K токенов
    """
    # ШАГ 1: Найти целевое подразделение
    target_unit = organization_cache.find_unit_by_path(target_path)
    if not target_unit:
        return self._create_minimal_fallback(target_path)

    # ШАГ 2: Получить родительскую цепочку (вверх по иерархии)
    parent_chain = self._get_parent_chain(target_path, levels_up)

    # ШАГ 3: Получить дочерние подразделения (вниз по иерархии)
    children_tree = self._get_children_tree(target_unit, levels_down)

    # ШАГ 4: Получить peer departments (на том же уровне)
    peers = self._get_peer_units(target_path, max_peers=5)

    # ШАГ 5: Сводная статистика по остальной организации
    org_summary = self._get_organization_summary()

    # ШАГ 6: Собрать компактную структуру
    optimized_structure = {
        "target": {
            "path": target_path,
            "name": target_unit["name"],
            "level": target_unit["level"],
            "positions": target_unit["positions"],
            "headcount": target_unit.get("headcount", 0),
            "full_details": True  # Флаг, что это целевое подразделение
        },
        "hierarchy": {
            "parent_chain": parent_chain,  # Контекст сверху
            "children": children_tree,  # Подчиненные
            "peers": peers  # Соседи на том же уровне
        },
        "organization_context": org_summary,  # Общая картина
        "metadata": {
            "total_units_in_full_structure": 567,
            "units_included_in_context": len(parent_chain) + len(children_tree) + len(peers) + 1,
            "compression_ratio": f"{((567 - (len(parent_chain) + len(children_tree) + len(peers) + 1)) / 567 * 100):.1f}%"
        }
    }

    return optimized_structure
```

#### Вспомогательные методы:

```python
def _get_parent_chain(self, target_path: str, levels: int) -> List[Dict[str, Any]]:
    """
    Получить цепочку родительских подразделений вверх по иерархии.

    Example:
        target_path = "Блок развития/ДИТ/Отдел разработки/Группа backend"
        levels = 2

        Result: [
            {"name": "ДИТ", "level": 2, "positions_count": 45, ...},
            {"name": "Блок развития", "level": 1, "positions_count": 150, ...}
        ]
    """
    path_parts = [p.strip() for p in target_path.split("/") if p.strip()]
    parent_chain = []

    # Идем от целевого подразделения вверх
    for i in range(1, min(levels + 1, len(path_parts))):
        parent_path = "/".join(path_parts[:-i])
        parent_unit = organization_cache.find_unit_by_path(parent_path)

        if parent_unit:
            parent_chain.append({
                "name": parent_unit["name"],
                "path": parent_path,
                "level": parent_unit["level"],
                "positions_count": len(parent_unit["positions"]),
                "headcount": parent_unit.get("headcount", 0),
                # НЕ включаем полный список позиций - только статистика
            })

    return parent_chain


def _get_children_tree(self, unit: Dict[str, Any], levels: int) -> List[Dict[str, Any]]:
    """
    Получить дерево дочерних подразделений вниз по иерархии.

    Example:
        unit = "Отдел разработки"
        levels = 1

        Result: [
            {"name": "Группа backend", "positions_count": 12, ...},
            {"name": "Группа frontend", "positions_count": 8, ...},
            {"name": "Группа mobile", "positions_count": 6, ...}
        ]
    """
    children = []

    if levels <= 0 or "children" not in unit:
        return children

    for child_name, child_data in unit.get("children", {}).items():
        child_info = {
            "name": child_name,
            "positions_count": len(child_data.get("positions", [])),
            "headcount": child_data.get("headcount", 0),
            # Рекурсивно для следующего уровня (если levels > 1)
        }

        if levels > 1:
            child_info["children"] = self._get_children_tree(child_data, levels - 1)

        children.append(child_info)

    return children


def _get_peer_units(self, target_path: str, max_peers: int = 5) -> List[Dict[str, Any]]:
    """
    Получить peer подразделения (на том же уровне иерархии).

    Полезно для понимания контекста: "Какие еще отделы есть в этом департаменте?"

    Example:
        target_path = "Блок развития/ДИТ/Отдел разработки"

        Result: [
            {"name": "Отдел инфраструктуры", "positions_count": 20, ...},
            {"name": "Отдел аналитики", "positions_count": 15, ...},
            {"name": "Отдел поддержки", "positions_count": 18, ...}
        ]
    """
    path_parts = [p.strip() for p in target_path.split("/") if p.strip()]

    if len(path_parts) < 2:
        return []  # Нет peer'ов на верхнем уровне

    # Получаем родительское подразделение
    parent_path = "/".join(path_parts[:-1])
    parent_unit = organization_cache.find_unit_by_path(parent_path)

    if not parent_unit or "children" not in parent_unit:
        return []

    # Собираем всех "братьев/сестер" (кроме самого target)
    target_name = path_parts[-1]
    peers = []

    for peer_name, peer_data in parent_unit["children"].items():
        if peer_name != target_name:  # Исключаем сам target
            peers.append({
                "name": peer_name,
                "positions_count": len(peer_data.get("positions", [])),
                "headcount": peer_data.get("headcount", 0)
            })

            if len(peers) >= max_peers:
                break

    return peers


def _get_organization_summary(self) -> Dict[str, Any]:
    """
    Получить сводную статистику по всей организации.

    Дает общее понимание масштаба компании без детализации.

    Result: {
        "total_business_units": 567,
        "total_positions": 1487,
        "total_headcount": 2500,
        "major_blocks": [
            {"name": "Блок развития", "headcount": 450, "units_count": 120},
            {"name": "Блок коммерции", "headcount": 380, "units_count": 95},
            ...
        ]
    }
    """
    # Используем уже закешированные данные из organization_cache
    all_units = organization_cache.get_all_business_units_with_paths()

    total_headcount = 0
    total_positions = 0
    blocks_summary = {}

    for path, unit in all_units.items():
        total_positions += len(unit.get("positions", []))
        total_headcount += unit.get("headcount", 0)

        # Извлекаем блок верхнего уровня
        path_parts = path.split("/")
        if len(path_parts) > 0:
            block_name = path_parts[0]

            if block_name not in blocks_summary:
                blocks_summary[block_name] = {
                    "name": block_name,
                    "headcount": 0,
                    "units_count": 0
                }

            blocks_summary[block_name]["headcount"] += unit.get("headcount", 0)
            blocks_summary[block_name]["units_count"] += 1

    # Сортируем блоки по численности (топ-5)
    top_blocks = sorted(
        blocks_summary.values(),
        key=lambda x: x["headcount"],
        reverse=True
    )[:5]

    return {
        "total_business_units": len(all_units),
        "total_positions": total_positions,
        "total_headcount": total_headcount,
        "major_blocks": top_blocks
    }
```

#### Интеграция в prepare_langfuse_variables():

```python
# В методе prepare_langfuse_variables() в data_loader.py

# ❌ СТАРЫЙ КОД (удалить):
"OrgStructure": json.dumps(
    self._get_organization_structure_with_target(f"{department}/{position}"),
    ensure_ascii=False,
    indent=2,
),  # 101K токенов

# ✅ НОВЫЙ КОД (добавить):
"OrgStructure": json.dumps(
    self._extract_relevant_org_branch(
        target_path=f"{department}/{position}",
        levels_up=2,
        levels_down=1
    ),
    ensure_ascii=False,
    indent=2,
),  # ~5K токенов (95% экономия)
```

#### Тестирование:

```python
# Создать тест в tests/test_data_loader_optimization.py

def test_extract_relevant_org_branch():
    """Тест оптимизации извлечения оргструктуры"""
    loader = DataLoader()

    # Тест 1: Проверка размера
    target_path = "Блок развития/ДИТ/Отдел разработки"
    result = loader._extract_relevant_org_branch(target_path)

    result_json = json.dumps(result, ensure_ascii=False)
    result_tokens = len(result_json) / 3.5  # Оценка токенов

    assert result_tokens < 6000, f"Слишком много токенов: {result_tokens}"
    assert result_tokens > 4000, f"Слишком мало токенов: {result_tokens}"

    # Тест 2: Проверка структуры
    assert "target" in result
    assert "hierarchy" in result
    assert "organization_context" in result

    # Тест 3: Проверка наличия ключевых данных
    assert result["target"]["full_details"] == True
    assert len(result["hierarchy"]["parent_chain"]) <= 2
    assert "metadata" in result

    print(f"✅ Тест пройден! Токены: {result_tokens:.0f}")
```

#### Метрики успеха:

- ✅ Токены: < 6,000 (было 101,000)
- ✅ Время выполнения: < 50ms
- ✅ Качество генерации: не ухудшается
- ✅ Все тесты проходят

---

## 📋 НАПРАВЛЕНИЕ 2: Сжатие карты компании

### Задача 2.1: Создать сжатую версию карты компании

**Файл:** `backend/core/data_loader.py`
**Метод:** `_load_company_map_compressed()`
**Приоритет:** 🟡 ВЫСОКИЙ
**Время:** 3-4 часа

#### Анализ текущей карты:

```markdown
# Текущий размер: ~110,000 символов (~51K токенов)

Проблемы:
1. Много повторяющихся заголовков/форматирования
2. Избыточные примеры
3. Дублирующиеся описания процессов
4. Длинные исторические справки
```

#### Стратегия сжатия:

```python
def _load_company_map_compressed(self) -> str:
    """
    Загрузка сжатой версии карты компании А101.

    Оптимизация:
    1. Удаление повторяющихся секций
    2. Сокращение примеров (оставить 1-2 ключевых)
    3. Удаление markdown форматирования (лишние #, -, *)
    4. Извлечение только критичных секций для генерации профилей

    Цель: 110K символов → 30K символов (73% сжатие)
    """
    cache_key = "company_map_compressed"

    if cache_key not in self._cache:
        # Загружаем полную карту
        full_map = self._load_company_map_cached()

        # Применяем сжатие
        compressed_map = self._apply_company_map_compression(full_map)

        self._cache[cache_key] = compressed_map

        logger.info(
            f"Company map compressed: {len(full_map)} → {len(compressed_map)} chars "
            f"({(1 - len(compressed_map)/len(full_map))*100:.1f}% compression)"
        )

    return self._cache[cache_key]


def _apply_company_map_compression(self, full_map: str) -> str:
    """
    Применение алгоритмов сжатия к карте компании.

    Шаги:
    1. Парсинг markdown структуры
    2. Извлечение критичных секций
    3. Удаление избыточности
    4. Сборка сжатой версии
    """

    # ШАГ 1: Определяем критичные секции (нужны для генерации профилей)
    CRITICAL_SECTIONS = [
        "Миссия и ценности А101",
        "Корпоративная культура",
        "Ключевые направления деятельности",
        "Организационная структура (общее описание)",
        "HR политики и процессы",
        # НЕ включаем: исторические справки, детальные финансовые данные, маркетинговые материалы
    ]

    # ШАГ 2: Извлечение секций
    sections = self._parse_markdown_sections(full_map)

    # ШАГ 3: Фильтрация + сжатие каждой секции
    compressed_sections = []

    for section in sections:
        if self._is_critical_section(section["title"], CRITICAL_SECTIONS):
            # Сжимаем контент секции
            compressed_content = self._compress_section_content(section["content"])
            compressed_sections.append({
                "title": section["title"],
                "content": compressed_content
            })

    # ШАГ 4: Сборка итогового документа
    compressed_map = "# Карта Компании А101 (Сжатая версия для генерации профилей)\n\n"

    for section in compressed_sections:
        compressed_map += f"## {section['title']}\n\n"
        compressed_map += f"{section['content']}\n\n"

    return compressed_map


def _compress_section_content(self, content: str) -> str:
    """
    Сжатие контента секции без потери критичной информации.

    Техники:
    1. Удаление избыточного markdown форматирования
    2. Сокращение списков (топ-5 вместо топ-20)
    3. Удаление примеров (оставить 1 ключевой)
    4. Объединение похожих пунктов
    """

    # Удаляем лишнее форматирование
    content = content.replace("**", "").replace("*", "")
    content = content.replace("---", "")

    # Сокращаем длинные списки
    lines = content.split("\n")
    compressed_lines = []
    list_item_count = 0
    in_list = False

    for line in lines:
        # Если это элемент списка
        if line.strip().startswith("-") or line.strip().startswith("•"):
            if not in_list:
                in_list = True
                list_item_count = 0

            list_item_count += 1

            # Оставляем только топ-5 элементов списка
            if list_item_count <= 5:
                compressed_lines.append(line)
            elif list_item_count == 6:
                compressed_lines.append("  - ... (дополнительные пункты опущены)")
        else:
            in_list = False
            compressed_lines.append(line)

    return "\n".join(compressed_lines)
```

#### Создание сжатой версии файла:

```bash
# Скрипт для создания сжатой карты компании
# scripts/create_compressed_company_map.py

import sys
sys.path.append(".")

from backend.core.data_loader import DataLoader

loader = DataLoader()

# Загружаем и сжимаем
full_map = loader._load_company_map_cached()
compressed_map = loader._apply_company_map_compression(full_map)

# Сохраняем в отдельный файл
with open("data/Карта Компании А101 (сжатая).md", "w", encoding="utf-8") as f:
    f.write(compressed_map)

print(f"✅ Сжатая карта создана!")
print(f"   Оригинал: {len(full_map):,} символов")
print(f"   Сжатая: {len(compressed_map):,} символов")
print(f"   Экономия: {(1 - len(compressed_map)/len(full_map))*100:.1f}%")
```

#### Интеграция:

```python
# В методе prepare_langfuse_variables()

# ❌ СТАРЫЙ КОД:
"company_map": self._load_company_map_cached(),  # 51K токенов

# ✅ НОВЫЙ КОД:
"company_map": self._load_company_map_compressed(),  # ~12K токенов
```

#### Метрики успеха:

- ✅ Токены: < 15,000 (было 51,000)
- ✅ Сохранены все критичные секции
- ✅ Качество генерации не ухудшилось

---

## 📋 НАПРАВЛЕНИЕ 3: Условная загрузка IT систем

### Задача 3.1: Загружать IT системы только для IT-департаментов

**Файл:** `backend/core/data_loader.py`
**Метод:** `_load_it_systems_conditional()`
**Приоритет:** 🟢 СРЕДНИЙ
**Время:** 2 часа

#### Логика:

```python
def _should_load_it_systems(self, department: str, position: str) -> bool:
    """
    Определяет, нужно ли загружать IT системы для данной позиции.

    IT системы релевантны только для:
    1. IT департаментов (ДИТ, Цифровизация, etc)
    2. Технических позиций в других департаментах
    3. Позиций, работающих с системами (Аналитик, Администратор)
    """

    # Список IT департаментов
    IT_DEPARTMENTS = [
        "ДИТ",
        "Департамент информационных технологий",
        "Отдел цифровизации",
        "Дирекция по цифровой трансформации",
    ]

    # Технические позиции (по ключевым словам)
    TECHNICAL_KEYWORDS = [
        "программист", "разработчик", "developer",
        "архитектор", "администратор", "devops",
        "аналитик", "analyst", "bi", "data",
        "qa", "тестировщик", "инженер"
    ]

    # Проверка 1: IT департамент?
    for it_dept in IT_DEPARTMENTS:
        if it_dept.lower() in department.lower():
            return True

    # Проверка 2: Техническая позиция?
    position_lower = position.lower()
    for keyword in TECHNICAL_KEYWORDS:
        if keyword in position_lower:
            return True

    return False


def _load_it_systems_conditional(
    self,
    department: str,
    position: str
) -> str:
    """
    Условная загрузка IT систем.

    Если релевантно → загружаем полную информацию
    Если не релевантно → возвращаем краткую справку или пустую строку
    """

    if self._should_load_it_systems(department, position):
        # Загружаем полную информацию
        logger.info(f"Loading IT systems for {department}/{position} (relevant)")
        return self._load_it_systems_cached()
    else:
        # Возвращаем краткую справку
        logger.info(f"Skipping IT systems for {department}/{position} (not relevant)")
        return """# IT Системы компании А101

Для данной позиции детальное описание IT систем не требуется.
Общая информация: компания использует современный стек корпоративных систем
для автоматизации бизнес-процессов."""
```

#### Интеграция:

```python
# В методе prepare_langfuse_variables()

# ❌ СТАРЫЙ КОД:
"it_systems": self._load_it_systems_cached(),  # Всегда 4.5K токенов

# ✅ НОВЫЙ КОД:
"it_systems": self._load_it_systems_conditional(department, position),  # 0-4.5K токенов
```

#### Метрики успеха:

- ✅ Экономия токенов: ~70% случаев (не IT позиции)
- ✅ Время загрузки: -30% для не IT позиций

---

## 📋 НАПРАВЛЕНИЕ 4: Кеширование обработанного контекста

### Задача 4.1: Кешировать обработанный контекст для повторных генераций

**Файл:** `backend/core/context_cache.py` (новый)
**Приоритет:** 🟢 СРЕДНИЙ
**Время:** 3-4 часа

#### Идея:

Если генерируем профили для одного департамента несколько раз подряд,
многие данные (оргструктура, KPI, карта компании) можно использовать повторно.

#### Реализация:

```python
# backend/core/context_cache.py

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

class ContextCache:
    """
    Кеш обработанного контекста для ускорения повторных генераций.

    Кеширует:
    1. Извлеченную оргструктуру для департамента
    2. Сжатую карту компании
    3. KPI данные

    TTL: 1 час (данные обновляются редко)
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get_org_structure(
        self,
        department: str,
        position: str
    ) -> Optional[Dict[str, Any]]:
        """Получить закешированную оргструктуру"""
        cache_key = self._make_org_key(department, position)
        return self._get_cached_value(cache_key)

    def set_org_structure(
        self,
        department: str,
        position: str,
        structure: Dict[str, Any]
    ):
        """Закешировать оргструктуру"""
        cache_key = self._make_org_key(department, position)
        self._set_cached_value(cache_key, structure)

    def _make_org_key(self, department: str, position: str) -> str:
        """Создать ключ кеша для оргструктуры"""
        # Используем hash для компактности
        data = f"org:{department}:{position}"
        return hashlib.md5(data.encode()).hexdigest()

    def _get_cached_value(self, key: str) -> Optional[Any]:
        """Получить значение из кеша с проверкой TTL"""
        if key not in self._cache:
            return None

        # Проверяем TTL
        if datetime.now() - self._timestamps[key] > self.ttl:
            # Кеш истек
            del self._cache[key]
            del self._timestamps[key]
            return None

        return self._cache[key]

    def _set_cached_value(self, key: str, value: Any):
        """Сохранить значение в кеш"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

# Глобальный экземпляр
context_cache = ContextCache(ttl_seconds=3600)  # 1 час
```

#### Интеграция в DataLoader:

```python
# В методе prepare_langfuse_variables()

# Проверяем кеш
cached_org = context_cache.get_org_structure(department, position)

if cached_org:
    logger.info(f"Using cached org structure for {department}/{position}")
    org_structure = cached_org
else:
    logger.info(f"Generating org structure for {department}/{position}")
    org_structure = self._extract_relevant_org_branch(
        target_path=f"{department}/{position}"
    )

    # Кешируем результат
    context_cache.set_org_structure(department, position, org_structure)
```

#### Метрики успеха:

- ✅ При повторных генерациях: ускорение на 90%
- ✅ Экономия CPU на обработку контекста

---

## 📊 Суммарная экономия

### До оптимизации:

| Компонент | Токены |
|-----------|--------|
| OrgStructure | 101,000 |
| company_map | 51,000 |
| it_systems | 4,500 |
| Остальное | 1,500 |
| **ИТОГО** | **158,000** |

### После оптимизации:

| Компонент | Токены | Экономия |
|-----------|--------|----------|
| OrgStructure (оптимизированная) | 5,000 | 96,000 (95%) |
| company_map (сжатая) | 12,000 | 39,000 (76%) |
| it_systems (условная) | 1,500 | 3,000 (67%) |
| Остальное | 1,500 | 0 |
| **ИТОГО** | **20,000** | **138,000 (87%)** |

### Финансовая экономия (на 1000 профилей):

- **До:** $5.22
- **После:** $0.66
- **ЭКОНОМИЯ:** $4.56 (87%)

---

## 🗓️ План реализации (Пошаговый)

### День 1 (6 часов):

**09:00-11:00** - Задача 1.1: Создать `_extract_relevant_org_branch()`
- Написать основной метод
- Написать вспомогательные методы
- Добавить docstrings

**11:00-12:00** - Обед

**12:00-14:00** - Задача 1.1 (продолжение): Тестирование
- Создать unit тесты
- Провести интеграционные тесты
- Замерить токены

**14:00-16:00** - Задача 1.1 (продолжение): Интеграция
- Обновить `prepare_langfuse_variables()`
- Протестировать на реальных данных
- Убедиться, что качество не упало

**16:00-17:00** - Code review + документация

### День 2 (4 часа):

**09:00-11:00** - Задача 2.1: Сжатие карты компании
- Написать `_apply_company_map_compression()`
- Создать сжатую версию файла

**11:00-12:00** - Обед

**12:00-13:00** - Задача 2.1 (продолжение): Тестирование
- Проверить качество сжатия
- Замерить токены

**13:00-14:00** - Задача 2.1 (продолжение): Интеграция
- Обновить `prepare_langfuse_variables()`

### День 3 (4 часа):

**09:00-11:00** - Задача 3.1: Условная загрузка IT систем
- Написать `_should_load_it_systems()`
- Написать `_load_it_systems_conditional()`

**11:00-12:00** - Обед

**12:00-13:00** - Задача 3.1 (продолжение): Тестирование

**13:00-14:00** - Задача 4.1: Кеширование контекста
- Создать `ContextCache` класс
- Интегрировать в DataLoader

### День 4 (4 часа):

**09:00-11:00** - Финальное тестирование всей системы
- End-to-end тесты
- Замер метрик (токены, время, качество)

**11:00-12:00** - Обед

**12:00-14:00** - Документация + развертывание
- Обновить README
- Создать migration guide
- Deploy на staging

### День 5 (2 часа):

**09:00-10:00** - Мониторинг production
- Проверить метрики
- Собрать feedback

**10:00-11:00** - Ретроспектива + планирование следующих шагов

---

## ✅ Чек-лист перед развертыванием

- [ ] Все unit тесты проходят
- [ ] Интеграционные тесты проходят
- [ ] Замерены токены (цель: < 25,000)
- [ ] Качество генерации не ухудшилось (A/B тест)
- [ ] Документация обновлена
- [ ] Code review выполнен
- [ ] Staging тестирование пройдено
- [ ] Создан rollback план
- [ ] Команда проинформирована

---

## 🚨 Риски и митигация

### Риск 1: Потеря качества генерации

**Вероятность:** Средняя
**Воздействие:** Высокое

**Митигация:**
- A/B тестирование на 50 профилях до и после оптимизации
- Сравнение completeness_score и validation_score
- Если качество падает > 5% → откатываем изменения

### Риск 2: Ошибки в извлечении релевантной структуры

**Вероятность:** Средняя
**Воздействие:** Среднее

**Митигация:**
- Comprehensive unit тесты для edge cases
- Fallback к полной структуре при ошибках
- Логирование всех случаев, когда fallback сработал

### Риск 3: Кеш становится устаревшим

**Вероятность:** Низкая
**Воздействие:** Среднее

**Митигация:**
- TTL = 1 час (данные обновляются редко)
- Возможность принудительной очистки кеша
- Версионирование данных в кеше

---

## 📈 Метрики успеха

### Технические метрики:

- ✅ Токены контекста: < 25,000 (сейчас 158,000)
- ✅ Время prepare_langfuse_variables(): < 100ms (сейчас ~300ms)
- ✅ Стоимость генерации 1000 профилей: < $1.00 (сейчас $5.22)

### Качественные метрики:

- ✅ completeness_score: >= текущего значения
- ✅ validation_score: >= текущего значения
- ✅ Feedback от HR: "качество не ухудшилось"

### Операционные метрики:

- ✅ Все тесты проходят
- ✅ Code coverage: >= 80%
- ✅ Zero production incidents

---

## 🔄 Следующие шаги после оптимизации контекста

1. Generic KPI fallback (Направление из анализа)
2. Адаптивная иерархия объема профилей
3. Улучшение промпта (убрать противоречия)
4. Система обратной связи от HR

---

## 📞 Контакты и ресурсы

**Документация:**
- [Анализ контекста](../analysis/context_collection_analysis.md)
- [Анализ промпта](../analysis/prompt_analysis_report.md)
- [Feedback анализ](../analysis/feedback_inventory.md)

**Код:**
- `backend/core/data_loader.py` - основной файл
- `backend/core/organization_cache.py` - кеш оргструктуры
- `backend/core/context_cache.py` - новый кеш контекста

**Тесты:**
- `tests/test_data_loader_optimization.py` - новые тесты

---

**Статус документа:** ✅ Готов к реализации
**Последнее обновление:** 2025-10-25
**Версия:** 1.0
