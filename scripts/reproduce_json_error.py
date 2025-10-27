#!/usr/bin/env python3
"""
Try to reproduce the JSONDecodeError by simulating production scenario.

Key differences from test:
1. Using OpenAI SDK (AsyncOpenAI) like in production
2. Using Langfuse wrapper
3. Same model and parameters as production
4. Multiple concurrent requests (stress test)
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


async def single_generation_test(test_id: int):
    """Single generation test."""

    api_key = os.getenv("OPENROUTER_API_KEY")

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Simulate production prompt (large)
    large_text = "x" * 50000  # ~50K chars
    prompt = f"""Generate a detailed HR profile based on this data:

Company data: {large_text}
Department: {large_text}

Return JSON: {{"position": "test", "details": "..."}}
"""

    messages = [{"role": "user", "content": prompt}]

    logger.info(f"[Test {test_id}] Starting generation...")
    start = time.time()

    try:
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=4000,
        )

        duration = time.time() - start
        logger.info(f"[Test {test_id}] ✅ Completed in {duration:.2f}s")
        logger.info(f"[Test {test_id}] Response ID: {response.id}")
        logger.info(f"[Test {test_id}] Content length: {len(response.choices[0].message.content)}")

        return {"success": True, "duration": duration, "test_id": test_id}

    except Exception as e:
        duration = time.time() - start
        logger.error(f"[Test {test_id}] ❌ Failed after {duration:.2f}s: {e}")
        return {"success": False, "duration": duration, "test_id": test_id, "error": str(e)}


async def concurrent_test(num_requests: int = 5):
    """Run multiple concurrent requests to stress test."""

    logger.info(f"Starting concurrent test with {num_requests} requests...")

    tasks = [single_generation_test(i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Analyze results
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
    failed = len(results) - successful

    logger.info("\n" + "="*80)
    logger.info("RESULTS:")
    logger.info("="*80)
    logger.info(f"Total requests: {num_requests}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")

    if failed > 0:
        logger.info("\nFailed requests:")
        for r in results:
            if isinstance(r, dict) and not r.get("success"):
                logger.info(f"  Test {r['test_id']}: {r.get('error', 'Unknown error')}")

    return results


async def test_with_langfuse():
    """Test with Langfuse integration like production."""

    try:
        from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI
        logger.info("Testing with Langfuse integration...")

        api_key = os.getenv("OPENROUTER_API_KEY")
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")

        if not all([api_key, langfuse_public_key, langfuse_secret_key]):
            logger.warning("Langfuse keys not found, skipping Langfuse test")
            return

        client = LangfuseAsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        messages = [{"role": "user", "content": "Test" * 10000}]

        logger.info("Sending request with Langfuse...")
        start = time.time()

        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=4000,
        )

        duration = time.time() - start
        logger.info(f"✅ Langfuse test completed in {duration:.2f}s")

    except ImportError:
        logger.warning("Langfuse not installed, skipping Langfuse test")
    except Exception as e:
        logger.error(f"❌ Langfuse test failed: {e}", exc_info=True)


async def main():
    """Run all tests."""

    logger.info("="*80)
    logger.info("OpenRouter JSONDecodeError Reproduction Script")
    logger.info("="*80)

    # Test 1: Single request
    logger.info("\n1. Single request test...")
    await single_generation_test(0)

    # Test 2: Concurrent requests
    logger.info("\n2. Concurrent requests test...")
    await concurrent_test(3)

    # Test 3: With Langfuse
    logger.info("\n3. Langfuse integration test...")
    await test_with_langfuse()

    logger.info("\n" + "="*80)
    logger.info("All tests completed")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(main())
