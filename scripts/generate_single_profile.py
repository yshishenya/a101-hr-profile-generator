#!/usr/bin/env python3
"""
Simple script to generate a single profile directly using ProfileGenerator.
Usage: python scripts/generate_single_profile.py "Position Title" "Department Name"
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.profile_generator import ProfileGenerator
from backend.models.database import initialize_db_manager, get_db_manager
from backend.core.config import config


async def generate_profile(position_title: str, department_name: str) -> dict:
    """Generate a profile and return the result"""

    # Create generator (uses config for settings)
    generator = ProfileGenerator()

    print(f"\n🚀 Generating profile:")
    print(f"   Position: {position_title}")
    print(f"   Department: {department_name}")
    print()

    # Generate profile
    result = await generator.generate_profile(
        position=position_title,
        department=department_name
    )

    # Save to output directory
    output_dir = Path('output/profiles')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Clean filename
    safe_position = position_title.replace('/', '_').replace(' ', '_')
    safe_department = department_name.replace('/', '_').replace(' ', '_')
    filename = f'{safe_position}_{safe_department}_{timestamp}.json'
    output_path = output_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Profile saved to: {output_path}")
    print(f"📊 Profile size: {len(json.dumps(result))} bytes")

    return {
        'output_path': str(output_path),
        'result': result
    }


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print("Usage: python scripts/generate_single_profile.py 'Position Title' 'Department Name'")
        print("\nExample:")
        print("  python scripts/generate_single_profile.py 'Ведущий архитектор 2 категории' 'Бюро комплексного проектирования'")
        sys.exit(1)

    position_title = sys.argv[1]
    department_name = sys.argv[2]

    result = asyncio.run(generate_profile(position_title, department_name))

    print(f"\n📁 Output path: {result['output_path']}")


if __name__ == '__main__':
    main()
