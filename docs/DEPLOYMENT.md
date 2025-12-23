# Deployment Guide

## 🎯 Production Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Code coverage > 90%
- [ ] Security scan complete (`bandit`)
- [ ] Dependencies updated (`pip-audit`)
- [ ] Environment variables configured
- [ ] Secrets in secure storage (not `.env`)
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Rate limits configured
- [ ] Circuit breaker tuned

### Deployment Options

## Option 1: AWS ECS/Fargate

### 1.1 Build Docker Image

```bash
# Build
docker build -t openrouter-app:latest .

# Tag for ECR
docker tag openrouter-app:latest \
  <account-id>.dkr.ecr.<region>.amazonaws.com/openrouter-app:latest

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/openrouter-app:latest
```

### 1.2 Store Secrets in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name openrouter/api-key \
  --secret-string '{"OPENROUTER_API_KEY":"sk-or-v1-xxxxx"}'
```

### 1.3 ECS Task Definition

```json
{
  "family": "openrouter-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "<ecr-image>",
      "secrets": [
        {
          "name": "OPENROUTER_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openrouter/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/openrouter-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Option 2: Kubernetes

### 2.1 Create Namespace

```bash
kubectl create namespace openrouter-app
```

### 2.2 Create Secret

```bash
kubectl create secret generic openrouter-secret \
  --from-literal=api-key=sk-or-v1-xxxxx \
  -n openrouter-app
```

### 2.3 Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openrouter-app
  namespace: openrouter-app
  labels:
    app: openrouter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openrouter
  template:
    metadata:
      labels:
        app: openrouter
    spec:
      containers:
      - name: app
        image: <your-image>
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: openrouter-secret
              key: api-key
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: openrouter-service
  namespace: openrouter-app
spec:
  selector:
    app: openrouter
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openrouter-hpa
  namespace: openrouter-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openrouter-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2.4 Deploy

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods -n openrouter-app
kubectl logs -f <pod-name> -n openrouter-app
```

## Option 3: Google Cloud Run

### 3.1 Build and Deploy

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/<project-id>/openrouter-app

# Deploy to Cloud Run
gcloud run deploy openrouter-app \
  --image gcr.io/<project-id>/openrouter-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets OPENROUTER_API_KEY=openrouter-key:latest
```

## Monitoring Setup

### Prometheus Metrics

```python
# Add to your app
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
request_counter = Counter('openrouter_requests_total', 'Total requests')
request_duration = Histogram('openrouter_request_duration_seconds', 'Request duration')
error_counter = Counter('openrouter_errors_total', 'Total errors', ['error_type'])

# Expose metrics endpoint
start_http_server(8001)
```

### CloudWatch Logs (AWS)

```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

## Health Checks

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    """Liveness probe."""
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    """Readiness probe."""
    # Check dependencies
    try:
        client = OpenRouterClient()
        # Test API connectivity
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503
```

## Scaling Considerations

### Horizontal Scaling

- Use stateless design
- Store state externally (Redis, DynamoDB)
- Use load balancer
- Configure HPA (Horizontal Pod Autoscaler)

### Vertical Scaling

- Monitor resource usage
- Adjust CPU/memory limits
- Consider memory-optimized instances for large context windows

### Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_requests: int, window: int):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def allow_request(self) -> bool:
        now = time.time()
        self.requests = [r for r in self.requests if now - r < self.window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

rate_limiter = RateLimiter(max_requests=100, window=60)
```

## Cost Optimization

### 1. Use Free Models in Development

```python
ENVIRONMENT=development → xiaomi/mimo-v2-flash:free
ENVIRONMENT=production → deepseek/deepseek-chat (paid)
```

### 2. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_completion(prompt: str):
    return client.chat_completion([Message(role="user", content=prompt)])
```

### 3. Monitor Costs

```python
# Daily cost alerts
if daily_cost > threshold:
    send_alert_to_team()
```

## Security Hardening

### 1. Network Policies (Kubernetes)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: openrouter-netpol
spec:
  podSelector:
    matchLabels:
      app: openrouter
  policyTypes:
  - Ingress
  - Egress
  egress:
  - to:
    - podSelector: {}
  - ports:
    - port: 443
      protocol: TCP
```

### 2. Pod Security Standards

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: openrouter-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

### 3. Secrets Rotation

```bash
# Rotate API key every 90 days
# Update in secrets manager
# Rolling restart deployment
kubectl rollout restart deployment/openrouter-app -n openrouter-app
```

## Disaster Recovery

### Backup Strategy

- Configuration backups (daily)
- Database backups (if applicable)
- Secrets backup to secure location

### Failover Plan

1. Monitor circuit breaker state
2. Automatic fallback to secondary model
3. Alert on-call engineer
4. Execute runbook

### Runbook

See [RUNBOOK.md](RUNBOOK.md) for operational procedures.

## Performance Tuning

### Connection Pool Size

```python
from requests.adapters import HTTPAdapter

adapter = HTTPAdapter(
    pool_connections=20,  # Adjust based on load
    pool_maxsize=40
)
```

### Timeout Configuration

```python
# Production timeouts
REQUEST_TIMEOUT=30  # Adjust based on model
CONNECT_TIMEOUT=10
READ_TIMEOUT=30
```

### Circuit Breaker Tuning

```python
FAILURE_THRESHOLD=5      # Errors before opening
RECOVERY_TIMEOUT=60      # Seconds before retry
SUCCESS_THRESHOLD=3      # Successes to close
```

## Post-Deployment Validation

```bash
# 1. Health check
curl https://your-app.com/health

# 2. Test API
curl -X POST https://your-app.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# 3. Check logs
kubectl logs -f deployment/openrouter-app -n openrouter-app

# 4. Monitor metrics
# Check Prometheus/Grafana dashboards

# 5. Load test
# Use k6, locust, or similar
```

## Rollback Procedure

```bash
# Kubernetes
kubectl rollout undo deployment/openrouter-app -n openrouter-app

# AWS ECS
aws ecs update-service \
  --cluster <cluster> \
  --service openrouter-service \
  --task-definition openrouter-app:<previous-revision>
```

## Support Contacts

- **On-Call Engineer**: pagerduty@company.com
- **Platform Team**: platform@company.com
- **OpenRouter Support**: https://openrouter.ai/support
