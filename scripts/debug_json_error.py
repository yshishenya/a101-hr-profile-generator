#!/usr/bin/env python3
"""
Debug script to reproduce and analyze JSONDecodeError from OpenRouter API.

This script tests if OpenRouter returns malformed JSON responses under specific conditions:
- Large prompts (47K+ tokens)
- Long generation times (70s+)
- Different models and parameters
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


async def test_openrouter_response():
    """Test OpenRouter API with simple request to check response format."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment")
        return

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Simple test message
    messages = [
        {
            "role": "user",
            "content": "Return a simple JSON: {\"test\": \"value\"}"
        }
    ]

    try:
        logger.info("Testing simple OpenRouter API call...")
        start = time.time()

        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=100,
        )

        duration = time.time() - start
        logger.info(f"✅ Request completed in {duration:.2f}s")
        logger.info(f"Response ID: {response.id}")
        logger.info(f"Model: {response.model}")
        logger.info(f"Content: {response.choices[0].message.content}")

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSONDecodeError: {e}")
        logger.error(f"Error at line {e.lineno}, column {e.colno}, char {e.pos}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)


async def test_large_prompt():
    """Test with large prompt similar to production scenario."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment")
        return

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Create a large prompt (approximately 45K tokens)
    large_text = "Test data. " * 5000  # ~50K chars ≈ 12K tokens
    prompt = f"""
You are an HR profile generator. Generate a JSON profile based on this data:

Company info: {large_text}
Department info: {large_text}
Position requirements: {large_text}

Return ONLY valid JSON with the following structure:
{{
    "position_name": "Test Position",
    "department": "Test Department",
    "responsibilities": ["responsibility 1", "responsibility 2"]
}}
"""

    messages = [{"role": "user", "content": prompt}]
    prompt_length = len(prompt)
    estimated_tokens = prompt_length // 4

    logger.info(f"Testing with large prompt: {prompt_length} chars, ~{estimated_tokens} tokens")

    try:
        start = time.time()

        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=4000,
        )

        duration = time.time() - start
        logger.info(f"✅ Large request completed in {duration:.2f}s")
        logger.info(f"Response ID: {response.id}")
        logger.info(f"Usage: {response.usage}")
        logger.info(f"Content length: {len(response.choices[0].message.content)} chars")

        # Try to parse content as JSON
        try:
            content = response.choices[0].message.content
            parsed = json.loads(content)
            logger.info(f"✅ Response is valid JSON: {list(parsed.keys())}")
        except json.JSONDecodeError as je:
            logger.warning(f"Response is not valid JSON: {je}")
            logger.info(f"First 500 chars: {content[:500]}")

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSONDecodeError during API call: {e}")
        logger.error(f"Error at line {e.lineno}, column {e.colno}, char {e.pos}")
        logger.error("This means OpenRouter returned invalid JSON in HTTP response body")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)


async def test_with_raw_httpx():
    """Test with raw httpx to see actual HTTP response."""
    import httpx

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment")
        return

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-5-mini",
        "messages": [
            {"role": "user", "content": "Say 'test' in JSON format"}
        ],
        "temperature": 0.1,
        "max_tokens": 100,
    }

    try:
        logger.info("Testing with raw httpx client...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            logger.info(f"Content-Type: {response.headers.get('content-type')}")
            logger.info(f"Content length: {len(response.content)} bytes")

            # Log raw response
            raw_text = response.text
            logger.info(f"Raw response (first 1000 chars):")
            logger.info(f"REPR: {repr(raw_text[:1000])}")
            logger.info(raw_text[:1000])

            # Try to parse
            try:
                data = response.json()
                logger.info(f"✅ Response parsed successfully")
                logger.info(f"Keys: {list(data.keys())}")
            except json.JSONDecodeError as je:
                logger.error(f"❌ Failed to parse JSON: {je}")
                logger.error(f"Raw content: {raw_text[:2000]}")

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)


async def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("OpenRouter JSONDecodeError Debug Script")
    logger.info("=" * 80)

    logger.info("\n1. Testing simple API call...")
    await test_openrouter_response()

    logger.info("\n2. Testing with raw httpx...")
    await test_with_raw_httpx()

    logger.info("\n3. Testing with large prompt...")
    await test_large_prompt()

    logger.info("\n" + "=" * 80)
    logger.info("Tests completed")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
