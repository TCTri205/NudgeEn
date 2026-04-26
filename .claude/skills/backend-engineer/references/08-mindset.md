# Mindset — Trade-off Thinking & BigTech Engineering Culture

---

## 1. Consultation Protocol — Hỏi trước khi giải

**Nguyên tắc**: Một engineer giỏi không đưa solution ngay. Họ hỏi đúng câu hỏi trước.

### Template hỏi theo loại vấn đề

**Khi user hỏi về system design:**

```
"Trước khi recommend, mình cần hiểu rõ hơn:
1. Hệ thống phục vụ bao nhiêu users (DAU)? QPS peak?
2. Latency requirement — P99 < bao nhiêu ms?
3. Data consistency: dữ liệu có được phép stale không?
4. Budget/month?
5. Team size — bao nhiêu engineers, ops capacity?
6. Greenfield hay existing system?"
```

**Khi user hỏi chọn database:**

```
"Để chọn đúng database, cần biết:
1. Data structure: relational, document, hay key-value?
2. Query patterns: đọc nhiều hay ghi nhiều?
3. Cần ACID transactions không?
4. Scale: bao nhiêu records, growth rate?
5. Read latency target?
6. Team đã dùng gì chưa? (familiarity matters)
7. Self-hosted hay managed?"
```

**Khi user hỏi chọn message queue:**

```
"Cần clarify:
1. Throughput: messages/second?
2. Cần message ordering không?
3. Replay messages được không?
4. Delivery guarantee cần: at-most / at-least / exactly once?
5. Simple background jobs hay complex multi-step workflow?
6. Ops burden team có thể handle không?"
```

---

## 2. Trade-off Framework

**Mọi quyết định kỹ thuật đều có cost. Nhiệm vụ của engineer là làm trade-off EXPLICIT.**

### Trade-off Template

```
Decision: [Technology / Pattern / Architecture]

Benefits:
  + [Benefit 1]: [Why it matters]
  + [Benefit 2]: [Why it matters]

Trade-offs:
  - [Trade-off 1]: [Impact + mitigation]
  - [Trade-off 2]: [Impact + mitigation]

When to reconsider:
  → Trigger 1 (e.g., "when traffic exceeds X")
  → Trigger 2 (e.g., "when team grows beyond Y")

Alternatives considered:
  Option A: [Why not chosen]
  Option B: [Why not chosen]
```

### Common Trade-offs to articulate

```
Microservices vs Monolith:
  Microservices: Independent deploy, scale, team autonomy
  BUT: Network latency, distributed transactions, ops complexity
  Verdict: Start monolith, extract services when pain point is clear

Strong vs Eventual Consistency:
  Strong: Simpler programming model, no stale reads
  BUT: Higher latency, lower availability during partitions
  Verdict: Default strong, relax per use case (feed, catalog OK with eventual)

Synchronous vs Asynchronous:
  Sync: Simple, predictable, easy to debug
  BUT: Tight coupling, cascading failures, throughput limited
  Verdict: Sync for user-facing reads, async for side effects

Caching vs No Caching:
  Cache: Lower latency, less DB load
  BUT: Cache invalidation complexity, stale data risk, memory cost
  Verdict: Cache aggressively, invalidate carefully

SQL vs NoSQL:
  SQL: ACID, relational queries, mature tooling
  BUT: Harder to scale horizontally, schema migrations
  NoSQL: Horizontal scale, flexible schema
  BUT: No joins, eventual consistency, less mature
  Verdict: PostgreSQL by default, NoSQL when specific need proven
```

---

## 3. Architecture Decision Record (ADR)

**Mọi quyết định quan trọng phải được document.**

```markdown
# ADR-NNN: [Title]

**Date**: 2025-03-21
**Status**: Proposed | Accepted | Deprecated | Superseded
**Deciders**: [Team/people involved]

## Context
[Tại sao cần quyết định này? Vấn đề gì đang giải quyết?]

## Decision
[Quyết định là gì?]

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative / Trade-offs
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Change in workflow]

## Alternatives Considered
### Option A: [Name]
[Why not chosen]

### Option B: [Name]
[Why not chosen]

## Review Date
[When to revisit this decision, e.g., "When we exceed 1M users"]
```

---

## 4. Back-of-Envelope Calculations

**Hãy nhớ các số này khi estimate:**

```
Time:
  1ms   = 1,000μs
  1s    = 1,000ms
  1min  = 60s
  1hr   = 3,600s
  1day  = 86,400s
  1year = 31,536,000s (~31.5M seconds)

Traffic:
  100M requests/day = ~1,160 RPS
  Peak = 3-5x average
  Example: 1M DAU, each makes 10 requests/day = 10M req/day = 115 RPS avg, ~500 RPS peak

Data:
  1KB = 1,024 bytes
  1MB = 1,024KB
  1GB = 1,024MB
  1TB = 1,024GB

Throughput benchmarks (rough, 2025):
  1 CPU core: ~10K simple operations/second
  PostgreSQL: ~5K writes/sec, ~50K reads/sec (w/ indexes)
  MySQL/Vitess: ~5K TPS per shard
  Redis: ~100K ops/sec
  Kafka: ~1M msgs/sec per broker
  HTTP API (Node.js): ~10K req/sec (single process)

Storage:
  1 user record: ~1KB
  1M users: ~1GB
  1B users: ~1TB
  
  1 order record (with items): ~5KB
  1M orders/day: ~5GB/day = ~1.8TB/year
  
  1 Kafka message: ~1KB average
  1M messages/day: ~1GB/day
```

### Worked Example

```
Problem: Design a URL shortener
Target: 100M users, each creates 1 URL/day, 100:1 read/write ratio

Traffic:
  Writes: 100M/day = ~1,160 writes/sec
  Reads: 116,000 reads/sec (100:1 ratio)
  Peak reads: ~500,000 reads/sec

Storage:
  1 URL mapping: ~500 bytes
  New URLs/day: 100M × 500B = 50GB/day
  5 years: 50GB × 365 × 5 = ~91TB

Design implications:
  Writes: Single region PostgreSQL can handle 1,160/sec → OK initially
  Reads: 116K/sec → needs aggressive caching (Redis)
  Storage: 91TB → need sharding or distributed DB (Cassandra/DynamoDB)
  URL generation: Snowflake IDs or Base62 encoding
```

---

## 5. Common Anti-Patterns to Avoid

### Architecture Anti-Patterns

```
Distributed Monolith:
  Chia microservices nhưng share chung 1 DB
  → Không được benefit gì, thêm network overhead
  Fix: Database per service

God Service:
  OrderService gọi vào Users, Payments, Inventory, Shipping, Notification
  → Single point of failure, bottleneck, hard to test
  Fix: Domain boundaries, event-driven communication

Chatty Microservices:
  Service A gọi Service B 20 lần cho 1 operation
  → N+1 ở network level
  Fix: API aggregation (BFF), data duplication, event-driven

Premature Microservices:
  3-person team, 15 microservices
  → Overhead kills velocity
  Fix: Modular monolith first

Sync Everything:
  Every inter-service call is synchronous HTTP
  → Cascading failures, tight coupling
  Fix: Async for side effects, sync only for required data
```

### Code Anti-Patterns

```
Anemic Domain Model:
  Classes with only getters/setters, all logic in service layer
  → Service grows to 2000 lines, impossible to test
  Fix: Move business logic into domain entities

Feature Flags as Dead Code:
  Flag shipped 2 years ago, always true, cleanup never happened
  → Complexity, confusion
  Fix: Feature flag lifecycle policy, auto-expire old flags

Swallowed Exceptions:
  catch (e) { console.log(e); }
  → Silent failures in production
  Fix: Either handle meaningfully or propagate with context

Implicit State:
  Function behavior depends on global state or hidden mutable state
  → Impossible to test, race conditions
  Fix: Pure functions, explicit dependency injection
```

---

## 6. BigTech Engineering Culture

| Principle                  | Meaning in Practice                            |
|----------------------------|------------------------------------------------|
| **Bias for action**        | Ship, measure, iterate. Done > perfect         |
| **Ownership**              | You own the whole system, not just "your code" |
| **Dive deep**              | Know your metrics. "I think" → "Data shows"    |
| **Think big, start small** | Design for 10x, build for today                |
| **Disagree and commit**    | Voice concerns, then commit to team decision   |
| **Write things down**      | If not documented, it doesn't exist            |
| **Blameless postmortem**   | Systems fail, humans don't fail — systems do   |
| **Error budget**           | Failures are budget, not disasters             |

---

## 7. Interview/Design Session Framework

**Khi giải system design:**

```
Step 1: CLARIFY (5 min)
  Functional requirements: What features?
  Non-functional: Scale, latency, availability, consistency
  Explicit out of scope: What are we NOT building?

Step 2: ESTIMATE (3 min)
  Back-of-envelope: users, QPS, storage
  Identify order of magnitude challenges

Step 3: HIGH-LEVEL DESIGN (10 min)
  Diagram: clients → LB → services → DB
  Data flow (not code flow)
  Identify bottlenecks early

Step 4: DEEP DIVE (15 min)
  Focus on most complex/interesting part
  DB schema, API design, caching strategy, consensus mechanism

Step 5: JUSTIFY & TRADE-OFFS (5 min)
  Why this over alternatives?
  What breaks at 10x scale?
  What would you do differently with more time?

Red flags in system design:
  ❌ Jumping to solution without clarifying
  ❌ No back-of-envelope numbers
  ❌ Single point of failure ignored
  ❌ No mention of failure scenarios
  ❌ Over-engineering for current scale
  ❌ Can't explain trade-offs
```
