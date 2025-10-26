#!/usr/bin/env python3
"""
Synchronize production config.json schema with job_profile_schema.json

This script ensures that the schema used in production API matches
the canonical schema definition, preventing schema drift.

Usage:
    python scripts/sync_production_schema.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CANONICAL_SCHEMA = PROJECT_ROOT / "templates" / "job_profile_schema.json"
PRODUCTION_CONFIG = PROJECT_ROOT / "templates" / "prompts" / "production" / "config.json"


def load_canonical_schema():
    """Load the canonical schema from job_profile_schema.json"""
    print(f"📖 Loading canonical schema from: {CANONICAL_SCHEMA}")

    with open(CANONICAL_SCHEMA, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Extract schema from response_format.json_schema.schema
    schema = config.get("response_format", {}).get("json_schema", {}).get("schema", {})

    if not schema:
        raise ValueError("Could not extract schema from canonical config")

    print(f"✅ Loaded schema with {len(schema.get('properties', {}))} top-level properties")
    return schema


def load_production_config():
    """Load current production config"""
    print(f"📖 Loading production config from: {PRODUCTION_CONFIG}")

    with open(PRODUCTION_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)

    print(f"✅ Loaded config (model={config.get('model')}, strict={config.get('response_format', {}).get('json_schema', {}).get('strict')})")
    return config


def create_updated_config(canonical_schema):
    """Create updated production config with canonical schema"""
    print("🔧 Creating updated config with canonical schema...")

    updated_config = {
        "model": "google/gemini-2.5-flash-lite",  # Correct model
        "temperature": 0.1,
        "max_tokens": 20000,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "Universal Corporate Job Profile Schema",
                "strict": True,
                "schema": canonical_schema  # Use canonical schema directly
            }
        }
    }

    print("✅ Created updated config")
    return updated_config


def save_production_config(config):
    """Save updated config to production"""
    # Create backup first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PRODUCTION_CONFIG.parent / f"config.json.before_sync_{timestamp}"

    print(f"💾 Creating backup: {backup_path.name}")
    with open(PRODUCTION_CONFIG, "r", encoding="utf-8") as f_in:
        with open(backup_path, "w", encoding="utf-8") as f_out:
            f_out.write(f_in.read())

    # Save new config
    print(f"💾 Saving updated config to: {PRODUCTION_CONFIG}")
    with open(PRODUCTION_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("✅ Config saved successfully")


def validate_schema(schema):
    """Validate that schema has required structure"""
    print("🔍 Validating schema structure...")

    errors = []

    # Check top-level type
    if schema.get("type") != "object":
        errors.append("Schema type must be 'object'")

    # Check required properties exist
    required_props = [
        "position_title",
        "department_broad",
        "department_specific",
        "responsibility_areas",
        "careerogram"
    ]

    properties = schema.get("properties", {})
    for prop in required_props:
        if prop not in properties:
            errors.append(f"Missing required property: {prop}")

    # Check careerogram structure
    careerogram = properties.get("careerogram", {})
    if careerogram.get("type") != "object":
        errors.append("careerogram must be type 'object'")

    careerogram_props = careerogram.get("properties", {})

    # Check source_positions structure
    source_positions = careerogram_props.get("source_positions", {})
    if source_positions.get("type") != "object":
        errors.append("source_positions must be type 'object'")

    source_pos_props = source_positions.get("properties", {})
    if "direct_predecessors" not in source_pos_props:
        errors.append("source_positions must have 'direct_predecessors'")
    if "cross_functional_entrants" not in source_pos_props:
        errors.append("source_positions must have 'cross_functional_entrants'")

    # Check target_pathways structure
    target_pathways = careerogram_props.get("target_pathways", {})
    if target_pathways.get("type") != "object":
        errors.append("target_pathways must be type 'object'")

    target_props = target_pathways.get("properties", {})
    for growth_type in ["vertical_growth", "horizontal_growth", "expert_growth"]:
        if growth_type not in target_props:
            errors.append(f"target_pathways must have '{growth_type}'")
        else:
            growth = target_props[growth_type]
            if growth.get("type") != "array":
                errors.append(f"{growth_type} must be type 'array'")

    # Check responsibility_areas.area type
    resp_areas = properties.get("responsibility_areas", {})
    items = resp_areas.get("items", {})
    item_props = items.get("properties", {})
    area = item_props.get("area", {})
    if area.get("type") != "string":
        errors.append("responsibility_areas.area must be type 'string'")

    # Check for reasoning fields (should NOT exist)
    reasoning_fields = [
        "reasoning_context_analysis",
        "position_classification_reasoning",
        "responsibility_areas_reasoning",
        "professional_skills_reasoning",
        "careerogram_reasoning"
    ]

    found_reasoning = [f for f in reasoning_fields if f in properties]
    if found_reasoning:
        errors.append(f"Found reasoning fields (should not exist): {', '.join(found_reasoning)}")

    # Report results
    if errors:
        print("❌ Schema validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Schema validation passed")
        return True


def main():
    """Main synchronization flow"""
    print("=" * 70)
    print("🔄 PRODUCTION SCHEMA SYNCHRONIZATION")
    print("=" * 70)
    print()

    try:
        # Load canonical schema
        canonical_schema = load_canonical_schema()

        # Validate canonical schema
        if not validate_schema(canonical_schema):
            print("\n❌ Canonical schema validation failed. Aborting.")
            return 1

        # Load current production config
        current_config = load_production_config()

        # Create updated config
        updated_config = create_updated_config(canonical_schema)

        # Save updated config
        save_production_config(updated_config)

        print()
        print("=" * 70)
        print("✅ SYNCHRONIZATION COMPLETE")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print(f"   - Canonical schema: {CANONICAL_SCHEMA.name}")
        print(f"   - Production config: {PRODUCTION_CONFIG.name}")
        print(f"   - Schema properties: {len(canonical_schema.get('properties', {}))}")
        print(f"   - Strict mode: {updated_config['response_format']['json_schema']['strict']}")
        print()
        print("🎯 Next steps:")
        print("   1. Test generation with a sample department")
        print("   2. Validate generated profiles pass strict schema validation")
        print("   3. Monitor for any schema-related errors")
        print()

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON decode error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
