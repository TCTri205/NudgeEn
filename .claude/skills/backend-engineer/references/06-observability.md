# Observability — Logs, Metrics, Traces, SLO

## The 3 Pillars

| Pillar  | Tool                  | What it answers           |
|---------|-----------------------|---------------------------|
| Logs    | Winston + Loki        | What happened?            |
| Metrics | Prometheus + Grafana  | How much / how often?     |
| Traces  | OpenTelemetry + Tempo | Where did the request go? |

## Structured Logging

```typescript
// ❌ String interpolation (not queryable)
logger.log(`User ${userId} placed order ${orderId}`);

// ✅ Structured JSON (queryable, filterable)
logger.log({
  event: 'order.placed',
  orderId, customerId, amount,
  durationMs: Date.now() - start,
  requestId,
});

// Log levels
logger.error({ event: 'payment.failed', error: err.message, orderId });  // Alert needed
logger.warn({ event: 'rate_limit.approaching', userId, rate: 80 });       // Monitor
logger.info({ event: 'user.registered', userId });                         // Audit trail
logger.debug({ event: 'cache.miss', key });                                // Dev only

// NEVER log: passwords, tokens, credit cards, SSN
```

## RED Method Metrics

```typescript
// Rate, Errors, Duration — for every service
const httpRequests = new Counter({ name: 'http_requests_total', labelNames: ['method', 'route', 'status'] });
const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5],
});

// In interceptor:
const end = httpDuration.startTimer({ method, route });
// ...process...
httpRequests.inc({ method, route, status });
end({ status });
```

## OpenTelemetry Setup

```typescript
// tracing.ts — load BEFORE app
const sdk = new NodeSDK({
  resource: new Resource({ [SERVICE_NAME]: 'order-service', [SERVICE_VERSION]: '1.0.0' }),
  traceExporter: new OTLPTraceExporter({ url: process.env.OTEL_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations()], // Auto-instrument HTTP, PG, Redis
});
sdk.start();

// Custom business spans
const tracer = trace.getTracer('order-service');
async processOrder(orderId: string) {
  return tracer.startActiveSpan('processOrder', async (span) => {
    span.setAttributes({ 'order.id': orderId });
    try {
      await this.doWork();
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      throw err;
    } finally {
      span.end();
    }
  });
}
```

## SLO / Error Budget

```
SLO = 99.9% availability
Error budget = 0.1% = 43.2 minutes/month allowed downtime

Budget policy:
  > 50% remaining: Deploy freely, experiment
  < 50% remaining: Slow down, focus on reliability
  Exhausted: Freeze deploys, reliability only

SLI examples:
  Availability: % requests returning non-5xx
  Latency: % requests under 500ms
  Error rate: % requests not erroring
```

## Prometheus Alerts

```yaml
groups:
  - name: backend-slo
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 2m
        annotations:
          summary: "Error rate > 1% for 2 minutes — SLO burn"

      - alert: HighP99Latency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "P99 > 1 second — latency SLO at risk"

      - alert: KafkaConsumerLag
        expr: kafka_consumer_group_lag > 10000
        for: 5m
        annotations:
          summary: "Consumer falling behind — check for processing bottleneck"
```

## Health Checks

```typescript
@Get('/ready')
@HealthCheck()
readiness() {
  return this.health.check([
    () => this.db.pingCheck('database'),
    () => this.redis.pingCheck('redis'),
    () => this.kafka.pingCheck('kafka'),
    () => this.disk.checkStorage('storage', { thresholdPercent: 0.9 }),
  ]);
}

@Get('/live')
liveness() { return { status: 'ok' }; }  // K8s restarts if this fails
```
