#!/usr/bin/env python3
"""
Check if OpenRouter accidentally returns streaming response.

According to the errors:
- "Expecting value: line 343 column 1 (char 1881)"
- "Expecting value: line 687 column 1 (char 3773)"

The error says "Expecting value" not "Extra data", which means:
- JSON parser found a syntax error
- Not a valid JSON value at that position
- Could be empty line, whitespace, or unexpected character
"""

import asyncio
import os
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv

load_dotenv()


async def test_long_generation():
    """Test with very long generation to see if response format changes."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not found")
        return

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Create a prompt that will generate LONG response (similar to profile generation)
    long_prompt = """
You are a professional HR profile generator. Create a DETAILED job description
for a Software Engineer position. Include:

1. Position Overview (3 paragraphs)
2. Key Responsibilities (20+ items, each with detailed explanation)
3. Required Qualifications (15+ items with details)
4. Desired Qualifications (10+ items)
5. Technical Skills Required (15+ specific technologies)
6. Soft Skills (10+ with explanations)
7. Day-to-day Activities (15+ detailed scenarios)
8. Career Growth Opportunities (5+ paragraphs)
9. Team Structure (3 paragraphs)
10. Company Culture (3 paragraphs)

Return ONLY as JSON with this structure:
{
  "position_name": "...",
  "overview": "...",
  "responsibilities": [...],
  "required_qualifications": [...],
  "desired_qualifications": [...],
  "technical_skills": [...],
  "soft_skills": [...],
  "daily_activities": [...],
  "career_growth": "...",
  "team_structure": "...",
  "company_culture": "..."
}

Make it VERY detailed and comprehensive. Each array should have many items.
Each string field should be multiple paragraphs.
"""

    payload = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": long_prompt}],
        "temperature": 0.1,
        "max_tokens": 4000,  # Allow long response
        "stream": False,  # Explicitly disable streaming
    }

    print("Testing long generation with OpenRouter...")
    print(f"Max tokens: {payload['max_tokens']}")
    print(f"Stream: {payload['stream']}")

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            print("\nSending request...")
            response = await client.post(url, json=payload, headers=headers)

            print(f"\nStatus: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Transfer-Encoding: {response.headers.get('transfer-encoding', 'N/A')}")
            print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
            print(f"Response size: {len(response.content)} bytes")

            # Check raw content
            raw_text = response.text
            print(f"\nRaw response length: {len(raw_text)} chars")
            print(f"First 100 chars REPR: {repr(raw_text[:100])}")
            print(f"Last 100 chars REPR: {repr(raw_text[-100:])}")

            # Check for specific characters at error positions
            if len(raw_text) > 1881:
                print(f"\nCharacter at position 1881 (error pos 1):")
                print(f"  Context: {repr(raw_text[1870:1890])}")

            if len(raw_text) > 3773:
                print(f"\nCharacter at position 3773 (error pos 2):")
                print(f"  Context: {repr(raw_text[3763:3783])}")

            # Count lines
            lines = raw_text.split('\n')
            print(f"\nTotal lines: {len(lines)}")
            if len(lines) >= 343:
                print(f"Line 343 content: {repr(lines[342][:100])}")
            if len(lines) >= 687:
                print(f"Line 687 content: {repr(lines[686][:100])}")

            # Try to parse
            try:
                import json
                data = json.loads(raw_text)
                print(f"\n✅ Response parsed successfully")
                print(f"Keys: {list(data.keys())}")

                # Check if content is very long
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0].get('message', {}).get('content', '')
                    print(f"Content length: {len(content)} chars")

                    # Check for reasoning field (new in gpt-5-mini)
                    reasoning = data['choices'][0].get('message', {}).get('reasoning', '')
                    if reasoning:
                        print(f"Reasoning length: {len(reasoning)} chars")
                        print(f"Reasoning preview: {reasoning[:200]}...")

            except json.JSONDecodeError as e:
                print(f"\n❌ JSONDecodeError: {e}")
                print(f"Error at line {e.lineno}, column {e.colno}, char {e.pos}")

                # Show context around error
                error_pos = e.pos
                start = max(0, error_pos - 100)
                end = min(len(raw_text), error_pos + 100)
                print(f"\nContext around error position {error_pos}:")
                print(f"REPR: {repr(raw_text[start:end])}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_long_generation())
