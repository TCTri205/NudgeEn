# Coding Standards — SOLID, Clean Code & NestJS

## SOLID Principles

### S — Single Responsibility

```typescript
// ❌ One class doing everything
class UserService {
  create() {} sendEmail() {} generateInvoice() {} logActivity() {}
}

// ✅ Separate concerns
class UserService { create() {} }
class EmailService { sendWelcome() {} }
class InvoiceService { generate() {} }
```

### O — Open/Closed (Strategy Pattern)

```typescript
interface PaymentProvider {
  charge(amount: number): Promise<Result>;
}
class StripeProvider implements PaymentProvider {}
class VNPayProvider implements PaymentProvider {}

// Add new provider WITHOUT changing PaymentService
class PaymentService {
  async charge(method: string, amount: number) {
    const provider = this.providers.get(method);
    if (!provider) throw new UnsupportedMethodError(method);
    return provider.charge(amount);
  }
}
```

### L — Liskov Substitution

Subclass must be substitutable for base class without breaking behavior.
Design by interface, not inheritance.

### I — Interface Segregation

Split fat interfaces. Client shouldn't implement what it doesn't use.

### D — Dependency Inversion

```typescript
// Depend on abstractions (interfaces), not concretions
interface OrderRepository { save(order: Order): Promise<void>; }
@Injectable()
class OrderService {
  constructor(
    @Inject(ORDER_REPO) private repo: OrderRepository, // interface
  ) {}
}
```

## Clean Code Rules

### Naming

```typescript
// Clear, self-documenting names
const sessionExpirationDays = 30;          // not: const d = 30
const isEligibleForRefund = order.canRefund();  // not: const ok = ...
async function calculateOrderTotal(items: OrderItem[]): Promise<Money> {}

// Boolean: is/has/can/should prefix
const isActive = true;
const hasPermission = user.roles.includes(Role.ADMIN);
```

### Functions

```typescript
// Do one thing, under 20 lines ideally
// No hidden side effects
// Explicit parameters, no implicit state

// ❌ Hidden side effects
async processUser(id: string) {
  const user = await this.userRepo.findById(id);
  user.lastLogin = new Date();  // surprise mutation
  globalStats.loginCount++;      // surprise global mutation
  return user;
}

// ✅ Explicit
async recordLogin(userId: string): Promise<void> {
  await this.userRepo.updateLastLogin(userId, new Date());
}
```

### Error Handling

```typescript
// ❌ Swallow errors
try { await processPayment(); } catch (e) { console.log(e); }

// ❌ Generic errors
throw new Error('Something went wrong');

// ✅ Domain errors with context
class PaymentFailedError extends Error {
  constructor(readonly reason: string, readonly orderId: string) {
    super(`Payment failed for order ${orderId}: ${reason}`);
  }
}

// ✅ Global exception filter
@Catch()
class GlobalFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    if (exception instanceof DomainError) {
      return res.status(422).json({ error: { code: exception.code, message: exception.message }});
    }
    // Log unexpected errors with context
    this.logger.error('Unexpected', { stack: exception.stack, requestId });
    return res.status(500).json({ error: { code: 'INTERNAL_ERROR' }});
  }
}
```

## NestJS Conventions

### Project Structure

```
src/
├── modules/
│   └── orders/
│       ├── controllers/orders.controller.ts
│       ├── services/orders.service.ts
│       ├── repositories/orders.repository.ts
│       ├── entities/order.entity.ts
│       ├── dto/create-order.dto.ts
│       ├── events/order-placed.event.ts
│       └── orders.module.ts
├── common/
│   ├── filters/        # Exception filters
│   ├── guards/         # Auth guards
│   ├── interceptors/   # Logging, transform
│   └── decorators/     # Custom decorators
└── app.module.ts
```

### DTO Validation

```typescript
export class CreateOrderDto {
  @IsEmail()
  @Transform(({ value }) => value.toLowerCase().trim())
  email: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}

// main.ts
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,           // Strip unknown fields
  forbidNonWhitelisted: true,
  transform: true,
}));
```

### Interceptors for Cross-Cutting Concerns

```typescript
@Injectable()
class LoggingInterceptor implements NestInterceptor {
  intercept(ctx: ExecutionContext, next: CallHandler): Observable<any> {
    const start = Date.now();
    const req = ctx.switchToHttp().getRequest();
    return next.handle().pipe(
      tap({ 
        next: () => this.logger.log({ method: req.method, url: req.url, ms: Date.now() - start }),
        error: (err) => this.logger.error({ url: req.url, error: err.message }),
      }),
    );
  }
}
```

## Testing Strategy

### Test Pyramid

```
        /\ E2E (few, slow, expensive)
       /  \
      /----\ Integration (medium)
     /      \
    /--------\ Unit Tests (many, fast, cheap)
```

### Unit Test Template

```typescript
describe('OrderService.placeOrder', () => {
  let service: OrderService;
  let orderRepo: jest.Mocked<OrderRepository>;

  beforeEach(() => {
    orderRepo = { save: jest.fn(), findById: jest.fn() };
    service = new OrderService(orderRepo, createMock<EventBus>());
  });

  it('should save order and emit event', async () => {
    // Arrange
    orderRepo.save.mockResolvedValue(buildOrder());
    // Act
    await service.placeOrder(buildCreateOrderDto());
    // Assert
    expect(orderRepo.save).toHaveBeenCalledTimes(1);
  });

  it('should throw DomainError when cart is empty', async () => {
    await expect(service.placeOrder({ items: [] })).rejects.toThrow(DomainError);
  });
});
```

## Code Review Checklist

```
Correctness:  [ ] Logic correct [ ] Edge cases handled [ ] No N+1 queries
Performance:  [ ] Indexes used [ ] No unnecessary data loading
Security:     [ ] Input validated [ ] Auth checked [ ] No sensitive data logged
Observability:[ ] Business events logged [ ] Errors have context
Tests:        [ ] Happy path covered [ ] Error cases covered
```
