#!/usr/bin/env python3
"""
Генерация 4 тестовых профилей с P0.5-enhanced prompt (Langfuse v49).
Критический тест для валидации P0.2 и P0.4 enforcement.
"""

import json
import requests
import time
from pathlib import Path

# Base configuration
API_URL = "http://localhost:8022/api"
OUTPUT_DIR = Path("/home/yan/A101/HR/output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Test profiles to generate
PROFILES = [
    {
        "department": "Департамент информационных технологий",
        "position": "Backend Python Developer",
        "output_file": "profile_backend_python_p05_v49.json",
        "description": "Technical role - tests P0.1, P0.3 (IT frameworks)"
    },
    {
        "department": "Бухгалтерия",
        "position": "Главный бухгалтер",
        "output_file": "profile_chief_accountant_p05_v49.json",
        "description": "Finance role - tests P0.1, P0.3 (МСФО, РСБУ)"
    },
    {
        "department": "Департамент персонала",
        "position": "HR Business Partner",
        "output_file": "profile_hrbp_p05_v49.json",
        "description": "CRITICAL TEST: HR role - tests P0.2 (soft skills methodologies), P0.3 (ТК РФ), P0.4 (uniqueness)"
    },
    {
        "department": "Отдел продаж",
        "position": "Менеджер по продажам B2B",
        "output_file": "profile_sales_b2b_p05_v49.json",
        "description": "CRITICAL TEST: Sales role - tests P0.2 (SPIN, BATNA), P0.4 (uniqueness)"
    }
]


def get_auth_token():
    """Get JWT auth token"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    response.raise_for_status()
    return response.json()["access_token"]


def generate_profile(token, department, position):
    """Generate single profile"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "department": department,
        "position": position
    }

    print(f"\n🚀 Generating: {position}")
    print(f"   Department: {department}")

    response = requests.post(
        f"{API_URL}/generation/start",
        headers=headers,
        json=payload,
        timeout=600  # 10 minutes timeout
    )

    response.raise_for_status()
    return response.json()


def verify_p05_prompt(profile_data):
    """Verify that P0.5 prompt (v49) was used"""
    # Check metadata for prompt version
    if isinstance(profile_data, dict):
        # Look for prompt_version or metadata
        metadata = profile_data.get("metadata", {})
        prompt_version = metadata.get("prompt_version")

        if prompt_version:
            if prompt_version >= 49:
                return True, prompt_version
            else:
                return False, prompt_version

    return None, None


def main():
    print("="*80)
    print("P0.5 TEST PROFILES GENERATION (Langfuse v49)")
    print("="*80)

    # Get auth token
    print("\n🔐 Authenticating...")
    try:
        token = get_auth_token()
        print("✅ Authenticated successfully")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # Generate all profiles
    results = []

    for i, profile_spec in enumerate(PROFILES, 1):
        print(f"\n{'='*80}")
        print(f"PROFILE {i}/4: {profile_spec['position']}")
        print(f"{'='*80}")
        print(f"📝 {profile_spec['description']}")

        try:
            # Generate
            start_time = time.time()
            profile_data = generate_profile(
                token,
                profile_spec["department"],
                profile_spec["position"]
            )
            generation_time = time.time() - start_time

            # Verify P0.5 prompt used
            used_p05, version = verify_p05_prompt(profile_data)

            if used_p05:
                print(f"✅ P0.5 prompt verified (version {version})")
            elif used_p05 is False:
                print(f"⚠️  OLD prompt used (version {version}) - NOT P0.5!")
            else:
                print(f"⚠️  Could not verify prompt version")

            # Save to file
            output_path = OUTPUT_DIR / profile_spec["output_file"]
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Generated in {generation_time:.1f}s")
            print(f"📁 Saved to: {output_path}")

            results.append({
                "profile": profile_spec["position"],
                "status": "success",
                "time": generation_time,
                "output_file": str(output_path),
                "p05_verified": used_p05,
                "prompt_version": version
            })

        except Exception as e:
            print(f"❌ Generation failed: {e}")
            results.append({
                "profile": profile_spec["position"],
                "status": "failed",
                "error": str(e)
            })

    # Summary
    print(f"\n{'='*80}")
    print("GENERATION SUMMARY")
    print(f"{'='*80}\n")

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]

    print(f"✅ Successful: {len(successful)}/4")
    print(f"❌ Failed: {len(failed)}/4")

    if successful:
        print(f"\n📊 Generated profiles:")
        for r in successful:
            p05_status = "✅ v49" if r.get("p05_verified") else f"⚠️  v{r.get('prompt_version', '?')}"
            print(f"  - {r['profile']:<30} {r['time']:>6.1f}s  {p05_status}")

    if failed:
        print(f"\n❌ Failed profiles:")
        for r in failed:
            print(f"  - {r['profile']}: {r.get('error', 'Unknown error')}")

    # Next steps
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}\n")
    print("1. Run validation:")
    print("   python scripts/validate_p0_profiles.py")
    print("\n2. Check for P0.2 enforcement (soft skills with methodologies)")
    print("3. Check for P0.4 enforcement (unique proficiency levels)")
    print("\n4. Expected improvements:")
    print("   - P0.2: 0% → 95%+ soft skills with methodologies")
    print("   - P0.4: 50% → 95%+ unique proficiency levels")
    print("   - Quality Score: 8.14 → 9.2+/10")

    # Save results
    results_file = OUTPUT_DIR / "p05_generation_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
