# Security Playbook — OWASP, Auth & Zero Trust

## OWASP Top 10 — Must Know

### A01: Broken Access Control

```typescript
// ❌ Check auth but not ownership
const order = await this.orderService.findById(id); // user A sees user B's order!

// ✅ Scope to requesting user
const order = await this.orderRepo.findOne({ where: { id, customerId: user.id }});
if (!order) throw new NotFoundException(); // 404 not 403 (don't reveal existence)
```

### A03: Injection Prevention

```typescript
// ❌ SQL Injection
db.query(`SELECT * FROM users WHERE email = '${email}'`); // NEVER

// ✅ Parameterized
db.query('SELECT * FROM users WHERE email = $1', [email]);
// ✅ ORM (handles it automatically)
userRepo.findOne({ where: { email } });

// ❌ NoSQL Injection
await db.users.find({ username: req.body.username }); // if body = {"$gt": ""}

// ✅ Validate and sanitize input first (class-validator)
```

### A02: Cryptographic Failures

```typescript
// ❌ MD5/SHA1 for passwords
const hash = sha1(password);  // BROKEN

// ✅ Argon2id (preferred) or bcrypt
const hash = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 2 ** 16, timeCost: 3, parallelism: 1,
});

// ✅ Constant-time comparison (timing attack prevention)
const valid = crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
```

### A04: Rate Limiting + Account Lockout

```typescript
@Post('/auth/login')
@Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 attempts/minute
async login(@Body() dto: LoginDto) {
  const user = await this.userRepo.findByEmail(dto.email);
  
  // Account lockout after 10 failures
  if (user?.failedLoginAttempts >= 10) {
    if (user.lockedUntil > new Date()) throw new AccountLockedError();
  }
  
  const valid = await argon2.verify(user.passwordHash, dto.password);
  if (!valid) {
    await this.userRepo.incrementFailedAttempts(user.id);
    throw new UnauthorizedException('Invalid credentials');
  }
  
  await this.userRepo.resetFailedAttempts(user.id);
  return this.issueTokens(user);
}
```

### A07: JWT Best Practices

```typescript
// Access token: short-lived (15 min), stateless
const accessToken = jwt.sign({ sub: user.id, role: user.role }, privateKey, {
  algorithm: 'RS256',  // Asymmetric: verify without secret
  expiresIn: '15m',
  issuer: 'auth-service',
  audience: 'api',
  jwtid: ulid(),       // For blacklisting
});

// Refresh token: long-lived (7 days), stored in DB, rotated on use
async refreshTokens(refreshToken: string) {
  const stored = await this.tokenRepo.findByToken(refreshToken);
  if (!stored || stored.isRevoked || stored.expiresAt < new Date()) {
    throw new UnauthorizedException('Invalid refresh token');
  }
  await this.tokenRepo.revoke(stored.id);  // Rotate: old → revoked
  return this.issueTokens(stored.userId);
}

// Logout: blacklist JWT jti in Redis
async logout(jwtPayload: JwtPayload) {
  const ttl = jwtPayload.exp - Math.floor(Date.now() / 1000);
  await this.redis.setex(`blacklist:${jwtPayload.jti}`, ttl, '1');
}
```

### A08: SSRF Prevention

```typescript
// ❌ Fetch user-provided URL directly
const data = await fetch(req.body.webhookUrl);

// ✅ Whitelist domains + validate
const ALLOWED = ['api.stripe.com', 'api.sendgrid.com'];
const url = new URL(req.body.webhookUrl);
if (!ALLOWED.includes(url.hostname)) throw new BadRequestException('Domain not allowed');
if (url.protocol !== 'https:') throw new BadRequestException('HTTPS only');
if (isPrivateIP(url.hostname)) throw new BadRequestException('Private IPs blocked');
```

## RBAC Implementation

```typescript
enum Permission {
  ORDER_READ = 'order:read',
  ORDER_WRITE = 'order:write',
  USER_MANAGE = 'user:manage',
}

const rolePermissions = {
  [Role.CUSTOMER]: [Permission.ORDER_READ, Permission.ORDER_WRITE],
  [Role.ADMIN]: Object.values(Permission),
};

@Injectable()
class PermissionGuard implements CanActivate {
  canActivate(ctx: ExecutionContext): boolean {
    const required = this.reflector.get<Permission[]>('permissions', ctx.getHandler());
    if (!required?.length) return true;
    const user = ctx.switchToHttp().getRequest().user;
    return required.every(p => rolePermissions[user.role]?.includes(p));
  }
}

@Delete('/orders/:id')
@RequirePermissions(Permission.ORDER_WRITE)
async deleteOrder() {}
```

## Security Checklist per PR

```
[ ] All endpoints have auth guard (public ones explicitly marked)
[ ] Resource ownership scoped in DB query
[ ] Input validated with class-validator (whitelist: true)
[ ] No sensitive data logged (passwords, tokens, PII)
[ ] SQL uses parameterized queries or ORM
[ ] Sensitive data in env vars, not code
[ ] File uploads: validate type + size
[ ] HTTPS enforced, CORS configured
[ ] npm audit passes
```

## Helmet + CORS Setup

```typescript
// main.ts
app.use(helmet({
  contentSecurityPolicy: true,
  hsts: { maxAge: 31536000 },
}));

app.enableCors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
});
```
