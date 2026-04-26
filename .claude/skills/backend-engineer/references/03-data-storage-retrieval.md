# Data — Storage, Retrieval & Processing

## Database Selection, Internals, Stream/Batch Processing (DDIA)

---

## 1. Database Selection Matrix

### Hỏi trước khi chọn

```
1. Data structure: relational / document / KV / graph / time-series?
2. OLTP (many small txn) hay OLAP (few large analytics)?
3. ACID required hay eventual consistency OK?
4. Scale: rows, QPS, growth rate?
5. Team familiarity + managed vs self-hosted?
```

### Selection Guide

```
Default choice → PostgreSQL (almost always correct starting point)

Need ACID + relational?       → PostgreSQL
Need global multi-region SQL? → CockroachDB / Google Spanner
Need MySQL compat + sharding? → Vitess / PlanetScale
Write-heavy, petabyte scale?  → Cassandra / ScyllaDB
Real-time analytics, OLAP?    → ClickHouse / Apache Druid
Cache / simple KV?            → Redis
Document, flexible schema?    → MongoDB
Data warehouse / BI?          → Snowflake / BigQuery / Redshift
Time-series (metrics, IoT)?   → TimescaleDB / InfluxDB
Graph relationships?          → Neo4j
Vector / semantic search?     → pgvector / Pinecone / Qdrant
Embedded analytics?           → DuckDB
```

---

## 2. Storage Engines — How Databases Work Internally (DDIA Ch.3)

### B-Tree (Standard RDBMS)

```
Balanced tree of fixed-size pages (4KB)
Branching factor: hundreds of references per page
Depth: O(log n) → 4-level B-tree handles up to 256TB

Write: find leaf page → update in place → WAL for crash recovery
Read: traverse root → leaf

WAL (Write-Ahead Log):
  BEFORE modifying B-tree → write to WAL
  Crash → replay WAL → restore consistent state

Used by: PostgreSQL, MySQL, SQLite (almost every RDBMS)
✓ Fast reads, predictable performance
✗ Slower writes (random I/O, in-place update)
```

### LSM-Tree / SSTable (Log-Structured)

```
Core idea: Append-only. Never overwrite. Merge periodically.

Write path:
  1. Write to in-memory sorted structure (memtable: red-black tree)
  2. Memtable reaches threshold → flush to disk as SSTable (sorted file)
  3. Background compaction: merge SSTables, remove duplicates/tombstones

Read path:
  1. Check memtable (newest)
  2. Check newest SSTable on disk
  3. Check older SSTables...
  Bloom filter: quickly determine if key NOT in a segment (skip disk read)

Write Amplification: 1 write → multiple writes over lifespan (compaction)
Sequential writes: MUCH faster than random writes (especially HDD)

Used by: LevelDB, RocksDB, Cassandra, HBase, Lucene (Elasticsearch)
✓ High write throughput, good for write-heavy workloads
✗ Slower reads (check multiple files), compaction overhead
```

**B-Tree vs LSM-Tree — When to Choose:**

```
                B-Tree          LSM-Tree
Write perf      ⚠️ Slower      ✅ Faster
Read perf       ✅ Faster      ⚠️ Check multiple files
Write amplif.   Low             High (compaction)
Space amplif.   Lower           Higher (during compaction)
Predictability  High            Less (compaction spikes)
SSD             Good enough     Very fast
HDD             OK              Much better (sequential writes)

Rule: RDBMS reads → B-Tree. Write-heavy at scale → LSM-Tree.
```

### Column-Oriented Storage (OLAP)

```
Row storage:    [id=1, name=Alice, price=99, qty=3, date=2025-01-01]
                [id=2, name=Bob,   price=49, qty=1, date=2025-01-02]

Column storage: [id: 1,2,3,4...] [name: Alice,Bob,...] [price: 99,49,...]

Why 10-1000x faster for analytics:
  Query: SELECT SUM(price) WHERE date > X
  Row:    Read ALL columns for every row, discard unused (wasted I/O)
  Column: Read ONLY price and date columns (minimal I/O)

Compression: same data type in one block → very high compression (10-15x)
Vectorized execution: SIMD operations on column arrays
Only read columns needed by query

Used by: ClickHouse, Apache Parquet, Amazon Redshift, Snowflake
NOT for OLTP: updates expensive (rewrite column files)
```

---

## 3. PostgreSQL — Deep Dive

### Index Selection

```sql
-- B-tree (default): equality, range, sort
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- Composite: selectivity high column FIRST (equality before range)
CREATE INDEX idx_orders_cust_date ON orders(customer_id, created_at DESC);

-- Partial: index only a subset → smaller, faster
CREATE INDEX idx_pending ON orders(created_at)
WHERE status = 'pending';  -- Only index pending orders

-- GIN: JSONB, arrays, full-text search
CREATE INDEX idx_metadata ON products USING gin(metadata);
CREATE INDEX idx_fts ON articles USING gin(to_tsvector('english', content));

-- BRIN: sequential inserts (logs, time-series) — tiny index
CREATE INDEX idx_logs ON logs USING brin(created_at);
```

### Query Optimization

```sql
-- Always EXPLAIN ANALYZE before optimizing
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE customer_id=$1 AND status='pending';

-- Red flags:
-- Seq Scan on large table → needs index
-- High "buffers hit=read" ratio → disk I/O bottleneck, needs cache/memory
-- Nested Loop with many rows → may need Hash Join

-- N+1 Prevention: JOIN or eager load
-- ❌ Loop + individual queries
-- ✅ Single JOIN
SELECT o.*, c.name, c.email
FROM orders o JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending';

-- Pagination: cursor-based NOT offset (offset scans all preceding rows)
-- ❌ OFFSET 10000 LIMIT 20 (scans 10,020 rows)
-- ✅ WHERE id > $last_id ORDER BY id LIMIT 20
```

### Partitioning

```sql
-- Range partition by date (most common for time-series data)
CREATE TABLE events (
  id BIGSERIAL, user_id UUID, event_type TEXT, created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2025_q1 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- Queries with created_at filter scan only relevant partition
-- pg_partman extension: auto-create partitions by schedule
```

---

## 4. Cassandra — Wide-Column at Scale

### Data Modeling Rules (opposite of SQL)

```
Rule: Design table FOR your query, not your relationships
      Denormalize, duplication is OK, no JOINs

Example: "Get orders by user, sorted by date"
CREATE TABLE orders_by_user (
  user_id UUID,
  created_at TIMESTAMP,
  order_id UUID,
  status TEXT,
  total DECIMAL,
  PRIMARY KEY (user_id, created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

Partition key: (user_id) → determines which node stores the data
Clustering key: (created_at, order_id) → sort order within partition
```

### Tunable Consistency

```
QUORUM: W + R > N → consistent, slower
ONE:    fast, eventually consistent
ALL:    all nodes confirm, very slow, don't use normally

Pick per-operation based on requirement
```

### When NOT to Use Cassandra

```
✗ Need JOINs or complex relational queries
✗ ACID transactions critical
✗ Team < 10 people (ops burden too high)
✗ < 1M rows (totally overkill)
✗ Frequent schema changes
```

---

## 5. Redis — Beyond Caching

### Caching Patterns

```typescript
// Cache-Aside (most common)
async getUser(id: string): Promise<User> {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  const user = await db.users.findById(id);
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  return user;
}

// Write-Through: write to both cache and DB simultaneously
async updateUser(id: string, data: UpdateUserDto) {
  const user = await db.users.update(id, data);
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  return user;
}

// Distributed Lock (Redlock algorithm)
async withLock<T>(resource: string, ttl: number, fn: () => Promise<T>) {
  const lockKey = `lock:${resource}`;
  const lockValue = ulid();
  const acquired = await redis.set(lockKey, lockValue, 'NX', 'PX', ttl * 1000);
  if (!acquired) throw new Error(`Cannot acquire lock: ${resource}`);
  try {
    return await fn();
  } finally {
    // Lua: only release if WE still own the lock (atomic check+delete)
    const script = `if redis.call("get",KEYS[1])==ARGV[1] then return redis.call("del",KEYS[1]) else return 0 end`;
    await redis.eval(script, 1, lockKey, lockValue);
  }
}
```

### Pub/Sub vs Streams

```
Pub/Sub: ephemeral, fire-and-forget
  → Messages lost if subscriber offline
  → Use for: real-time notifications, cache invalidation broadcast

Streams: persistent, consumer groups, ACK, replay
  → Messages stored until deleted
  → Use for: event log, reliable processing, audit trail
  → Like "Kafka lite" — good up to ~10K msg/sec per stream
```

---

## 6. CDC — Change Data Capture

```yaml
# Debezium: reads PostgreSQL WAL → publishes to Kafka
# Source DB = leader, derived systems = followers of change stream

connector.class: io.debezium.connector.postgresql.PostgresConnector
database.hostname: postgres
database.dbname: myapp
plugin.name: pgoutput
table.include.list: public.orders, public.payments

# Each change → Kafka topic: myapp.public.orders
# Payload: { before: {...}, after: {...}, op: "c/u/d/r" }
```

**Use cases:**

```
→ Sync DB → Elasticsearch (search without JOINs)
→ Populate CQRS read models from write DB
→ Cache invalidation (Redis)
→ Audit log (immutable stream)
→ Data pipeline to analytics DB (ClickHouse)
→ Event sourcing bootstrap
```

---

## 7. OLAP Databases

### ClickHouse — Real-time Analytics

```sql
-- Column-oriented, vectorized execution, 10-1000x faster than PG for analytics

CREATE TABLE order_events (
  event_date Date,
  order_id UUID,
  user_id UUID,
  event_type LowCardinality(String),  -- Dictionary encoding for low-cardinality
  amount Decimal(10, 2),
  created_at DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)   -- Partition by month
ORDER BY (user_id, event_date);      -- Primary key (physical sort order)

-- Analytics on billions of rows: sub-second
SELECT toStartOfDay(event_date) AS day, sum(amount) AS revenue
FROM order_events
WHERE event_date >= today() - 30
GROUP BY day ORDER BY day DESC;
```

**Use ClickHouse when:**

```
✓ Aggregations on > 10M rows frequently
✓ Real-time dashboards and metrics
✓ Audit logs, event tracking
✓ Analytics that doesn't need frequent UPDATE/DELETE
✗ OLTP workload (use PostgreSQL)
✗ Need complex JOINs between frequently updated tables
```

---

## 8. Data Systems Architecture (DDIA Ch.10-12)

### The Core Insight: Log as Integration Backbone

```
Every database is fundamentally: event log + materialized views
  Event log = immutable record of all changes (WAL, Kafka topic, event store)
  Current state = materialized view of log (can be rebuilt!)

This connects seemingly different systems:
  CDC: database changes → events → downstream systems
  Event Sourcing: events as source of truth → state derived by replay
  Kafka: distributed, durable event log
  CQRS: separate write (log) from read (materialized views)

All are instances of: "Mutable state derived from immutable event log"
Log = ground truth. Everything else = cache or view of the log.
```

### OLTP vs OLAP — Different Everything

```
                OLTP                    OLAP
Main use        Interactive apps        Business analytics
Read pattern    Small rows by key       Aggregate millions of rows
Write pattern   Random, low latency     Bulk ETL import
Dataset         GB to TB                TB to PB
Bottleneck      Disk seek time          Disk BANDWIDTH
Storage         Row-oriented            Column-oriented
Query type      Indexed lookup          Complex aggregations
Users           Thousands (end users)   Hundreds (analysts)
DB examples     PostgreSQL, MySQL       ClickHouse, Snowflake
```

### Batch Processing (MapReduce Philosophy)

```
Unix philosophy (pipes): do one thing well, compose with pipes
  cat log | grep ERROR | sort | uniq -c | sort -rn | head -10

MapReduce applies same to distributed systems:
  Map:    extract (key, value) from each record
  Sort:   framework groups all values by key
  Reduce: aggregate values with same key

Key principles:
  Immutable inputs: never modify input files
  Output = new derived data (can rebuild by re-running)
  Fault tolerance: if task fails → re-run (deterministic)

Modern engines (Spark, Flink):
  DAG of operators instead of Map→Reduce→Map→Reduce
  In-memory pipelining (avoid intermediate disk writes)
  Spark: RDDs, batch and streaming unified API
  Flink: treats batch as bounded stream
```

### Stream Processing — Batch on Unbounded Data

```
Batch:  bounded input, job completes when done
Stream: unbounded input, job never "completes"

Log-based messaging (Kafka):
  Append-only partitioned log
  Consumer groups track own offset independently
  Multiple groups = multiple independent consumers
  Message replay from any point → powerful for debugging, rebuilding

Log compaction: keep only LATEST value per key
  Bridges log and database (full history vs current state)
  Good for bootstrapping new consumers with current state

Time in streams:
  Event time:      when event actually happened (device clock)
  Processing time: when event arrives at processor (server clock)
  These differ: mobile offline hours, network delay, clock skew
  
  Watermarks: progress indicator "all events up to time T arrived"
  Stragglers: ignore, or publish correction when late event arrives

Fault tolerance:
  Microbatching (Spark Streaming): break into tiny batches, rerun on failure
  Checkpointing (Flink): snapshot state periodically, replay since checkpoint
  Idempotent writes: process twice = same result (required for at-least-once)
```

### Lambda vs Kappa Architecture

```
Lambda Architecture (older):
  Batch layer:   accurate, complete, all historical data
  Speed layer:   approximate, real-time, recent data only
  Serving layer: merge results
  Problem: two codebases (batch + stream) must stay in sync

Kappa Architecture (simpler):
  Single stream processor handles everything
  For historical data: replay from Kafka beginning in batch mode
  One codebase, easier to maintain
  Use: Flink/Beam support both batch and streaming from same code
```

### Correctness in Data Systems

```
End-to-End Argument:
  Duplicate suppression at messaging layer is NOT enough
  App must be idempotent end-to-end (use request ID as deduplication key)

Timeliness vs Integrity:
  Timeliness: user sees result quickly (eventual consistency OK)
  Integrity:  no data corruption, no double charges (must be exact)
  These are SEPARATE requirements!
  → Most user-facing: timeliness OK
  → Financial operations: integrity critical, use exact-once semantics

Auditability:
  Event-based systems naturally auditable (every change is an event)
  Continuously verify: does derived data match source?
  Catch silent data corruption early (checksums, reconciliation jobs)
```

---

## 9. Database Migration Best Practices

```typescript
// Zero-downtime migration strategy (backward-compatible steps):
// 1. Add nullable column (backward compatible)
// 2. Deploy code that writes to both old AND new column
// 3. Backfill new column
// 4. Deploy code that reads from new column only
// 5. Add NOT NULL constraint, drop old column

// Always use migration tool (TypeORM, Flyway, Liquibase, Prisma Migrate)
// NEVER manually DDL in production
// Every migration must be: reversible or have rollback plan
```
