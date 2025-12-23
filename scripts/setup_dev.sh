#!/bin/bash
# =============================================================================
# OpenRouter + Manus AI - Development Environment Setup
# =============================================================================
# Автоматическая настройка dev окружения для работы с проектом
#
# Что делает этот скрипт:
# 1. Создает Python virtual environment
# 2. Устанавливает все зависимости
# 3. Создает .env файл из .env.example
# 4. Создает необходимые директории
# 5. Инициализирует базу данных
# 6. Проверяет что все работает
#
# Использование:
#   chmod +x scripts/setup_dev.sh
#   ./scripts/setup_dev.sh
# =============================================================================

set -e  # Выйти при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для красивого вывода
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# Проверка системных требований
# =============================================================================

info "Проверка системных требований..."

# Проверка Python версии
if ! command -v python3 &> /dev/null; then
    error "Python 3 не найден! Установите Python 3.11 или новее."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
info "Найден Python $PYTHON_VERSION"

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    error "pip3 не найден! Установите pip."
    exit 1
fi

success "Системные требования выполнены"

# =============================================================================
# Создание Virtual Environment
# =============================================================================

info "Создание Python virtual environment..."

if [ -d "venv" ]; then
    warning "venv уже существует. Хотите пересоздать? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        success "venv пересоздан"
    else
        info "Используем существующий venv"
    fi
else
    python3 -m venv venv
    success "venv создан"
fi

# Активация venv
source venv/bin/activate
success "venv активирован"

# =============================================================================
# Установка зависимостей
# =============================================================================

info "Обновление pip..."
pip install --upgrade pip --quiet

info "Установка зависимостей из requirements.txt..."
pip install -r requirements.txt --quiet

success "Все зависимости установлены"

# =============================================================================
# Настройка окружения
# =============================================================================

info "Настройка .env файла..."

if [ -f ".env" ]; then
    warning ".env уже существует"
    warning "Хотите пересоздать из .env.example? Текущий .env будет сохранен как .env.backup (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cp .env .env.backup
        cp .env.example .env
        success ".env пересоздан (старый сохранен как .env.backup)"
        warning "ВАЖНО: Отредактируйте .env и добавьте ваши API ключи!"
    else
        info "Используем существующий .env"
    fi
else
    cp .env.example .env
    success ".env создан из .env.example"
    warning "ВАЖНО: Отредактируйте .env и добавьте ваши API ключи!"
fi

# =============================================================================
# Создание директорий
# =============================================================================

info "Создание необходимых директорий..."

mkdir -p logs
mkdir -p .manus_cache
mkdir -p src/manus
mkdir -p src/webhooks
mkdir -p src/database

success "Все директории созданы"

# =============================================================================
# Проверка структуры проекта
# =============================================================================

info "Проверка структуры проекта..."

REQUIRED_FILES=(
    "src/openrouter/__init__.py"
    "src/manus/__init__.py"
    "config/settings.py"
    "requirements.txt"
)

ALL_GOOD=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        error "Отсутствует файл: $file"
        ALL_GOOD=false
    fi
done

if [ "$ALL_GOOD" = true ]; then
    success "Структура проекта корректна"
else
    error "Некоторые файлы отсутствуют. Проверьте структуру проекта."
    exit 1
fi

# =============================================================================
# Инициализация базы данных (опционально)
# =============================================================================

info "Хотите инициализировать базу данных SQLite? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    info "Создание базы данных..."

    # Создаем простую таблицу для задач
    python3 - << EOF
import sqlite3
import os

db_path = os.getenv('DB_PATH', './manus_tasks.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        type TEXT,
        status TEXT,
        github_url TEXT,
        manus_task_id TEXT,
        prompt TEXT,
        result TEXT,
        cost_usd REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT,
        event_type TEXT,
        payload TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    )
''')

conn.commit()
conn.close()
print("База данных инициализирована успешно")
EOF

    success "База данных создана"
fi

# =============================================================================
# Тестирование установки
# =============================================================================

info "Проверка что все модули импортируются..."

python3 - << EOF
try:
    from src.openrouter import OpenRouterClient
    from src.manus import ManusClient, ManusWebhookHandler
    from config.settings import Settings
    print("✅ Все импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    success "Все модули импортируются корректно"
else
    error "Проблемы с импортом модулей"
    exit 1
fi

# =============================================================================
# Финальные инструкции
# =============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
success "🎉 Development окружение настроено успешно!"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
info "Следующие шаги:"
echo ""
echo "  1. Активируйте virtual environment:"
echo "     ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "  2. Отредактируйте .env и добавьте ваши API ключи:"
echo "     ${GREEN}nano .env${NC}"
echo ""
echo "     Обязательные ключи:"
echo "       - OPENROUTER_API_KEY"
echo "       - MANUS_API_KEY"
echo "       - MANUS_WEBHOOK_SECRET (для webhooks)"
echo "       - GITHUB_TOKEN (для GitHub integration)"
echo ""
echo "  3. Запустите тесты:"
echo "     ${GREEN}pytest tests/${NC}"
echo ""
echo "  4. Попробуйте примеры:"
echo "     ${GREEN}python examples/basic_usage.py${NC}"
echo ""
echo "  5. (Опционально) Запустите dashboard:"
echo "     ${GREEN}python -m src.manus.dashboard${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
info "Документация: README.md, CLAUDE.md, ARCHITECTURE.md"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
