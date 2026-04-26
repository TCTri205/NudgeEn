# Distributed Systems — Core Concepts

## CAP, Replication, Partitioning, Transactions, Consensus

> "In a system with thousands of nodes, something is always broken." — DDIA

---

## 1. CAP Theorem & Consistency Models

### CAP — Hiểu đúng

```
Trong network partition (P luôn xảy ra trong production):
Chọn C (Consistency=Linearizable) hoặc A (Availability)

CP: HBase, etcd, ZooKeeper, CockroachDB
  → Partition xảy ra: refuse request, trả error
  → Dùng: banking, inventory, distributed locks

AP: Cassandra, DynamoDB (default), CouchDB
  → Partition xảy ra: serve stale data
  → Dùng: social feed, product catalog, DNS

Nuance: Nhiều hệ thống tune per-operation
  Cassandra: consistency=ONE (AP) hoặc QUORUM (CP)
```

### PACELC & Consistency Spectrum

```
Even without partition: trade-off between Latency và Consistency
  DynamoDB: PA/EL → Available + Low Latency by default
  PostgreSQL: PC/EC → Consistent always

Consistency levels (weakest → strongest):
  Eventual:      Data converges eventually, stale reads OK
                 Use: social feeds, product catalog
  Causal:        Causally related ops preserved in order
                 "Reply appears after original post"
  Read-Your-Writes: You always see your own writes
                 Implement: route reads to primary for 60s after write
  Monotonic Reads: Never see older state than previously read
                 Implement: hash(user_id) → same replica
  Linearizable:  Every read sees most recent write, instant
                 Cost: high latency (must sync all nodes)
                 Use: financial transactions, distributed locks
```

---

## 2. Replication

### Single-Leader (Most Common)

```
1 Leader → ALL writes
N Followers → replication log → serve reads

Replication log: PostgreSQL WAL, MySQL binlog, MongoDB oplog

Sync vs Async:
  Sync:     leader waits for follower ACK → durability, slow
  Async:    leader confirms immediately → fast, risk data loss on crash
  Semi-sync: 1 sync follower + rest async (PostgreSQL default)

Failover problems:
  Async: new leader may miss recent writes → data DISCARDED
  Split-brain: both think they're leader
  Fix: Fencing tokens — monotonically increasing token,
       storage rejects writes with token ≤ last seen
```

### Replication Lag Problems & Fixes

```
Read-Your-Writes:
  Problem: post comment → read from stale replica → comment missing!
  Fix:     route reads to primary for 60s after any write

Monotonic Reads:
  Problem: user sees 5 comments, refreshes → sees 3 (different replica)
  Fix:     hash(user_id) → always same replica

Consistent Prefix Reads:
  Problem: in sharded DB, reply appears before original message
  Fix:     causally related writes → same partition
```

### Multi-Leader & Leaderless

```
Multi-leader: each datacenter has a leader, sync async between DCs
  Problem: WRITE CONFLICTS when two leaders accept writes to same data
  Fix: LWW (last write wins, risky), CRDTs, app-level resolution
  Use: multi-datacenter, offline clients (like Google Docs)

Leaderless (Cassandra/DynamoDB):
  Any node accepts writes
  Quorum: W + R > N → at least 1 node in common
    N=3, W=2, R=2 → 2+2>3 guaranteed overlap
  Read repair: fix stale replica during reads
  Sloppy quorum: write to available nodes when designated nodes down
```

---

## 3. Partitioning (Sharding)

### Core Strategies

```
Key Range:
  Contiguous range per partition (A-F, G-M...)
  ✓ Range queries efficient
  ✗ Hotspot risk (timestamps: all writes → current partition)

Hash (most common):
  hash(key) → partition, EVEN distribution
  ✗ Range queries = scatter-gather all partitions
  WRONG: hash(key) % num_nodes → adding node moves almost ALL keys
  RIGHT: fixed partitions >> nodes (10x), assign partitions to nodes
         Adding node: steal some partitions (minimal movement)

Consistent Hashing:
  Virtual ring + vnodes per physical node
  Adding node: only adjacent vnodes rebalance
  Use: Cassandra, DynamoDB, Redis Cluster

Hotspot fix:
  Celebrity (30M followers): add random suffix 0-9 to key
  Write: random suffix, Read: query all 10, merge results
```

### Secondary Indexes Partitioning

```
Local (document-partitioned): index in same partition as data
  ✓ Fast writes (1 partition), ✗ Reads = scatter-gather

Global (term-partitioned): index partitioned by indexed value
  ✓ Reads from 1 partition, ✗ Writes update multiple partitions
  Used by: DynamoDB Global Secondary Indexes
```

---

## 4. Transactions — ACID & Isolation

### ACID — True Meanings

```
Atomicity:   ALL-or-nothing on CRASH RECOVERY (not about concurrency!)
             WAL + undo log rollback incomplete transactions

Consistency: Business invariants always hold
             *** APP'S RESPONSIBILITY, not DB's ***
             DB helps: NOT NULL, UNIQUE, FK, CHECK constraints

Isolation:   Concurrent transactions appear serial
             Multiple levels — where all complexity lives

Durability:  Committed data survives crashes
             Single node: fsync to disk
             Distributed: replicated to N nodes before ACK
```

### Isolation Levels

**Read Committed (PostgreSQL default):**

```
Prevents: dirty reads (reading uncommitted data), dirty writes
NOT prevent: read skew, write skew, phantom reads

How: Return OLD value during uncommitted update (no read locks)

What still goes wrong (Read Skew):
  T1: reads balance=$500
  T2: transfers $100 → commits → balance=$400
  T1: reads again → $400 (different value in same txn!)
```

**Snapshot Isolation (MVCC):**

```
Each transaction sees a consistent snapshot at start time
Rows tagged with created_by, deleted_by (txn IDs)
You see: created_by < your_txn_id, not deleted

Prevents: read skew, dirty reads
"Readers never block writers, writers never block readers"
NOT prevent: write skew, phantoms
```

**Write Skew & Phantoms:**

```
Write Skew: each txn reads same data, updates DIFFERENT objects
  Invariant violated by combined result

Doctor on-call:
  T1 (Alice): count(oncall)=2 → alice.oncall=false
  T2 (Bob):   count(oncall)=2 → bob.oncall=false
  Result: 0 doctors! Invariant violated.

Phantom: write skew where check involves ROW ABSENCE
  T1: no seat A booked → INSERT booking for seat A
  T2: no seat A booked → INSERT booking for seat A → double booking!

Fix: SELECT FOR UPDATE (lock rows being checked)
     OR SERIALIZABLE isolation
```

**Serializability — Strongest:**

```
Two-Phase Locking (2PL) — Pessimistic [MySQL InnoDB, SQL Server]:
  Shared lock (readers) + Exclusive lock (writers)
  Writers block EVERYONE (including readers — unlike MVCC)
  Deadlock risk → DB detects, aborts one transaction
  Predicate locks fix phantoms; index-range locks cheaper

Serializable Snapshot Isolation (SSI) — Optimistic [PostgreSQL]:
  Snapshot isolation + conflict detection at COMMIT time
  Tracks stale MVCC reads and writes affecting prior reads
  If conflict → abort one, retry
  ✓ No read blocking, ✗ NOT linearizable (reads from snapshot)

Actual Serial Execution [Redis, VoltDB]:
  Single thread, transactions truly serial
  ✓ Simple, ✗ Low throughput, must fit in memory
```

---

## 5. Distributed Transactions

### Saga (Recommended for Microservices)

```
2PC NOT viable: coordinator is SPOF, participants hold locks waiting
Use Saga: sequence of local transactions + compensating actions

Orchestration Saga (Temporal/code):
  Central orchestrator calls each step, handles failures explicitly
  Easier to trace, test, reason about

Compensating transactions (always define before implementing):
  Reserve inventory → Charge payment → Create shipment
  If charge fails → Release inventory (compensation)
```

### Outbox Pattern — Guaranteed Message Delivery

```sql
-- Atomic: save entity + event in SAME DB transaction
BEGIN;
  INSERT INTO orders (id, status) VALUES ($1, 'placed');
  INSERT INTO outbox (topic, payload, created_at)
    VALUES ('order.placed', $2, NOW());
COMMIT;

-- Background worker: poll outbox → publish to Kafka → mark published
-- Guarantees at-least-once delivery
```

### Idempotency

```typescript
// Problem: retry → duplicate operations (double charge!)
// Solution: Idempotency keys

async createPayment(idempotencyKey: string, dto: PaymentDto) {
  const cached = await redis.get(`idem:${idempotencyKey}`);
  if (cached) return JSON.parse(cached);  // Same result for same key
  
  const result = await paymentGateway.charge(dto);
  await redis.setex(`idem:${idempotencyKey}`, 86400, JSON.stringify(result));
  return result;
}
```

---

## 6. Consensus (Raft) & Ordering

### Why Consensus

```
Problems requiring consensus:
  Leader election: EXACTLY 1 leader (split-brain = disaster)
  Uniqueness: EXACTLY 1 user claims username
  Distributed locks: EXACTLY 1 process holds lock

Raft algorithm:
  Leader elected by majority vote → appends to log → replicates
  Commit: once MAJORITY have entry → committed, return to client
  Failover: follower timeout → new election → higher epoch wins
  Used by: etcd, CockroachDB, TiKV, InfluxDB, Consul

ZooKeeper / etcd:
  Implement total order broadcast = solved consensus
  Use for: leader election, config management, service discovery
  NOT for primary data storage
```

### Ordering in Distributed Systems

```
Causal Order: if A caused B, everyone sees A before B
  Git branches: causally consistent (see changes you branched from)

Total Order Broadcast: all nodes receive messages in SAME ORDER
  Kafka partitions: total order within partition
  Raft log: total order across cluster

Linearizability vs Serializability:
  Linearizability: recency guarantee on individual READS/WRITES
  Serializability: isolation guarantee for TRANSACTIONS
  Strict serializability: both (2PL achieves this)
  SSI: serializable but NOT linearizable (reads from snapshot)
```

---

## 7. The Trouble with Distributed Systems

### Networks, Clocks, Process Pauses

```
Networks: packet loss, delay, partition — all possible anytime
  Cannot distinguish crashed from slow node → only timeout helps
  Retries: exponential backoff + jitter (prevent thundering herd)

Clocks:
  Wall clock: NTP-synced but drifts, can jump BACKWARD
              NEVER use for event ordering across machines
  Monotonic: always increasing within 1 process only
  Logical (Lamport timestamps): counter, increment per event
              When sending: include counter in message
              On receive: max(local, received) + 1

Process pauses (GC, VM migration, memory swap):
  Process believes it holds lock → actually expired during pause
  Fix: Fencing tokens — monotonically increasing from lock server
       Storage rejects writes with token ≤ last seen token
```

---

## 8. Circuit Breaker & Rate Limiting

### Circuit Breaker

```
CLOSED → normal, track failures
OPEN → reject immediately (fail fast)
HALF-OPEN → probe recovery

Transitions:
  → OPEN: failure rate > 50% in 30s (min 10 requests)
  → HALF-OPEN: after 30s timeout
  → CLOSED: N consecutive successes
  → OPEN again: any failure in HALF-OPEN
```

```typescript
const breaker = new CircuitBreaker(paymentService.charge, {
  timeout: 3000, errorThresholdPercentage: 50,
  resetTimeout: 30000, volumeThreshold: 10,
});
breaker.fallback(() => ({ status: 'queued', message: 'Payment queued' }));
```

### Sliding Window Rate Limiter

```typescript
async rateLimit(userId: string, limit: number, windowSecs: number) {
  const key = `rate:${userId}`;
  const now = Date.now();
  const pipe = redis.pipeline();
  pipe.zremrangebyscore(key, 0, now - windowSecs * 1000);
  pipe.zcard(key);
  pipe.zadd(key, now, `${now}-${Math.random()}`);
  pipe.expire(key, windowSecs);
  const results = await pipe.exec();
  const count = results[1][1] as number;
  return count <= limit; // true = allowed
}
```

---

## 9. Distributed ID Generation

```
UUID v4:   Simple, no coordination, NOT sortable, 128 bits
Snowflake: [timestamp 41b][datacenter 5b][worker 5b][sequence 12b]
           Sortable by time, compact, no coordination
ULID:      [time 48b][random 80b], URL-safe string, sortable
           Recommended for most backend use cases

Database sequence: Simple/monotonic but SPOF at scale
```

```typescript
import { ulid } from 'ulid';
@Entity()
class Order {
  @PrimaryColumn('varchar', { length: 26 })
  id: string = ulid(); // Sortable: ORDER BY id ≈ ORDER BY created_at
}
```
