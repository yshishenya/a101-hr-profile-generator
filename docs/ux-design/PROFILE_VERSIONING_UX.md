# Profile Versioning: UX Design & Implementation

**Date**: 2025-10-26
**Status**: CRITICAL DESIGN DECISION
**Context**: Profiles can have multiple versions (edits, regenerations)

---

## 🎯 Problem Statement

### Scenarios where versions are created:

1. **Manual Edit** (Week 7 feature)
   - User edits profile content → New version created
   - Old version preserved in history

2. **Regeneration**
   - User clicks "Regenerate" → New version created with fresh AI generation
   - Old version preserved for comparison

3. **Multiple Generations by Different Users**
   - HR Manager generates v1
   - Department Head regenerates → v2
   - Executive requests regeneration → v3

### Key Questions:

1. **Which version to show by default?**
   - Latest? First? Best quality?

2. **How to indicate multiple versions exist?**
   - Badge? Dropdown? Timeline?

3. **How to compare versions?**
   - Side-by-side? Diff view? Sequential?

4. **How to switch between versions?**
   - Dropdown? Timeline slider? Version picker?

5. **Can users delete versions?**
   - Delete individual? Delete all? Rollback?

6. **How to track who created which version?**
   - Author? Timestamp? Reason?

---

## 👥 User Scenarios Analysis

### Scenario 1: "Проверка истории изменений"

**User**: Елена (HR Manager)

**Story**:
```
1. Елена открывает профиль "Аналитик данных"
2. Видит, что профиль был изменен 3 раза
3. Хочет понять:
   - Кто внес изменения?
   - Что изменилось?
   - Когда это произошло?
4. Хочет вернуться к предыдущей версии
```

**Pain Points**:
- ❌ Нет визуальной истории
- ❌ Непонятно, что изменилось между версиями
- ❌ Сложно сравнивать версии

---

### Scenario 2: "Выбор лучшей версии"

**User**: Сергей (Department Head)

**Story**:
```
1. Сергей сгенерировал профиль "ML Engineer"
2. Не понравился результат → Regenerate
3. Снова не понравился → Regenerate
4. Теперь есть 3 версии:
   - v1: Quality 75%, too generic
   - v2: Quality 85%, better details
   - v3: Quality 80%, good but missing key skills
5. Хочет выбрать v2 как "активную" версию
```

**Pain Points**:
- ❌ Нет способа пометить "лучшую" версию
- ❌ Сложно сравнить качество версий
- ❌ Все версии равнозначны

---

### Scenario 3: "Audit Trail"

**User**: Ирина (C-Level)

**Story**:
```
1. Ирина проверяет профиль "Директор по ИТ"
2. Видит, что профиль менялся 5 раз
3. Хочет понять:
   - Кто и когда вносил изменения?
   - Была ли ручная правка или regeneration?
   - Почему так много версий?
4. Нужен audit trail для compliance
```

**Pain Points**:
- ❌ Нет полной истории действий
- ❌ Не видно причины изменений
- ❌ Нет audit log

---

## 🎨 UX Design Options

### Option 1: Version Dropdown (Simple)

**Concept**: Simple dropdown in table + viewer

```
Table Row:
┌─────────────────────────────────────────────────────┐
│ ✅ Аналитик данных | Анализ данных | v3 (latest) ▾ │
│    Quality: 85%     | 2025-10-26   | [View] [Down] │
└─────────────────────────────────────────────────────┘

On click dropdown:
┌─────────────────────────────────┐
│ v3 (Latest) - 2025-10-26 ✓      │
│ v2 - 2025-10-25                 │
│ v1 (Original) - 2025-10-20      │
└─────────────────────────────────┘
```

**Pros**:
- ✅ Simple UI
- ✅ Familiar pattern
- ✅ Easy to implement

**Cons**:
- ❌ No comparison
- ❌ Limited metadata
- ❌ No visual timeline
- ❌ Can't see differences

---

### Option 2: Version Timeline (Visual) - RECOMMENDED

**Concept**: Visual timeline showing version history

```
Profile Viewer:
┌──────────────────────────────────────────────────────┐
│ Аналитик данных                                      │
├──────────────────────────────────────────────────────┤
│ 📅 Version History:                                  │
│                                                       │
│ ●────────●────────●────────●  [Timeline Slider]      │
│ v1       v2       v3       v4 (current)              │
│ Oct 20   Oct 22   Oct 25   Oct 26                    │
│                                                       │
│ Current: v4 (Latest) - Oct 26, 2025                  │
│ Created by: Иванов И.И. (Auto-generated)            │
│ Quality: 90% | Completeness: 95%                     │
│                                                       │
│ Changes from v3:                                     │
│ • Added 3 new responsibilities                       │
│ • Updated professional skills                        │
│ • Improved KPI metrics                               │
│                                                       │
│ [◀ Previous] [Compare Versions] [Next ▶]            │
└──────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Visual history
- ✅ Easy navigation
- ✅ Shows changes
- ✅ Clear current version

**Cons**:
- ❌ More complex UI
- ❌ Takes more space

---

### Option 3: Version Panel (Sidebar) - ADVANCED

**Concept**: Dedicated version panel with full metadata

```
Profile Viewer:
┌────────────────────┬────────────────────────────────┐
│ Version Panel      │ Profile Content                │
├────────────────────┤                                │
│ 📋 Versions (4)    │ Position: Аналитик данных      │
│                    │                                │
│ ● v4 CURRENT       │ Department: Анализ данных      │
│   Oct 26, 10:30    │                                │
│   Иванов И.        │ [Content tabs...]              │
│   Auto-regen       │                                │
│   Q: 90% C: 95%    │                                │
│   [View] [Set]     │                                │
│                    │                                │
│ ○ v3               │                                │
│   Oct 25, 14:20    │                                │
│   Петров С.        │                                │
│   Manual edit      │                                │
│   Q: 85% C: 90%    │                                │
│   [View] [Set]     │                                │
│                    │                                │
│ ○ v2               │                                │
│   Oct 22, 09:15    │                                │
│   Сидоров А.       │                                │
│   Regenerated      │                                │
│   Q: 88% C: 92%    │                                │
│   [View] [Set]     │                                │
│                    │                                │
│ ○ v1 ORIGINAL      │                                │
│   Oct 20, 16:45    │                                │
│   Иванов И.        │                                │
│   First generation │                                │
│   Q: 75% C: 80%    │                                │
│   [View] [Set]     │                                │
│                    │                                │
│ [Compare Selected] │                                │
└────────────────────┴────────────────────────────────┘
```

**Pros**:
- ✅ Full version metadata
- ✅ Easy comparison
- ✅ Clear version management
- ✅ Audit trail

**Cons**:
- ❌ Complex UI
- ❌ Takes screen space
- ❌ More development time

---

### Option 4: Hybrid Approach (BEST BALANCE)

**Concept**: Version badge in table + Timeline in modal

```
Table (Compact):
┌─────────────────────────────────────────────────────┐
│ ✅ Аналитик данных | Анализ данных | 📚 v4 (4 ver.) │
│    Quality: 90%     | 2025-10-26   | [View] [Down]  │
└─────────────────────────────────────────────────────┘

Modal (Detailed):
┌──────────────────────────────────────────────────────┐
│ Аналитик данных                        [X]           │
├──────────────────────────────────────────────────────┤
│ [Content] [Metadata] [📚 Versions (4)]               │
│                                                       │
│ When "Versions" tab clicked:                         │
│                                                       │
│ 📅 Timeline:                                         │
│ ●────────●────────●────────● (viewing v4)            │
│ v1       v2       v3       v4                        │
│                                                       │
│ Current Version: v4 (Latest)                         │
│ ┌──────────────────────────────────────────┐        │
│ │ Created: Oct 26, 2025 10:30 AM           │        │
│ │ Author: Иванов Иван (Auto-generated)     │        │
│ │ Type: Regeneration                        │        │
│ │ Quality: 90% | Completeness: 95%         │        │
│ │                                           │        │
│ │ Changes from v3:                          │        │
│ │ • +3 responsibilities                     │        │
│ │ • Updated skills section                  │        │
│ │ • Improved KPI metrics                    │        │
│ │                                           │        │
│ │ [Download] [Set as Active] [Compare]     │        │
│ └──────────────────────────────────────────┘        │
│                                                       │
│ Previous Versions:                                   │
│ ┌──────────────────────────────────────────┐        │
│ │ v3 - Oct 25, 14:20 - Петров (Edit)       │        │
│ │ Q: 85% C: 90%          [View] [Compare]  │        │
│ └──────────────────────────────────────────┘        │
│ ┌──────────────────────────────────────────┐        │
│ │ v2 - Oct 22, 09:15 - Сидоров (Regen)     │        │
│ │ Q: 88% C: 92%          [View] [Compare]  │        │
│ └──────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Compact in table (doesn't clutter)
- ✅ Detailed when needed (in modal)
- ✅ Good balance complexity/features
- ✅ Scalable UI

**Cons**:
- ❌ Requires modal interaction for details

---

## 📊 Comparison Matrix

| Feature | Simple Dropdown | Timeline | Sidebar | Hybrid ★ |
|---------|----------------|----------|---------|----------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Version Visibility** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Metadata Richness** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Comparison** | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Audit Trail** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Screen Space** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mobile Friendly** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Dev Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

**TOTAL SCORE**:
- Simple Dropdown: 28/40
- Timeline: 32/40
- Sidebar: 33/40
- **Hybrid: 37/40** ⭐ **WINNER**

---

## 🎯 RECOMMENDATION: Hybrid Approach

### Implementation Details

#### 1. Version Badge in Table

```vue
<!-- In PositionsTable row -->
<template #item.version="{ item }">
  <v-chip
    v-if="item.version_count > 1"
    size="small"
    prepend-icon="mdi-layers"
  >
    v{{ item.current_version }} ({{ item.version_count }})
  </v-chip>
  <span v-else class="text-caption text-medium-emphasis">
    v1
  </span>
</template>
```

#### 2. Versions Tab in Modal

```vue
<!-- ProfileViewerModal.vue -->
<v-tabs v-model="activeTab">
  <v-tab value="content">Content</v-tab>
  <v-tab value="metadata">Metadata</v-tab>
  <v-tab value="versions">
    Versions
    <v-badge v-if="versionCount > 1" :content="versionCount" inline />
  </v-tab>
</v-tabs>

<v-window-item value="versions">
  <ProfileVersionsPanel
    :profile-id="profile.profile_id"
    :current-version="profile.version"
  />
</v-window-item>
```

#### 3. Version Timeline Component

```vue
<!-- ProfileVersionsPanel.vue -->
<template>
  <v-card-text>
    <!-- Timeline Visualization -->
    <div class="mb-6">
      <div class="text-subtitle-2 mb-2">Version Timeline</div>
      <v-timeline density="compact" side="end">
        <v-timeline-item
          v-for="version in versions"
          :key="version.version_number"
          :dot-color="version.version_number === currentVersion ? 'primary' : 'grey'"
          size="small"
        >
          <template #opposite>
            <div class="text-caption">{{ formatDate(version.created_at) }}</div>
          </template>

          <v-card
            :color="version.version_number === currentVersion ? 'surface-variant' : undefined"
            elevation="0"
          >
            <v-card-title class="text-body-1">
              <v-chip
                v-if="version.version_number === currentVersion"
                size="x-small"
                color="primary"
              >
                CURRENT
              </v-chip>
              Version {{ version.version_number }}
              <v-chip
                v-if="version.version_number === 1"
                size="x-small"
                class="ml-2"
              >
                ORIGINAL
              </v-chip>
            </v-card-title>

            <v-card-text>
              <div class="d-flex flex-column ga-1">
                <div>
                  <v-icon size="small">mdi-account</v-icon>
                  {{ version.created_by }}
                </div>
                <div>
                  <v-icon size="small">mdi-tag</v-icon>
                  {{ getVersionTypeLabel(version.type) }}
                </div>
                <div>
                  <v-icon size="small">mdi-chart-line</v-icon>
                  Quality: {{ version.quality_score }}%
                  | Completeness: {{ version.completeness_score }}%
                </div>

                <!-- Changes Summary (if available) -->
                <div v-if="version.changes_summary" class="mt-2">
                  <div class="text-caption font-weight-bold">Changes:</div>
                  <ul class="text-caption">
                    <li v-for="change in version.changes_summary" :key="change">
                      {{ change }}
                    </li>
                  </ul>
                </div>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-btn
                v-if="version.version_number !== currentVersion"
                size="small"
                variant="text"
                @click="viewVersion(version)"
              >
                View
              </v-btn>
              <v-btn
                v-if="version.version_number !== currentVersion"
                size="small"
                variant="text"
                color="primary"
                @click="setAsActive(version)"
              >
                Set as Active
              </v-btn>
              <v-btn
                size="small"
                variant="text"
                @click="compareWithCurrent(version)"
              >
                Compare
              </v-btn>
              <v-btn
                size="small"
                variant="text"
                :href="getDownloadUrl(version)"
              >
                Download
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-timeline-item>
      </v-timeline>
    </div>
  </v-card-text>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface ProfileVersion {
  version_number: number
  created_at: string
  created_by: string
  type: 'generated' | 'regenerated' | 'edited'
  quality_score: number
  completeness_score: number
  changes_summary?: string[]
  content_hash?: string
}

interface Props {
  profileId: string
  currentVersion: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'version-changed': [version: number]
}>()

const versions = ref<ProfileVersion[]>([])
const loading = ref(false)

onMounted(async () => {
  await loadVersions()
})

async function loadVersions() {
  loading.value = true
  try {
    // API call to get version history
    const response = await fetch(`/api/profiles/${props.profileId}/versions`)
    versions.value = await response.json()
  } finally {
    loading.value = false
  }
}

function getVersionTypeLabel(type: string): string {
  const labels = {
    generated: 'First Generation',
    regenerated: 'Regenerated',
    edited: 'Manual Edit'
  }
  return labels[type] || type
}

function viewVersion(version: ProfileVersion) {
  // Open version in new modal or switch content
  emit('version-changed', version.version_number)
}

function setAsActive(version: ProfileVersion) {
  // Confirm and set as active version
  if (confirm(`Set version ${version.version_number} as active?`)) {
    // API call to update active version
  }
}

function compareWithCurrent(version: ProfileVersion) {
  // Open comparison view
}

function getDownloadUrl(version: ProfileVersion): string {
  return `/api/profiles/${props.profileId}/download/json?version=${version.version_number}`
}

function formatDate(date: string): string {
  return new Date(date).toLocaleString('ru-RU', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
```

---

## 🗄️ Backend Data Model

### Database Schema

```sql
-- Existing profiles table
CREATE TABLE profiles (
  profile_id INTEGER PRIMARY KEY,
  position_id TEXT NOT NULL,
  current_version INTEGER DEFAULT 1,
  -- ... other fields
);

-- NEW: Profile versions table
CREATE TABLE profile_versions (
  version_id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_id INTEGER NOT NULL,
  version_number INTEGER NOT NULL,

  -- Version metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by_user_id INTEGER NOT NULL,
  created_by_username TEXT NOT NULL,

  -- Version type
  version_type TEXT NOT NULL CHECK(version_type IN ('generated', 'regenerated', 'edited')),

  -- Content
  profile_content TEXT NOT NULL,  -- JSON

  -- Quality metrics
  validation_score REAL,
  completeness_score REAL,

  -- Change tracking
  changes_summary TEXT,  -- JSON array of changes
  content_hash TEXT,     -- For deduplication

  -- Metadata
  generation_metadata TEXT,  -- JSON

  FOREIGN KEY (profile_id) REFERENCES profiles(profile_id),
  UNIQUE(profile_id, version_number)
);

CREATE INDEX idx_profile_versions_profile ON profile_versions(profile_id);
CREATE INDEX idx_profile_versions_created ON profile_versions(created_at DESC);
```

### API Endpoints

```python
# GET /api/profiles/{id}/versions
# Returns list of all versions for a profile
@router.get("/{profile_id}/versions")
async def get_profile_versions(
    profile_id: str,
    user: dict = Depends(get_current_user)
) -> List[ProfileVersionResponse]:
    """Get all versions of a profile."""
    versions = await db.get_profile_versions(profile_id)
    return [
        ProfileVersionResponse(
            version_number=v.version_number,
            created_at=v.created_at,
            created_by=v.created_by_username,
            type=v.version_type,
            quality_score=v.validation_score,
            completeness_score=v.completeness_score,
            changes_summary=json.loads(v.changes_summary) if v.changes_summary else None
        )
        for v in versions
    ]

# GET /api/profiles/{id}/versions/{version_number}
# Get specific version content
@router.get("/{profile_id}/versions/{version_number}")
async def get_profile_version(
    profile_id: str,
    version_number: int,
    user: dict = Depends(get_current_user)
) -> ProfileDetailResponse:
    """Get specific version of a profile."""
    version = await db.get_profile_version(profile_id, version_number)
    return ProfileDetailResponse(
        profile_id=profile_id,
        version=version_number,
        profile=json.loads(version.profile_content),
        metadata=json.loads(version.generation_metadata),
        created_at=version.created_at,
        created_by_username=version.created_by_username
    )

# PUT /api/profiles/{id}/versions/{version_number}/set-active
# Set specific version as active
@router.put("/{profile_id}/versions/{version_number}/set-active")
async def set_active_version(
    profile_id: str,
    version_number: int,
    user: dict = Depends(get_current_user)
):
    """Set a specific version as the active version."""
    await db.update_profile_current_version(profile_id, version_number)
    return {"success": True, "message": f"Version {version_number} is now active"}

# GET /api/profiles/{id}/versions/compare?v1=1&v2=3
# Compare two versions
@router.get("/{profile_id}/versions/compare")
async def compare_versions(
    profile_id: str,
    v1: int,
    v2: int,
    user: dict = Depends(get_current_user)
):
    """Compare two versions of a profile."""
    version1 = await db.get_profile_version(profile_id, v1)
    version2 = await db.get_profile_version(profile_id, v2)

    diff = compute_profile_diff(
        json.loads(version1.profile_content),
        json.loads(version2.profile_content)
    )

    return ComparisonResponse(
        v1=v1,
        v2=v2,
        differences=diff
    )
```

---

## 🎨 Version Creation Logic

### When Regenerating

```python
async def regenerate_profile(
    profile_id: str,
    user: dict,
    reason: Optional[str] = None
) -> ProfileVersion:
    """
    Regenerate profile and create new version.
    """
    # 1. Get current profile
    current_profile = await db.get_profile(profile_id)

    # 2. Generate new content
    new_content = await llm_service.generate_profile(
        position=current_profile.position,
        department=current_profile.department
    )

    # 3. Calculate changes
    changes = compare_profiles(
        old=json.loads(current_profile.content),
        new=new_content
    )

    # 4. Create new version
    new_version_number = current_profile.current_version + 1

    version = await db.create_profile_version(
        profile_id=profile_id,
        version_number=new_version_number,
        version_type='regenerated',
        profile_content=json.dumps(new_content),
        created_by_user_id=user['id'],
        created_by_username=user['username'],
        changes_summary=json.dumps(changes),
        validation_score=new_content.get('validation_score'),
        completeness_score=new_content.get('completeness_score'),
        generation_metadata=json.dumps({
            'reason': reason,
            'model': 'gemini-2.5-flash',
            'temperature': 0.7,
            'tokens': {...}
        })
    )

    # 5. Update current version pointer
    await db.update_profile_current_version(profile_id, new_version_number)

    return version
```

### When Editing (Week 7)

```python
async def edit_profile(
    profile_id: str,
    updates: dict,
    user: dict
) -> ProfileVersion:
    """
    Edit profile content and create new version.
    """
    # 1. Get current version
    current_version = await db.get_current_profile_version(profile_id)
    current_content = json.loads(current_version.profile_content)

    # 2. Apply edits
    updated_content = apply_edits(current_content, updates)

    # 3. Track changes
    changes = compute_edit_changes(current_content, updated_content)

    # 4. Create new version
    new_version_number = current_version.version_number + 1

    version = await db.create_profile_version(
        profile_id=profile_id,
        version_number=new_version_number,
        version_type='edited',
        profile_content=json.dumps(updated_content),
        created_by_user_id=user['id'],
        created_by_username=user['username'],
        changes_summary=json.dumps(changes),
        validation_score=validate_profile(updated_content),
        completeness_score=calculate_completeness(updated_content),
        generation_metadata=json.dumps({
            'edit_type': 'manual',
            'fields_changed': list(updates.keys())
        })
    )

    # 5. Update current version
    await db.update_profile_current_version(profile_id, new_version_number)

    return version
```

---

## 🔍 Version Comparison UI

### Comparison Modal

```vue
<!-- VersionComparisonModal.vue -->
<template>
  <v-dialog v-model="show" max-width="1400" scrollable>
    <v-card>
      <v-card-title>
        Compare Versions
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" @click="show = false" />
      </v-card-title>

      <v-card-subtitle>
        Version {{ v1.version_number }} vs Version {{ v2.version_number }}
      </v-card-subtitle>

      <v-divider />

      <v-card-text>
        <v-row>
          <!-- Left: Version 1 -->
          <v-col cols="6">
            <v-card color="surface-variant">
              <v-card-title>
                Version {{ v1.version_number }}
                <v-chip size="small" class="ml-2">{{ v1.type }}</v-chip>
              </v-card-title>
              <v-card-subtitle>
                {{ formatDate(v1.created_at) }} by {{ v1.created_by }}
              </v-card-subtitle>
              <v-card-text>
                <ProfileContent :profile="v1.content" :highlight="differences.removed" />
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Right: Version 2 -->
          <v-col cols="6">
            <v-card color="surface-variant">
              <v-card-title>
                Version {{ v2.version_number }}
                <v-chip size="small" class="ml-2">{{ v2.type }}</v-chip>
              </v-card-title>
              <v-card-subtitle>
                {{ formatDate(v2.created_at) }} by {{ v2.created_by }}
              </v-card-subtitle>
              <v-card-text>
                <ProfileContent :profile="v2.content" :highlight="differences.added" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Differences Summary -->
        <v-card class="mt-4" color="info" variant="tonal">
          <v-card-title>Changes Summary</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="(change, index) in differences.summary"
                :key="index"
                :prepend-icon="getChangeIcon(change.type)"
              >
                <v-list-item-title>{{ change.description }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-card-text>

      <v-card-actions>
        <v-btn @click="show = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
```

---

## ✅ Implementation Checklist

### Phase 1: Backend (Days 1-2)
- [ ] Create `profile_versions` table
- [ ] Add `current_version` field to `profiles` table
- [ ] Implement version creation logic
- [ ] Add version history API endpoints
- [ ] Add version comparison API endpoint
- [ ] Migration script for existing profiles

### Phase 2: Frontend Components (Days 3-4)
- [ ] Update `UnifiedPosition` type with version info
- [ ] Add version badge to `PositionsTable`
- [ ] Create `ProfileVersionsPanel` component
- [ ] Create `ProfileVersionTimeline` component
- [ ] Add "Versions" tab to `ProfileViewerModal`

### Phase 3: Version Actions (Day 5)
- [ ] Implement "Set as Active" action
- [ ] Implement "Compare" action
- [ ] Implement version switching
- [ ] Update download to support version parameter

### Phase 4: Testing (Day 6)
- [ ] Test version creation on regeneration
- [ ] Test version creation on edit
- [ ] Test version switching
- [ ] Test comparison UI
- [ ] Test version download

---

## 🎯 Decision Summary

### ✅ APPROVED DESIGN: Hybrid Approach

**Implementation**:
1. **Table**: Version badge `v4 (4 versions)` - compact
2. **Modal**: Full version timeline with metadata
3. **Timeline**: Visual history with quality scores
4. **Actions**: View, Set as Active, Compare, Download
5. **Backend**: New `profile_versions` table

**Benefits**:
- ✅ Clean table UI (not cluttered)
- ✅ Rich version details when needed
- ✅ Full audit trail
- ✅ Easy comparison
- ✅ Flexible version management

**Timeline**: +6 days (included in Week 7 inline editing feature)

---

**Next**: Implement unified profiles interface with version support
