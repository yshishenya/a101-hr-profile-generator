#!/usr/bin/env python3
"""
Test JSON parsing with leading whitespace.
"""

import json

# Simulate OpenRouter response with leading whitespace
response_with_whitespace = """







{"id":"test","model":"gpt-5-mini","choices":[{"message":{"content":"test"}}]}
"""

response_clean = '{"id":"test","model":"gpt-5-mini","choices":[{"message":{"content":"test"}}]}'

print("1. Testing JSON parsing with leading whitespace:")
print(f"   String length: {len(response_with_whitespace)}")
print(f"   First 50 chars repr: {repr(response_with_whitespace[:50])}")

try:
    data = json.loads(response_with_whitespace)
    print(f"   ✅ SUCCESS: Parsed with whitespace")
    print(f"   Keys: {list(data.keys())}")
except json.JSONDecodeError as e:
    print(f"   ❌ FAILED: {e}")
    print(f"   Error at line {e.lineno}, column {e.colno}, char {e.pos}")

print("\n2. Testing JSON parsing with stripped whitespace:")
try:
    data = json.loads(response_with_whitespace.strip())
    print(f"   ✅ SUCCESS: Parsed after strip()")
    print(f"   Keys: {list(data.keys())}")
except json.JSONDecodeError as e:
    print(f"   ❌ FAILED: {e}")

print("\n3. Testing clean JSON:")
try:
    data = json.loads(response_clean)
    print(f"   ✅ SUCCESS: Parsed clean JSON")
    print(f"   Keys: {list(data.keys())}")
except json.JSONDecodeError as e:
    print(f"   ❌ FAILED: {e}")

# Test what character position causes the error
print("\n4. Finding the issue:")
print(f"   Character at position 343: {repr(response_with_whitespace[342:345]) if len(response_with_whitespace) > 342 else 'N/A'}")
print(f"   Character at position 1881: {repr(response_with_whitespace[1880:1883]) if len(response_with_whitespace) > 1880 else 'N/A'}")

# Simulate error from logs
print("\n5. Simulating the error from logs:")
# "Expecting value: line 343 column 1 (char 1881)"
# This means: at line 343, column 1, which is character position 1881

# Let's calculate: if response has many newlines at start,
# line 343 column 1 means 342 newlines + 1 char = position depends on content
test_response = '\n' * 342 + '{"test": "value"}'
print(f"   Test string: {len(test_response)} chars, starts with {repr(test_response[:20])}")
try:
    json.loads(test_response)
    print(f"   ✅ JSON with 342 leading newlines parsed OK")
except json.JSONDecodeError as e:
    print(f"   ❌ JSON with 342 leading newlines failed: {e}")
    print(f"   Error at line {e.lineno}, column {e.colno}, char {e.pos}")
