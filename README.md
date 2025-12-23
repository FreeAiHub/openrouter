# OpenRouter + Manus Integration

This repository provides a small, focused integration between OpenRouter and Manus AI.  
It exposes a simple Python client, webhook handler, and examples for running async LLM tasks via Manus.

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/FreeAiHub/openrouter.git
cd openrouter

# choose one: uv / pip / poetry, here is a simple pip example

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Fill in the required keys:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx
MANUS_API_KEY=sk-manus-xxxxxxxx
MANUS_BASE_URL=https://api.manus.ai/v1
```

Other variables in `.env.example` are optional and used for dashboards, GitHub webhooks, and monitoring.

### 3. Run tests

```bash
# all tests
pytest -q

# unit tests for Manus client
pytest tests/test_manus.py -q

# integration examples
pytest tests/test_full_integration.py tests/test_simple.py -q
```

### 4. Run example

The simplest way to see the integration in action:

```bash
python examples/manus_example.py
```

This script sends a task to Manus and prints the result from the ManusClient.

---

## How to Import

### Basic Usage

```python
from manus import ManusClient, ManusWebhookHandler

# Create Manus client
client = ManusClient(api_key="sk-manus-xxx")

# Create a task
task = client.create_task(
    prompt="Analyze this Python code",
    context="def hello(): print('Hello, world!')"
)

# Wait for result
result = client.wait_for_completion(task["task_id"])
print(result["result"])
```

### With OpenRouter

```python
from src.openrouter import OpenRouterClient, Message
from manus import ManusClient

# OpenRouter for chat
or_client = OpenRouterClient()
messages = [Message(role="user", content="What is AI?")]
response = or_client.chat_completion(messages)

# Manus for code analysis
manus_client = ManusClient()
task = manus_client.create_task(
    prompt="Review this code",
    context="code_here.py"
)
```

---

## Design Principles

Our architecture follows these core engineering principles:

- **Clear Boundaries**: Strict separation between client layer, webhook handlers, and persistence layer. Each component has a single responsibility.
- **Typed Models**: All external payloads use Pydantic models for validation and type safety. No raw dictionaries.
- **Explicit Error Handling**: Comprehensive exception hierarchy with retry logic and circuit breakers for external API calls.
- **Phase Separation**: Phase 1 focuses on core integration (Manus + OpenRouter). Phase 2 adds DX improvements (monitoring, webhooks, persistence).
- **Observability First**: Structured logging, metrics, and health checks built-in from day one, not bolted on later.

---

## Project Structure

Key parts of the project:

- `src/manus/`  
  - `client.py` – ManusClient, high‑level API for creating and polling tasks via Manus.  
  - `models.py` – Pydantic models for tasks, results, and internal payloads.  
  - `webhook.py` – ManusWebhookHandler for processing Manus webhooks.  
  - `exceptions.py` – typed exceptions for Manus errors and timeouts.  
  - `__init__.py` – public exports for `ManusClient` and `ManusWebhookHandler`.
- `examples/`  
  - `manus_example.py` – minimal example using ManusClient.
- `tests/`  
  - `test_manus.py` – unit tests for Manus integration.  
  - `test_full_integration.py`, `test_simple.py` – integration-style tests and flow checks.

See `PROJECT_STRUCTURE.txt` for a more detailed, commented structure description.

---

## Architecture

High‑level ideas:

- All external Manus access goes through `ManusClient`.  
- Webhook callbacks are handled by `ManusWebhookHandler` and can be wired to any ASGI/WSGI framework.  
- Pydantic models provide strict validation for inputs/outputs, making the integration safer to extend.

For a deeper explanation of design decisions and Phase 1 goals, see:

- `ARCHITECTURE.md` – core concepts and internal components.  
- `PHASE1_SUCCESS.md` – notes on completing Phase 1 (scope, testing, planned Phase 2).

---

## Environment & Configuration

Most configuration is done via environment variables:

- Minimal required variables are at the top of `.env.example`.  
- Optional settings cover GitHub webhooks, dashboards, databases, logging, and rate limiting.

You can keep your local `.env` small and only add optional variables if you enable corresponding features.

---

## Roadmap (Phase 2)

Phase 2 focuses on production-ready features: monitoring, webhooks, and persistence.

### 🎯 Planned Features

**1. Dashboard & Monitoring (UI)**  
- Real-time task monitoring with filters and pagination  
- REST API: `GET /api/tasks`, `GET /api/stats`  
- WebSocket for live updates  
- Simple API key authentication  
- [Issue #1](https://github.com/FreeAiHub/openrouter/issues/1)

**2. GitHub Webhooks Integration**  
- Automatic processing of GitHub Issues and PRs  
- Full flow: GitHub → Webhook → Validation → Manus → GitHub Update  
- Comprehensive failure handling and retry logic  
- Unit & integration tests with mocks  
- [Issue #2](https://github.com/FreeAiHub/openrouter/issues/2)

**3. Database & Task History**  
- Normalized schema: tasks, events, metrics, retry queue  
- Repository pattern with idempotency guarantees  
- Alembic migrations and backup strategy  
- Performance benchmarks (< 100ms queries)  
- [Issue #3](https://github.com/FreeAiHub/openrouter/issues/3)

### 📊 Success Metrics
- **Performance**: API response time < 200ms (p95)
- **Reliability**: 99.9% uptime, < 0.1% error rate
- **Test Coverage**: 90%+ across all Phase 2 components
- **Scalability**: Support 1000+ concurrent tasks

---

## Status

Phase 1 (Manus integration + tests) is complete:

- Manus client with typed models and error handling.  
- Webhook handler skeleton.  
- Unit and integration tests with high coverage.  

Phase 2 (dashboards, GitHub automation, extended monitoring) can be built on top of this foundation.

## Documentation

- `ARCHITECTURE.md` – internal architecture notes.
- `PHASE1_SUCCESS.md` – Phase 1 scope and status.
- `PROJECT_STRUCTURE.txt` – detailed file layout.
- `docs/archive/*` – internal guides and planning notes (not required for usage).

---

## Next Steps

To start contributing to Phase 2:

1. **Pick an issue**: Choose one of the three Phase 2 issues above
2. **Read the spec**: Each issue has detailed acceptance criteria
3. **Create a branch**: `git checkout -b feature/phase2-dashboard`
4. **Submit PR**: Include tests, documentation, and performance benchmarks

All code changes must trigger automated builds and tests via GitHub Actions.
