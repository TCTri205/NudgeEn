# EPIC-05: Production Readiness

- **Status:** Pending (Planned for Sprint 4)
- **Priority:** P1 - High
- **Source requirement:** PRD-v1.md, ARCHITECTURE.md (Deployment Recommendation)
- **Impacted domains:** Platform, DevOps, Infrastructure, Observability

---

## Summary

Deploy NudgeEn to production environments with full observability, reliability, and scaling capabilities. This epic transforms the development prototype into a production-grade system that can handle real user traffic, recover from failures gracefully, and scale as the user base grows. It implements the deployment architecture, monitoring, alerting, and operational processes needed to run the service reliably. This epic is the final milestone before beta launch, ensuring the system is stable, observable, and maintainable.

---

## Current State / Gap

- **Implemented:** All feature epics (EPIC-00 through EPIC-04) — authentication, messaging, persona, memory, pedagogy.
- **Missing:** Production deployment, CI/CD pipelines with automated testing, monitoring and alerting, log aggregation, error tracking, database backups, SSL/TLS enforcement, rate limiting in production, health checks, disaster recovery, load testing, security hardening.

---

## Problem / Opportunity

Without production readiness, the platform cannot:
- Handle real user traffic reliably
- Recover from failures quickly
- Scale to meet demand
- Provide visibility into system health
- Meet security and compliance requirements

Launching without this epic would result in frequent outages, slow incident response, poor user experience, and potential data loss. This epic is the gate between "works on my machine" and "production-grade service."

---

## Desired Outcome

After this epic is complete:
- Application is deployed to production (Vercel for web, Render/Fly for API/workers)
- CI/CD pipelines run automated tests on every PR and deploy on merge to main
- Monitoring dashboards show real-time metrics (requests, latency, errors, queue depth)
- Alerts notify team of critical issues (PagerDuty/Slack)
- Logs are aggregated and searchable (ELK/Datadog)
- Database backups run daily with tested restore procedures
- Health checks confirm system readiness
- Rate limiting protects against abuse
- SSL/TLS is enforced (HTTPS only)
- Rollback procedures are documented and tested

This outcome matters because production readiness determines whether users have a reliable, trustworthy experience or encounter frequent outages and data loss.

---

## Users / Use Cases

- **Primary users:** Development team, Operations team, End users (indirectly)
- **Main use cases:**
  - Developer pushes code → CI runs tests → CD deploys to production
  - System detects high error rate → Alerts team → Team investigates
  - Database failure → Automatic failover → Backup restore if needed
  - User requests page → Load balancer routes to healthy instance
  - Team reviews metrics → Identifies bottleneck → Scales service
- **Important edge cases:**
  - Deployment failure → Automatic rollback
  - Database connection exhaustion → PgBouncer pooling
  - Queue backlog → Worker scaling
  - DDoS attack → Rate limiting + CDN protection

---

## Scope

### In scope

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

### Out of scope

- ❌ On-premises deployment options
- ❌ Multi-region active-active deployment (initial launch)
- ❌ Advanced chaos engineering practices
- ❌ Custom infrastructure (k8s) - using managed services
- ❌ 24/7 on-call rotation setup
- ❌ Advanced AIOps/ML-based alerting

---

## Capability Slices

- **Slice 1: Deployment Infrastructure** — Vercel, Render/Fly, managed PostgreSQL, managed Redis
- **Slice 2: CI/CD Pipelines** — GitHub Actions, automated testing, deployment automation
- **Slice 3: Monitoring & Observability** — Metrics (Prometheus/Grafana), logging, tracing
- **Slice 4: Reliability & Recovery** — Backups, health checks, graceful shutdown, rollback
- **Slice 5: Security & Performance** — SSL/TLS, rate limiting, security scanning, Core Web Vitals
- **Slice 6: Operations** — Cost monitoring, capacity planning, runbooks, compliance

---

## Facts / Assumptions / Constraints / Unknowns

- **Facts:**
  - Vercel is the chosen platform for Next.js frontend
  - Render/Railway/Fly.io for backend API and workers
  - Managed PostgreSQL (Supabase/Neon/RDS)
  - Managed Redis (Upstash/Redis Enterprise)
  - GitHub Actions for CI/CD
  - Sentry for error tracking
- **Assumptions:**
  - Initial user load: <1000 concurrent users
  - Team can respond to alerts within 1 hour
  - Monthly infrastructure budget: $200-500 (initial)
- **Constraints:**
  - Uptime target: >99.9% monthly
  - MTTR (Mean Time To Recovery): <15 minutes
  - P95 response time: <500ms (API), <100ms (web)
  - Database backups: daily, retained 30 days
  - Rate limit: 50 messages/24hr per user (production)
- **Unknowns:**
  - Exact production hosting provider (Render vs Railway vs Fly.io)
  - Final cost at scale
  - Traffic patterns and peak hours

---

## Proposed Solution

**Deployment Architecture:**
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

**CI/CD Pipeline (GitHub Actions):**
```yaml
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
      redis:
        image: redis:7

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
        run: cd web && npm run type-check
      - name: Run tests
        run: |
          cd api && pytest
          cd ../web && npm test
      - name: Deploy (on main)
        if: github.ref == 'refs/heads/main'
        run: ./deploy.sh
```

**Monitoring Stack:**
- **Metrics:** Prometheus + Grafana (request count, latency, error rate, queue depth)
- **Logging:** Structured JSON logs → ELK/Datadog
- **Tracing:** OpenTelemetry → Jaeger/Zipkin
- **Alerting:** Grafana Alerts → Slack/PagerDuty

**Health Checks:**
```python
@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness_check():
    checks = {
        "api": True,
        "database": await check_postgres(),
        "redis": await check_redis(),
    }
    healthy = all(checks.values())
    return {"status": "ready" if healthy else "not ready", "checks": checks}

@router.get("/health/live")
async def liveness_check():
    return {"status": "alive"}
```

**Key tradeoffs:**
- Chose managed services over self-hosted (less ops overhead, faster iteration)
- Chose single-region deployment (simpler, cost-effective for MVP)
- Chose GitHub Actions over custom CI (integration, free tier)

---

## Dependencies / Rollout / Risks

### Dependencies

- **External:**
  - Vercel — Frontend hosting
  - Render/Railway/Fly.io — Backend and worker hosting
  - Supabase/Neon/RDS — Managed PostgreSQL
  - Upstash/Redis Enterprise — Managed Redis
  - Sentry — Error tracking
  - GitHub Actions — CI/CD
  - Terraform (optional) — Infrastructure as Code

- **Internal:**
  - **All previous epics** — Must be feature-complete

### Rollout notes

- Deploy to staging first, validate, then production
- Enable monitoring in logging mode before alerting
- Test backup restore procedure before launch
- Gradual traffic ramp-up (internal → beta users → public)

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Production outage | Critical | Low | Staging testing, health checks, quick rollback |
| Data loss | Critical | Very Low | Automated backups, point-in-time recovery |
| Cost overrun | High | Medium | Budget alerts, autoscaling limits |
| Security breach | Critical | Low | Security headers, rate limiting, audits |
| Performance degradation | High | Medium | Monitoring, alerting, capacity planning |
| Deployment failure | Medium | Low | CI/CD testing, rollback capability |

---

## Epic Done Criteria

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

---

## Task Writer Handoff

- **Epic slug:** EPIC-05
- **Epic file path:** `docs/project-management/epics/EPIC-05.md`
- **Original requirement:** PRD-v1.md, ARCHITECTURE.md (Deployment Recommendation)
- **Epic summary:** Production deployment, observability, reliability, and scaling
- **Impacted domains:** Platform, DevOps, Infrastructure, Observability
- **Desired outcome:** Production-grade system with 99.9% uptime, full observability, disaster recovery
- **In-scope outcomes:** Deployment, CI/CD, monitoring, backups, security, scaling
- **Non-goals:** Multi-region, k8s, 24/7 on-call, advanced AIOps
- **Capability slices:** 6 slices (deployment, CI/CD, monitoring, reliability, security, operations)
- **Facts:** Vercel, Render/Fly, managed PostgreSQL/Redis, GitHub Actions, Sentry
- **Assumptions:** <1000 concurrent users, 1hr alert response, $200-500/month budget
- **Constraints:** >99.9% uptime, <15min MTTR, <500ms P95 API, daily backups
- **Unknowns:** Exact hosting provider, cost at scale, traffic patterns
- **Proposed solution summary:** Vercel + Render/Fly + managed services + GitHub Actions + monitoring stack
- **Dependencies:** EPIC-00, EPIC-01, EPIC-02, EPIC-03, EPIC-04 (all must be complete)
- **Rollout notes:** Staging first, logging before alerting, test backup restore, gradual ramp-up
- **Risks:** Outage, data loss, cost overrun, security breach, performance degradation
- **Task splitting hints:** Split by slice (deployment → CI/CD → monitoring → reliability → security → ops)
- **Validation expectations:** All criteria testable, uptime measurable, rollback tested

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-26 | System | Initial version based on project documentation |
| 2.0 | 2026-04-27 | Assistant | Standardized to epic-template.md format |
