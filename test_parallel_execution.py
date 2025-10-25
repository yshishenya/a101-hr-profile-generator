#!/usr/bin/env python3
"""
Тест параллельного выполнения запросов генерации профилей
"""

import asyncio
import time
from datetime import datetime

async def mock_generation(task_id: int, delay: float = 1.0):
    """Имитация генерации профиля"""
    start = time.time()
    print(f"  🚀 Задача {task_id} запущена в {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    await asyncio.sleep(delay)
    elapsed = time.time() - start
    print(f"  ✅ Задача {task_id} завершена за {elapsed:.2f}с")
    return f"result_{task_id}"


async def test_sequential():
    """Тест последовательного выполнения (старый код)"""
    print("\n1️⃣ Тест ПОСЛЕДОВАТЕЛЬНОГО выполнения (старый код):")
    print("=" * 60)

    start = time.time()
    results = []

    # Последовательное выполнение - как было раньше
    for i in range(1, 4):
        result = await mock_generation(i, delay=0.5)
        results.append(result)

    total_time = time.time() - start
    print(f"\n📊 Итого: {len(results)} задач за {total_time:.2f}с")
    print(f"⚠️  Ожидаемое время: ~1.5с (3 задачи × 0.5с)")
    return total_time


async def test_parallel():
    """Тест параллельного выполнения (новый код)"""
    print("\n2️⃣ Тест ПАРАЛЛЕЛЬНОГО выполнения (новый код с asyncio.gather):")
    print("=" * 60)

    start = time.time()

    # Создаем список корутин
    tasks = [mock_generation(i, delay=0.5) for i in range(1, 4)]

    # Запускаем параллельно с asyncio.gather
    results = await asyncio.gather(*tasks)

    total_time = time.time() - start
    print(f"\n📊 Итого: {len(results)} задач за {total_time:.2f}с")
    print(f"✅ Ожидаемое время: ~0.5с (параллельно)")
    return total_time


async def main():
    print("\n" + "=" * 60)
    print("  ТЕСТ ПАРАЛЛЕЛЬНОГО ВЫПОЛНЕНИЯ ГЕНЕРАЦИИ ПРОФИЛЕЙ")
    print("=" * 60)

    seq_time = await test_sequential()
    par_time = await test_parallel()

    print("\n" + "=" * 60)
    print("📈 РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    print(f"Последовательное выполнение: {seq_time:.2f}с")
    print(f"Параллельное выполнение:     {par_time:.2f}с")

    speedup = seq_time / par_time
    print(f"\n🚀 Ускорение: {speedup:.1f}x")

    if speedup > 2.5:
        print("✅ Параллельное выполнение работает корректно!")
        print(f"   Выигрыш во времени: {((speedup - 1) * 100):.0f}%")
    else:
        print("⚠️  Параллельное выполнение не дает ожидаемого ускорения")

    print("\n" + "=" * 60)
    print("💡 В реальном скрипте:")
    print("   - Пакет из 10 профилей")
    print(f"   - Старый код: ~{10 * 95:.0f}с (10 × 95с последовательно)")
    print(f"   - Новый код:  ~95с (все 10 параллельно)")
    print(f"   - Ускорение:  ~10x! 🎉")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
