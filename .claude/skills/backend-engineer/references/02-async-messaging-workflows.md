# Async, Messaging & Workflows

## Message Queues, CQRS, Event Sourcing, Temporal

---

## 1. Queue Selection Framework

### Hỏi trước khi chọn

```
1. Throughput cần thiết? (messages/second)
2. Cần message ordering không?
3. Cần replay messages không?
4. Delivery guarantee: at-most-once / at-least-once / exactly-once?
5. Workflow có nhiều bước phụ thuộc nhau không?
6. Ops burden team có thể handle không?
```

### Decision Matrix

```
┌────────────────┬──────────┬──────────┬──────────┬──────────┐
│                │ BullMQ   │ RabbitMQ │ SQS/SNS  │ Kafka    │
├────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Simple jobs    │ ✅ Best  │ ✅ Good  │ ✅ Good  │ ❌ Overkill│
│ Priority queue │ ✅       │ ✅       │ ❌       │ ❌       │
│ Complex routing│ ❌       │ ✅ Best  │ ⚠️ SNS  │ ⚠️      │
│ Message replay │ ❌       │ ❌       │ ❌       │ ✅ Best  │
│ Event streaming│ ❌       │ ⚠️      │ ❌       │ ✅ Best  │
│ Throughput     │ ⚠️ Redis │ ✅ Good  │ ✅ Good  │ ✅ Best  │
│ Fully managed  │ ✅ Redis  │ ❌       │ ✅ Best  │ ✅ MSK   │
│ Ops simplicity │ ✅ Best  │ ⚠️      │ ✅ Best  │ ❌ Complex│
│ Cost (small)   │ ✅ Cheap │ ✅ Cheap │ ✅ Cheap │ ❌ Expensive│
└────────────────┴──────────┴──────────┴──────────┴──────────┘

Tier mapping:
  Tier 0-1 (MVP → early growth):   BullMQ
  Tier 1-2 (growth → scale):       RabbitMQ or SQS
  Tier 3+ (high scale):            Kafka
  Complex multi-step workflows:     Temporal (any tier)
```

---

## 2. BullMQ — Redis-backed Job Queue

**Best for:** Background jobs, scheduled tasks, simple async. Tier 0-2.

```typescript
// Setup
BullModule.forRoot({
  connection: { host: 'localhost', port: 6379 },
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: 1000,
    removeOnFail: 5000,
  },
});

// Producer
await this.emailQueue.add('order-confirmation', { orderId }, {
  delay: 0, priority: 1,
});

// Delayed job (7 days after order)
await this.emailQueue.add('follow-up-review', { orderId }, {
  delay: 7 * 24 * 60 * 60 * 1000,
});

// Processor
@Processor('email')
class EmailProcessor extends WorkerHost {
  @Process('order-confirmation')
  async handle(job: Job<{ orderId: string }>) {
    await this.mailer.sendConfirmation(job.data.orderId);
    // Throws → BullMQ retries based on attempts config
  }
}
```

---

## 3. RabbitMQ — Advanced Routing

**Best for:** Complex routing, pub/sub patterns, microservice communication.

### Exchange Types

```
Direct:   route by exact routing key
          order-service → "payment.process" → payment-service

Topic:    route by pattern (* = 1 word, # = 0+ words)
          "order.#" matches: order.placed, order.updated, order.item.added
          "*.placed" matches: order.placed, payment.placed

Fanout:   broadcast to ALL bound queues
          notification-fanout → email-queue, sms-queue, push-queue

Dead Letter Queue (DLX): failed messages → separate queue for inspection
```

```typescript
// Publisher
await this.amqp.publish('orders', 'order.placed', event, {
  persistent: true,   // Survive broker restart
  messageId: event.id, // Deduplication
});

// Consumer with DLQ
@RabbitSubscribe({
  exchange: 'orders',
  routingKey: 'order.placed',
  queue: 'inventory.order-placed',
  queueOptions: {
    deadLetterExchange: 'orders.dlx',
    messageTtl: 3600000,  // 1 hour TTL
  },
  errorHandler: defaultNackErrorHandler, // Nack → goes to DLQ
})
async handleOrderPlaced(message: OrderPlacedEvent) {
  await this.inventoryService.reserve(message.orderId, message.items);
}
```

---

## 4. AWS SQS + SNS

**Best for:** Fully AWS-native apps, want zero ops.

```typescript
// SQS FIFO: exactly-once within deduplication window, ordering per group
await sqs.send(new SendMessageCommand({
  QueueUrl,
  MessageBody: JSON.stringify(body),
  MessageGroupId: groupId,          // FIFO ordering
  MessageDeduplicationId: ulid(),   // FIFO dedup
}));

// Consumer: long polling + idempotency
async processMessage(message: Message) {
  const processed = await redis.get(`processed:${message.MessageId}`);
  if (processed) return; // Already handled
  
  await this.handleEvent(JSON.parse(message.Body));
  await redis.setex(`processed:${message.MessageId}`, 86400, '1');
  await sqs.send(new DeleteMessageCommand({
    QueueUrl, ReceiptHandle: message.ReceiptHandle,
  }));
}

// SNS for fanout: 1 publish → multiple SQS queues
// SNS topic → filter policy → SQS queues (per service)
```

---

## 5. Apache Kafka — Event Streaming

**Best for:** High-throughput (>100K msg/sec), event replay, cross-team event sharing.

### Core Concepts

```
Topic: named channel, like a table in a DB
Partition: ordering guaranteed WITHIN partition, not across
  key-based routing → same key → same partition → ordering per entity

Consumer Groups:
  Same group: each partition consumed by 1 consumer (work queue)
  Different groups: each group sees ALL messages (fanout)

Offset: position in partition, consumer commits after processing
  Crash → resume from committed offset (at-least-once)

Log compaction: keep only LATEST value per key
  Like a KV database backed by log
  Good for: maintaining current state (vs full event history)
```

```typescript
// Producer: key-based partition routing for ordering
await this.producer.send({
  topic: 'orders-v1',
  messages: [{
    key: event.orderId,   // Same order → same partition → ordered
    value: JSON.stringify(event),
    headers: {
      'event-type': 'order.placed',
      'schema-version': '1',
      'correlation-id': event.correlationId,
    },
  }],
});

// Consumer: manual offset commit for exactly-once semantics
@MessagePattern('orders-v1')
async handleOrderEvent(@Ctx() ctx: KafkaContext) {
  const { offset, partition } = ctx.getMessage();
  try {
    await this.processEvent(JSON.parse(ctx.getMessage().value.toString()));
    await ctx.getConsumer().commitOffsets([{
      topic: 'orders-v1', partition, offset: (parseInt(offset)+1).toString(),
    }]);
  } catch (err) {
    // Don't commit → will reprocess after restart
    throw err;
  }
}
```

### Kafka vs Other Queues

```
Use Kafka when:
  ✓ > 100K messages/second sustained
  ✓ Multiple teams consume same events independently
  ✓ Need replay / reprocessing (audit, analytics, ML)
  ✓ Event ordering with partitioning
  ✓ CDC pipeline

Don't use Kafka when:
  ✗ Simple background jobs (use BullMQ/SQS — much simpler)
  ✗ Team < 5 engineers (ops overhead too high)
  ✗ < 10K msg/sec (overkill, expensive)
```

---

## 6. CQRS — Command Query Responsibility Segregation

### When to Use / Avoid

```
Use CQRS when:
  ✓ Read/Write load very different (>10:1 ratio)
  ✓ Read model needs many different shapes for different clients
  ✓ Scaling read and write independently
  ✓ Using Event Sourcing (requires CQRS to query efficiently)

Avoid when:
  ✗ Simple CRUD (under-engineering is fine)
  ✗ Team < 5 engineers
  ✗ Data needs strong consistency immediately after write
  ✗ Startup in early product-market fit phase
```

### Implementation

```typescript
// ── WRITE SIDE ──────────────────────────────────────
class PlaceOrderCommand {
  constructor(
    readonly customerId: string,
    readonly items: OrderItem[],
    readonly correlationId = ulid(),
  ) {}
}

@CommandHandler(PlaceOrderCommand)
class PlaceOrderHandler implements ICommandHandler<PlaceOrderCommand> {
  async execute(cmd: PlaceOrderCommand): Promise<string> {
    const order = Order.place(cmd.customerId, cmd.items); // Domain logic in model
    await this.orderRepo.save(order);
    await this.eventBus.publishAll(order.pullDomainEvents());
    return order.id;
  }
}

// Rich domain model (NOT anemic)
class Order {
  private _events: DomainEvent[] = [];

  static place(customerId: string, items: OrderItem[]): Order {
    if (items.length === 0) throw new DomainError('Order must have items');
    const order = new Order();
    order.id = ulid();
    order.status = OrderStatus.PENDING;
    order._events.push(new OrderPlacedEvent({ orderId: order.id, customerId, items }));
    return order;
  }

  confirm(): void {
    if (this.status !== OrderStatus.PENDING) throw new DomainError('Only pending orders can be confirmed');
    this.status = OrderStatus.CONFIRMED;
    this._events.push(new OrderConfirmedEvent({ orderId: this.id }));
  }

  pullDomainEvents(): DomainEvent[] {
    const events = [...this._events];
    this._events = [];
    return events;
  }
}

// ── READ SIDE ───────────────────────────────────────
// Query: read-optimized, specific to one use case
@QueryHandler(GetOrderSummaryQuery)
class GetOrderSummaryHandler {
  async execute(query: GetOrderSummaryQuery): Promise<OrderSummaryDto> {
    // Read from denormalized view — no joins needed
    return this.orderSummaryView.findOne({
      where: { id: query.orderId, customerId: query.requestingUserId },
    });
  }
}

// Read Model: denormalized, pre-aggregated, fast to query
@Entity('order_summary_view')
class OrderSummaryView {
  @PrimaryColumn() id: string;
  @Column() customerId: string;
  @Column() customerName: string;    // Denormalized from user — no JOIN
  @Column() customerEmail: string;
  @Column() status: string;
  @Column('decimal') total: number;
  @Column('jsonb') items: OrderItemSummary[];  // Pre-aggregated
}

// Projector: keeps read model in sync with write events
@EventsHandler(OrderPlacedEvent)
class OrderSummaryProjector {
  async handle(event: OrderPlacedEvent): Promise<void> {
    const customer = await this.userService.getById(event.customerId);
    await this.repo.save({
      id: event.orderId, customerId: event.customerId,
      customerName: customer.name, status: 'pending',
      total: event.total, items: event.items,
    });
  }
}
```

---

## 7. Event Sourcing

### When to Use / Avoid

```
Use Event Sourcing when:
  ✓ "History of changes" is a business requirement (banking ledger, order timeline)
  ✓ Full audit trail required by compliance
  ✓ Time-travel queries: "Account state on date X?"
  ✓ Need to rebuild read models from scratch

Avoid when:
  ✗ History not a business requirement (just use updated_at + CQRS)
  ✗ Team unfamiliar with eventual consistency
  ✗ CRUD apps with no need for replay
```

### Core Pattern

```typescript
// Event Store: append-only log (never UPDATE)
@Entity('domain_events')
class StoredEvent {
  @PrimaryColumn() id: string;
  @Column() aggregateId: string;   // orderId
  @Column() aggregateType: string; // 'Order'
  @Column() eventType: string;     // 'OrderPlaced'
  @Column('int') version: number;  // For optimistic locking
  @Column('jsonb') payload: object;
  @Column() occurredAt: Date;
}

// Event-Sourced Aggregate
class Order {
  private _version = 0;
  private _events: DomainEvent[] = [];
  id: string; status: OrderStatus; items: OrderItem[];

  // Rehydrate from event history: replay all events → current state
  static rehydrate(events: DomainEvent[]): Order {
    const order = new Order();
    for (const event of events) order.apply(event, false);
    return order;
  }

  private apply(event: DomainEvent, isNew = true): void {
    if (event instanceof OrderPlacedEvent) {
      this.id = event.orderId;
      this.status = OrderStatus.PENDING;
      this.items = event.items;
    } else if (event instanceof OrderConfirmedEvent) {
      this.status = OrderStatus.CONFIRMED;
    }
    this._version++;
    if (isNew) this._events.push(event);
  }
}

// Snapshot: optimization for long-lived aggregates
// If 10,000 events per order → slow rehydration
// Solution: snapshot every 100 events, then only replay events after snapshot
async findById(orderId: string): Promise<Order> {
  const snapshot = await this.snapshotRepo.findLatest(orderId);
  const events = await this.eventStore.findAfterVersion(orderId, snapshot?.version ?? 0);
  const order = snapshot ? Order.fromSnapshot(snapshot.state) : new Order();
  for (const event of events) order.apply(event.payload, false);
  return order;
}
```

---

## 8. Temporal — Durable Execution Engine

### Netflix Case Study

```
Problem: Clouddriver (Spinnaker) had 4% transient deployment failures
  Root cause: state stored in-memory, retry logic inconsistent, no visibility

After Temporal: failures dropped from 4% → 0.0001% (4.5 orders of magnitude)
Netflix uses Temporal for: CDN operations, Live streaming reliability,
  Media encoding (Plato platform), Flink blue-green deployments

Quote: "Without Temporal, we would be lagging behind significantly from where we are.
       I don't think that the product I work on would be successful at all
       if Temporal were not part of the solution." — Rob Zienert, Netflix
```

### Core Architecture

```
Temporal Cluster:
  Frontend Service: gRPC entry point for SDKs
  History Service:  Stores complete event history per workflow (4 CPU, 6+ GiB)
                    Sharded (1024+ shards) — most resource-intensive service
  Matching Service: Task Queue management, routes tasks to workers
                    Auto-partitions task queues under high load
  Worker Service:   Internal system workflows

Sync Match vs Async Match:
  Sync: worker poller waiting → task arrives → hand off immediately (ideal)
  Async: no poller → task goes to persistence DB → retrieved later
  Poll Sync Rate target: > 99%
  If < 90%: add more workers/pollers
```

### Workflow Basics — Determinism Rules

```typescript
// Temporal replays workflow history on crash recovery
// Workflow code MUST be deterministic

// ❌ NON-DETERMINISTIC — NEVER in Workflow code
const delay = Math.random() * 1000;    // Different each replay!
const now = Date.now();                 // Different timestamp each replay!
const id = uuid();                      // Different UUID each replay!

// ✅ DETERMINISTIC — use Temporal APIs
export async function orderFulfillmentWorkflow(orderId: string): Promise<void> {
  const { reserveInventory, processPayment, createShipment, sendConfirmation } =
    proxyActivities<typeof activities>({
      startToCloseTimeout: '30s',
      retry: { maximumAttempts: 3, initialInterval: '1s', backoffCoefficient: 2 },
    });

  await reserveInventory(orderId);

  const paymentResult = await processPayment(orderId);
  if (paymentResult.status === 'failed') {
    await compensateInventoryReservation(orderId);
    throw new Error(`Payment failed: ${paymentResult.reason}`);
  }

  await createShipment(orderId);

  // Sleep 7 days — Temporal persists state, no cron needed!
  await sleep('7 days');
  await sendReviewRequest(orderId);
}

// Activities: actual implementations, CAN have side effects
export const activities = {
  async reserveInventory(orderId: string): Promise<void> {
    const order = await orderRepo.findById(orderId);
    await inventoryService.reserve(order.items);
    // Throws → Temporal retries per retry policy
  },
};
```

### Worker Architecture — Key Parameters

```typescript
const worker = await Worker.create({
  taskQueue: 'order-processing',
  workflowsPath: require.resolve('./workflows'),
  activities,

  // Pollers: speed of PICKING UP tasks from queue
  // (usually default is enough, increase if schedule-to-start latency high)
  maxConcurrentWorkflowTaskPollers: 5,
  maxConcurrentActivityTaskPollers: 20,

  // Slots: max tasks executing SIMULTANEOUSLY
  // Monitor: worker_task_slots_available > 0 always
  maxConcurrentWorkflowTaskExecutions: 100,
  maxConcurrentActivityTaskExecutions: 200,

  // Rate limiting (protect downstream services)
  maxActivitiesPerSecond: 100,           // Per worker
  maxTaskQueueActivitiesPerSecond: 500,  // Across ALL workers on this queue
});
```

```
Poller vs Slot distinction (critical to understand):
  Pollers: HOW FAST tasks are picked up from Temporal service
  Slots:   HOW MANY tasks execute simultaneously

If schedule-to-start latency high:
  → Check worker_task_slots_available
  → If slots > 0 and latency high: add more pollers
  → If slots = 0: add more workers or increase slot count

IO-bound activities (HTTP, DB): high concurrency OK (threads waiting mostly)
CPU-bound activities (encoding): low concurrency = num_cpu_cores

Separate task queues by workload type:
  'io-tasks': maxConcurrentActivityTaskExecutions: 500
  'cpu-tasks': maxConcurrentActivityTaskExecutions: 4 (= CPU cores)
```

### Production Patterns

```typescript
// Versioning — handle code changes without breaking running workflows
export async function orderWorkflow(orderId: string) {
  if (patched('add-notification-step')) {
    await sendOrderNotification(orderId);  // Only for new workflows
  }
}

// Continue-As-New — for workflows that run "forever" (history size limit)
export async function monitoringWorkflow(targetId: string, iteration = 0) {
  for (let i = 0; i < 1000; i++) {
    await checkAndAlert(targetId);
    await sleep('1 minute');
  }
  // Restart with fresh history, pass state forward
  await continueAsNew<typeof monitoringWorkflow>(targetId, iteration + 1000);
}

// Signals + Queries: interact with running workflows
wf.setHandler(pauseSignal, () => { isPaused = true; });   // External → workflow
wf.setHandler(statusQuery, () => currentStatus);           // Read current state

// From client:
await handle.signal('pause');
const status = await handle.query('status');
```

### Temporal vs Alternatives

```
BullMQ:         Simple background jobs, short-lived (< 30 min), Redis already in stack
AWS Step Fns:   Fully managed, AWS-only, JSON-based, low volume
Temporal:       Complex multi-step, long-running (days/weeks), full audit trail
                Cross-service orchestration, complex retry per activity
Airflow:        Data pipelines, DAG-based, Python-centric

Don't use Temporal for:
  ✗ Simple background jobs → BullMQ
  ✗ Pure event fanout → Kafka/RabbitMQ
  ✗ Team with no ops capacity for Temporal cluster
```

---

## 9. Messaging Patterns Reference

### Fan-out / Pub-Sub

```
Kafka:     1 topic + N consumer groups (each group sees all messages)
RabbitMQ:  Fanout exchange → N queues bound to it
SNS→SQS:   SNS topic → N SQS queues
Redis:     Pub/Sub (ephemeral, fire-and-forget)
```

### Work Queue (Competing Consumers)

```
Each message processed by EXACTLY ONE consumer
BullMQ:    default behavior
RabbitMQ:  multiple consumers on same queue
SQS:       default (at-least-once)
Kafka:     multiple consumers in SAME consumer group
```

### Delivery Guarantees Comparison

```
At-most-once:   fire-and-forget, message may be lost (Redis Pub/Sub)
At-least-once:  retry on failure, may process twice (SQS, RabbitMQ, Kafka)
                → requires idempotent handlers!
Exactly-once:   Kafka with idempotent producer + transactions
                Temporal: framework guarantees each activity runs to completion
```
