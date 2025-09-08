#!/bin/bash

# Скрипт для запуска A101 HR Frontend
# Поддерживает разные режимы запуска: local, docker, docker-compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для цветного вывода
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Функция помощи
show_help() {
    echo "🎨 A101 HR Frontend Starter"
    echo ""
    echo "Usage: $0 [mode] [options]"
    echo ""
    echo "Modes:"
    echo "  local         - Запуск локально через Python"
    echo "  docker        - Запуск в Docker контейнере (только frontend)"
    echo "  compose       - Запуск через docker-compose (frontend + backend)"
    echo "  compose-dev   - Запуск frontend через docker-compose в dev режиме"
    echo ""
    echo "Options:"
    echo "  --build       - Пересборка Docker образов"
    echo "  --logs        - Показать логи после запуска"
    echo "  --help, -h    - Показать эту справку"
    echo ""
    echo "Examples:"
    echo "  $0 local                    # Запуск локально"
    echo "  $0 docker --build          # Пересборка и запуск в Docker"
    echo "  $0 compose --logs          # Запуск через compose с просмотром логов"
    echo ""
}

# Проверка зависимостей
check_dependencies() {
    if [[ "$1" == "local" ]]; then
        if ! command -v python3 &> /dev/null; then
            log_error "Python3 не найден. Установите Python 3.11+"
            exit 1
        fi
        
        if ! python3 -c "import nicegui" &> /dev/null; then
            log_warning "NiceGUI не установлен. Установка зависимостей..."
            pip install -r requirements.txt
        fi
    else
        if ! command -v docker &> /dev/null; then
            log_error "Docker не найден. Установите Docker"
            exit 1
        fi
        
        if [[ "$1" == "compose"* ]]; then
            if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
                log_error "Docker Compose не найден"
                exit 1
            fi
        fi
    fi
}

# Проверка backend доступности
check_backend() {
    local backend_url="$1"
    log_info "Проверка доступности backend: $backend_url"
    
    if curl -s -f "$backend_url/health" > /dev/null; then
        log_success "Backend доступен"
        return 0
    else
        log_warning "Backend недоступен на $backend_url"
        return 1
    fi
}

# Запуск локально
start_local() {
    log_info "🚀 Запуск A101 HR Frontend локально..."
    
    # Проверяем .env файл
    if [[ ! -f ".env" ]]; then
        log_warning ".env файл не найден, создаем из .env.example"
        cp .env.example .env
    fi
    
    # Проверяем backend
    if ! check_backend "http://localhost:8022"; then
        log_warning "Запустите backend командой: python -m backend.main"
    fi
    
    # Запускаем frontend
    export PYTHONPATH="$PROJECT_ROOT"
    cd frontend
    python main.py
}

# Запуск в Docker
start_docker() {
    local build_flag=""
    if [[ "$2" == "--build" ]]; then
        build_flag="--build"
        log_info "🔨 Пересборка Docker образа..."
    fi
    
    log_info "🐳 Запуск A101 HR Frontend в Docker контейнере..."
    
    # Проверяем backend на хост машине
    if ! check_backend "http://localhost:8022"; then
        log_warning "Запустите backend локально или используйте режим 'compose'"
    fi
    
    docker-compose -f docker-compose.frontend.yml up $build_flag
}

# Запуск через docker-compose (полная система)
start_compose() {
    local build_flag=""
    local logs_flag=""
    
    for arg in "$@"; do
        case $arg in
            --build)
                build_flag="--build"
                log_info "🔨 Пересборка Docker образов..."
                ;;
            --logs)
                logs_flag="--follow"
                ;;
        esac
    done
    
    log_info "🐳 Запуск полной системы A101 HR через docker-compose..."
    
    # Запуск всех сервисов
    if [[ -n "$logs_flag" ]]; then
        docker-compose up $build_flag --detach
        log_success "Сервисы запущены в фоне"
        log_info "📊 Статус сервисов:"
        docker-compose ps
        echo ""
        log_info "📱 URLs:"
        log_info "  Frontend: http://localhost:8033"
        log_info "  Backend:  http://localhost:8022"
        echo ""
        log_info "📜 Просмотр логов..."
        docker-compose logs --follow
    else
        docker-compose up $build_flag
    fi
}

# Запуск frontend в dev режиме
start_compose_dev() {
    local build_flag=""
    
    if [[ "$2" == "--build" ]]; then
        build_flag="--build"
        log_info "🔨 Пересборка Docker образа..."
    fi
    
    log_info "🐳 Запуск A101 HR Frontend в dev режиме..."
    
    # Проверяем backend на хост машине
    if ! check_backend "http://localhost:8022"; then
        log_error "Backend должен быть запущен локально для dev режима"
        log_info "Запустите: python -m backend.main"
        exit 1
    fi
    
    docker-compose -f docker-compose.frontend.yml up $build_flag
}

# Главная функция
main() {
    local mode="${1:-local}"
    
    case "$mode" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "local")
            check_dependencies "local"
            start_local
            ;;
        "docker")
            check_dependencies "docker"
            start_docker "$@"
            ;;
        "compose")
            check_dependencies "compose"
            start_compose "$@"
            ;;
        "compose-dev")
            check_dependencies "compose"
            start_compose_dev "$@"
            ;;
        *)
            log_error "Неизвестный режим: $mode"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Обработка Ctrl+C
trap 'echo -e "\n${YELLOW}[INFO]${NC} Получен сигнал остановки..."; exit 0' INT

# Запуск
log_info "🏢 A101 HR Profile Generator - Frontend Starter"
main "$@"