# Анализ паттернов ошибок генерации профилей

## Дата анализа
2025-10-26

## Сводная таблица генераций

| Timestamp | Version | Position | Result | Duration | Error Position | Error Type |
|-----------|---------|----------|--------|----------|----------------|------------|
| 15:22:10 | v52 | Backend Python Developer Test V52 | FAILED | 72.43s | line 343, char 1881 | JSONDecodeError |
| 15:38:38 | v52 | HR Business Partner V52 Retry | FAILED | 144.63s | line 687, char 3773 | JSONDecodeError |
| 16:02:14 | v53 (gemini-v3-simple) | Backend Developer Gemini Test | SUCCESS | 29.17s | - | - |

## Детальный анализ

### 1. Успешная генерация (16:02:14)
```
Prompt: a101-hr-profile-gemini-v3-simple
Model: google/gemini-2.0-flash-001 (via OpenRouter)
Duration: 29.17s
Flow:
  - ProfileGenerator initialized
  - Langfuse prompt retrieved successfully
  - Compiled prompt using Langfuse compile()
  - Generation completed without errors
  - Profile validation: 100% complete, 0 errors
  - Profile saved successfully
```

### 2. Неудачные генерации (v52)

#### Генерация 1 (15:22:10 - 15:23:23)
```
Prompt: a101-hr-profile-gemini-v3-simple
Position: Backend Python Developer Test V52
Duration: 72.43s (в 2.5x дольше успешной)
Error: JSONDecodeError: Expecting value: line 343 column 1 (char 1881)

Traceback origin:
  - openai/_response.py:265 → response.json()
  - httpx/_models.py:832 → jsonlib.loads(self.content)
  - Python json.decoder → raw_decode failure

Логирование:
  - ❌ "Unexpected OpenAI API error"
  - ❌ "Langfuse generation failed after 72.43s"
  - ⚠️ Validation запустилась несмотря на ошибку генерации
```

#### Генерация 2 (15:38:38 - 15:41:02)
```
Prompt: a101-hr-profile-gemini-v3-simple
Position: HR Business Partner V52 Retry
Duration: 144.63s (в 5x дольше успешной!)
Error: JSONDecodeError: Expecting value: line 687 column 1 (char 3773)

Traceback origin: идентичный первой ошибке
Логирование: идентичное первой ошибке
```

## Паттерны ошибок

### Общие признаки неудачных генераций:

1. **Аномально долгое время выполнения**
   - Успешная: 29.17s
   - Неудачная 1: 72.43s (+148%)
   - Неудачная 2: 144.63s (+396%)

2. **JSONDecodeError на разных позициях**
   - Error 1: line 343, char 1881
   - Error 2: line 687, char 3773
   - **Паттерн**: ошибка всегда на column 1 (начало строки)

3. **Источник ошибки**
   - Ошибка происходит при парсинге HTTP response от OpenRouter
   - `response.json()` не может распарсить `response.content`
   - **Гипотеза**: OpenRouter возвращает невалидный JSON или частичный ответ

4. **Одинаковый промпт**
   - Все 3 генерации используют `a101-hr-profile-gemini-v3-simple`
   - Успешная и неудачные используют одну и ту же конфигурацию
   - **Вывод**: проблема не в промпте, а в ответе от API

5. **Логика после ошибки**
   - После JSONDecodeError всё равно запускается "Validating generated profile"
   - **Проблема в коде**: валидация не должна запускаться при ошибке генерации

## Технический анализ

### Stack trace анализ:
```python
# Цепочка вызовов:
llm_client.py:472 → generate_profile_from_langfuse()
  ↓
llm_client.py:149 → _create_generation_with_prompt()
  ↓
langfuse/openai.py:911 → _wrap_async (wrapper)
  ↓
openai/.../completions.py:2603 → create()
  ↓
openai/_base_client.py:1688 → _process_response()
  ↓
openai/_response.py:265 → _parse()
  ↓
httpx/_models.py:832 → response.json()
  ↓
json.decoder.py:356 → CRASH: JSONDecodeError
```

### Критическая точка:
**`openai/_response.py` пытается распарсить `response.content` как JSON**, но получает:
- Либо пустой ответ
- Либо частичный JSON (обрывается на строке 343 или 687)
- Либо невалидный формат (HTML error page, timeout message)

### Почему разные позиции ошибок?
- **line 343 (char 1881)**: Модель сгенерировала ~1.8KB данных, затем прервалась
- **line 687 (char 3773)**: Модель сгенерировала ~3.7KB данных, затем прервалась
- **Паттерн**: Оба раза обрыв на column 1 = начало новой строки
- **Гипотеза**: Timeout/connection issue во время streaming

## Гипотезы о причинах

### 🔴 Гипотеза 1: Timeout на стороне OpenRouter
**Вероятность: ВЫСОКАЯ**
- Генерации с ошибками в 2.5-5x длиннее успешной
- OpenRouter может прерывать слишком долгие запросы
- Модель Gemini 2.0 Flash может медленно работать при больших промптах

**Проверка**:
```python
# Проверить в llm_client.py:
- Есть ли timeout настройки для httpx client?
- Какой timeout по умолчанию в openai SDK?
```

### 🔴 Гипотеза 2: Частичный ответ от модели (streaming issue)
**Вероятность: СРЕДНЯЯ**
- Ошибки всегда на column 1 = начало строки в JSON
- Похоже на обрыв во время streaming
- SDK пытается распарсить неполный JSON

**Проверка**:
- Используется ли streaming? (response_format={"type": "json_object"})
- Может ли SDK корректно обработать частичные ответы?

### 🟡 Гипотеза 3: Rate limiting от OpenRouter
**Вероятность: НИЗКАЯ**
- Если бы был rate limit, был бы HTTP 429 error
- JSONDecodeError означает что ответ получен, но невалиден
- Но: могут быть "мягкие" лимиты без HTTP ошибок

### 🟡 Гипотеза 4: Проблема с конкретными позициями
**Вероятность: НИЗКАЯ**
- "Backend Python Developer" и "HR Business Partner" - разные роли
- Успешная генерация тоже для Backend Developer
- **Вывод**: не зависит от контента позиции

## Рекомендации

### Немедленные действия:

1. **Добавить логирование raw response**
   ```python
   # В llm_client.py перед response.json():
   logger.debug(f"Raw response status: {response.status_code}")
   logger.debug(f"Raw response content length: {len(response.content)}")
   logger.debug(f"Raw response headers: {response.headers}")
   if response.status_code != 200:
       logger.error(f"Non-200 response: {response.content[:1000]}")
   ```

2. **Увеличить timeout**
   ```python
   # В конфигурации OpenAI client:
   client = openai.AsyncOpenAI(
       timeout=180.0,  # было 120? увеличить до 3 минут
       max_retries=2
   )
   ```

3. **Добавить try-catch для JSONDecodeError**
   ```python
   try:
       response = await self.client.chat.completions.create(...)
   except json.JSONDecodeError as e:
       logger.error(f"Invalid JSON from API at {e.pos}: {response.content[:2000]}")
       raise
   ```

4. **Исправить логику валидации**
   ```python
   # profile_generator.py: НЕ валидировать если генерация упала
   try:
       result = await self.llm_client.generate_profile_from_langfuse(...)
       if result:  # только если успешно
           self._validate_profile(result)
   except Exception as e:
       logger.error(f"Generation failed: {e}")
       return None  # не продолжать
   ```

### Дальнейшие исследования:

1. Проверить Langfuse trace для failed генераций
2. Сравнить размер промпта (input tokens) для успешных vs failed
3. Проверить статистику OpenRouter для этих запросов
4. Тестировать с разными моделями (Claude vs Gemini)

## Заключение

**Основная причина**: OpenRouter/Gemini API возвращает невалидный/частичный JSON ответ при длительных генерациях (>70s).

**Механизм**:
1. Модель начинает генерировать ответ
2. Процесс занимает слишком много времени (timeout на промежуточном proxy?)
3. Соединение обрывается на середине JSON
4. OpenAI SDK получает неполный JSON и падает с JSONDecodeError

**Решение**:
1. Увеличить timeouts
2. Добавить retry logic с экспоненциальным backoff
3. Добавить fallback на другую модель при repeated failures
4. Улучшить error handling и логирование

**Приоритет**: P0 - Critical (блокирует генерацию профилей)
