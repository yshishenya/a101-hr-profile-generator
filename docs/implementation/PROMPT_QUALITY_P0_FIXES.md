# Phase P0: Critical Prompt Quality Fixes

**Date**: 2025-10-26
**Status**: Ready for Implementation
**Priority**: P0 (CRITICAL)
**Effort**: 2-3 hours
**Expected Impact**: Quality 5/10 ’ 8.5/10

---

## Context

Based on analysis in `docs/analysis/PROMPT_QUALITY_FIXES_PROPOSAL.md`:

**Current State**:
-  Schema fixed (careerogram structure, area type)
-  Reasoning fields restored (6 Chain-of-Thought fields)
- L Prompt missing CoT instructions
- L Prompt has wrong careerogram example
- L No skill category naming guidance
- L No proficiency_level mapping rules

**Root Cause**: Prompt doesn't teach LLM HOW to use reasoning fields effectively.

---

## P0.1: Add Chain-of-Thought Instructions (45 min)

**File**: `templates/prompts/production/prompt.txt`
**Location**: After ")  " section (around line 30)

**What to Add**:

```markdown
---

## ™ CHAIN-OF-THOUGHT: /",/ !",!", +(/

Schema A>45@68B reasoning ?>;O - MB> 8=AB@C<5=B 4;O AB@C:BC@8@>20==>3> <KH;5=8O.

**/",+  /:**

### 1. reasoning_context_analysis (=0;87 :>=B5:AB0 - 4 :><?>=5=B0)

**a) hierarchy_analysis**:
@>0=0;878@C9 85@0@E8G5A:>5 ?>;>65=85:
- #@>25=L: {{hierarchy_level}} (1=B>?, 2=A@54=89, 3=A?5F80;8AB)
- CBL: {{full_hierarchy_path}}
- >?@>A: 0A:>;L:> 2KA>:> 2 AB@C:BC@5?

@8<5@: "#@>25=L 3 (A?5F80;8AB). CBL:  ’ 5?0@B0<5=B ’ B45; ’ @C??0. 4 C@>2=O 4> CEO."

**b) management_status_reasoning**:
>38:0 >?@545;5=8O subordinates_count:
- A;8 2 =0720=88 " C:>2>48B5;L/0G0;L=8:/8@5:B>@" ’ A:>@55 2A53> 5ABL
- A;8 "!?5F80;8AB/@>3@0<<8AB" ’ A:>@55 2A53> =5B
- A;8 2 AB@C:BC@5 =5B ?>4G8=5==KE ’ null

**c) functional_role_identification**:
$>@<0B: [59AB285] 4;O [&5;L]
- IT: " 07@01>B:0 8 ?>445@6:0" 4;O "=D>@<0F8>==K5 A8AB5<K"
- HR: ">41>@ 8 040?B0F8O" 4;O "'5;>25G5A:85 @5AC@AK"

**d) data_completeness_assessment**:
- high: >;=0O 85@0@E8O + KPI + 4>;6=>AB=K5 8=AB@C:F88
- medium: '0AB8G=K5 40==K5 (AB@C:BC@0 5ABL, KPI =5B)
- low: 8=8<C< (B>;L:> =0720=85)

### 2. professional_skills_reasoning (8-H03>2K9 ?@>F5AA)

**(03 1**: 7 responsibility_areas 872;5:8 >A=>2=K5 459AB28O
**(03 2**: @C??8@C9 459AB28O ?> :0B53>@8O< (3-7 :0B53>@89)
**(03 3**: ;O :064>9 :0B53>@88 >?@545;8 4-8 :>=:@5B=KE =02K:>2
**(03 4**: F5=8 C@>25=L 2;045=8O (1-4) =0 >A=>25 {{hierarchy_level}}
**(03 5**: !>?>AB02L C@>25=L A >?8A0=85< (AB@>30O B01;8F0!)
**(03 6**: >102L ?@8<5G0=8O 345 =5>1E>48<>
**(03 7**: @>25@L ?>;=>BC - 2A5 >1;0AB8 >B25BAB25==>AB8 ?>:@KBK?
**(03 8**: $8=0;878@C9 A?8A>:

### 3. careerogram_reasoning

**source_positions**:
- direct_predecessors: "0 65 25@B8:0;L, C@>25=L =865
- cross_functional_entrants: !<56=K5 DC=:F88, ?>E>685 =02K:8

**target_pathways**:
- vertical_growth: 25@E ?> 85@0@E88 (C?@02;5=85)
- horizontal_growth: !<56=K5 DC=:F88 (B>B 65 C@>25=L)
- expert_growth: #3;C1;5=85 M:A?5@B87K (157 C?@02;5=8O)

### 4. performance_metrics_reasoning

** //  /  KPI**:
1. @>G8B09 {{kpi_content}}
2. ;O :064>3> KPI A>7409 <5B@8:C
3. 0?8H8 A2O7L KPI ’ Metric

---
```

**Impact**: LLM understands HOW to fill reasoning fields ’ structured thinking ’ better quality

---

## P0.2: Fix Careerogram Example (15 min)

**File**: `templates/prompts/production/prompt.txt`
**Location**: Lines 37-61 (careerogram section)

**Current (WRONG)**:
```markdown
*   **[   4;O >4=>3> M;5<5=B0 2 `vertical_growth`]:**
    {
      "target_position": " C:>2>48B5;L 3@C??K",
      ...
    }
```

**Replace With (CORRECT)**:
```markdown
*   **`careerogram`:** 0@L5@=K5 B@05:B>@88.

    **!" #"#  (AB@>3> ?> AE5<5)**:
    ```json
    {
      "source_positions": {
        "direct_predecessors": [";04H89 ?@>3@0<<8AB 1!", "@>3@0<<8AB 1! 2 :0B53>@88"],
        "cross_functional_entrants": ["!8AB5<=K9 04<8=8AB@0B>@", "87=5A-0=0;8B8: CRM"]
      },
      "target_pathways": {
        "vertical_growth": [{
          "position": "54CI89 ?@>3@0<<8AB 1!",
          "department": "{{full_hierarchy_path}}/@C??0 @07@01>B:8 1!",
          "rationale": "AB5AB25==K9 @>AB A C3;C1;5=85< M:A?5@B87K",
          "competency_bridge": {
            "strengthen_skills": ["@E8B5:BC@0 1! (2’3)", ">4-@52LN (1’2)"],
            "acquire_skills": ["0AB02=8G5AB2>", "@>5:B8@>20=85 <>4C;59"]
          }
        }],
        "horizontal_growth": [{
          "position": "@E8B5:B>@ 8=D>@<0F8>==KE A8AB5<",
          "department": " '00101'/"/B45; @07@01>B:8/@C??0 0@E8B5:BC@K",
          "rationale": "5@5E>4 : ?@>5:B8@>20=8N C@>2=O ?@54?@8OB8O",
          "competency_bridge": {
            "strengthen_skills": ["!8AB5<=>5 <KH;5=85 (2’4)"],
            "acquire_skills": ["Enterprise 0@E8B5:BC@0", "=B53@0F8>==K5 ?0BB5@=K"]
          }
        }],
        "expert_growth": [{
          "position": ";02=K9 A?5F80;8AB ?> 1!",
          "department": "{{full_hierarchy_path}}",
          "rationale": "-:A?5@B=K9 B@5: 157 C?@02;5=8O",
          "competency_bridge": {
            "strengthen_skills": ["1! ;0BD>@<0 (3’4)", "?B8<870F8O (3’4)"],
            "acquire_skills": ["5B>48G5A:0O @01>B0", ">=AC;LB8@>20=85"]
          }
        }]
      }
    }
    ```

    ** **:
    - A?>;L7C9 ", ACI5AB2CNI85 4>;6=>AB8 87 {{org_structure}}
    - rationale - :@0B:>5 (1-2 ?@54;>65=8O) >1>A=>20=85
    - competency_bridge - :>=:@5B=K5 =02K:8 4;O ?5@5E>40
```

**Impact**: Correct structure ’ schema validation passes ’ careerogram usable

---

## P0.3: Add Skill Category Naming Guide (15 min)

**File**: `templates/prompts/production/prompt.txt`
**Location**: In professional_skills section (around line 33)

**Add Before Existing Text**:
```markdown
*   **`professional_skills`:** @>D5AA8>=0;L=K5 =02K:8 ?> :0B53>@8O<.

    **NAMING CONVENTION 4;O skill_category**:

      ,+ $ ": "=0=8O 8 C<5=8O 2 >1;0AB8 [:>=:@5B=0O >1;0ABL]"

    **@8<5@K**:
    - "=0=8O 8 C<5=8O 2 >1;0AB8 @07@01>B:8 =0 1!"
    - "=0=8O 8 C<5=8O 2 >1;0AB8 0@E8B5:BC@=>3> ?@>5:B8@>20=8O"
    - "=0=8O 8 C<5=8O 2 >1;0AB8 C?@02;5=8O ?@>5:B0<8"
    - "=0=8O 8 C<5=8O 2 >1;0AB8 @01>BK A 1070<8 40==KE"
    - "=0=8O 8 C<5=8O 2 >1;0AB8 8=B53@0F89 8 API"
    - "=0=8O 8 C<5=8O 2 >1;0AB8 :><<C=8:0F88 8 2708<>459AB28O"

    L  !,#:
    - 0?A: "!" ",+/ &!!+"
    - !;MH8: "#?@02;5=85/>>@48=0F8O"
    - 5?>=OB=K5 011@5280BC@K

    **>;8G5AB2>**: 3-7 :0B53>@89 (7028A8B >B A;>6=>AB8 4>;6=>AB8)
    **02K:>2 2 :0B53>@88**: 4-8 =02K:>2
```

**Impact**: Professional, consistent category naming ’ no more "!" ",+/ &!!+"

---

## P0.4: Add proficiency_level Mapping Table (10 min)

**File**: `templates/prompts/production/prompt.txt`
**Location**: Inside professional_skills section (after category naming)

**Add**:
```markdown
    **!"  !""!" proficiency_level ” proficiency_description**:

    | #@>25=L | ?8A0=85 ("'+ "!"!) |
    |---------|--------------------------|
    | 1 | "=0=85 >A=>2, >?KB ?@8<5=5=8O 7=0=89 8 =02K:>2 =0 ?@0:B8:5 =5>1O70B5;5=" |
    | 2 | "!CI5AB25==K5 7=0=8O 8 @53C;O@=K9 >?KB ?@8<5=5=8O 7=0=89 =0 ?@0:B8:5" |
    | 3 | "!CI5AB25==K5 7=0=8O 8 >?KB ?@8<5=5=8O 7=0=89 2 A8BC0F8OE ?>2KH5==>9 A;>6=>AB8, 2 B.G. 2 :@878A=KE A8BC0F8OE" |
    | 4 | "-:A?5@B=K5 7=0=8O, 4>;6=>ABL ?>4@07C<5205B ?5@540GC 7=0=89 8 >?KB0 4@C38<" |

       "'! :
    - A;8 proficiency_level = 2, B> description /", B5:AB 4;O C@>2=O 2
    -  35=5@8@C9 A2>8 >?8A0=8O
    -  A<5H8209 C@>2=8
```

**Impact**: 100% accurate level/description pairing ’ no confusion

---

## P0.5: Create Backup Before Changes (5 min)

**Commands**:
```bash
# Backup current prompt
cp templates/prompts/production/prompt.txt \
   templates/prompts/production/prompt.txt.before_p0_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -lh templates/prompts/production/prompt.txt*
```

**Impact**: Safety net for rollback

---

## Implementation Checklist

### Pre-Implementation
- [ ] Create backup of prompt.txt
- [ ] Read current prompt.txt fully
- [ ] Understand existing structure

### Implementation
- [ ] P0.1: Add Chain-of-Thought instructions (45 min)
- [ ] P0.2: Fix careerogram example (15 min)
- [ ] P0.3: Add skill category naming guide (15 min)
- [ ] P0.4: Add proficiency_level mapping table (10 min)

### Validation
- [ ] Read updated prompt.txt to verify changes
- [ ] Check that all sections are properly formatted
- [ ] Ensure Russian text is readable (UTF-8)
- [ ] Verify line numbers make sense

---

## Testing Plan

### Test 1: Specialist Position
**Input**:
- Position: "@>3@0<<8AB 1!"
- Department: "5?0@B0<5=B 8=D>@<0F8>==KE B5E=>;>389"

**Expected**:
- reasoning_context_analysis: Filled with 4 components
- professional_skills: Categories follow "=0=8O 8 C<5=8O 2 >1;0AB8 X" format
- careerogram: Nested object structure (not flat arrays)
- proficiency_level matches proficiency_description 100%

**Validation Script**:
```bash
python scripts/validate_profile.py test_profile_programmer.json
```

### Test 2: Manager Position
**Input**:
- Position: "0G0;L=8: >B45;0 @07@01>B:8"
- Department: "5?0@B0<5=B 8=D>@<0F8>==KE B5E=>;>389"

**Expected**:
- management_level: "middle_management"
- subordinates_count: number (not null)
- Leadership skills at level 3-4
- Reasoning explains management status

---

## Success Criteria

After P0 implementation:
-  100% schema validation pass rate
-  100% careerogram structure correctness
-  100% proficiency_level/description accuracy
-  100% skill category naming compliance
-  Reasoning quality: 8+/10 (manual review)
-  Overall quality: 5/10 ’ 8.5/10

---

## Rollback Plan

If tests fail:
```bash
# Restore backup
cp templates/prompts/production/prompt.txt.before_p0_YYYYMMDD_HHMMSS \
   templates/prompts/production/prompt.txt

# Verify restoration
diff templates/prompts/production/prompt.txt \
     templates/prompts/production/prompt.txt.before_p0_YYYYMMDD_HHMMSS
```

---

## Next Steps After P0

Once P0 is complete and validated:
1. Implement Phase P1 (KPI ’ Metrics strengthening)
2. Add few-shot examples
3. Implement validation checkpoints

See: `docs/analysis/PROMPT_QUALITY_FIXES_PROPOSAL.md` for full roadmap

---

**Status**: =Ë READY - Begin implementation
**Estimated Time**: 2-3 hours
**Risk**: LOW (have backups, reversible changes)
