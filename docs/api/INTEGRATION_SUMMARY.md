# Vue.js Frontend Integration Summary

**Quick Reference Guide for Frontend Developers**

---

## Quick Start

### 1. Base Configuration

```typescript
// API Base URL
const API_BASE_URL = 'http://localhost:8022'; // Development
const API_BASE_URL = 'https://api.a101.com/hr'; // Production

// All endpoints require JWT Bearer token (except /health and /)
Authorization: Bearer {access_token}
```

### 2. Authentication Flow

```
1. POST /api/auth/login → Get access_token
2. Store token in localStorage
3. Add token to all requests via Authorization header
4. Token expires after 24 hours
5. Use POST /api/auth/refresh to get new token
```

---

## Critical Endpoints for Frontend

### Authentication (Required First)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/auth/login` | POST | Login and get JWT token | `{ access_token, user_info }` |
| `/api/auth/me` | GET | Get current user info | `UserInfo` |
| `/api/auth/logout` | POST | Logout (invalidate session) | `{ success: true }` |

### Dashboard (Home Page)

| Endpoint | Method | Purpose | Use Case |
|----------|--------|---------|----------|
| `/api/dashboard/stats` | GET | Full dashboard statistics | Main dashboard page |
| `/api/dashboard/stats/minimal` | GET | Essential metrics only | Compact widgets, mobile |
| `/api/dashboard/stats/activity` | GET | Recent activity feed | Activity timeline |

### Profile Generation (Main Feature)

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/api/generation/start` | POST | Start async generation | Returns `task_id` |
| `/api/generation/{task_id}/status` | GET | Poll task status | Poll every 2-3 seconds |
| `/api/generation/{task_id}/result` | GET | Get final result | Only when status=completed |
| `/api/generation/tasks/active` | GET | List user's active tasks | For "My Tasks" view |

### Profile Management (CRUD)

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/api/profiles/` | GET | List profiles (paginated) | Supports filtering & search |
| `/api/profiles/{id}` | GET | Get single profile | Full profile data |
| `/api/profiles/{id}` | PUT | Update metadata | Only employee_name & status |
| `/api/profiles/{id}` | DELETE | Archive profile | Soft delete (status=archived) |
| `/api/profiles/{id}/restore` | POST | Restore archived profile | status→completed |
| `/api/profiles/{id}/download/json` | GET | Download JSON file | File download |
| `/api/profiles/{id}/download/md` | GET | Download Markdown | File download |
| `/api/profiles/{id}/download/docx` | GET | Download Word document | File download |

### Organization Catalog (Search & Browse)

| Endpoint | Method | Purpose | Recommended |
|----------|--------|---------|-------------|
| `/api/organization/search-items` | GET | All 567 business units | ✅ Use for autocomplete |
| `/api/organization/unit` | POST | Get unit details by path | ✅ Use instead of catalog |
| `/api/organization/stats` | GET | Organization statistics | For analytics |
| `/api/catalog/departments` | GET | Legacy department list | ⚠️ Use organization API |
| `/api/catalog/search` | GET | Search departments | ⚠️ Use organization API |

---

## Data Flow Examples

### Example 1: User Login

```typescript
// 1. User submits login form
const credentials = { username: 'admin', password: 'admin123', remember_me: false };

// 2. Call login API
const response = await fetch('http://localhost:8022/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(credentials),
});

// 3. Store token
const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('user_info', JSON.stringify(data.user_info));

// 4. All subsequent requests include token
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json',
};
```

### Example 2: Generate Profile (Async Pattern)

```typescript
// Step 1: Start generation
const startRequest = {
  department: 'Группа анализа данных',
  position: 'Аналитик данных',
  employee_name: 'Иванов Иван',
  temperature: 0.1,
  save_result: true,
};

const startResponse = await fetch('http://localhost:8022/api/generation/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(startRequest),
});

const { task_id } = await startResponse.json();
// task_id: "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1"

// Step 2: Poll status every 2 seconds
const pollStatus = async () => {
  const statusResponse = await fetch(
    `http://localhost:8022/api/generation/${task_id}/status`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );

  const { task, result } = await statusResponse.json();

  console.log(`Status: ${task.status}, Progress: ${task.progress}%`);

  if (task.status === 'completed') {
    console.log('Profile generated!', result);
    clearInterval(pollInterval);
    // Navigate to profile view
    router.push(`/profiles/${result.profile_id}`);
  } else if (task.status === 'failed') {
    console.error('Generation failed:', task.error_message);
    clearInterval(pollInterval);
  }
};

const pollInterval = setInterval(pollStatus, 2000);
```

### Example 3: List Profiles with Filters

```typescript
// Get page 1 with 10 items, filtered by department
const params = new URLSearchParams({
  page: '1',
  limit: '10',
  department: 'Группа анализа данных',
  status: 'completed',
});

const response = await fetch(
  `http://localhost:8022/api/profiles/?${params}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

const data = await response.json();

console.log('Profiles:', data.profiles); // Array of ProfileSummary
console.log('Pagination:', data.pagination); // { page, limit, total, has_next, has_prev }
console.log('Filters:', data.filters_applied); // Applied filters
```

### Example 4: Download Profile File

```typescript
// Method 1: Direct link (requires token in URL or cookie)
const downloadUrl = `/api/profiles/${profileId}/download/docx`;
window.open(downloadUrl); // Browser handles download

// Method 2: Fetch with blob
const response = await fetch(
  `http://localhost:8022/api/profiles/${profileId}/download/docx`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `profile_${profileId}.docx`;
document.body.appendChild(a);
a.click();
window.URL.revokeObjectURL(url);
document.body.removeChild(a);
```

### Example 5: Organization Search (Autocomplete)

```typescript
// Get all searchable items for autocomplete dropdown
const response = await fetch(
  'http://localhost:8022/api/organization/search-items',
  { headers: { 'Authorization': `Bearer ${token}` } }
);

const { data } = await response.json();

// data.items: Array<{ display_name, full_path, positions_count, hierarchy }>
const autocompleteOptions = data.items.map(item => ({
  label: item.display_name, // "ДИТ (Блок ОД)"
  value: item.full_path, // "Блок операционного директора/Департамент информационных технологий"
  subtitle: `${item.positions_count} позиций`,
}));

// Use in autocomplete/select component
```

---

## Key Data Models for TypeScript

### User & Authentication

```typescript
interface UserInfo {
  id: number;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string; // ISO 8601
  last_login: string | null;
}

interface LoginResponse {
  success: boolean;
  access_token: string;
  token_type: 'bearer';
  expires_in: number; // seconds (86400 = 24 hours)
  user_info: UserInfo;
}
```

### Profile Generation

```typescript
interface GenerationRequest {
  department: string;
  position: string;
  employee_name?: string;
  temperature?: number; // 0.0-1.0, default 0.1
  save_result?: boolean; // default true
}

interface GenerationTask {
  task_id: string; // UUID
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  current_step?: string;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  estimated_duration?: number; // seconds
}
```

### Profile Data

```typescript
interface ProfileSummary {
  profile_id: string; // UUID
  department: string;
  position: string;
  employee_name: string | null;
  status: 'completed' | 'failed' | 'processing' | 'archived';
  validation_score: number; // 0.0-1.0
  completeness_score: number; // 0.0-1.0
  created_at: string; // ISO 8601
  created_by_username: string | null;
  actions?: {
    download_json: string;
    download_md: string;
    download_docx: string;
  };
}

interface ProfileListResponse {
  profiles: ProfileSummary[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied: {
    department?: string;
    position?: string;
    search?: string;
    status?: string;
  };
}
```

### Dashboard

```typescript
interface DashboardStats {
  success: boolean;
  data: {
    summary: {
      departments_count: number;
      positions_count: number;
      profiles_count: number;
      completion_percentage: number;
      active_tasks_count: number;
    };
    departments: {
      total: number;
      with_positions: number;
      average_positions: number;
    };
    positions: {
      total: number;
      with_profiles: number;
      without_profiles: number;
      coverage_percent: number;
    };
    profiles: {
      total: number;
      percentage_complete: number;
    };
    active_tasks: GenerationTask[];
    metadata: {
      last_updated: string; // ISO 8601
    };
  };
}
```

---

## Error Handling

### Standard Error Response

```typescript
interface ErrorResponse {
  success: false;
  timestamp: string;
  error: string; // Human-readable message
  details?: ErrorDetail[];
  path?: string;
  request_id?: string;
}

interface ErrorDetail {
  code: string;
  message: string;
  field?: string;
}
```

### Common HTTP Status Codes

- **200 OK**: Success
- **401 Unauthorized**: Invalid/expired token → Redirect to login
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Handling Pattern

```typescript
async function apiCall() {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired - redirect to login
        localStorage.removeItem('access_token');
        router.push('/login');
        return;
      }

      const error = await response.json();
      throw new Error(error.error || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // Show error notification to user
    notify.error(error.message);
    throw error;
  }
}
```

---

## Performance Tips

### 1. Caching

```typescript
// Cache organization search items (changes rarely)
let cachedSearchItems: SearchableItem[] | null = null;

async function getSearchItems() {
  if (cachedSearchItems) {
    return cachedSearchItems;
  }

  const response = await fetch('/api/organization/search-items', { headers });
  const data = await response.json();
  cachedSearchItems = data.data.items;

  return cachedSearchItems;
}
```

### 2. Debouncing Search

```typescript
import { debounce } from 'lodash-es';

const searchProfiles = debounce(async (query: string) => {
  const params = new URLSearchParams({ search: query, limit: '20' });
  const response = await fetch(`/api/profiles/?${params}`, { headers });
  const data = await response.json();
  // Update UI with results
}, 300); // Wait 300ms after user stops typing
```

### 3. Pagination

```typescript
// Load more pattern
const loadMore = async () => {
  currentPage++;
  const params = new URLSearchParams({
    page: currentPage.toString(),
    limit: '20',
  });

  const response = await fetch(`/api/profiles/?${params}`, { headers });
  const data = await response.json();

  profiles.value.push(...data.profiles); // Append to existing list
  hasMore.value = data.pagination.has_next;
};
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:8033` (NiceGUI frontend - current)
- `http://127.0.0.1:8033`

**For Vue.js development**, add your dev server URL to `CORS_ORIGINS` in `.env`:

```bash
CORS_ORIGINS=http://localhost:8033,http://127.0.0.1:8033,http://localhost:5173
```

---

## Testing the API

### Using cURL

```bash
# 1. Login
curl -X POST http://localhost:8022/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123", "remember_me": false}'

# Save the access_token from response
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Get dashboard stats
curl -X GET http://localhost:8022/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"

# 3. List profiles
curl -X GET "http://localhost:8022/api/profiles/?page=1&limit=5" \
  -H "Authorization: Bearer $TOKEN"

# 4. Start generation
curl -X POST http://localhost:8022/api/generation/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "Группа анализа данных",
    "position": "Аналитик данных",
    "employee_name": "Тест Тестов",
    "temperature": 0.1
  }'
```

### Using Postman

1. **Import Collection**: Available at `/docs` (Swagger UI has export option)
2. **Set Environment Variable**: `API_BASE_URL = http://localhost:8022`
3. **Add Authorization**: Bearer Token with `{{access_token}}`

---

## Recommended Frontend Structure

```
src/
├── api/
│   ├── client.ts              # Axios client with interceptors
│   ├── types.ts               # TypeScript interfaces
│   ├── auth.service.ts        # Authentication API calls
│   ├── profile.service.ts     # Profile CRUD operations
│   ├── catalog.service.ts     # Organization catalog
│   ├── dashboard.service.ts   # Dashboard statistics
│   └── index.ts               # Export all services
├── composables/
│   ├── useAuth.ts             # Authentication state management
│   ├── useTaskPolling.ts      # Poll generation task status
│   ├── useProfiles.ts         # Profile list state
│   └── useDashboard.ts        # Dashboard data
├── stores/
│   ├── auth.store.ts          # Pinia store for auth
│   ├── profiles.store.ts      # Pinia store for profiles
│   └── ui.store.ts            # UI state (notifications, loading)
├── views/
│   ├── LoginView.vue
│   ├── DashboardView.vue
│   ├── ProfileListView.vue
│   ├── ProfileDetailView.vue
│   ├── ProfileGenerateView.vue
│   └── SettingsView.vue
└── components/
    ├── ProfileCard.vue
    ├── TaskStatusIndicator.vue
    ├── DepartmentAutocomplete.vue
    └── DownloadButtons.vue
```

---

## Next Steps

1. **Read Full API Spec**: See `API_SPECIFICATION.md` for complete documentation
2. **Setup Axios Client**: Use the code examples in "Vue.js Integration Guide"
3. **Implement Authentication**: Start with login/logout flow
4. **Build Dashboard**: Use `/api/dashboard/stats` endpoint
5. **Implement Profile Generation**: Use async task pattern with polling
6. **Add Profile Management**: CRUD operations + file downloads

---

## Support Resources

- **Swagger UI**: http://localhost:8022/docs (Interactive API testing)
- **ReDoc**: http://localhost:8022/redoc (Alternative documentation)
- **Health Check**: http://localhost:8022/health (API status)
- **Full Specification**: `docs/api/API_SPECIFICATION.md`
- **Backend Code**: `backend/api/` directory

---

**Last Updated**: 2025-10-25
**API Version**: 1.0.0
