# 🎯 План Развития Проекта OpenRouter + Manus AI

**Дата создания**: 2025-12-23
**Статус**: Активная разработка
**Цель**: Создание полноценной enterprise-grade интеграции OpenRouter + Manus AI с автоматизацией через GitHub webhooks

---

## 📊 Текущий Статус Проекта

| Компонент | Статус | Файл/Путь | Примечания |
|-----------|--------|-----------|------------|
| OpenRouter API Client | ✅ Готово | [src/openrouter/](src/openrouter/) | Enterprise-grade клиент |
| Manus Client | ✅ Готово | [manus_client.py](manus_client.py) | Базовая интеграция |
| Configuration | ✅ Готово | [config/settings.py](config/settings.py) | Pydantic settings |
| Examples | ✅ Готово | [examples/](examples/) | 7 практических примеров |
| Tests | ✅ Готово | [tests/](tests/) | Unit + Integration |
| Documentation | ✅ Готово | [README.md](README.md), [docs/](docs/) | Полная документация |
| Real-Time Monitor | 📋 План | - | Нужно добавить |
| Web Dashboard | 📋 План | - | Нужно создать |
| GitHub Webhooks | 📋 План | - | Основная задача |
| Deployment | 📋 План | - | Docker + CI/CD |

---

## 🏗️ Архитектура Проекта

```
openrouter-1/
│
├── 📁 src/
│   ├── openrouter/              # ✅ Core OpenRouter API
│   │   ├── __init__.py
│   │   ├── client.py            # Enterprise client
│   │   ├── models.py            # Pydantic models
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── utils.py
│   │
│   └── services/                # ✅ Higher-level services
│       ├── __init__.py
│       ├── conversation.py
│       ├── streaming.py
│       └── cost_tracker.py
│
├── 📁 config/                   # ✅ Configuration
│   ├── __init__.py
│   └── settings.py              # Pydantic settings
│
├── 📁 examples/                 # ✅ Usage examples
│   ├── basic_usage.py           # 7 examples
│   ├── original_examples.py
│   └── original_test.py
│
├── 📁 tests/                    # ✅ Tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_integration.py
│
├── 📁 docs/                     # ✅ Documentation
│   └── DEPLOYMENT.md
│
├── 📄 manus_client.py           # ✅ Manus integration
├── 📄 requirements.txt          # ✅ Dependencies
├── 📄 .env.example              # ✅ Environment template
├── 📄 README.md                 # ✅ Main docs
└── 📄 CLAUDE.md                 # 📍 ВЫ ЗДЕСЬ - План развития
```

---

## 🎯 План на Завтра: Фаза 1 - Организация

### Шаг 1: Наведение Порядка (30 минут)

#### 1.1 Структурировать файлы Manus

**Цель**: Переместить Manus компоненты в правильную структуру

**Задачи**:
- [ ] Создать директорию `src/manus/`
- [ ] Переместить `manus_client.py` → `src/manus/client.py`
- [ ] Создать `src/manus/__init__.py`
- [ ] Создать `src/manus/models.py` для Manus Pydantic моделей
- [ ] Создать `src/manus/exceptions.py` для Manus исключений

**Файлы для создания**:
```python
# src/manus/__init__.py
from .client import ManusClient
from .webhook import ManusWebhookHandler

__all__ = ["ManusClient", "ManusWebhookHandler"]
```

**Результат**: Чистая структура с разделением OpenRouter и Manus кода

---

#### 1.2 Добавить недостающие компоненты

**Файлы из Ubuntu сервера** (упомянутые в вашем сообщении):

- [ ] `manus_realtime_monitor.py` → `src/manus/monitor.py`
- [ ] `manus_dashboard.py` → `src/manus/dashboard.py`
- [ ] `manus_demo.py` → `examples/manus_demo.py`

**Вопрос**: У вас есть эти файлы локально? Если нет, создадим новые.

---

#### 1.3 Обновить .gitignore

**Добавить**:
```gitignore
# Manus specific
.manus_cache/
manus_tasks.db

# Logs
logs/
*.log

# Environment
.env
.env.local
.env.production

# OS
.DS_Store
Thumbs.db
```

**Результат**: Защита от случайного коммита секретов

---

### Шаг 2: Документация (20 минут)

#### 2.1 Создать ARCHITECTURE.md

**Содержание**:
- Общая архитектура системы
- Поток данных GitHub → Manus → OpenRouter
- Диаграммы взаимодействия компонентов
- Принципы проектирования

#### 2.2 Создать WEBHOOKS_PLAN.md

**Детальный план реализации webhooks**:
1. GitHub Issue webhook endpoint
2. Manus task completion webhook
3. Автоматическое создание комментариев
4. Обработка ошибок

#### 2.3 Обновить README.md

**Добавить секции**:
- Интеграция с Manus AI
- Quick Start для обеих систем
- Примеры webhook workflow

---

### Шаг 3: Environment Setup (15 минут)

#### 3.1 Расширить .env.example

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEFAULT_MODEL=xiaomi/mimo-v2-flash:free
ENVIRONMENT=development

# Manus AI Configuration
MANUS_API_KEY=your-manus-api-key-here
MANUS_BASE_URL=https://api.manus.ai/v1
MANUS_WEBHOOK_SECRET=your-webhook-secret

# GitHub Configuration (для webhooks)
GITHUB_TOKEN=your-github-pat
GITHUB_WEBHOOK_SECRET=your-github-webhook-secret
GITHUB_REPO=FreeAiHub/openrouter

# Application Settings
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=9090

# Database (для сохранения истории задач)
DB_PATH=./manus_tasks.db
```

#### 3.2 Создать setup script

**Файл**: `scripts/setup_dev.sh`

```bash
#!/bin/bash
# Автоматическая настройка dev окружения

echo "🚀 Настройка OpenRouter + Manus Dev Environment"

# Создать venv
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Скопировать .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env создан - заполните API ключи!"
else
    echo "⚠️  .env уже существует"
fi

# Создать директории
mkdir -p logs
mkdir -p .manus_cache

echo "✅ Setup завершен!"
echo "📝 Следующий шаг: отредактируйте .env и добавьте API ключи"
```

---

## 🎯 План на Завтра: Фаза 2 - Разработка

### Шаг 4: Real-Time Monitor (1 час)

**Цель**: Создать систему мониторинга задач Manus в реальном времени

#### 4.1 Создать src/manus/monitor.py

**Функционал**:
- Отслеживание статуса задач
- Live-обновления в терминале
- Цветной вывод
- Прогресс-бары
- Callbacks для событий

**Технологии**:
```python
# Rich для красивого терминала
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

# Asyncio для real-time updates
import asyncio
```

#### 4.2 Пример использования

```python
from src.manus import ManusClient
from src.manus.monitor import ManusMonitor

# Создать monitor
monitor = ManusMonitor(client=ManusClient())

# Отслеживать задачу
monitor.track_task(
    task_id="task_123",
    on_progress=lambda p: print(f"Progress: {p}%"),
    on_complete=lambda r: print(f"Done: {r}")
)
```

---

### Шаг 5: Web Dashboard (1.5 часа)

**Цель**: Web-интерфейс для управления задачами

#### 5.1 Создать src/manus/dashboard.py

**Стек**:
- Flask для backend
- WebSockets для live updates
- HTML/CSS/JS для frontend
- Chart.js для графиков

**Функции**:
1. **Список задач** с статусами
2. **Создание новых задач** через форму
3. **Live-статистика**: успешных/неудачных задач
4. **История выполнения**
5. **Метрики стоимости** (через OpenRouter)

#### 5.2 Routes

```python
@app.route('/')
def index():
    # Dashboard главная страница

@app.route('/api/tasks')
def list_tasks():
    # Список всех задач

@app.route('/api/tasks/<task_id>')
def get_task(task_id):
    # Детали задачи

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    # Создать новую задачу
```

#### 5.3 Запуск

```bash
python -m src.manus.dashboard
# Откроется на http://localhost:5000
```

---

### Шаг 6: GitHub Webhooks Integration (2 часа)

**Цель**: Автоматизация GitHub ↔ Manus

#### 6.1 Создать src/webhooks/github_handler.py

**События для обработки**:

1. **Issue Created** → Отправить в Manus для анализа
2. **PR Opened** → Code review через Manus
3. **PR Updated** → Повторный анализ
4. **Comment Added** → Обработать команды

**Пример flow**:

```
GitHub: New Issue "Bug in client.py"
    ↓
Webhook → Flask endpoint
    ↓
Create Manus Task: "Analyze bug in client.py"
    ↓
Manus анализирует через OpenRouter
    ↓
Manus возвращает результат
    ↓
GitHub: Создать комментарий с решением
```

#### 6.2 Создать src/webhooks/manus_handler.py

**Обработка событий от Manus**:

1. **Task Completed** → Создать комментарий в GitHub
2. **Task Failed** → Уведомить об ошибке
3. **Task Progress** → Обновить статус

#### 6.3 Flask Application

**Файл**: `src/webhooks/app.py`

```python
from flask import Flask, request, jsonify
from src.webhooks.github_handler import GitHubWebhookHandler
from src.webhooks.manus_handler import ManusWebhookHandler

app = Flask(__name__)

@app.route('/webhooks/github', methods=['POST'])
def github_webhook():
    """Endpoint для GitHub webhooks"""
    handler = GitHubWebhookHandler()
    return handler.process(request)

@app.route('/webhooks/manus', methods=['POST'])
def manus_webhook():
    """Endpoint для Manus webhooks"""
    handler = ManusWebhookHandler()
    return handler.process(request)

@app.route('/health')
def health():
    return {"status": "ok"}
```

---

### Шаг 7: Database для истории (30 минут)

**Цель**: Сохранять историю задач для аналитики

#### 7.1 SQLite Schema

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    type TEXT,  -- 'github_issue', 'pr_review', 'manual'
    status TEXT,  -- 'pending', 'running', 'completed', 'failed'
    github_url TEXT,
    manus_task_id TEXT,
    prompt TEXT,
    result TEXT,
    cost_usd REAL,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    event_type TEXT,
    payload JSON,
    timestamp TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);
```

#### 7.2 ORM Models

**Файл**: `src/database/models.py`

```python
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    type = Column(String)
    status = Column(String)
    # ... другие поля
```

---

## 🎯 План на Завтра: Фаза 3 - Тестирование

### Шаг 8: End-to-End Testing (1 час)

#### 8.1 Тестовый сценарий

1. ✅ **Создать тестовый Issue на GitHub**
2. ✅ **Webhook срабатывает** → отправляет в Manus
3. ✅ **Manus обрабатывает** через OpenRouter
4. ✅ **Результат возвращается** → создается комментарий
5. ✅ **Проверить базу данных** → задача сохранена

#### 8.2 Integration Tests

**Файл**: `tests/test_webhook_flow.py`

```python
def test_github_issue_to_manus_flow():
    # 1. Симулировать GitHub webhook
    # 2. Проверить создание Manus задачи
    # 3. Дождаться результата
    # 4. Проверить комментарий в GitHub
```

---

## 📋 Детальный Checklist на Завтра

### 🌅 Утро (9:00 - 12:00)

- [ ] **9:00-9:30** - Создать структуру `src/manus/`
- [ ] **9:30-10:00** - Переместить и рефакторить `manus_client.py`
- [ ] **10:00-10:30** - Создать `ARCHITECTURE.md` и `WEBHOOKS_PLAN.md`
- [ ] **10:30-11:00** - Обновить `.env.example` и создать setup script
- [ ] **11:00-12:00** - Создать Real-Time Monitor (`src/manus/monitor.py`)

### ☀️ День (12:00 - 15:00)

- [ ] **12:00-13:00** - Перерыв
- [ ] **13:00-14:30** - Создать Web Dashboard (`src/manus/dashboard.py`)
- [ ] **14:30-15:00** - Тестирование dashboard локально

### 🌆 Вечер (15:00 - 18:00)

- [ ] **15:00-17:00** - Создать GitHub Webhooks integration
  - [ ] `src/webhooks/github_handler.py`
  - [ ] `src/webhooks/manus_handler.py`
  - [ ] `src/webhooks/app.py`
- [ ] **17:00-17:30** - Создать Database models
- [ ] **17:30-18:00** - End-to-End тесты

---

## 🎯 Метрики Успеха

### День 1 (Завтра)

- [x] ✅ Чистая структура проекта
- [ ] ✅ Real-Time Monitor работает
- [ ] ✅ Web Dashboard доступен на localhost
- [ ] ✅ Webhook endpoints созданы
- [ ] ✅ База данных инициализирована
- [ ] ✅ Все тесты проходят

### День 2 (Послезавтра)

- [ ] ✅ Webhooks развернуты на production сервере
- [ ] ✅ GitHub repository подключен
- [ ] ✅ Первый успешный Issue → Manus → Comment flow
- [ ] ✅ Документация обновлена
- [ ] ✅ CI/CD pipeline настроен

### Неделя 1

- [ ] ✅ 10+ успешных автоматизированных Issue resolutions
- [ ] ✅ Dashboard показывает метрики
- [ ] ✅ Стоимость операций отслеживается
- [ ] ✅ Команда может использовать систему

---

## 💰 Оценка Стоимости

### Разработка (FREE)

- OpenRouter: `xiaomi/mimo-v2-flash:free` → **$0.00**
- Manus API: (нужно уточнить pricing)
- GitHub: Free tier → **$0.00**

### Production

**Сценарий**: 100 Issues/день

- OpenRouter: 100 × 2000 tokens × $0.00 = **$0.00** (free models)
- Manus: (уточнить)
- Infrastructure: $5-10/месяц (VPS для webhooks)

**Итого**: ~$10/месяц для полной автоматизации

---

## 🛠️ Технический Stack

### Backend
- **Python 3.11+**
- **Flask** - Webhook endpoints
- **SQLAlchemy** - ORM
- **Pydantic** - Validation
- **Requests** - HTTP client

### Frontend (Dashboard)
- **Flask** - Server
- **Jinja2** - Templates
- **Chart.js** - Графики
- **WebSockets** - Live updates

### Infrastructure
- **Git** - Version control
- **GitHub Actions** - CI/CD
- **Docker** - Containerization
- **Nginx** - Reverse proxy (production)

### Monitoring
- **Rich** - Terminal UI
- **Prometheus** - Metrics (optional)
- **Structlog** - Logging

---

## 📚 Документация для Изучения

### Перед началом работы:

1. **Manus API Docs**: https://open.manus.ai/docs
2. **GitHub Webhooks**: https://docs.github.com/en/webhooks
3. **OpenRouter Models**: https://openrouter.ai/models
4. **Flask Webhooks**: https://flask.palletsprojects.com/

### Референсы в коде:

- [src/openrouter/client.py](src/openrouter/client.py) - Пример enterprise client
- [config/settings.py](config/settings.py) - Pydantic настройки
- [tests/test_integration.py](tests/test_integration.py) - Integration testing

---

## 🚨 Важные Напоминания

### Безопасность

1. ⚠️ **НИКОГДА** не коммитить `.env`
2. ⚠️ **Всегда** проверять webhook signatures
3. ⚠️ **Использовать** secrets manager в production
4. ⚠️ **Ограничить** rate limiting на endpoints

### API Keys

```bash
# НЕ делитесь этими ключами!
MANUS_API_KEY=sk-Ng1s... (из вашего сообщения)
OPENROUTER_API_KEY=(ваш ключ)
GITHUB_TOKEN=(ваш PAT)
```

### Git Workflow

```bash
# Всегда перед работой
git pull origin main

# После каждого шага
git add .
git commit -m "feat: описание изменений"

# В конце дня
git push origin main
```

---

## 📞 Вопросы для Уточнения

Перед началом работы завтра, нужно уточнить:

1. **Manus API Pricing**: Какая модель оплаты? Free tier?
2. **Файлы с Ubuntu**: Есть ли локально `manus_realtime_monitor.py`, `manus_dashboard.py`, `manus_demo.py`?
3. **GitHub Repo**: У вас есть admin доступ к https://github.com/FreeAiHub/openrouter?
4. **Deployment**: Где планируете развернуть webhooks? (Heroku, VPS, AWS?)
5. **Приоритеты**: Что важнее: Monitor, Dashboard или Webhooks?

---

## 🎯 Итоговая Цель

**К концу завтрашнего дня иметь**:

1. ✅ Чистую, организованную структуру проекта
2. ✅ Работающий Real-Time Monitor
3. ✅ Web Dashboard для визуализации
4. ✅ Базовую webhook integration (локально)
5. ✅ Полную документацию процесса
6. ✅ Готовность к production deployment

**Результат**: Полноценная система автоматизации GitHub ↔ Manus ↔ OpenRouter

---

## 📝 Заметки

- Этот файл - живой документ, обновляется по мере прогресса
- Отмечайте выполненные задачи галочками
- Добавляйте новые идеи в секцию "Идеи для будущего"
- Фиксируйте проблемы и решения

---

## 💡 Идеи для Будущего

- [ ] Поддержка нескольких GitHub репозиториев
- [ ] Slack/Discord уведомления
- [ ] Автоматическое создание PR с фиксами
- [ ] Machine Learning для приоритизации задач
- [ ] Интеграция с Jira/Linear
- [ ] Мобильное приложение для мониторинга

---

**Последнее обновление**: 2025-12-23
**Следующий пересмотр**: После завершения Фазы 1

**Готовы начать? Вперед! 🚀**
