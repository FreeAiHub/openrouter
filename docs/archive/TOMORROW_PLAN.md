# 🌅 План на Завтра - Быстрый Старт

**Дата**: 2025-12-24
**Цель дня**: Организация проекта + Real-Time Monitor + Web Dashboard + Webhooks

---

## ⏰ Расписание

### 🌅 9:00 - 12:00 | ФАЗА 1: Организация

#### 9:00-9:30 | Структура Manus
```bash
mkdir -p src/manus
mkdir -p src/webhooks
mkdir -p scripts
mkdir -p logs

# Создать файлы
touch src/manus/__init__.py
touch src/manus/client.py
touch src/manus/models.py
touch src/manus/exceptions.py
touch src/manus/monitor.py
touch src/manus/dashboard.py
```

#### 9:30-10:00 | Рефакторинг manus_client.py
- [ ] Переместить код в `src/manus/client.py`
- [ ] Создать Pydantic models в `src/manus/models.py`
- [ ] Обновить imports

#### 10:00-10:30 | Документация
- [ ] Создать `ARCHITECTURE.md`
- [ ] Создать `WEBHOOKS_PLAN.md`
- [ ] Обновить `README.md`

#### 10:30-11:00 | Environment Setup
- [ ] Обновить `.env.example`
- [ ] Создать `scripts/setup_dev.sh`
- [ ] Обновить `.gitignore`

#### 11:00-12:00 | Real-Time Monitor
- [ ] Создать `src/manus/monitor.py`
- [ ] Добавить Rich library
- [ ] Тестировать локально

---

### ☀️ 13:00 - 15:00 | ФАЗА 2: Web Dashboard

#### 13:00-14:30 | Dashboard Development
- [ ] Создать Flask app в `src/manus/dashboard.py`
- [ ] HTML templates
- [ ] REST API endpoints
- [ ] WebSocket для live updates

#### 14:30-15:00 | Dashboard Testing
- [ ] Запустить локально
- [ ] Проверить все routes
- [ ] Тест создания задач

---

### 🌆 15:00 - 18:00 | ФАЗА 3: Webhooks

#### 15:00-16:00 | GitHub Webhook Handler
- [ ] Создать `src/webhooks/github_handler.py`
- [ ] Issue created event
- [ ] PR opened event
- [ ] Signature verification

#### 16:00-17:00 | Manus Webhook Handler
- [ ] Создать `src/webhooks/manus_handler.py`
- [ ] Task completed event
- [ ] GitHub comment creation

#### 17:00-17:30 | Flask Webhook App
- [ ] Создать `src/webhooks/app.py`
- [ ] Routes для GitHub и Manus
- [ ] Health check endpoint

#### 17:30-18:00 | Database + Tests
- [ ] Создать `src/database/models.py`
- [ ] SQLite schema
- [ ] End-to-end tests

---

## 🎯 Конкретные Задачи

### Задача 1: Переместить Manus Client

**Было**:
```
manus_client.py (в корне)
```

**Станет**:
```
src/manus/
├── __init__.py
├── client.py
├── models.py
├── exceptions.py
└── webhook.py
```

**Команды**:
```bash
# Создать структуру
mkdir -p src/manus
cd src/manus

# Создать файлы
cat > __init__.py << 'EOF'
"""Manus AI Integration Package"""
from .client import ManusClient
from .webhook import ManusWebhookHandler

__all__ = ["ManusClient", "ManusWebhookHandler"]
EOF

# Переместить существующий код
mv ../../manus_client.py ./client.py
```

---

### Задача 2: Real-Time Monitor

**Файл**: `src/manus/monitor.py`

**Зависимости**:
```bash
pip install rich websockets
```

**Основной функционал**:
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import asyncio

class ManusMonitor:
    def __init__(self, client):
        self.client = client
        self.console = Console()

    async def track_task(self, task_id, interval=2):
        """Отслеживать задачу в реальном времени"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]Task {task_id}", total=100)

            while not progress.finished:
                status = await self.client.get_task(task_id)

                if status.get("status") == "completed":
                    progress.update(task, completed=100)
                    break
                elif status.get("status") == "failed":
                    self.console.print(f"[red]Task failed: {status.get('error')}")
                    break

                await asyncio.sleep(interval)
```

---

### Задача 3: Web Dashboard

**Файл**: `src/manus/dashboard.py`

**Структура**:
```python
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.manus import ManusClient

app = Flask(__name__)
CORS(app)

client = ManusClient()

@app.route('/')
def index():
    """Главная страница dashboard"""
    return render_template('dashboard.html')

@app.route('/api/tasks')
def list_tasks():
    """API: Список всех задач"""
    # TODO: Получить из БД
    return jsonify({"tasks": []})

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """API: Создать новую задачу"""
    data = request.json
    task = client.create_task(
        prompt=data['prompt'],
        context=data.get('context')
    )
    return jsonify(task)

@app.route('/api/stats')
def stats():
    """API: Статистика"""
    return jsonify({
        "total": 0,
        "completed": 0,
        "failed": 0,
        "running": 0
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**HTML Template**: `src/manus/templates/dashboard.html`

---

### Задача 4: GitHub Webhooks

**Файл**: `src/webhooks/github_handler.py`

**Flow**:
```python
import hmac
import hashlib
from flask import request, jsonify
from src.manus import ManusClient

class GitHubWebhookHandler:
    def __init__(self):
        self.client = ManusClient()
        self.secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    def verify_signature(self, payload, signature):
        """Проверить GitHub webhook signature"""
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    def handle_issue_opened(self, issue_data):
        """Обработать новый issue"""
        title = issue_data['title']
        body = issue_data['body']
        url = issue_data['html_url']

        # Создать задачу в Manus
        task = self.client.create_task(
            prompt=f"Analyze GitHub Issue: {title}\n\n{body}",
            context=url
        )

        return {
            "status": "task_created",
            "manus_task_id": task.get('id')
        }

    def process(self, request):
        """Обработать webhook request"""
        # Проверить signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not self.verify_signature(request.data, signature):
            return jsonify({"error": "Invalid signature"}), 403

        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json

        if event_type == 'issues':
            action = payload['action']
            if action == 'opened':
                return self.handle_issue_opened(payload['issue'])

        return jsonify({"status": "ignored"})
```

---

### Задача 5: Database для истории

**Файл**: `src/database/models.py`

```python
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    type = Column(String)  # 'github_issue', 'pr_review', 'manual'
    status = Column(String)  # 'pending', 'running', 'completed', 'failed'
    github_url = Column(String, nullable=True)
    manus_task_id = Column(String)
    prompt = Column(String)
    result = Column(JSON, nullable=True)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Инициализация
engine = create_engine('sqlite:///manus_tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
```

---

## 📋 Checklist на Конец Дня

### Обязательно
- [ ] Структура `src/manus/` создана
- [ ] `manus_client.py` перемещен и рефакторен
- [ ] Real-Time Monitor работает
- [ ] Web Dashboard запускается на localhost:5000
- [ ] Webhook endpoints созданы (даже если не развернуты)
- [ ] База данных инициализирована
- [ ] `.env.example` обновлен
- [ ] `.gitignore` обновлен

### Желательно
- [ ] Документация обновлена (ARCHITECTURE.md, WEBHOOKS_PLAN.md)
- [ ] Tests написаны
- [ ] README.md обновлен с новыми инструкциями

### Можно отложить
- [ ] Production deployment webhooks
- [ ] CI/CD pipeline
- [ ] Docker контейнеры

---

## 🛠️ Команды для Быстрого Старта

### Утренняя Инициализация

```bash
cd /Users/investing/GitHub/openrouter-1

# Создать структуру
mkdir -p src/manus src/webhooks src/database scripts logs .manus_cache

# Создать файлы
touch src/manus/{__init__.py,client.py,models.py,exceptions.py,monitor.py,dashboard.py}
touch src/webhooks/{__init__.py,app.py,github_handler.py,manus_handler.py}
touch src/database/{__init__.py,models.py}

# Установить зависимости
pip install rich flask flask-cors websockets sqlalchemy

# Проверить структуру
tree -L 3 src/
```

### Тестирование компонентов

```bash
# Тест Monitor
python -m src.manus.monitor

# Тест Dashboard
python -m src.manus.dashboard
# Открыть: http://localhost:5000

# Тест Webhook App
python -m src.webhooks.app
# curl http://localhost:5001/health
```

---

## 💡 Полезные Snippets

### Быстрое создание __init__.py

```bash
cat > src/manus/__init__.py << 'EOF'
"""
Manus AI Integration Package

Provides:
- ManusClient: API client
- ManusMonitor: Real-time monitoring
- ManusWebhookHandler: Webhook processing
"""
from .client import ManusClient
from .monitor import ManusMonitor
from .webhook import ManusWebhookHandler

__version__ = "0.1.0"
__all__ = ["ManusClient", "ManusMonitor", "ManusWebhookHandler"]
EOF
```

### Быстрый .gitignore update

```bash
cat >> .gitignore << 'EOF'

# Manus specific
.manus_cache/
manus_tasks.db
manus_tasks.db-journal

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
EOF
```

---

## 🎯 Ожидаемый Результат

К концу дня у вас будет:

```
openrouter-1/
├── src/
│   ├── manus/              ✅ Организованный код Manus
│   │   ├── client.py       ✅ Refactored
│   │   ├── monitor.py      ✅ Работает
│   │   └── dashboard.py    ✅ Работает
│   │
│   ├── webhooks/           ✅ Webhook handlers
│   │   ├── app.py          ✅ Flask app
│   │   ├── github_handler.py
│   │   └── manus_handler.py
│   │
│   └── database/           ✅ Persistence
│       └── models.py       ✅ SQLAlchemy
│
├── scripts/
│   └── setup_dev.sh        ✅ Автоматизация
│
├── ARCHITECTURE.md         ✅ Документация
├── WEBHOOKS_PLAN.md        ✅ План webhooks
└── .env.example            ✅ Обновлен
```

---

## 📞 Если что-то пойдет не так

### Проблема: Import errors
```bash
# Решение: Убедиться что в каждой директории есть __init__.py
find src -type d -exec touch {}/__init__.py \;
```

### Проблема: Rich не устанавливается
```bash
# Решение: Обновить pip
pip install --upgrade pip
pip install rich
```

### Проблема: Flask не находит templates
```bash
# Решение: Создать папку templates
mkdir -p src/manus/templates
```

---

## 🚀 Мотивация

После завтрашнего дня вы будете иметь:

1. ✅ **Профессиональную структуру** проекта
2. ✅ **Красивый терминал** с real-time мониторингом
3. ✅ **Web интерфейс** для управления задачами
4. ✅ **Готовую базу** для webhook автоматизации
5. ✅ **Фундамент** для production deployment

**Это будет крутой проект!** 🔥

---

**Начинаем завтра в 9:00! Удачи! 🎯**
