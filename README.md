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
