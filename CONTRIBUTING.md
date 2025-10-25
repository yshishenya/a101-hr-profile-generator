# Contributing to HR Profile Generator

Спасибо за интерес к проекту! Мы рады любому вкладу.

## 🎯 Как внести вклад

### 1. Найдите задачу

- Проверьте [Memory Bank Current Tasks](.memory_bank/current_tasks.md) для активных задач
- Посмотрите открытые issues в репозитории
- Предложите новую функцию через issue

### 2. Настройте окружение

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/a101-hr-profile-generator.git
cd a101-hr-profile-generator

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте .env файл
cp .env.example .env
# Отредактируйте .env с вашими API ключами
```

### 3. Создайте ветку

```bash
# Создайте feature branch
git checkout -b feature/amazing-feature

# Или bugfix branch
git checkout -b bugfix/fix-something
```

### 4. Разработка

#### 📖 Обязательное чтение

**ПЕРЕД началом работы прочитайте:**

1. **[Memory Bank README](.memory_bank/README.md)** - Основная память проекта
2. **[Tech Stack](.memory_bank/tech_stack.md)** - Технологический стек
3. **[Coding Standards](.memory_bank/guides/coding_standards.md)** - Стандарты кодирования
4. **[CLAUDE.md](CLAUDE.md)** - Конфигурация проекта для AI ассистентов

#### ✅ Стандарты кода

**Python Code Style:**
- Python 3.11+
- Type hints для всех функций
- Docstrings в Google Style
- Black для форматирования (line length: 100)
- Ruff для линтинга
- mypy для проверки типов

**Async/Await:**
- Все I/O операции ДОЛЖНЫ быть асинхронными
- Используйте `httpx` (НЕ requests)
- Используйте `aiofiles` для файловых операций
- Используйте async драйверы для БД

**Пример правильного кода:**

```python
import httpx
from typing import Dict, Any

async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data from external API.

    Args:
        url: The URL to fetch from

    Returns:
        JSON response as dictionary

    Raises:
        httpx.HTTPError: If request fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
```

#### 🚫 Запрещено

1. Синхронные I/O в async коде
2. Использование `Any` в type hints
3. Хранение секретов в коде
4. Raw SQL без параметризации
5. Пустые exception handlers

### 5. Тестирование

```bash
# Запустите тесты
pytest

# С покрытием
pytest --cov=backend --cov-report=html

# Проверка типов
mypy backend/

# Форматирование
black .

# Линтинг
ruff check .
```

### 6. Commit

**Используйте Conventional Commits:**

```bash
# Новая функция
git commit -m "feat: add user authentication endpoint"

# Исправление бага
git commit -m "fix: resolve timeout issue in LLM client"

# Документация
git commit -m "docs: update API endpoint documentation"

# Рефакторинг
git commit -m "refactor: simplify profile generation logic"

# Тесты
git commit -m "test: add tests for KPI mapping"

# Performance
git commit -m "perf: optimize data loader caching"
```

### 7. Push и Pull Request

```bash
# Push вашей ветки
git push origin feature/amazing-feature

# Создайте Pull Request через GitHub
```

## 📝 Pull Request Guidelines

### Checklist перед PR:

- [ ] Все тесты проходят (`pytest`)
- [ ] Код отформатирован (`black .`)
- [ ] Линтер не выдает ошибок (`ruff check .`)
- [ ] Type hints проверены (`mypy backend/`)
- [ ] Документация обновлена (если нужно)
- [ ] [Memory Bank](.memory_bank/) обновлен (если нужно)
- [ ] CHANGELOG.md обновлен

### В описании PR укажите:

1. **Что изменено**: Краткое описание изменений
2. **Почему**: Зачем нужны эти изменения
3. **Как тестировать**: Инструкции для проверки
4. **Screenshots**: Если изменения затрагивают UI
5. **Breaking changes**: Если есть breaking changes

## 🏗️ Архитектурные принципы

Следуйте принципам проекта из [Memory Bank](.memory_bank/):

1. **AI-First**: Используйте LLM для творческой генерации
2. **Deterministic Logic**: Детерминированная логика для маппинга данных
3. **Async/Await**: Все I/O операции асинхронные
4. **Type Safety**: Строгая типизация
5. **Single Source of Truth**: Одна точка для каждого типа данных

## 📚 Ресурсы

### Документация
- [README](README.md) - Общая информация о проекте
- [docs/](docs/) - Полная документация
- [Memory Bank](.memory_bank/) - Техническая память проекта

### Полезные ссылки
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Langfuse Documentation](https://langfuse.com/docs)

## 🔄 Рабочий процесс

### Для новых функций:

1. Создайте issue с описанием
2. Обсудите подход в issue
3. Создайте ветку `feature/feature-name`
4. Следуйте [New Feature Workflow](.memory_bank/workflows/new_feature.md)
5. Обновите [Current Tasks](.memory_bank/current_tasks.md)
6. Создайте PR

### Для багов:

1. Создайте issue с воспроизведением
2. Создайте ветку `bugfix/bug-name`
3. Следуйте [Bug Fix Workflow](.memory_bank/workflows/bug_fix.md)
4. Добавьте тест, воспроизводящий баг
5. Исправьте и убедитесь, что тест проходит
6. Создайте PR

## 💬 Вопросы?

- Создайте issue с меткой `question`
- Проверьте [Memory Bank](.memory_bank/) для технических деталей
- Посмотрите [docs/](docs/) для документации

## 📄 License

Внося вклад, вы соглашаетесь, что ваш код будет лицензирован под MIT License.

---

Спасибо за вклад в HR Profile Generator! 🎉
