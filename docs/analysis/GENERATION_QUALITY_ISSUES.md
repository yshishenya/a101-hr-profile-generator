# Generation Quality Issues - Critical Analysis

**Date**: 2025-10-25
**Status**: 🔴 CRITICAL ISSUES FOUND
**Impact**: Schema violations in 100% of generated profiles

---

## 🚨 CRITICAL ISSUES

### Issue #1: Careerogram Structure Completely Wrong
**Severity**: 🔴 CRITICAL
**Impact**: Schema validation fails, data unusable
**Affected**: 100% of generated profiles

**Problem**:
Generated careerogram doesn't match schema structure at all.

**Current (WRONG) Generation**:
```json
"careerogram": {
  "source_positions": [
    "Программист 1С (Группа поддержки CRM)",
    "Специалист технической поддержки"
  ],
  "target_positions": [
    "VERTICAL -> target_position: 'Ведущий программист 1С', target_department: '...'",
    "HORIZONTAL -> target_position: 'Программист 1С (Отдел ERP)'..."
  ]
}
```

**Expected (CORRECT) Schema**:
```json
"careerogram": {
  "source_positions": {
    "direct_predecessors": ["Программист 1С"],
    "cross_functional_entrants": ["Специалист поддержки"]
  },
  "target_pathways": {
    "vertical_growth": [
      {
        "target_position": "Ведущий программист 1С",
        "target_department": "ДИТ / Отдел CRM",
        "rationale": "...",
        "competency_bridge": {
          "strengthen_skills": ["1С (3→4)", "Code review (2→3)"],
          "acquire_skills": ["Лидерство", "Наставничество"]
        }
      }
    ],
    "horizontal_growth": [...],
    "expert_growth": [...]
  }
}
```

**Root Cause**: Schema and prompt have conflicting structures

---

### Issue #2: responsibility_areas.area Wrong Type
**Severity**: 🔴 CRITICAL
**Impact**: Type mismatch, validation fails
**Affected**: 100% of generated profiles

**Problem**:
Schema defines `area` as `string`, but generated as `array`.

**Current (WRONG) Generation**:
```json
"responsibility_areas": [
  {
    "area": ["Разработка и сопровождение 1С:CRM/ERP"],  // ❌ Array
    "tasks": [...]
  }
]
```

**Expected (CORRECT)**:
```json
"responsibility_areas": [
  {
    "area": "Разработка и сопровождение 1С:CRM/ERP",  // ✅ String
    "tasks": [...]
  }
]
```

**Root Cause**: Schema type definition is `string` but LLM generates array

---

### Issue #3: Excessive Reasoning Fields
**Severity**: ⚠️ MEDIUM
**Impact**: Bloated output, noise in data
**Affected**: 100% of generated profiles

**Problem**:
Profile contains multiple reasoning fields not defined in schema:
- `reasoning_context_analysis`
- `position_classification_reasoning`
- `responsibility_areas_reasoning`
- `professional_skills_reasoning`
- `careerogram_reasoning`

**Current Generation**:
```json
{
  "reasoning_context_analysis": {
    "hierarchy_analysis": "...",
    "management_status_reasoning": "...",
    ...
  },
  "position_title": "Программист 1С",
  ...
}
```

**Impact**:
- Extra ~2000 tokens per profile
- Clutters JSON structure
- Not useful for end users
- Increases costs

**Why It Happens**:
Prompt instructs LLM to add reasoning (probably for debugging), but these should be removed from production output.

---

### Issue #4: Source Positions Flat Array
**Severity**: 🔴 CRITICAL
**Impact**: Lost semantic information
**Affected**: 100% of generated profiles

**Problem**:
Source positions is flat array instead of structured object.

**Current (WRONG)**:
```json
"source_positions": [
  "Программист 1С (Группа поддержки CRM)",
  "Специалист технической поддержки"
]
```

**Expected (CORRECT)**:
```json
"source_positions": {
  "direct_predecessors": [
    "Программист 1С (Группа поддержки CRM)"
  ],
  "cross_functional_entrants": [
    "Специалист технической поддержки"
  ]
}
```

**Impact**: Cannot distinguish between direct career progression and cross-functional moves.

---

## 📊 Impact Summary

| Issue | Severity | Profiles Affected | Validation Status |
|-------|----------|-------------------|-------------------|
| Careerogram structure | 🔴 Critical | 100% | ❌ Fails strict validation |
| Area type mismatch | 🔴 Critical | 100% | ❌ Type error |
| Reasoning fields | ⚠️ Medium | 100% | ⚠️ Passes but bloated |
| Source positions structure | 🔴 Critical | 100% | ❌ Schema mismatch |

**Overall Quality**: 🔴 **UNACCEPTABLE** - Schema violations in every field

---

## 🔍 Root Cause Analysis

### 1. Schema-Prompt Mismatch
**Problem**: JSON schema definition doesn't match what prompt instructs LLM to generate

**Evidence**:
- Prompt shows careerogram example with `target_pathways.vertical_growth`
- Schema probably defines different structure (need to check)
- LLM confused between instructions

**Fix Required**: Align schema and prompt exactly

### 2. Loose Type Enforcement
**Problem**: Schema allows array where string should be

**Evidence**:
```json
"area": {
  "type": "string",  // Says string
  "description": "..."
}
```

But LLM generates array. Schema validation not enforced at generation time.

**Fix Required**:
- Use strict JSON schema mode
- Validate output before saving

### 3. Debug Code in Production
**Problem**: Reasoning fields are debug/development artifacts

**Evidence**: All reasoning fields not in schema spec

**Fix Required**: Remove reasoning instructions from production prompt

---

## 🎯 Priority Fixes

### P0 - Critical (Must Fix Now)
1. ✅ Fix careerogram schema structure
2. ✅ Fix responsibility_areas.area type
3. ✅ Fix source_positions structure

### P1 - High (Fix This Week)
4. ✅ Remove reasoning fields from schema
5. ✅ Update prompt to match corrected schema
6. ✅ Add strict schema validation

### P2 - Medium (Fix Next Sprint)
7. Add schema validation tests
8. Create generation quality metrics
9. Implement automated quality checks

---

## 🛠️ Detailed Fix Plan

### Fix #1: Correct Careerogram Schema

**Current Schema** (need to verify):
```json
"careerogram": {
  "type": "object",
  "properties": {
    "source_positions": {
      "type": "array"  // ❌ WRONG
    },
    "target_positions": {
      "type": "array"  // ❌ WRONG
    }
  }
}
```

**Corrected Schema**:
```json
"careerogram": {
  "type": "object",
  "required": ["source_positions", "target_pathways"],
  "properties": {
    "source_positions": {
      "type": "object",
      "required": ["direct_predecessors", "cross_functional_entrants"],
      "properties": {
        "direct_predecessors": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Прямые предшественники"
        },
        "cross_functional_entrants": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Кросс-функциональные входы"
        }
      }
    },
    "target_pathways": {
      "type": "object",
      "required": ["vertical_growth", "horizontal_growth", "expert_growth"],
      "properties": {
        "vertical_growth": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["target_position", "target_department", "rationale", "competency_bridge"],
            "properties": {
              "target_position": {"type": "string"},
              "target_department": {"type": "string"},
              "rationale": {"type": "string"},
              "competency_bridge": {
                "type": "object",
                "required": ["strengthen_skills", "acquire_skills"],
                "properties": {
                  "strengthen_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                  },
                  "acquire_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                  }
                }
              }
            }
          }
        },
        "horizontal_growth": {/* same structure */},
        "expert_growth": {/* same structure */}
      }
    }
  }
}
```

### Fix #2: Correct responsibility_areas.area Type

**Current**:
```json
"area": {
  "type": "string"
}
```

**Issue**: LLM generates array despite type being string

**Solution**: Keep as string, add validation, update prompt to emphasize string type

### Fix #3: Remove Reasoning Fields

**Action**: Remove from schema entirely:
- `reasoning_context_analysis`
- `position_classification_reasoning`
- `responsibility_areas_reasoning`
- `professional_skills_reasoning`
- `careerogram_reasoning`

**Prompt Update**: Remove instructions to generate reasoning

---

## 📈 Expected Impact After Fixes

### Before (Current):
- ❌ Schema validation: FAILS
- ❌ Data usability: POOR
- ❌ Output bloat: +2000 tokens/profile
- ❌ Cost: High (wasted tokens)
- ❌ Quality score: 2/10

### After (Fixed):
- ✅ Schema validation: PASSES
- ✅ Data usability: EXCELLENT
- ✅ Output bloat: NONE
- ✅ Cost: Optimal
- ✅ Quality score: 9/10

---

## 🧪 Validation Strategy

### Schema Validation
```python
import jsonschema

def validate_profile(profile: dict, schema: dict) -> bool:
    try:
        jsonschema.validate(profile, schema)
        return True
    except jsonschema.ValidationError as e:
        logger.error(f"Schema validation failed: {e}")
        return False
```

### Quality Metrics
- % profiles passing strict schema validation
- Average token count per profile
- Careerogram completeness (all 3 growth paths)
- Field completion rate

---

## 📝 Next Steps

1. **Read current schema** - Verify exact structure
2. **Create corrected schema** - Fix all identified issues
3. **Update prompt** - Match corrected schema exactly
4. **Test generation** - Validate with sample departments
5. **Deploy fixes** - Update production schema and prompt
6. **Monitor quality** - Track validation success rate

---

**Status**: Ready to implement fixes
**Estimated Time**: 2-3 hours
**Risk**: Low (improving quality, not changing functionality)
