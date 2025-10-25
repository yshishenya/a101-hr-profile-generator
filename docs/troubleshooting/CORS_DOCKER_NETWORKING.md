# CORS & Docker Networking Troubleshooting

**Date**: 2025-10-25
**Status**: ✅ Resolved
**Impact**: Vue.js frontend authentication now works in Docker environment

---

## Problem Description

### Symptoms
```
Access to XMLHttpRequest at 'http://app:8022/api/auth/login' from origin
'http://localhost:5173' has been blocked by CORS policy:
Redirect is not allowed for a preflight request.

POST http://app:8022/api/auth/login net::ERR_FAILED
```

### Environment
- **Frontend**: Vue.js 3 + Vite dev server (port 5173) in Docker container
- **Backend**: FastAPI (port 8022) with `network_mode: "host"`
- **Issue**: Frontend container cannot reach backend at `http://app:8022`

---

## Root Cause Analysis

### 1. Backend Network Mode
Backend uses `network_mode: "host"` which bypasses Docker bridge network:
```yaml
services:
  app:
    network_mode: "host"
```

### 2. Frontend Network Isolation
Frontend runs in bridge network and cannot resolve `app` hostname when backend is on host network.

### 3. Axios Configuration
Frontend axios was hardcoded to `http://localhost:8022` which doesn't work inside Docker container:
```typescript
// ❌ BAD - doesn't work in Docker
baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022'
```

---

## Solution

### Architecture Overview
```
Browser (localhost:5173)
    ↓ /api/auth/login
Vite Dev Server (Docker container)
    ↓ Proxy to http://host.docker.internal:8022/api/auth/login
Backend (host network, port 8022)
    ↓ ✅ CORS headers + response
Browser receives JWT token
```

### 1. Configure Vite Proxy
**File**: `frontend-vue/vite.config.ts`

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8022',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

### 2. Update Axios Configuration
**File**: `frontend-vue/src/services/api.ts`

```typescript
const api: AxiosInstance = axios.create({
  // Empty baseURL enables Vite proxy
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

**Key change**: Use nullish coalescing (`??`) instead of OR (`||`) to allow empty string.

### 3. Docker Compose Configuration
**File**: `docker-compose.yml`

```yaml
services:
  frontend-vue:
    environment:
      - VITE_BACKEND_URL=http://host.docker.internal:8022
    extra_hosts:
      # Enable host.docker.internal on Linux
      - "host.docker.internal:host-gateway"
```

**Critical for Linux**: `extra_hosts` enables `host.docker.internal` resolution.

### 4. Backend CORS Configuration
**File**: `.env`

```bash
CORS_ORIGINS=*
TRUSTED_HOSTS=localhost,127.0.0.1,0.0.0.0,app,host.docker.internal,49.12.122.181
```

Added `host.docker.internal` to TRUSTED_HOSTS for TrustedHostMiddleware.

### 5. Development Environment
**File**: `frontend-vue/.env.development`

```bash
# Empty to use Vite proxy
VITE_API_BASE_URL=
```

---

## Verification Steps

### 1. Test CORS Preflight
```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -I http://localhost:8022/api/auth/login
```

Expected headers:
```
access-control-allow-origin: http://localhost:5173
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
access-control-allow-credentials: true
access-control-allow-headers: Content-Type,Authorization
```

### 2. Test Login
```bash
curl -X POST http://localhost:5173/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Expected response:
```json
{
  "success": true,
  "access_token": "eyJhbGci...",
  "user_info": {...}
}
```

### 3. Test from Frontend Container
```bash
docker compose exec frontend-vue wget -O- -q http://host.docker.internal:8022/health
```

Should return health check JSON without errors.

---

## Production Considerations

### Option 1: Use Bridge Network (Recommended)
Switch backend to bridge network for consistency:

```yaml
services:
  app:
    networks:
      - a101hr_network
  frontend-vue:
    networks:
      - a101hr_network
    environment:
      - VITE_BACKEND_URL=http://app:8022
```

### Option 2: Keep Host Network
If backend must use host network, ensure frontend has proper proxy configuration as documented above.

---

## Related Files

- [docker-compose.yml](../../docker-compose.yml)
- [vite.config.ts](../../frontend-vue/vite.config.ts)
- [api.ts](../../frontend-vue/src/services/api.ts)
- [.env.development](../../frontend-vue/.env.development)
- [backend config.py](../../backend/core/config.py)

---

## Lessons Learned

1. **Docker networking modes matter**: `host` vs `bridge` affects hostname resolution
2. **Linux needs extra_hosts**: `host.docker.internal` isn't available by default on Linux
3. **Vite proxy is powerful**: Use it for development instead of CORS workarounds
4. **Operator choice matters**: `??` vs `||` for baseURL configuration
5. **TRUSTED_HOSTS middleware**: Don't forget to add proxy hosts to whitelist

---

**Last Updated**: 2025-10-25
**Resolution Time**: ~2 hours
**Impact**: Vue.js MVP auth now fully functional ✅
