#!/usr/bin/env python3
"""
Test script for generating Architect 3 profile.
Loads environment variables first, then runs the generator.
"""
import asyncio
import sys
from pathlib import Path

# Load environment variables BEFORE importing any project modules
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
print(f"✅ Loaded environment from: {env_path}")

# Verify critical env vars
import os
print(f"OPENROUTER_API_KEY present: {bool(os.getenv('OPENROUTER_API_KEY'))}")
print(f"LANGFUSE_PUBLIC_KEY present: {bool(os.getenv('LANGFUSE_PUBLIC_KEY'))}")

# Override BASE_DATA_PATH for local execution (not Docker)
project_root = Path(__file__).parent
os.environ['BASE_DATA_PATH'] = str(project_root)
print(f"BASE_DATA_PATH set to: {project_root}")

# Now import project modules
sys.path.insert(0, str(Path(__file__).parent))
from backend.core.profile_generator import ProfileGenerator


async def generate_architect_profile():
    """Generate profile for Architect 3 category."""
    print("\n" + "="*80)
    print("TEST 1 OF 3: Generating profile for Архитектор 3 категории")
    print("="*80 + "\n")

    generator = ProfileGenerator()

    result = await generator.generate_profile(
        department='Бюро комплексного проектирования',
        position='Архитектор 3 категории',
        employee_name='Reference Test - Architect 3',
        temperature=0.1,
        save_result=True
    )

    return result


def main():
    """Main execution function."""
    try:
        result = asyncio.run(generate_architect_profile())

        print("\n" + "="*80)
        print("GENERATION RESULT")
        print("="*80)

        if result.get('success'):
            print(f"✅ Status: SUCCESS")
            print(f"📋 Profile ID: {result.get('profile_id')}")
            print(f"📄 File path: {result.get('file_path')}")

            # Print metadata
            metadata = result.get('metadata', {})
            generation = metadata.get('generation', {})
            print(f"\n🔧 Generation Details:")
            print(f"   Department: {generation.get('department')}")
            print(f"   Position: {generation.get('position')}")
            print(f"   Employee: {generation.get('employee_name')}")
            print(f"   Duration: {generation.get('duration', 0):.2f}s")

            return 0
        else:
            print(f"❌ Status: FAILED")
            errors = result.get('errors', [])
            for error in errors:
                print(f"   Error: {error}")

            warnings = result.get('warnings', [])
            for warning in warnings:
                print(f"   Warning: {warning}")

            return 1

    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
