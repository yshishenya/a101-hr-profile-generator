# Vue.js Frontend - Docker Setup

## Обзор

Vue.js frontend упакован в Docker с поддержкой двух режимов:
- **Development**: Vite dev server с HMR (hot module replacement)
- **Production**: Nginx с оптимизированной сборкой

## Быстрый старт

### Development режим (рекомендуется для разработки)

```bash
# Из корневой директории проекта
docker-compose up frontend-vue

# Или с rebuil

d
docker-compose up --build frontend-vue
```

Доступ: **http://localhost:5173**

### Production режим

```bash
# Установить переменную окружения
export FRONTEND_MODE=production

# Запустить
docker-compose up --build frontend-vue
```

Доступ: **http://localhost:8080**

## Структура Docker

### Multi-stage Dockerfile

```
┌─────────────────────────────────────┐
│  Stage 1: Builder                   │
│  - Node 20 Alpine                   │
│  - npm ci + npm run build           │
│  - Создает /app/dist                │
└─────────────────────────────────────┘
         ↓                      ↓
┌──────────────────┐   ┌──────────────────┐
│ Stage 2: Dev     │   │ Stage 3: Prod    │
│ - Node 20 Alpine │   │ - Nginx Alpine   │
│ - Vite dev       │   │ - Serve dist/    │
│ - HMR enabled    │   │ - API proxy      │
└──────────────────┘   └──────────────────┘
```

### Порты

| Режим | Порт | Назначение |
|-------|------|------------|
| Development | 5173 | Vite dev server |
| Production | 8080 → 80 | Nginx |

### Volumes (Development)

```yaml
volumes:
  - ./src:/app/src:ro              # Source code (read-only)
  - ./public:/app/public:ro        # Public assets
  - ./index.html:/app/index.html:ro
  - ./vite.config.ts:/app/vite.config.ts:ro
  - /app/node_modules              # Prevent overwrite
```

## Переменные окружения

### Docker Compose

```bash
# .env file
FRONTEND_MODE=development  # or production
NODE_ENV=development       # or production
```

### Runtime (Vite)

```bash
VITE_API_BASE_URL=http://app:8022
VITE_APP_TITLE=A101 HR Profile Generator
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEBUG=true
```

## Команды

### Сборка

```bash
# Development
docker-compose build frontend-vue

# Production
FRONTEND_MODE=production docker-compose build frontend-vue
```

### Запуск

```bash
# Только frontend
docker-compose up frontend-vue

# Весь стек (backend + frontend + frontend-vue)
docker-compose up

# В фоне
docker-compose up -d frontend-vue
```

### Логи

```bash
# Следить за логами
docker-compose logs -f frontend-vue

# Последние 100 строк
docker-compose logs --tail=100 frontend-vue
```

### Остановка

```bash
# Остановить
docker-compose stop frontend-vue

# Остановить и удалить
docker-compose down frontend-vue
```

### Пересборка

```bash
# С очисткой кеша
docker-compose build --no-cache frontend-vue

# С pull свежих образов
docker-compose build --pull frontend-vue
```

## Health Checks

### Development

```bash
curl http://localhost:5173/
```

### Production

```bash
curl http://localhost:8080/health
```

## Troubleshooting

### Проблема: Port already in use

```bash
# Найти процесс
lsof -i:5173

# Убить процесс
kill -9 <PID>

# Или изменить порт в docker-compose.yml
ports:
  - "5174:5173"
```

### Проблема: Changes not reflecting (HMR не работает)

```bash
# Перезапустить контейнер
docker-compose restart frontend-vue

# Или пересобрать
docker-compose up --build frontend-vue
```

### Проблема: CORS errors

Проверьте что backend доступен по адресу `http://app:8022` внутри Docker network.

```bash
# Проверить connectivity
docker-compose exec frontend-vue wget -O- http://app:8022/health
```

### Проблема: node_modules не синхронизируются

Volume `/app/node_modules` предотвращает перезапись node_modules с хоста. Это нормально.

Если нужно обновить зависимости:

```bash
# Пересобрать образ
docker-compose build --no-cache frontend-vue
```

## Production Deployment

### Build production image

```bash
cd frontend-vue
docker build --target production -t a101hr-frontend-vue:latest .
```

### Run production container

```bash
docker run -d \
  --name a101hr-frontend-vue \
  -p 8080:80 \
  --network a101hr_network \
  a101hr-frontend-vue:latest
```

### Nginx features

- ✅ Gzip compression
- ✅ Static asset caching (1 year)
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- ✅ API proxy to backend
- ✅ SPA fallback (history mode routing)
- ✅ Health check endpoint

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ http://localhost:5173 (dev)
       │ http://localhost:8080 (prod)
       ↓
┌─────────────────┐
│  Frontend Vue   │
│  (Container)    │
│                 │
│  Dev:  Vite     │
│  Prod: Nginx    │
└────────┬────────┘
         │
         │ /api → proxy
         ↓
┌─────────────────┐
│   Backend API   │
│  (Container)    │
│  FastAPI        │
│  Port: 8022     │
└─────────────────┘
```

## Файлы

```
frontend-vue/
├── Dockerfile          # Multi-stage build
├── .dockerignore       # Исключения для Docker
├── nginx.conf          # Nginx config for production
├── README.Docker.md    # Эта документация
└── src/                # Source code
```

## Ссылки

- [Vite Docker Guide](https://vitejs.dev/guide/build.html#docker)
- [Vue.js Production Deployment](https://vuejs.org/guide/best-practices/production-deployment.html)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)
