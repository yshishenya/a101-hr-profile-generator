# API Quick Reference Card

**HR Profile Generator API - Cheat Sheet**

---

## Base Configuration

```typescript
const API_URL = 'http://localhost:8022';
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

---

## Authentication

### Login
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
→ { access_token, user_info }
```

### Get Current User
```bash
GET /api/auth/me
→ { id, username, full_name, ... }
```

### Logout
```bash
POST /api/auth/logout
→ { success: true }
```

---

## Dashboard

### Full Stats
```bash
GET /api/dashboard/stats
→ { summary, departments, positions, profiles, active_tasks }
```

### Minimal Stats
```bash
GET /api/dashboard/stats/minimal
→ { positions_count, profiles_count, completion_percentage }
```

### Activity Feed
```bash
GET /api/dashboard/stats/activity
→ { active_tasks, recent_profiles }
```

---

## Profile Generation (Async)

### 1. Start Generation
```bash
POST /api/generation/start
{
  "department": "Группа анализа данных",
  "position": "Аналитик данных",
  "employee_name": "Иванов Иван",
  "temperature": 0.1
}
→ { task_id, status: "queued", estimated_duration: 45 }
```

### 2. Check Status (Poll every 2s)
```bash
GET /api/generation/{task_id}/status
→ {
  task: { status, progress, current_step },
  result: null | { profile, metadata }
}
```

### 3. Get Result
```bash
GET /api/generation/{task_id}/result
→ { success, profile, metadata }
```

### 4. Cancel Task
```bash
DELETE /api/generation/{task_id}
→ { message: "Задача отменена" }
```

### 5. Active Tasks
```bash
GET /api/generation/tasks/active
→ [ { task_id, status, progress, ... } ]
```

---

## Profile Management

### List Profiles
```bash
GET /api/profiles/?page=1&limit=20&department=ДИТ&status=completed
→ {
  profiles: [ { profile_id, department, position, ... } ],
  pagination: { page, total, has_next, has_prev }
}
```

### Get Profile
```bash
GET /api/profiles/{profile_id}
→ { profile_id, profile: {...}, metadata: {...} }
```

### Update Profile
```bash
PUT /api/profiles/{profile_id}
{
  "employee_name": "Новое ФИО",
  "status": "completed"
}
→ { message: "Profile updated successfully" }
```

### Archive Profile
```bash
DELETE /api/profiles/{profile_id}
→ { message: "Profile archived", status: "archived" }
```

### Restore Profile
```bash
POST /api/profiles/{profile_id}/restore
→ { message: "Profile restored", status: "completed" }
```

### Download Files
```bash
GET /api/profiles/{profile_id}/download/json   # JSON
GET /api/profiles/{profile_id}/download/md     # Markdown
GET /api/profiles/{profile_id}/download/docx   # Word
→ File download
```

---

## Organization Catalog

### Get All Search Items (567 units)
```bash
GET /api/organization/search-items
→ {
  items: [
    {
      display_name: "ДИТ (Блок ОД)",
      full_path: "Блок ОД/ДИТ",
      positions_count: 25,
      hierarchy: ["Блок ОД", "ДИТ"]
    }
  ],
  total_count: 567
}
```

### Get Business Unit Details
```bash
POST /api/organization/unit
{
  "unit_path": "Блок операционного директора/Департамент ИТ"
}
→ {
  name, path, level, positions,
  hierarchy_path, enriched_positions
}
```

### Get Organization Structure with Target
```bash
POST /api/organization/structure
{
  "target_path": "Блок ОД/ДИТ"
}
→ {
  target_path,
  total_business_units: 567,
  structure: { /* hierarchical tree */ }
}
```

### Organization Stats
```bash
GET /api/organization/stats
→ {
  business_units: { total_count: 567, by_levels: {...} },
  positions: { total_count: 1689 }
}
```

---

## Catalog (Legacy - Use Organization API)

### Departments
```bash
GET /api/catalog/departments?force_refresh=false
→ { departments: [...], total_count: 510 }
```

### Search Departments
```bash
GET /api/catalog/search?q=analyst
→ { departments: [...], total_count: 5 }
```

### Search Positions
```bash
GET /api/catalog/search/positions?q=manager&department=IT
→ {
  positions: [...],
  breakdown: { departments, levels, categories }
}
```

### Catalog Stats
```bash
GET /api/catalog/stats
→ {
  departments: { total_count, with_positions },
  positions: { total_count, levels_distribution }
}
```

### Clear Cache (Admin)
```bash
POST /api/catalog/cache/clear?cache_type=departments
→ { success: true, message: "Кеш очищен" }
```

---

## System Endpoints

### Health Check
```bash
GET /health
→ {
  status: "healthy",
  uptime_seconds: 3600,
  components: { api: "operational" },
  external_services: { openrouter_configured: true }
}
```

### Root Info
```bash
GET /
→ {
  service: "HR Profile Generator API",
  version: "1.0.0",
  docs: "/docs"
}
```

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 401 | Unauthorized | Login required / token expired |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Invalid input data |
| 500 | Server Error | Backend issue |

---

## Common Query Parameters

### Pagination
```
?page=1&limit=20
```

### Filtering
```
?department=ДИТ&position=Аналитик&status=completed
```

### Search
```
?search=analyst
```

### Force Refresh Cache
```
?force_refresh=true
```

---

## TypeScript Interfaces (Essential)

```typescript
// Auth
interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user_info: UserInfo;
}

// Generation
interface GenerationTask {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  current_step?: string;
}

// Profiles
interface ProfileSummary {
  profile_id: string;
  department: string;
  position: string;
  employee_name: string | null;
  status: string;
  created_at: string;
}

// Pagination
interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
  has_prev: boolean;
}
```

---

## Common Operations

### Axios Setup
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8022',
  headers: { 'Content-Type': 'application/json' }
});

// Add token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Polling Pattern
```typescript
async function pollTaskStatus(taskId: string) {
  const interval = setInterval(async () => {
    const { data } = await api.get(`/api/generation/${taskId}/status`);

    console.log(`Status: ${data.task.status}, Progress: ${data.task.progress}%`);

    if (['completed', 'failed', 'cancelled'].includes(data.task.status)) {
      clearInterval(interval);

      if (data.task.status === 'completed') {
        // Success - get result
        const result = await api.get(`/api/generation/${taskId}/result`);
        console.log('Profile:', result.data);
      }
    }
  }, 2000); // Poll every 2 seconds
}
```

### File Download
```typescript
async function downloadProfile(profileId: string, format: 'json' | 'md' | 'docx') {
  const response = await api.get(
    `/api/profiles/${profileId}/download/${format}`,
    { responseType: 'blob' }
  );

  const url = window.URL.createObjectURL(response.data);
  const a = document.createElement('a');
  a.href = url;
  a.download = `profile.${format}`;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

---

## Environment Variables

```bash
# Backend (.env)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemini-2.5-flash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
DATABASE_URL=sqlite:///data/profiles.db
JWT_SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:8033,http://localhost:5173

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8022
```

---

## Testing with cURL

```bash
# Save token
export TOKEN=$(curl -s -X POST http://localhost:8022/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Get dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8022/api/dashboard/stats | jq

# Start generation
TASK_ID=$(curl -s -X POST http://localhost:8022/api/generation/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"department":"ДИТ","position":"Аналитик"}' \
  | jq -r '.task_id')

# Check status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8022/api/generation/$TASK_ID/status | jq
```

---

## Performance Tips

1. **Cache organization data** (changes rarely)
2. **Debounce search** (300ms delay)
3. **Paginate large lists** (limit=20)
4. **Poll task status** every 2-3 seconds (not faster)
5. **Use minimal stats** for real-time widgets

---

## Security Notes

- ✅ All endpoints require JWT token (except /health, /)
- ✅ Token expires after 24 hours
- ✅ CORS enabled for configured origins
- ✅ HTTPS required in production
- ❌ Rate limiting NOT implemented yet

---

**Full Documentation**: See `API_SPECIFICATION.md`
**Integration Guide**: See `INTEGRATION_SUMMARY.md`
**Interactive Docs**: http://localhost:8022/docs

---

**API Version**: 1.0.0 | **Last Updated**: 2025-10-25
