#!/usr/bin/env python3
"""
Create Langfuse v54 WITHOUT response_format to restore v48 behavior.

Based on multi-agent root cause analysis:
- v48 worked: NO response_format
- v52 failed: WITH response_format (800-line schema)
- Solution: Create v54 like v48 (clean config)
"""

import os
import sys
from pathlib import Path

# Load .env variables
env_path = Path("/home/yan/A101/HR/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

sys.path.insert(0, "/home/yan/A101/HR")

from langfuse import Langfuse


def create_v54():
    """Create Langfuse v54 without response_format."""

    print("=" * 70)
    print("🔧 Creating Langfuse v54 - NO response_format (like v48)")
    print("=" * 70)
    print()

    # Initialize Langfuse
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        print("❌ Langfuse credentials not found")
        return False

    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host="https://cloud.langfuse.com"
    )

    # Get v52 prompt (has P0.5 improvements)
    print("📖 Reading v52 prompt...")
    try:
        v52 = langfuse.get_prompt('a101-hr-profile-gemini-v3-simple', version=52)
        print(f"✅ v52 loaded successfully")
        print(f"   Prompt length: {len(v52.prompt) if hasattr(v52, 'prompt') else 'N/A'} chars")
    except Exception as e:
        print(f"❌ Failed to load v52: {e}")
        return False

    # Create clean config WITHOUT response_format
    clean_config = {
        'model': 'gpt-5-mini',
        'temperature': 0.1,
        'max_tokens': 20000,
        # NO response_format - like v48!
    }

    print()
    print("🔧 Config for v54:")
    print(f"   Model: {clean_config['model']}")
    print(f"   Temperature: {clean_config['temperature']}")
    print(f"   Max tokens: {clean_config['max_tokens']}")
    print(f"   Response format: ❌ REMOVED (like v48)")
    print()

    # Create v54
    try:
        print("🚀 Creating v54 in Langfuse...")

        v54 = langfuse.create_prompt(
            name='a101-hr-profile-gemini-v3-simple',
            prompt=v52.prompt,  # Same prompt as v52 (P0.5)
            config=clean_config,  # But clean config (no response_format)
            labels=['production', 'v54-no-rf', 'latest'],
            type='text'
        )

        print()
        print("=" * 70)
        print("✅ SUCCESS! Langfuse v54 created")
        print("=" * 70)
        print(f"   Version: {v54.version if hasattr(v54, 'version') else 'N/A'}")
        print(f"   Labels: {v54.labels if hasattr(v54, 'labels') else 'N/A'}")
        print(f"   Config: Clean (model + temp + max_tokens only)")
        print()
        print("🎯 Expected behavior:")
        print("   - Like v48: 100% success rate")
        print("   - No timeout issues")
        print("   - No JSONDecodeError")
        print("   - Duration: ~120-150s (normal)")
        print()
        print("📋 Next steps:")
        print("   1. Restart Docker: docker compose restart app")
        print("   2. Test v54 on 2 profiles")
        print("   3. If successful → generate 4 final profiles")
        print()

        return True

    except Exception as e:
        print(f"❌ Failed to create v54: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_v54()
    exit(0 if success else 1)
