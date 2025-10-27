#!/usr/bin/env python3
"""
Test hypothesis: OpenRouter returns incomplete/truncated JSON when:
1. Response is very long
2. Generation takes long time
3. Some timeout or buffer limit is hit
"""

import json

# Hypothesis 1: JSON is truncated mid-stream
incomplete_json_1 = '''
{
  "id": "test",
  "model": "gpt-5-mini",
  "choices": [
    {
      "message": {
        "content": "This is a very long response that might be truncat'''

print("Test 1: Incomplete JSON (truncated mid-string)")
print(f"Length: {len(incomplete_json_1)} chars")
try:
    json.loads(incomplete_json_1)
    print("✅ Parsed successfully")
except json.JSONDecodeError as e:
    print(f"❌ JSONDecodeError: {e}")
    print(f"   Line {e.lineno}, column {e.colno}, char position {e.pos}")

# Hypothesis 2: JSON contains extra characters/data after valid JSON
json_with_extra = '''{"id":"test","model":"gpt-5-mini"}
Some extra text here that is not JSON
And maybe more lines of garbage data'''

print("\nTest 2: JSON with extra non-JSON data after")
print(f"Length: {len(json_with_extra)} chars")
try:
    json.loads(json_with_extra)
    print("✅ Parsed successfully")
except json.JSONDecodeError as e:
    print(f"❌ JSONDecodeError: {e}")
    print(f"   Line {e.lineno}, column {e.colno}, char position {e.pos}")

# Hypothesis 3: Multiple JSON objects (streaming response not properly closed)
multiple_jsons = '''{"id":"test1","model":"gpt-5-mini"}
{"id":"test2","model":"gpt-5-mini"}'''

print("\nTest 3: Multiple JSON objects")
print(f"Length: {len(multiple_jsons)} chars")
try:
    json.loads(multiple_jsons)
    print("✅ Parsed successfully")
except json.JSONDecodeError as e:
    print(f"❌ JSONDecodeError: {e}")
    print(f"   Line {e.lineno}, column {e.colno}, char position {e.pos}")

# Hypothesis 4: Character position 1881 analysis
# "Expecting value: line 343 column 1 (char 1881)"
# This means: at position 1881, expecting a value but found something else

print("\n" + "="*80)
print("ANALYSIS OF ERROR POSITIONS:")
print("="*80)
print("\nError 1: line 343 column 1 (char 1881)")
print("  - Line 343, column 1 means start of line 343")
print("  - Character position 1881")
print("  - If average line is 5.5 chars (343 lines → 1881 chars)")
print("  - Likely: truncated response or streaming issue")

print("\nError 2: line 687 column 1 (char 3773)")
print("  - Line 687, column 1 means start of line 687")
print("  - Character position 3773")
print("  - If average line is 5.5 chars (687 lines → 3773 chars)")
print("  - Likely: same issue but response got further")

print("\n" + "="*80)
print("HYPOTHESIS:")
print("="*80)
print("OpenRouter is returning STREAMING response that gets cut off")
print("The SDK expects complete JSON but receives partial stream")
print("Line 343/687 column 1 = empty line or unexpected character")
print("This happens when:")
print("  1. Response is very long (4K+ chars)")
print("  2. Generation takes long time (70s+)")
print("  3. Some connection timeout or buffer issue")
