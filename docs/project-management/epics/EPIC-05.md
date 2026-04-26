# EPIC-05: Production Readiness

**Focus:** Deployment, observability, reliability, scaling  
**Status:** Pending (Planned for Sprint 4)  
**Sprint:** Sprint 4: Production Readiness  
**Priority:** P1 - High

---

## Epic Description

Deploy NudgeEn to production environments with full observability, reliability, and scaling capabilities. This epic transforms the development prototype into a production-grade system that can handle real user traffic, recover from failures gracefully, and scale as the user base grows. It implements the deployment architecture, monitoring, alerting, and operational processes needed to run the service reliably.

This epic is the final milestone before beta launch, ensuring the system is stable, observable, and maintainable.

---

## Business Value

- **Reliability:** Minimize downtime and service disruptions
- **Scalability:** Support growth from 100 to 100k+ users
- **Maintainability:** Fast issue diagnosis and resolution
- **Cost Efficiency:** Right-size infrastructure based on actual usage
- **User Trust:** High availability and data durability
- **Team Velocity:** Clear observability enables faster feature development

---

## Scope

### In Scope

- ✅ Deployment to production (Vercel + Render/Railway/Fly)
- ✅ Environment separation (dev, staging, prod)
- ✅ CI/CD pipelines with automated testing
- ✅ Application monitoring and alerting
- ✅ Log aggregation and analysis
- ✅ Distributed tracing (web → API → workers)
- ✅ Error tracking (Sentry or equivalent)
- ✅ Performance monitoring (Core Web Vitals)
- ✅ Database backups and disaster recovery
- ✅ Redis persistence and HA configuration
- ✅ SSL/TLS certificates and HTTPS enforcement
- ✅ Rate limiting and DDoS protection
- ✅ Health check endpoints
- ✅ Graceful shutdown handling
- ✅ Database connection pooling (PgBouncer/Supavisor)
- ✅ Worker process management and scaling
- ✅ Queue monitoring and dead-letter handling
- ✅ Cost monitoring and alerting
- ✅ Infrastructure as Code (Terraform/configuration)
- ✅ Rollback procedures and strategies
- ✅ Zero-downtime deployment patterns
- ✅ Load testing and capacity planning
- ✅ Security scanning (dependencies, secrets)
- ✅ Compliance checks (GDPR, data retention)

### Out of Scope

- ❌ On-premises deployment options
- ❌ Multi-region active-active deployment (initial launch)
- ❌ Advanced chaos engineering practices
- ❌ Custom infrastructure (k8s) - using managed services
- ❌ 24/7 on-call rotation setup
- ❌ Advanced AIOps/ML-based alerting

---

## Key Requirements

### REQ-PROD-01: Multi-Environment Setup

**From:** ARCHITECTURE.md (Deployment Recommendation)

- **Development:** Local Docker or isolated cloud instances
- **Staging:** Separate database and Redis, mirrors production
- **Production:** High-availability setup with managed services

**Environment Variables:**
```bash
# .env.production
DATABASE_URL="postgresql://..."
REDIS_URL="redis://..."
AUTH_SECRET="..."
AUTH_TRUST_HOST="true"
NEXTAUTH_URL="https://app.nudgeen.com"
GEMINI_API_KEY="..."
GROQ_API_KEY="..."
SENTRY_DSN="..."
LOG_LEVEL="info"
```

### REQ-PROD-02: Deployment Architecture

**From:** TECHSTACK.md

- **Web:** Vercel (Next.js)
- **API:** Render / Railway / Fly.io
- **Workers:** Render / Railway / Fly.io (separate service)
- **Database:** Managed PostgreSQL (Supabase, Neon, or RDS)
- **Cache/Broker:** Managed Redis (Upstash or Redis Enterprise)

**Network Topology:**
```
User Browser
    │
    ↓ HTTPS
Vercel (Next.js) ─── CDN
    │
    ↓ API Requests (HTTPS)
Render/Fly (FastAPI) ──> Managed Postgres
    │                         │
    ↓                         ↓
Managed Redis ◄─── Taskiq Workers
```

### REQ-PROD-03: CI/CD Pipeline

**GitHub Actions Workflow:**
```yaml
name: CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: {POSTGRES_PASSWORD: postgres}
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with: {python-version: '3.12'}
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with: {node-version: '18'}
      
      - name: Install dependencies
        run: |
          cd api && pip install -r requirements.txt
          cd ../web && npm ci
      
      - name: Lint
        run: |
          cd api && ruff check .
          cd ../web && npm run lint
      
      - name: Type check
        run: |
          cd web && npm run type-check
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
        run: |
          cd api && pytest
          cd ../web && npm test
      
      - name: Deploy (on main)
        if: github.ref == 'refs/heads/main'
        run: ./deploy.sh
```

### REQ-PROD-04: Monitoring & Observability

**Metrics (Prometheus/Grafana):**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Chat-specific metrics
MESSAGES_SENT = Counter(
    'chat_messages_sent_total',
    'Total chat messages',
    ['user_id', 'conversation_id']
)

AI_RESPONSE_TIME = Histogram(
    'ai_response_duration_seconds',
    'AI response time',
    ['provider', 'model']
)

QUEUE_DEPTH = Gauge(
    'task_queue_depth',
    'Number of pending tasks',
    ['queue_name']
)

WORKER_FAILURES = Counter(
    'worker_failures_total',
    'Worker job failures',
    ['worker_type', 'error_type']
)
```

**Logging (Structured JSON):**
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration * 1000,
        user_id=getattr(request.state, "user_id", None),
        request_id=request.state.request_id
    )
    
    return response
```

**Tracing (OpenTelemetry):**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Jaeger/Zipkin
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

@app.post("/api/chat/send")
async def send_message(request: Request):
    with tracer.start_as_current_span("chat_send") as span:
        span.set_attribute("user.id", request.state.user_id)
        span.set_attribute("conversation.id", conversation_id)
        
        # Child span for LLM call
        with tracer.start_as_current_span("llm_generate"):
            response = await llm.generate(prompt)
```

### REQ-PROD-05: Health Checks

```python
# app/core/health.py
from fastapi import APIRouter
import asyncio
import redis.asyncio as redis
import asyncpg

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/health/ready")
async def readiness_check():
    """Check if app can serve traffic."""
    checks = {
        "api": True,
        "database": await check_postgres(),
        "redis": await check_redis(),
    }
    
    healthy = all(checks.values())
    return {
        "status": "ready" if healthy else "not ready",
        "checks": checks
    }

@router.get("/health/live")
async def liveness_check():
    """Check if app is alive."""
    return {"status": "alive"}

async def check_postgres():
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=5)
        await conn.fetchval("SELECT 1")
        await conn.close()
        return True
    except Exception:
        return False

async def check_redis():
    try:
        r = redis.from_url(REDIS_URL)
        await r.ping()
        await r.close()
        return True
    except Exception:
        return False
```

### REQ-PROD-06: Database Backups

```bash
#!/bin/bash
# backup.sh - Daily PostgreSQL backup

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
RETENTION_DAYS=30

# Take backup using pg_dump
pg_dump \
  --host=$DB_HOST \
  --username=$DB_USER \
  --format=custom \
  --file=$BACKUP_DIR/nudgeen_${DATE}.dump \
  $DB_NAME

# Upload to S3
aws s3 cp $BACKUP_DIR/nudgeen_${DATE}.dump s3://nudgeen-backups/

# Cleanup old backups
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete
```

### REQ-PROD-07: Worker Scaling

```yaml
# docker-compose.yml for local development
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nudgeen
    depends_on:
      - postgres
      - redis
  
  worker:
    build: ./workers
    command: taskiq worker -w workers.worker:broker
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nudgeen
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 2  # Scale workers
  
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: nudgeen
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### REQ-PROD-08: Rate Limiting Production

```python
# Enhanced rate limiting with Redis
from redis.asyncio import Redis
import time

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Sliding window rate limiter."""
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - window)
        # Count current
        pipeline.zcard(key)
        # Add current request
        pipeline.zadd(key, {str(now): now})
        # Set expiry
        pipeline.expire(key, window)
        
        results = await pipeline.execute()
        current = results[1]
        
        return current < limit
    
    async def get_reset_time(self, key: str, window: int) -> float:
        """Get when the rate limit resets."""
        oldest = await self.redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            return oldest[0][1] + window
        return time.time()

# Usage in FastAPI
rate_limiter = RateLimiter(redis_client)

@app.post("/api/chat/send")
async def send_message(request: Request):
    user_id = request.state.user_id
    key = f"rate_limit:{user_id}"
    
    if not await rate_limiter.is_allowed(key, limit=50, window=86400):
        reset = await rate_limiter.get_reset_time(key, 86400)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Reset": str(int(reset))}
        )
    
    # Process message...
```

### REQ-PROD-09: Error Tracking

```python
# Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        AsyncioIntegration(),
    ],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development"),
)

# Capture exceptions automatically
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### REQ-PROD-10: Security Headers

```python
# FastAPI middleware for security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.nudgeen.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## Acceptance Criteria

### Must Have

- [ ] Production deployment to Vercel (web) and Render/Fly (API + workers)
- [ ] Separate dev, staging, and prod environments
- [ ] CI/CD pipeline with automated tests on PR
- [ ] Automatic deployment on merge to main
- [ ] Application monitoring (metrics, logs, traces)
- [ ] Error tracking with Sentry
- [ ] Health check endpoints (`/health`, `/health/ready`, `/health/live`)
- [ ] Database backups (daily, retained 30 days)
- [ ] Redis persistence enabled
- [ ] SSL/TLS enforced (HTTPS only)
- [ ] Rate limiting in production (50 msgs/24hr)
- [ ] Connection pooling (PgBouncer/Supavisor)
- [ ] Worker process management (auto-restart on failure)
- [ ] Queue monitoring (dead-letter handling)
- [ ] Security headers configured
- [ ] Cost monitoring dashboard
- [ ] Rollback procedure documented and tested

### Should Have

- [ ] Multi-region deployment (active-passive)
- [ ] Load testing results (< 1000 concurrent users)
- [ ] Capacity planning document
- [ ] Incident response runbook
- [ ] Performance budgets (Core Web Vitals)
- [ ] Secrets rotation procedure
- [ ] Compliance audit trail (GDPR)

### Could Have

- [ ] Blue-green deployments
- [ ] Canary releases
- [ ] Chaos engineering tests
- [ ] AIOps alert correlation

### Won't Have (This Epic)

- ❌ On-premises deployment
- ❌ Custom Kubernetes cluster
- ❌ 24/7 on-call (initial launch)
- ❌ Advanced ML-based anomaly detection

---

## Dependencies

### External Dependencies

- **Vercel** - Frontend hosting
- **Render/Railway/Fly.io** - Backend and worker hosting
- **Supabase/Neon/RDS** - Managed PostgreSQL
- **Upstash/Redis Enterprise** - Managed Redis
- **Sentry** - Error tracking
- **GitHub Actions** - CI/CD
- **Terraform** (optional) - Infrastructure as Code

### Internal Dependencies

- **All previous epics** - Must be feature-complete

---

## Timeline & Milestones

**Sprint 4: Production Readiness** (Target: 3 weeks)

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| M1 | Week 1 Day 2 | Environment configuration files |
| M2 | Week 1 Day 4 | CI/CD pipeline (test only) |
| M3 | Week 1 Day 7 | Staging deployment |
| M4 | Week 2 Day 2 | Monitoring setup (metrics, logs) |
| M5 | Week 2 Day 4 | Error tracking (Sentry) |
| M6 | Week 2 Day 7 | Health checks implemented |
| M7 | Week 3 Day 2 | Backup and restore procedure |
| M8 | Week 3 Day 4 | Rate limiting in production |
| M9 | Week 3 Day 6 | Security audit and hardening |
| M10 | Week 3 Day 7 | Production deployment |

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Production outage | Critical | Low | Staging testing, health checks, quick rollback |
| Data loss | Critical | Very Low | Automated backups, point-in-time recovery |
| Cost overrun | High | Medium | Budget alerts, autoscaling limits |
| Security breach | Critical | Low | Security headers, rate limiting, audits |
| Performance degradation | High | Medium | Monitoring, alerting, capacity planning |
| Deployment failure | Medium | Low | CI/CD testing, rollback capability |

---

## Success Metrics

- **Uptime:** > 99.9% (monthly)
- **Mean Time To Recovery (MTTR):** < 15 minutes
- **Deployment Frequency:** Daily (on merge)
- **Lead Time for Changes:** < 24 hours
- **Change Failure Rate:** < 5%
- **Error Rate:** < 0.1% of requests
- **P95 Response Time:** < 500ms (API), < 100ms (web)
- **Queue Lag:** < 5 minutes (95th percentile)
- **Backup Success Rate:** 100%
- **Security Scan Passes:** 100%

---

## Out of Scope for This Epic

The following will be addressed in post-launch phases:

- Multi-region active-active deployment
- Advanced chaos engineering
- Custom infrastructure (k8s)
- 24/7 on-call rotation
- Advanced AIOps

---

## References

- [PRD-v1.md](../../PRD-v1.md) - Product requirements
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Architecture decisions
- [TECHSTACK.md](../../TECHSTACK.md) - Technology stack
- [DATABASE_GUIDELINES.md](../../DATABASE_GUIDELINES.md) - Database design
- [ONBOARDING.md](../../ONBOARDING.md) - Team onboarding

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
