# HR Profile Generator - API Documentation

**Complete API documentation for the A101 HR Profile Generator system**

---

## Documentation Overview

This directory contains comprehensive API documentation for integrating with the HR Profile Generator backend. The documentation is designed for frontend developers building Vue.js or other web applications.

### Available Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| **[API_SPECIFICATION.md](./API_SPECIFICATION.md)** | Complete API reference with all endpoints, request/response schemas, and data models | All developers |
| **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** | Quick start guide for Vue.js integration with code examples | Frontend developers |
| **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | Cheat sheet with common operations and cURL examples | All developers |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | System architecture, data flow diagrams, and technical design | Backend/System architects |

---

## Quick Start for Frontend Developers

### 1. Read This First

Start with **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** for:
- Vue.js setup instructions
- Authentication flow
- Common data flow patterns
- TypeScript type definitions
- Code examples

### 2. Development Workflow

```bash
# 1. Start the backend API
cd /home/yan/A101/HR
docker-compose up -d backend

# 2. API is available at:
http://localhost:8022

# 3. Test with health check:
curl http://localhost:8022/health

# 4. View interactive docs:
http://localhost:8022/docs  (Swagger UI)
http://localhost:8022/redoc (ReDoc)
```

### 3. Authentication Setup

```typescript
// Get access token
const response = await fetch('http://localhost:8022/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123',
    remember_me: false
  })
});

const { access_token } = await response.json();
localStorage.setItem('access_token', access_token);

// Use in all subsequent requests
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};
```

### 4. Core API Patterns

#### Profile Generation (Async)
```typescript
// 1. Start generation
const { task_id } = await fetch('/api/generation/start', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    department: 'Группа анализа данных',
    position: 'Аналитик данных'
  })
}).then(r => r.json());

// 2. Poll status every 2 seconds
const interval = setInterval(async () => {
  const { task } = await fetch(`/api/generation/${task_id}/status`, { headers })
    .then(r => r.json());

  console.log(`Progress: ${task.progress}%`);

  if (task.status === 'completed') {
    clearInterval(interval);
    // Get result
    const result = await fetch(`/api/generation/${task_id}/result`, { headers })
      .then(r => r.json());
    console.log('Profile:', result);
  }
}, 2000);
```

#### List Profiles with Pagination
```typescript
const params = new URLSearchParams({
  page: '1',
  limit: '20',
  department: 'ДИТ',
  status: 'completed'
});

const data = await fetch(`/api/profiles/?${params}`, { headers })
  .then(r => r.json());

console.log('Profiles:', data.profiles);
console.log('Total:', data.pagination.total);
console.log('Has Next:', data.pagination.has_next);
```

#### Get Organization Data for Autocomplete
```typescript
const { data } = await fetch('/api/organization/search-items', { headers })
  .then(r => r.json());

const options = data.items.map(item => ({
  label: item.display_name,    // "ДИТ (Блок ОД)"
  value: item.full_path,        // "Блок ОД/Департамент ИТ"
  subtitle: `${item.positions_count} positions`
}));
```

#### Download Profile File
```typescript
const response = await fetch(
  `/api/profiles/${profileId}/download/docx`,
  { headers }
);

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `profile.docx`;
a.click();
window.URL.revokeObjectURL(url);
```

---

## API Endpoints Summary

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/validate` - Validate token

### Profile Generation (Async)
- `POST /api/generation/start` - Start generation → Returns task_id
- `GET /api/generation/{task_id}/status` - Poll task status
- `GET /api/generation/{task_id}/result` - Get final result
- `DELETE /api/generation/{task_id}` - Cancel task
- `GET /api/generation/tasks/active` - List active tasks

### Profile Management (CRUD)
- `GET /api/profiles/` - List profiles (paginated, filterable)
- `GET /api/profiles/{id}` - Get single profile
- `PUT /api/profiles/{id}` - Update profile metadata
- `DELETE /api/profiles/{id}` - Archive profile
- `POST /api/profiles/{id}/restore` - Restore archived profile
- `GET /api/profiles/{id}/download/{format}` - Download file (json/md/docx)

### Organization Catalog
- `GET /api/organization/search-items` - All 567 business units (for autocomplete)
- `POST /api/organization/unit` - Get unit details by path
- `POST /api/organization/structure` - Get full org tree with highlighted target
- `GET /api/organization/stats` - Organization statistics

### Dashboard
- `GET /api/dashboard/stats` - Full dashboard statistics
- `GET /api/dashboard/stats/minimal` - Essential metrics only
- `GET /api/dashboard/stats/activity` - Recent activity feed

### Catalog (Legacy - Use Organization API)
- `GET /api/catalog/departments` - List departments
- `GET /api/catalog/search` - Search departments
- `GET /api/catalog/search/positions` - Search positions
- `GET /api/catalog/stats` - Catalog statistics

---

## Key Concepts

### 1. Authentication (JWT)

All endpoints require JWT Bearer token (except `/health` and `/`):

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Lifecycle**:
- Expires after 24 hours (configurable)
- Refresh with `POST /api/auth/refresh`
- Invalidate with `POST /api/auth/logout`

### 2. Async Profile Generation

Generation is asynchronous to handle long-running LLM calls (30-60 seconds):

```
1. POST /api/generation/start → { task_id }
2. Poll GET /api/generation/{task_id}/status every 2s
3. When status="completed", get result from response.result
```

### 3. Pagination

List endpoints support pagination:

```
?page=1&limit=20&department=ДИТ&status=completed

Response:
{
  "profiles": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4. Path-Based Organization Indexing

The system uses full paths to avoid duplicate department names:

```
"Блок операционного директора/Департамент информационных технологий"

Instead of:
"Департамент информационных технологий" (ambiguous - 57 lost units)
```

### 5. File Exports

Profiles can be downloaded in 3 formats:
- **JSON**: Raw profile data
- **Markdown**: Human-readable format
- **DOCX**: Microsoft Word document

---

## Data Models (TypeScript)

### Core Types

```typescript
// Authentication
interface UserInfo {
  id: number;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

// Profile Generation
interface GenerationRequest {
  department: string;
  position: string;
  employee_name?: string;
  temperature?: number;  // 0.0-1.0
  save_result?: boolean;
}

interface GenerationTask {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;  // 0-100
  current_step?: string;
  error_message?: string;
}

// Profiles
interface ProfileSummary {
  profile_id: string;
  department: string;
  position: string;
  employee_name: string | null;
  status: 'completed' | 'failed' | 'processing' | 'archived';
  validation_score: number;
  completeness_score: number;
  created_at: string;
  created_by_username: string | null;
}

// Organization
interface SearchableItem {
  display_name: string;     // "ДИТ (Блок ОД)"
  full_path: string;         // "Блок ОД/ДИТ"
  positions_count: number;
  hierarchy: string[];
}

// Pagination
interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}
```

See **[API_SPECIFICATION.md](./API_SPECIFICATION.md)** for complete type definitions.

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "timestamp": "2025-10-25T10:00:00Z",
  "error": "Resource not found",
  "details": {
    "code": "RESOURCE_NOT_FOUND",
    "resource": "profile",
    "resource_id": "abc123"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show permission error |
| 404 | Not Found | Show not found message |
| 422 | Validation Error | Show validation errors |
| 500 | Server Error | Show generic error |

### Error Handling Pattern

```typescript
try {
  const response = await fetch(url, { headers });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem('access_token');
      router.push('/login');
      return;
    }

    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }

  return await response.json();
} catch (error) {
  console.error('API Error:', error);
  // Show user-friendly error message
  notify.error(error.message);
  throw error;
}
```

---

## Performance Considerations

### Response Times

- **Simple queries** (cached): < 50ms
- **Database queries**: 50-200ms
- **Profile generation**: 30-60 seconds
- **File downloads**: 100-500ms

### Caching

- **Organization data**: Cached in-memory (75x speedup: 3ms vs 225ms)
- **Cache invalidation**: `force_refresh=true` parameter or admin cache clear

### Recommendations

1. **Cache organization data** in frontend (changes rarely)
2. **Debounce search** inputs (300ms delay)
3. **Use pagination** for large lists (limit=20-50)
4. **Poll task status** every 2-3 seconds (not faster)
5. **Use minimal stats** endpoint for real-time widgets

---

## CORS Configuration

The API accepts requests from:
- `http://localhost:8033` (NiceGUI - current frontend)
- `http://127.0.0.1:8033`

**For Vue.js development**, add to `.env`:

```bash
CORS_ORIGINS=http://localhost:8033,http://localhost:5173,http://127.0.0.1:5173
```

Restart the backend after changing CORS origins.

---

## Testing the API

### Using cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8022/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Get dashboard stats
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8022/api/dashboard/stats | jq

# 3. List profiles
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8022/api/profiles/?page=1&limit=5" | jq

# 4. Start generation
TASK_ID=$(curl -s -X POST http://localhost:8022/api/generation/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"department":"ДИТ","position":"Аналитик"}' \
  | jq -r '.task_id')

# 5. Check status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8022/api/generation/$TASK_ID/status | jq
```

### Using Postman

1. **Import**: Use Swagger UI at `/docs` to export OpenAPI spec
2. **Environment**: Set `API_BASE_URL = http://localhost:8022`
3. **Authorization**: Add Bearer Token with `{{access_token}}`

### Using Swagger UI

Interactive API testing available at:
- **Swagger UI**: http://localhost:8022/docs
- **ReDoc**: http://localhost:8022/redoc

---

## Common Integration Patterns

### Vue.js Composables

```typescript
// composables/useTaskPolling.ts
export function useTaskPolling(taskId: string) {
  const task = ref<GenerationTask | null>(null);
  const result = ref<any>(null);
  const error = ref<string | null>(null);

  const poll = async () => {
    try {
      const response = await profileService.getTaskStatus(taskId);
      task.value = response.task;

      if (response.task.status === 'completed') {
        result.value = response.result;
        stopPolling();
      }
    } catch (err) {
      error.value = err.message;
      stopPolling();
    }
  };

  const interval = setInterval(poll, 2000);
  const stopPolling = () => clearInterval(interval);

  onUnmounted(stopPolling);

  return { task, result, error };
}
```

### Axios Client Setup

```typescript
// api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  headers: { 'Content-Type': 'application/json' }
});

// Add token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
apiClient.interceptors.response.use(
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

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Problem**: `Access-Control-Allow-Origin` error

**Solution**:
```bash
# Add your frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:8033,http://localhost:5173

# Restart backend
docker-compose restart backend
```

#### 2. 401 Unauthorized

**Problem**: Token expired or invalid

**Solution**:
```typescript
// Check token expiration
const tokenData = JSON.parse(atob(token.split('.')[1]));
const isExpired = tokenData.exp * 1000 < Date.now();

if (isExpired) {
  // Refresh token or redirect to login
  await authService.refreshToken();
}
```

#### 3. Generation Timeout

**Problem**: Task stuck in "processing" state

**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Check if OpenRouter API key is configured
curl http://localhost:8022/health | jq '.external_services.openrouter_configured'
```

#### 4. File Download Fails

**Problem**: 404 error when downloading profile

**Solution**:
```typescript
// Ensure token is included in download request
const token = localStorage.getItem('access_token');
const url = `/api/profiles/${profileId}/download/docx`;

// Method 1: Include in header (preferred)
const response = await fetch(url, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Method 2: Include in query param (alternative)
window.open(`${url}?token=${token}`);
```

---

## Support Resources

### Documentation
- **Full API Spec**: [API_SPECIFICATION.md](./API_SPECIFICATION.md)
- **Integration Guide**: [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)
- **Quick Reference**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)

### Interactive Tools
- **Swagger UI**: http://localhost:8022/docs
- **ReDoc**: http://localhost:8022/redoc
- **Health Check**: http://localhost:8022/health

### Backend Code
- **API Endpoints**: `/home/yan/A101/HR/backend/api/`
- **Core Services**: `/home/yan/A101/HR/backend/core/`
- **Data Models**: `/home/yan/A101/HR/backend/models/`

### Memory Bank (Project Documentation)
- **Tech Stack**: `/home/yan/A101/HR/.memory_bank/tech_stack.md`
- **Coding Standards**: `/home/yan/A101/HR/.memory_bank/guides/coding_standards.md`
- **API Standards**: `/home/yan/A101/HR/.memory_bank/patterns/api_standards.md`
- **Error Handling**: `/home/yan/A101/HR/.memory_bank/patterns/error_handling.md`

---

## Next Steps

### For Frontend Developers

1. ✅ **Read** [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)
2. ✅ **Setup** Axios client with JWT interceptors
3. ✅ **Implement** authentication flow
4. ✅ **Build** dashboard using `/api/dashboard/stats`
5. ✅ **Add** profile generation with async polling
6. ✅ **Implement** profile list with pagination
7. ✅ **Add** file download functionality

### For Backend Developers

1. ✅ **Review** [ARCHITECTURE.md](./ARCHITECTURE.md)
2. ✅ **Understand** data flow and service layers
3. ✅ **Study** database schema and indexes
4. ✅ **Review** security architecture
5. ✅ **Plan** scaling strategy for production

### For System Architects

1. ✅ **Review** full system architecture
2. ✅ **Evaluate** scaling considerations
3. ✅ **Plan** production migration (SQLite → PostgreSQL)
4. ✅ **Design** distributed task queue (Redis + Celery)
5. ✅ **Setup** monitoring and observability

---

## Changelog

### Version 1.0.0 (2025-10-25)

**Initial Release**

- Complete API specification with 40+ endpoints
- JWT-based authentication system
- Async profile generation with LLM (Gemini 2.5 Flash)
- Profile CRUD operations with pagination
- Organization catalog with path-based indexing (567 business units)
- File export functionality (JSON, Markdown, DOCX)
- Dashboard statistics and activity feed
- Thread-safe SQLite database with connection pooling
- In-memory organization cache (75x performance improvement)
- CORS configuration for frontend integration
- Comprehensive error handling
- Interactive API documentation (Swagger UI, ReDoc)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-25
**Maintained By**: Backend Team
