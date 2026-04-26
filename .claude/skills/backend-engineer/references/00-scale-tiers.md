# Scale Tiers — Blueprint cho từng cấp độ hệ thống

> "Premature optimization is the root of all evil. But so is ignoring scale."

---

## Clarifying Questions — Hỏi trước khi design

```
1. Hiện tại có bao nhiêu users? DAU (daily active)?
2. Peak QPS là bao nhiêu? (requests/second)
3. Data write:read ratio là bao nhiêu?
4. Latency requirement: P99 < ? ms
5. Availability SLA: 99%? 99.9%? 99.99%?
6. Data consistency: strong hay eventual?
7. Team size và ops capability?
8. Cloud budget per month?
9. Timeline: khi nào cần go-live?
10. Đây là greenfield hay đang migrate?
```

---

## Tier 0 — Prototype / MVP (< 1,000 users)

**Mục tiêu**: Ship nhanh, validate idea. Cost tối thiểu. Đừng over-engineer.

### Architecture

```
Internet → Single Server (App + DB) → Object Storage (files)
```

### Tech Stack

```
Backend:   NestJS hoặc FastAPI (1 service)
Database:  PostgreSQL trên cùng server hoặc managed (Supabase, Neon)
Cache:     Không cần — PostgreSQL đủ nhanh
Queue:     Không cần — synchronous calls OK
Auth:      JWT + bcrypt
Hosting:   1 VPS (Railway, Render, Fly.io) hoặc AWS EC2 t3.small
Storage:   S3 hoặc Cloudflare R2
CDN:       Cloudflare free tier
```

### Cost estimate

```
~$20-50/month total
- App server: $10-20/month (Railway/Render)
- DB: $10-25/month (managed PostgreSQL)
- Storage: < $5/month
```

### Không cần / Tránh ở giai đoạn này

```
❌ Microservices (over-engineered)
❌ Kafka (way too complex)
❌ Redis cluster
❌ Kubernetes
❌ Read replicas
```

### Code của tier này

```typescript
// Simple, direct — không abstraction thừa
@Post('/orders')
async createOrder(@Body() dto: CreateOrderDto, @CurrentUser() user: User) {
  const order = await this.orderService.create(dto, user.id);
  await this.emailService.sendConfirmation(user.email, order); // sync OK ở scale này
  return order;
}
```

### Trigger để move lên Tier 1

- Response time > 500ms consistently
- DB CPU > 70% thường xuyên
- > 50 concurrent users gây issues
- Cần team thứ 2 làm việc song song

---

## Tier 1 — Early Growth (1,000 – 100,000 users)

**Mục tiêu**: Handle growth mà không rewrite. Tách concerns. Bắt đầu async.

### Architecture

```
Internet
    ↓
Load Balancer (AWS ALB / Nginx)
    ↓
App Servers x2-3 (stateless, horizontal scale)
    ↓              ↓
PostgreSQL      Redis Cache
(Primary +      (Sessions,
 1 Replica)      Hot data)
    ↓
S3 (files, assets)
```

### Key changes từ Tier 0

```
+ Read replica: tách read-heavy queries
+ Redis: cache hot data, sessions, rate limiting
+ Async jobs: BullMQ (Redis-backed) cho email, reports, webhooks
+ CDN: cache static assets
+ Health checks + basic monitoring (Prometheus + Grafana)
+ Secrets manager (AWS Secrets Manager / Doppler)
```

### Message Queue ở tier này: BullMQ (Redis-backed)

```typescript
// Đủ mạnh cho 80% use cases ở tier 1
// Không cần Kafka/RabbitMQ — overkill
@Processor('email')
class EmailProcessor {
  @Process('send-confirmation')
  async handleSendConfirmation(job: Job<{ orderId: string }>) {
    const order = await this.orderRepo.findById(job.data.orderId);
    await this.mailer.sendOrderConfirmation(order);
  }
}

// Enqueue từ controller
await this.emailQueue.add('send-confirmation', { orderId: order.id }, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
});
```

### Database strategy ở tier này

```typescript
// Routing reads vs writes
class DatabaseService {
  constructor(
    @InjectDataSource('primary') private primary: DataSource,
    @InjectDataSource('replica') private replica: DataSource,
  ) {}

  // Writes → primary
  async write<T>(fn: (ds: DataSource) => Promise<T>): Promise<T> {
    return fn(this.primary);
  }

  // Reads → replica (eventually consistent — acceptable ở tier 1)
  async read<T>(fn: (ds: DataSource) => Promise<T>): Promise<T> {
    return fn(this.replica);
  }
}
```

### Cost estimate

```
~$200-500/month
- App servers (2x t3.small): ~$30/month
- RDS PostgreSQL (db.t3.medium + replica): ~$150/month
- ElastiCache Redis (cache.t3.micro): ~$30/month
- ALB: ~$20/month
- CloudWatch, misc: ~$50/month
```

### Trigger để move lên Tier 2

- DB write QPS > 1,000/sec thường xuyên
- Single PostgreSQL không đủ dù đã optimize
- Team > 5 engineers, cần parallel development
- Features bắt đầu có domain boundaries rõ ràng

---

## Tier 2 — Scale-up (100,000 – 1,000,000 users)

**Mục tiêu**: Domain isolation, production-grade messaging, caching layers.

### Architecture

```
Internet
    ↓
CDN (CloudFront / Cloudflare)
    ↓
API Gateway (Kong / AWS API GW)
  Auth, Rate Limiting, Routing
    ↓
Service Mesh (internal)
    ├── User Service
    ├── Order Service ──→ RabbitMQ / SQS
    ├── Payment Service     ↓
    ├── Notification Service ←─ consumers
    └── Search Service
         ↓
   ┌─────┴────────────────────────┐
PostgreSQL Cluster   Elasticsearch   Redis Cluster
(sharded nếu cần)   (search/logs)   (cache, sessions)
```

### Modular Monolith TRƯỚC khi Microservices

```typescript
// Bắt đầu với modular monolith — tách module nhưng 1 codebase
// Module không share DB trực tiếp — giao tiếp qua internal events

// orders/orders.module.ts
@Module({
  imports: [TypeOrmModule.forFeature([Order, OrderItem])],
  providers: [OrderService, OrderRepository, OrderEventHandler],
  exports: [OrderService], // expose interface, không expose repo
})
export class OrdersModule {}

// payments/payment.event-handler.ts
@EventsHandler(OrderPlacedEvent)
class PaymentEventHandler implements IEventHandler<OrderPlacedEvent> {
  async handle(event: OrderPlacedEvent) {
    // Payment domain reacts to Order event — không gọi OrderService trực tiếp
    await this.paymentService.initiatePayment(event.orderId, event.amount);
  }
}
```

### Message Queue: RabbitMQ hoặc AWS SQS

**Chọn RabbitMQ khi:**

- Cần routing phức tạp (topic exchanges, dead letter queues)
- Message TTL quan trọng
- Self-hosted OK
- Need message acknowledgment + retry

**Chọn AWS SQS khi:**

- Fully managed, không muốn ops
- Simple FIFO hoặc standard queue
- Đang fully on AWS
- Cost predictable

```typescript
// RabbitMQ với NestJS
@Module({
  imports: [
    RabbitMQModule.forRoot({
      uri: process.env.RABBITMQ_URI,
      exchanges: [
        { name: 'orders', type: 'topic' },
        { name: 'payments', type: 'direct' },
      ],
    }),
  ],
})
export class AppModule {}

// Publisher
@Injectable()
class OrderService {
  constructor(private readonly amqp: AmqpConnection) {}

  async placeOrder(dto: CreateOrderDto): Promise<Order> {
    const order = await this.orderRepo.save(Order.create(dto));
    
    // Outbox pattern: save event trong cùng transaction
    await this.outboxRepo.save({
      exchange: 'orders',
      routingKey: 'order.placed',
      payload: { orderId: order.id, customerId: order.customerId, amount: order.total },
    });
    
    return order;
  }
}

// Consumer
@RabbitSubscribe({
  exchange: 'orders',
  routingKey: 'order.placed',
  queue: 'notification-service.order-placed',
  queueOptions: {
    deadLetterExchange: 'orders.dlx', // DLQ for failed messages
    messageTtl: 86400000, // 24 hours
  },
})
async handleOrderPlaced(payload: OrderPlacedEvent) {
  await this.notificationService.sendOrderConfirmation(payload.orderId);
}
```

### AWS SQS Pattern

```typescript
// SQS với idempotency
@Injectable()
class SqsConsumerService {
  async processMessage(message: SQSRecord): Promise<void> {
    const { orderId } = JSON.parse(message.body);
    const receiptHandle = message.receiptHandle;
    
    // Idempotency check — đã xử lý rồi thì skip
    const processed = await this.redis.get(`processed:${message.messageId}`);
    if (processed) return;
    
    await this.fulfillOrder(orderId);
    
    // Mark processed BEFORE delete (nếu crash sau delete, sẽ process lại)
    await this.redis.setex(`processed:${message.messageId}`, 86400, '1');
    await this.sqs.deleteMessage({ QueueUrl, ReceiptHandle: receiptHandle });
  }
}
```

### Cost estimate

```
~$2,000-8,000/month
- EKS (Kubernetes): ~$500/month + nodes
- RDS (Multi-AZ): ~$400/month
- ElastiCache (cluster): ~$200/month
- RabbitMQ (MQ): ~$100/month
- Elasticsearch: ~$300/month
- Data transfer, misc: ~$500/month
```

### Trigger để move lên Tier 3

- Single region không đủ cho latency requirements
- > 10,000 write QPS sustained
- Cần 99.99% availability (< 1h downtime/year)
- Data > 10TB, single PostgreSQL instance không đủ

---

## Tier 3 — High Scale (1M – 100M users)

**Mục tiêu**: Multi-region, data sharding, Kafka cho event streaming.

### Architecture

```
Global Traffic
    ↓
GeoDNS / Global Load Balancer
    ↓              ↓
Region US-East   Region AP-Southeast
    ↓                  ↓
[API Gateway]       [API Gateway]
[Services...]       [Services...]
    ↓                  ↓
    └──── Kafka ────────┘  (cross-region replication)
              ↓
    ┌─────────┴──────────┐
Cassandra           ClickHouse
(OLTP, global write) (Analytics)
              ↓
         Data Lake (S3)
```

### Kafka: when and why

```
Dùng Kafka ở tier 3+ khi:
✓ > 100,000 messages/second sustained
✓ Multiple teams consume same events independently
✓ Need event replay / reprocessing (audit, analytics, ML features)
✓ Cross-service event streaming với ordering guarantees
✓ Log aggregation ở scale lớn
✓ CDC (Change Data Capture) pipeline

KHÔNG dùng Kafka ở tier 0-2:
✗ Operational complexity cao (ZooKeeper/KRaft, partition management)
✗ Overkill cho simple async jobs (dùng BullMQ/SQS)
✗ Team cần expertise riêng
```

```typescript
// Kafka producer với NestJS
@Injectable()
class EventProducer {
  private readonly producer: Producer;

  async publishOrderPlaced(event: OrderPlacedEvent): Promise<void> {
    await this.producer.send({
      topic: 'orders',
      messages: [{
        key: event.orderId,  // Partition by orderId — ordering per order
        value: JSON.stringify(event),
        headers: {
          'event-type': 'order.placed',
          'schema-version': '1',
          'source-service': 'order-service',
          'correlation-id': event.correlationId,
        },
      }],
    });
  }
}

// Kafka consumer với consumer groups
@Injectable()
class InventoryConsumer implements OnModuleInit {
  private consumer: Consumer;

  async onModuleInit() {
    this.consumer = this.kafka.consumer({ groupId: 'inventory-service' });
    await this.consumer.subscribe({ topics: ['orders'], fromBeginning: false });
    
    await this.consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        const event = JSON.parse(message.value.toString());
        await this.handleMessage(event, message.headers);
      },
    });
  }
}
```

### Database sharding strategy

```
User table: shard by user_id % N
  → Shard 0: users 0, N, 2N...
  → Shard 1: users 1, N+1, 2N+1...

Order table: shard by created_at (time-based) + region
  → 2024_orders_us, 2024_orders_ap...

Hotspot avoidance:
  ❌ Shard by first letter (A-Z) → uneven distribution
  ✓ Shard by consistent hash → even distribution
  ✓ Virtual nodes → easier rebalancing
```

### Cost estimate

```
~$30,000-100,000/month
- Kubernetes (multi-region): ~$10,000/month
- Cassandra cluster: ~$5,000/month
- Kafka cluster (MSK): ~$3,000/month
- ClickHouse: ~$2,000/month
- CDN, data transfer: ~$10,000/month
- Engineering team (bigger cost than infra!)
```

---

## Tier 4 — Hyper Scale (100M – 1B+ users)

**Mục tiêu**: Custom infra, global consistency, cost per request optimization.

### Ở tier này: Build vs Buy decision

```
Google Spanner  → Global ACID (Spanner)
Meta's TAO      → Custom graph cache
Netflix's EVCache → Distributed Memcached
Uber's Cadence  → Now open-source Temporal
Twitter's Snowflake → Distributed ID generation

Bài học: BigTech build custom vì:
1. Scale vượt khỏi off-the-shelf capabilities
2. Cost optimization ở scale lớn (1% improvement = $millions)
3. Specific domain requirements không ai cover

NHƯNG: 99.9% engineers không bao giờ cần tier này.
Focus là KNOWING it exists, không phải implementing it.
```

### Key patterns ở tier 4

```
- Consistent Hashing Ring cho distributed caching
- Cell-based architecture (isolate blast radius)
- Dark launch / traffic shadowing (test với real traffic)
- Chaos engineering (Netflix Chaos Monkey)
- Custom load shedding + backpressure
- Global traffic management (Google GSLB)
- Edge computing (Cloudflare Workers, Lambda@Edge)
```

---

## Scale Decision Cheat Sheet

```
Users          Arch              DB              Queue           Cache
< 1K           Single server     PostgreSQL      None/BullMQ     None
1K - 100K      Vertical scale    PG + Replica    BullMQ          Redis single
100K - 1M      Horizontal scale  PG + sharding   RabbitMQ/SQS    Redis cluster
1M - 100M      Microservices     Cassandra+PG    Kafka           Redis cluster
100M - 1B+     Multi-region      Custom/Spanner  Kafka+Flink     Custom cache

Latency targets:
< 1K users:    P99 < 2s (users tolerate this for MVP)
1K-100K:       P99 < 500ms
100K-1M:       P99 < 200ms
1M+:           P99 < 100ms, P50 < 20ms

Availability targets:
MVP:           99% (7.3h downtime/month — OK)
Production:    99.9% (43min/month)
Serious prod:  99.99% (4.3min/month) — needs multi-AZ
Critical:      99.999% (26sec/month) — needs multi-region
```
