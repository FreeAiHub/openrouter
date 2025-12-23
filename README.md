# OpenRouter API Integration - Enterprise Edition

## 🎯 Overview

Enterprise-grade Python integration for OpenRouter API with production-ready features:

- ✅ Type-safe with Pydantic models
- ✅ Automatic retries with exponential backoff
- ✅ Circuit breaker pattern for fault tolerance
- ✅ Comprehensive error handling
- ✅ Cost tracking and monitoring
- ✅ Request/response logging
- ✅ Connection pooling
- ✅ Configuration management
- ✅ Test coverage

## 📋 Prerequisites

- Python 3.9+
- OpenRouter API key
- pip or poetry for dependency management

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd openrouter-integration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env
```

Required `.env` configuration:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEFAULT_MODEL=xiaomi/mimo-v2-flash:free
ENVIRONMENT=development
```

### 3. Basic Usage

```python
from src.openrouter import OpenRouterClient, Message

# Create client
with OpenRouterClient() as client:
    # Send message
    messages = [Message(role="user", content="Hello!")]
    response = client.chat_completion(messages)
    
    # Print response
    print(response.choices[0].message.content)
```

### 4. Run Examples

```bash
# Basic examples
python examples/basic_usage.py

# Streaming example
python examples/streaming_demo.py

# Batch processing
python examples/batch_processing.py
```

## 📚 Features

### Type-Safe API

All requests and responses use Pydantic models:

```python
from src.openrouter import Message, ChatCompletionResponse

messages = [Message(role="user", content="Hello")]
response: ChatCompletionResponse = client.chat_completion(messages)
```

### Automatic Retries

Built-in retry logic with exponential backoff:

```python
# Configured in settings
MAX_RETRIES=3
RETRY_DELAY=2
```

### Circuit Breaker

Prevents cascading failures:

```python
# Automatically handles:
# - Failure threshold: 5 errors
# - Recovery timeout: 60 seconds
# - States: CLOSED -> OPEN -> HALF_OPEN
```

### Cost Tracking

Monitor API costs in real-time:

```python
# Get cost estimate
cost = client.estimate_cost(
    model="xiaomi/mimo-v2-flash:free",
    input_tokens=100,
    output_tokens=50
)
print(cost.format_cost())  # $0.00 (Free)

# Get metrics summary
summary = client.get_metrics_summary()
print(f"Total cost: {summary['total_cost_usd']}")
```

### Streaming Support

Real-time response streaming:

```python
for chunk in client.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### Error Handling

Comprehensive exception hierarchy:

```python
from src.openrouter.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError
)

try:
    response = client.chat_completion(messages)
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except AuthenticationError:
    print("Invalid API key")
```

## 🏗️ Architecture

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │
┌────────▼────────┐
│   OpenRouter    │◄─────── Circuit Breaker
│     Client      │
└────────┬────────┘
         │
    ┌────┼────┐
    │    │    │
┌───▼──┐ │ ┌──▼────┐
│Retry │ │ │Session│
│Logic │ │ │Pool   │
└──────┘ │ └───────┘
         │
    ┌────▼─────┐
    │OpenRouter│
    │   API    │
    └──────────┘
```

### Components

- **Client**: Core API client with retry logic
- **Circuit Breaker**: Fault tolerance mechanism
- **Session Pool**: Connection pooling for performance
- **Models**: Pydantic schemas for type safety
- **Exceptions**: Custom exception hierarchy
- **Config**: Centralized configuration management

## 📊 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | Your API key |
| `DEFAULT_MODEL` | No | `xiaomi/mimo-v2-flash:free` | Default model |
| `ENVIRONMENT` | No | `development` | Environment name |
| `MAX_RETRIES` | No | `3` | Maximum retries |
| `REQUEST_TIMEOUT` | No | `30` | Timeout in seconds |
| `MAX_TOKENS_PER_REQUEST` | No | `2000` | Token limit |

### Model Configuration

```python
from config.settings import get_settings

settings = get_settings()
settings.default_model = "xiaomi/mimo-v2-flash:free"
settings.fallback_model = "kwaipilot/kat-coder-pro-v1:free"
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_client.py -v
```

## 📈 Monitoring

### Metrics

```python
# Get metrics summary
summary = client.get_metrics_summary()

# Outputs:
# {
#     "total_calls": 10,
#     "successful_calls": 9,
#     "failed_calls": 1,
#     "success_rate": "90.00%",
#     "total_tokens": 1500,
#     "total_cost_usd": "$0.00",
#     "average_duration_ms": "245.32"
# }
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Client will log:
# - Request/response details
# - Error information
# - Circuit breaker state changes
# - Retry attempts
```

## 🔒 Security

### Best Practices

1. **Never commit `.env`** - Always in `.gitignore`
2. **Use environment variables** - No hardcoded secrets
3. **Rotate API keys** - Regular key rotation
4. **Validate inputs** - Pydantic validation enabled
5. **Rate limiting** - Configured in settings

### API Key Management

```bash
# Development
export OPENROUTER_API_KEY="sk-or-v1-dev-key"

# Production (use secrets manager)
# AWS Secrets Manager
# HashiCorp Vault
# Kubernetes Secrets
```

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OPENROUTER_API_KEY=""
CMD ["python", "your_app.py"]
```

### Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openrouter-secret
type: Opaque
data:
  api-key: <base64-encoded-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openrouter-app
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: openrouter-secret
              key: api-key
```

## 🎓 Examples

### Example 1: Simple Chat

```python
from src.openrouter import OpenRouterClient, Message

with OpenRouterClient() as client:
    messages = [Message(role="user", content="Hello!")]
    response = client.chat_completion(messages)
    print(response.choices[0].message.content)
```

### Example 2: Conversation

```python
messages = []

# Turn 1
messages.append(Message(role="user", content="What is AI?"))
response = client.chat_completion(messages)
messages.append(Message(
    role="assistant",
    content=response.choices[0].message.content
))

# Turn 2
messages.append(Message(role="user", content="Give me an example"))
response = client.chat_completion(messages)
```

### Example 3: Streaming

```python
messages = [Message(role="user", content="Write a story")]

for chunk in client.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

## 📖 API Reference

See [API.md](docs/API.md) for complete API documentation.

## 🛠️ Troubleshooting

### Common Issues

**Issue**: `AuthenticationError: Invalid API key`

**Solution**: Check your `.env` file and verify API key is correct.

---

**Issue**: `RateLimitError: Rate limit exceeded`

**Solution**: Free tier has 50 requests/day limit. Wait or upgrade plan.

---

**Issue**: `ModelNotFoundError`

**Solution**: Check model ID is correct. List available models at openrouter.ai/models

## 📞 Support

- **Documentation**: [OpenRouter Docs](https://openrouter.ai/docs)
- **API Status**: [status.openrouter.ai](https://status.openrouter.ai)
- **Models**: [openrouter.ai/models](https://openrouter.ai/models)

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## ✨ Acknowledgments

- OpenRouter for providing unified AI API access
- Research by Manus for comprehensive testing
- Enterprise best practices from production deployments
