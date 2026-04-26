# Cost Optimization — Cloud Economics for Backend Engineers

---

## 1. Cost-First Thinking Framework

```
Hỏi trước khi design:
1. Budget per month là bao nhiêu?
2. Revenue per user là bao nhiêu? (giúp justify infra cost)
3. Cost hiện tại phân bổ như thế nào? (compute, DB, storage, egress)
4. Bottleneck của cost là gì? (usually: DB, data transfer, idle compute)
```

---

## 2. Tier vs Cost Trade-offs

```
"Make it work → Make it cheap → Make it fast"
Đừng optimize chi phí khi chưa có users. Đừng giữ kiến trúc đắt tiền khi scale nhỏ.
```

### Compute Cost Optimization

```
Right-sizing:
  Đừng run t3.xlarge nếu CPU average 10% → dùng t3.medium
  CloudWatch → Instance right-sizing recommendations
  Spot Instances: 60-80% cheaper, dùng cho stateless services
  Savings Plans / Reserved Instances: 30-40% discount cho committed usage

Auto-scaling:
  Scale to zero khi không có traffic (Lambda, Cloud Run, Fargate Spot)
  Scale based on QPS, không phải CPU alone

Container optimization:
  Multi-stage Docker builds → smaller images → faster cold starts
  Share base layers across services → less storage cost
```

### Database Cost Optimization

```
Over-provisioned RDS:
  Use Aurora Serverless v2: scales from 0.5 ACU → auto-scales
  Pauses when idle (dev/staging environments!)

Read replica abuse:
  Dont create read replicas for < 100 QPS
  Use ElastiCache to reduce DB reads

Data lifecycle:
  Archive cold data to S3 (costs 20x less than RDS)
  PostgreSQL partitioning → pg_partman → auto-drop old partitions

Compression:
  PostgreSQL: TOAST compression auto-applies to large columns
  ClickHouse: 10-15x compression vs raw data
```

### Storage Cost Optimization

```
S3 Intelligent Tiering:
  Auto-move objects between Standard → Infrequent → Archive
  Saves 40-70% for data accessed sporadically

Data transfer costs (often overlooked!):
  Same-region: Free
  Cross-AZ: $0.01/GB (adds up at scale!)
  Cross-region: $0.02-0.09/GB
  Internet egress: $0.08-0.09/GB

CDN reduces egress dramatically:
  CloudFront / Cloudflare in front of S3: cache static assets
  99% cache hit rate → 99% egress cost reduction
```

---

## 3. Caching Cost ROI

```
Cache hit: $0.001 (Redis sub-millisecond)
DB query: $0.01-0.10 (compute + I/O + connection)
→ 10-100x cost difference per request

ROI calculation:
  1M requests/day
  80% cache hit rate
  Saved DB queries: 800,000/day
  DB cost per query: $0.05/1000 = $0.00005
  Daily savings: 800,000 × $0.00005 = $40/day = $1,200/month
  ElastiCache cost: ~$30/month
  Net monthly saving: $1,170
```

### Cache Sizing

```
Don't cache everything. Cache:
  ✓ Expensive to compute (aggregations, ML predictions)
  ✓ Frequently read, rarely written (product catalog, user profiles)
  ✓ Tolerable staleness (news feed, search results)

Don't cache:
  ✗ Unique per-request data (personalized, real-time)
  ✗ Writes more than reads
  ✗ Very small data sets (already fast from DB)
  ✗ Sensitive financial data without audit trail need
```

---

## 4. Make vs Buy Analysis

```
Question: Kafka (self-managed) vs Amazon MSK (managed) vs Confluent Cloud?

Self-managed Kafka:
  Cost: 3 brokers × $200/month = $600/month + ops time (20-40h/month)
  Hidden cost: ops engineer time at $100-200/hour = $2,000-8,000/month

Amazon MSK:
  Cost: m5.xlarge cluster = ~$1,500/month
  No ops burden for maintenance, monitoring, upgrades

Confluent Cloud:
  Cost: $2,000-5,000/month
  Fully managed, best tooling, ksqlDB, connectors

Decision:
  < 1M msg/day: Don't use Kafka, use SQS/RabbitMQ ($50-200/month)
  1M-100M msg/day: Amazon MSK (managed, reasonable cost)
  > 100M msg/day + budget: Confluent Cloud or self-managed với dedicated team
```

---

## 5. AWS Architecture Cost Comparison

### Scenario: 10,000 DAU web app

**Option A: Traditional (ECS + RDS + ElastiCache)**

```
ECS Service (2x t3.small): ~$30/month
RDS PostgreSQL Multi-AZ (db.t3.medium): ~$100/month
ElastiCache Redis (cache.t3.micro): ~$25/month
ALB: ~$20/month
CloudWatch: ~$15/month
Total: ~$190/month
```

**Option B: Serverless (Lambda + Aurora Serverless + DynamoDB)**

```
Lambda (1M invocations): ~$0.20 (practically free at this scale)
Aurora Serverless v2 (0.5-2 ACU): ~$50/month
API Gateway: ~$15/month
Total: ~$65/month (65% cheaper)
```

**Khi nào dùng Serverless:**

```
✓ Variable/unpredictable traffic
✓ Background jobs (Lambda is perfect)
✓ Cost-sensitive early stage
✓ Event-driven workflows

Không dùng khi:
✗ Cold start latency matters (< 100ms requirement)
✗ Long-running tasks (Lambda max 15 min)
✗ Very high sustained QPS (container cheaper)
✗ Stateful connections (WebSockets, DB connection pools)
```

---

## 6. Cost Monitoring

```typescript
// Tag tất cả resources với cost allocation tags
// AWS: Cost Explorer → breakdown by tag

// Resource tagging convention
const tags = {
  'Environment': 'production',
  'Service': 'order-service',
  'Team': 'backend',
  'CostCenter': 'engineering',
};

// Alert khi cost anomaly
// AWS Cost Anomaly Detection → SNS → Slack notification
// Budget alert: $X/month threshold
```

---

## 7. Database Cost per Scale

```
Users          DB Recommendation              Monthly Cost (AWS)
< 1K           PostgreSQL on RDS t3.micro      $15-30
1K-10K         RDS t3.medium + 1 replica       $100-200
10K-100K       RDS r5.large Multi-AZ            $400-600
100K-1M        Aurora + read replicas           $1,000-3,000
1M-10M         Aurora Global + sharding         $5,000-15,000
10M+           Cassandra / DynamoDB             $10,000+

Storage cost (per GB per month):
  RDS (EBS gp3): $0.115
  Aurora: $0.10
  DynamoDB: $0.25
  S3 Standard: $0.023 (10x cheaper than RDS!)
  S3 Glacier: $0.004 (60x cheaper than RDS!)

Lesson: Move cold data to S3 aggressively
```
