# 🏗️ Архитектура OpenRouter + Manus AI Integration

**Версия**: 1.0
**Дата**: 2025-12-23
**Статус**: В разработке

---

## 📋 Содержание

1. [Общая Архитектура](#общая-архитектура)
2. [Компоненты Системы](#компоненты-системы)
3. [Потоки Данных](#потоки-данных)
4. [База Данных](#база-данных)
5. [API Endpoints](#api-endpoints)
6. [Безопасность](#безопасность)
7. [Масштабирование](#масштабирование)

---

## 🌐 Общая Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                         ПОЛЬЗОВАТЕЛЬ                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌─────────┐   ┌──────────┐  ┌──────────┐
        │ GitHub  │   │   CLI    │  │   Web    │
        │  Issues │   │ Terminal │  │Dashboard │
        │   PRs   │   │          │  │          │
        └────┬────┘   └────┬─────┘  └────┬─────┘
             │             │             │
             │ Webhooks    │ Commands    │ HTTP
             │             │             │
             ▼             ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                     WEBHOOK SERVER (Flask)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   GitHub     │  │    Manus     │  │     API      │        │
│  │   Handler    │  │   Handler    │  │   Endpoints  │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
└─────────┼──────────────────┼──────────────────┼───────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Manus Client   │    │ OpenRouter      │                    │
│  │  - create_task  │    │ Client          │                    │
│  │  - get_status   │    │ - chat_complete │                    │
│  │  - wait_result  │    │ - streaming     │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
└───────────┼──────────────────────┼─────────────────────────────┘
            │                      │
            │                      │
            ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│    Manus AI API     │  │  OpenRouter API     │
│  - Task Processing  │  │  - AI Models        │
│  - Code Analysis    │  │  - Chat Completion  │
│  - Testing          │  │  - Embeddings       │
└─────────────────────┘  └─────────────────────┘
            │                      │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  SQLite Database     │
            │  - Tasks History     │
            │  - Events Log        │
            │  - Metrics           │
            └──────────────────────┘
```

---

## 🧩 Компоненты Системы

### 1. Frontend Layer

#### 1.1 GitHub Interface
- **Назначение**: Автоматическая интеграция с Issues и PR
- **Технологии**: GitHub Webhooks
- **События**:
  - `issues.opened` - Новый issue
  - `pull_request.opened` - Новый PR
  - `issue_comment.created` - Комментарий

#### 1.2 Web Dashboard
- **Назначение**: Визуальный интерфейс управления
- **Технологии**: Flask + Jinja2 + WebSockets
- **Функции**:
  - Просмотр активных задач
  - Создание новых задач
  - Статистика и метрики
  - Real-time обновления

#### 1.3 CLI Terminal
- **Назначение**: Командная строка для разработчиков
- **Технологии**: Rich library
- **Функции**:
  - Мониторинг задач
  - Цветной вывод
  - Прогресс-бары
  - Интерактивные таблицы

---

### 2. Webhook Server Layer

#### 2.1 Flask Application

**Файл**: `src/webhooks/app.py`

```python
┌─────────────────────────────────────┐
│         Flask App (Port 5001)       │
│                                     │
│  Routes:                            │
│  • POST /webhooks/github            │
│  • POST /webhooks/manus             │
│  • GET  /health                     │
│  • GET  /metrics                    │
└─────────────────────────────────────┘
```

**Обязанности**:
- Принимать webhooks от GitHub
- Принимать callbacks от Manus
- Валидировать signatures
- Маршрутизировать события

#### 2.2 GitHub Webhook Handler

**Файл**: `src/webhooks/github_handler.py`

```python
class GitHubWebhookHandler:
    """
    Обработка событий от GitHub
    """

    ┌─────────────────────────────┐
    │  GitHub Event               │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Verify Signature           │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Parse Payload              │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Create Manus Task          │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Save to Database           │
    └─────────────────────────────┘
```

#### 2.3 Manus Webhook Handler

**Файл**: `src/webhooks/manus_handler.py`

```python
class ManusWebhookHandler:
    """
    Обработка событий от Manus
    """

    ┌─────────────────────────────┐
    │  Manus Callback             │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Get Task Result            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Format Response            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Post GitHub Comment        │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Update Database            │
    └─────────────────────────────┘
```

---

### 3. Application Layer

#### 3.1 Manus Client

**Файл**: `src/manus/client.py`

```python
class ManusClient:
    """
    Клиент для Manus AI API
    """

    Methods:
    ┌────────────────────────────────────┐
    │ • create_task(prompt, context)     │
    │   → Создать новую задачу           │
    │                                    │
    │ • get_task(task_id)                │
    │   → Получить статус задачи         │
    │                                    │
    │ • wait_for_completion(task_id)     │
    │   → Ждать завершения               │
    │                                    │
    │ • analyze_code(code_url)           │
    │   → Анализ кода                    │
    │                                    │
    │ • test_function(function_url)      │
    │   → Тестирование функции           │
    └────────────────────────────────────┘
```

**Ответственность**:
- HTTP запросы к Manus API
- Обработка ответов
- Управление retries
- Polling статуса задач

#### 3.2 OpenRouter Client

**Файл**: `src/openrouter/client.py`

```python
class OpenRouterClient:
    """
    Enterprise клиент для OpenRouter API
    """

    Features:
    ┌────────────────────────────────────┐
    │ • Circuit Breaker Pattern          │
    │ • Automatic Retries                │
    │ • Connection Pooling               │
    │ • Cost Tracking                    │
    │ • Request/Response Logging         │
    │ • Type Safety (Pydantic)           │
    └────────────────────────────────────┘

    Methods:
    ┌────────────────────────────────────┐
    │ • chat_completion(messages)        │
    │ • stream_chat_completion(messages) │
    │ • estimate_cost(model, tokens)     │
    │ • get_metrics_summary()            │
    └────────────────────────────────────┘
```

#### 3.3 Monitor

**Файл**: `src/manus/monitor.py`

```python
class ManusMonitor:
    """
    Real-time мониторинг задач
    """

    ┌────────────────────────────────────┐
    │  Rich Terminal UI                  │
    │                                    │
    │  • Цветной вывод                   │
    │  • Прогресс-бары                   │
    │  • Live таблицы                    │
    │  • Spinner анимация                │
    │  • Event callbacks                 │
    └────────────────────────────────────┘
```

---

### 4. Database Layer

#### 4.1 SQLite Schema

**Файл**: `src/database/models.py`

```sql
┌─────────────────────────────────────────────────┐
│                  tasks                          │
├─────────────────┬───────────────────────────────┤
│ id              │ TEXT PRIMARY KEY              │
│ type            │ TEXT                          │
│ status          │ TEXT                          │
│ github_url      │ TEXT                          │
│ manus_task_id   │ TEXT                          │
│ prompt          │ TEXT                          │
│ result          │ JSON                          │
│ cost_usd        │ REAL                          │
│ created_at      │ TIMESTAMP                     │
│ completed_at    │ TIMESTAMP                     │
└─────────────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                  events                         │
├─────────────────┬───────────────────────────────┤
│ id              │ INTEGER PRIMARY KEY AUTO      │
│ task_id         │ TEXT (FK -> tasks.id)         │
│ event_type      │ TEXT                          │
│ payload         │ JSON                          │
│ timestamp       │ TIMESTAMP                     │
└─────────────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                 metrics                         │
├─────────────────┬───────────────────────────────┤
│ id              │ INTEGER PRIMARY KEY AUTO      │
│ metric_name     │ TEXT                          │
│ value           │ REAL                          │
│ tags            │ JSON                          │
│ timestamp       │ TIMESTAMP                     │
└─────────────────┴───────────────────────────────┘
```

---

## 🔄 Потоки Данных

### Flow 1: GitHub Issue → Manus → GitHub Comment

```
┌─────────────────────────────────────────────────────────────────┐
│                    ОСНОВНОЙ WORKFLOW                            │
└─────────────────────────────────────────────────────────────────┘

1️⃣  User создает Issue на GitHub
    │
    │ POST /repos/FreeAiHub/openrouter/issues
    │
    ▼
2️⃣  GitHub отправляет webhook
    │
    │ POST https://your-server.com/webhooks/github
    │ Headers:
    │   X-GitHub-Event: issues
    │   X-Hub-Signature-256: sha256=...
    │ Body:
    │   {
    │     "action": "opened",
    │     "issue": {
    │       "number": 123,
    │       "title": "Bug in client.py",
    │       "body": "Description..."
    │     }
    │   }
    │
    ▼
3️⃣  Flask App получает webhook
    │
    │ @app.route('/webhooks/github')
    │
    ▼
4️⃣  GitHubWebhookHandler обрабатывает
    │
    │ • Проверяет signature
    │ • Парсит payload
    │ • Извлекает данные issue
    │
    ▼
5️⃣  Создает задачу в Manus
    │
    │ manus_client.create_task(
    │   prompt=f"Analyze bug: {issue_title}",
    │   context=issue_body
    │ )
    │
    │ Response:
    │ {
    │   "task_id": "manus_abc123",
    │   "status": "pending"
    │ }
    │
    ▼
6️⃣  Сохраняет в БД
    │
    │ Task(
    │   id="task_123",
    │   type="github_issue",
    │   github_url="https://github.com/.../issues/123",
    │   manus_task_id="manus_abc123",
    │   status="pending"
    │ )
    │
    ▼
7️⃣  Возвращает response GitHub
    │
    │ {
    │   "status": "accepted",
    │   "task_id": "task_123"
    │ }
    │
    ▼
8️⃣  Manus обрабатывает задачу
    │
    │ • Анализирует код через OpenRouter
    │ • Генерирует решение
    │ • Создает отчет
    │
    ▼
9️⃣  Manus отправляет callback
    │
    │ POST https://your-server.com/webhooks/manus
    │ {
    │   "task_id": "manus_abc123",
    │   "status": "completed",
    │   "result": {
    │     "analysis": "...",
    │     "solution": "...",
    │     "confidence": 0.95
    │   }
    │ }
    │
    ▼
🔟  ManusWebhookHandler обрабатывает
    │
    │ • Получает результат
    │ • Форматирует для GitHub
    │
    ▼
1️⃣1️⃣  Создает комментарий в GitHub Issue
    │
    │ POST /repos/FreeAiHub/openrouter/issues/123/comments
    │ {
    │   "body": "## 🤖 Manus AI Analysis\n\n..."
    │ }
    │
    ▼
1️⃣2️⃣  Обновляет БД
    │
    │ UPDATE tasks
    │ SET status='completed',
    │     result='{...}',
    │     completed_at=NOW()
    │ WHERE id='task_123'
    │
    ▼
✅  ГОТОВО - Issue имеет автоматический ответ!
```

---

### Flow 2: Manual Task через Dashboard

```
1️⃣  User открывает Dashboard
    │
    │ http://localhost:5000
    │
    ▼
2️⃣  Заполняет форму создания задачи
    │
    │ Prompt: "Test the chat_completion function"
    │ Context: "https://github.com/.../client.py"
    │
    ▼
3️⃣  POST /api/tasks/create
    │
    │ {
    │   "prompt": "...",
    │   "context": "..."
    │ }
    │
    ▼
4️⃣  ManusClient.create_task()
    │
    ▼
5️⃣  Real-time мониторинг через WebSocket
    │
    │ ws://localhost:5000/ws/tasks/task_123
    │
    │ Messages:
    │ {"status": "pending"}
    │ {"status": "running", "progress": 50}
    │ {"status": "completed", "result": {...}}
    │
    ▼
6️⃣  Dashboard отображает результат
    │
    ▼
✅  User видит результат в real-time
```

---

### Flow 3: CLI Monitoring

```
1️⃣  Developer запускает monitor
    │
    │ $ python -m src.manus.monitor --task task_123
    │
    ▼
2️⃣  Monitor создает Rich Console
    │
    │ ┌─────────────────────────────────────┐
    │ │ 🔄 Task: task_123                   │
    │ │ Status: Running                     │
    │ │ Progress: ████████░░░░░░ 50%        │
    │ │ Elapsed: 00:02:15                   │
    │ └─────────────────────────────────────┘
    │
    ▼
3️⃣  Polling задачи каждые 2 секунды
    │
    │ while True:
    │   status = manus_client.get_task(task_id)
    │   update_display(status)
    │   sleep(2)
    │
    ▼
4️⃣  При завершении показывает результат
    │
    │ ┌─────────────────────────────────────┐
    │ │ ✅ Task Completed!                  │
    │ │                                     │
    │ │ Result:                             │
    │ │ • Analysis: Success                 │
    │ │ • Issues Found: 2                   │
    │ │ • Confidence: 95%                   │
    │ │                                     │
    │ │ Duration: 00:03:42                  │
    │ │ Cost: $0.00 (Free model)            │
    │ └─────────────────────────────────────┘
    │
    ▼
✅  Developer видит детальный отчет
```

---

## 🔒 Безопасность

### 1. Webhook Signature Verification

#### GitHub Webhooks

```python
import hmac
import hashlib

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Проверка подписи GitHub webhook
    """
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        f"sha256={expected}",
        signature
    )
```

#### Manus Webhooks

```python
def verify_manus_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Проверка подписи Manus webhook
    """
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

### 2. API Key Management

```python
# ❌ ПЛОХО - Hardcoded keys
api_key = "sk-Ng1s0QVjeZXa1DjQjJw8..."

# ✅ ХОРОШО - Environment variables
import os
api_key = os.getenv("MANUS_API_KEY")

# ✅ ЛУЧШЕ - Secrets manager (production)
from aws_secretsmanager import get_secret
api_key = get_secret("manus_api_key")
```

---

### 3. Input Validation

```python
from pydantic import BaseModel, HttpUrl, validator

class TaskRequest(BaseModel):
    prompt: str
    context: HttpUrl | None = None

    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v) < 10:
            raise ValueError("Prompt слишком короткий")
        if len(v) > 5000:
            raise ValueError("Prompt слишком длинный")
        return v
```

---

### 4. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/tasks/create', methods=['POST'])
@limiter.limit("10 per minute")
def create_task():
    # ...
```

---

## 📈 Масштабирование

### Текущая Архитектура (MVP)

```
┌────────────────────────────────┐
│  Single Server                 │
│                                │
│  • Flask App                   │
│  • SQLite Database             │
│  • File-based logs             │
│  • In-memory cache             │
└────────────────────────────────┘

Limits:
• ~100 requests/minute
• ~1000 tasks/day
• Single point of failure
```

---

### Масштабированная Архитектура (Production)

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                     (Nginx)                             │
└───────────┬─────────────────────────────┬───────────────┘
            │                             │
            ▼                             ▼
    ┌───────────────┐             ┌───────────────┐
    │  Flask App 1  │             │  Flask App 2  │
    │  (Container)  │             │  (Container)  │
    └───────┬───────┘             └───────┬───────┘
            │                             │
            └──────────────┬──────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │   PostgreSQL   │
                  │   (Managed)    │
                  └────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │     Redis      │
                  │   (Caching)    │
                  └────────────────┘
```

**Характеристики**:
- Горизонтальное масштабирование (N серверов)
- Распределенная база данных
- Кеширование для скорости
- Fault tolerance

---

### Мониторинг и Observability

```
┌────────────────────────────────────────┐
│         Application Metrics            │
└────────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────┐
    │  Prometheus    │  ← Сбор метрик
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │    Grafana     │  ← Визуализация
    └────────────────┘

Метрики:
• Request rate
• Response time
• Error rate
• Task completion rate
• API costs
```

---

## 📊 API Endpoints Reference

### Webhook Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/webhooks/github` | GitHub webhook receiver | Signature |
| POST | `/webhooks/manus` | Manus callback receiver | Signature |

### API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/tasks` | Список всех задач | API Key |
| GET | `/api/tasks/{id}` | Детали задачи | API Key |
| POST | `/api/tasks/create` | Создать задачу | API Key |
| GET | `/api/stats` | Статистика | API Key |
| GET | `/health` | Health check | None |
| GET | `/metrics` | Prometheus metrics | None |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/tasks/{id}` | Live updates задачи |
| `ws://host/ws/stats` | Live статистика |

---

## 🔄 State Machine для Tasks

```
         ┌─────────┐
         │ CREATED │
         └────┬────┘
              │
              ▼
         ┌─────────┐
         │ PENDING │ ← Task создан, ждет обработки
         └────┬────┘
              │
              ▼
         ┌─────────┐
         │ RUNNING │ ← Manus обрабатывает
         └────┬────┘
              │
         ┌────┴─────┐
         │          │
         ▼          ▼
    ┌──────────┐ ┌──────┐
    │COMPLETED │ │FAILED│
    └──────────┘ └──────┘
         │          │
         ▼          ▼
    ┌─────────────────┐
    │    ARCHIVED     │
    └─────────────────┘
```

**Переходы**:
- `CREATED` → `PENDING`: Задача сохранена в БД
- `PENDING` → `RUNNING`: Manus начал обработку
- `RUNNING` → `COMPLETED`: Успешное завершение
- `RUNNING` → `FAILED`: Ошибка выполнения
- `COMPLETED/FAILED` → `ARCHIVED`: Через 30 дней

---

## 💡 Design Principles

### 1. Separation of Concerns
- Каждый компонент имеет одну ответственность
- Четкие границы между слоями
- Минимум coupling между модулями

### 2. Fail-Safe
- Graceful degradation
- Retry mechanisms
- Circuit breakers
- Comprehensive error handling

### 3. Observability
- Логирование всех событий
- Метрики производительности
- Distributed tracing
- Health checks

### 4. Scalability
- Stateless application servers
- Database connection pooling
- Async processing where possible
- Caching strategies

### 5. Security First
- Input validation
- Authentication/Authorization
- Secrets management
- Rate limiting

---

## 📝 Заметки

- Архитектура основана на микросервисном подходе
- Легко масштабируется горизонтально
- Готова к containerization (Docker)
- Поддерживает cloud deployment (AWS, GCP, Azure)
- Следует best practices Flask + SQLAlchemy

---

**Последнее обновление**: 2025-12-23
**Версия**: 1.0
**Автор**: Claude + Team
