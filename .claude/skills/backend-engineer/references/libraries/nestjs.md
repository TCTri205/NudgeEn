---
library: nestjs
package: "@nestjs/common"
context7_library_id: /nestjs/docs.nestjs.com
synced_version: latest
project_version: v11.0.1
declared_range: ^11.0.1
benchmark_score: 84.77
source_reputation: High
last_synced: 2026-03-22
coverage: modules, controllers, services, DI, guards, pipes, interceptors, exception filters, ConfigModule, JWT, validation, TypeORM, transactions, migrations, relations, registerAs, forwardRef, APP_GUARD, APP_INTERCEPTOR, custom decorators, file upload, pagination
---

# NestJS v11

Progressive Node.js framework with TypeScript, DI, and modular architecture. Built on Express by default.

## Module System

```typescript
import { Module } from '@nestjs/common'
import { CatsController } from './cats.controller'
import { CatsService } from './cats.service'

@Module({
  imports: [],          // other modules to import
  controllers: [CatsController],
  providers: [CatsService],
  exports: [CatsService], // make available to importing modules
})
export class CatsModule {}
```

## Service (Provider)

```typescript
import { Injectable } from '@nestjs/common'

@Injectable()
export class CatsService {
  private readonly cats: Cat[] = []

  findAll(): Cat[] {
    return this.cats
  }

  findOne(id: string): Cat | undefined {
    return this.cats.find(c => c.id === id)
  }

  create(cat: CreateCatDto): Cat {
    const newCat = { id: randomUUID(), ...cat }
    this.cats.push(newCat)
    return newCat
  }
}
```

## Controller

```typescript
import { Controller, Get, Post, Body, Param, Delete, HttpCode, HttpStatus } from '@nestjs/common'

@Controller('cats')
export class CatsController {
  constructor(private readonly catsService: CatsService) {}

  @Get()
  findAll() {
    return this.catsService.findAll()
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.catsService.findOne(id)
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() createCatDto: CreateCatDto) {
    return this.catsService.create(createCatDto)
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string) {
    return this.catsService.remove(id)
  }
}
```

## Validation Pipe (global)

```typescript
// main.ts
import { ValidationPipe } from '@nestjs/common'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,      // strip unknown properties
      transform: true,      // auto-transform types
      forbidNonWhitelisted: true,
    }),
  )
  await app.listen(process.env.PORT ?? 3000)
}
```

## DTO with class-validator

```typescript
import { IsString, IsEmail, IsInt, Min, IsOptional } from 'class-validator'

export class CreateUserDto {
  @IsString()
  name: string

  @IsEmail()
  email: string

  @IsInt()
  @Min(0)
  age: number

  @IsOptional()
  @IsString()
  bio?: string
}
```

## `as const` vs `enum` in TypeScript

Modern TypeScript code prefers `as const` objects over `enum`. Reasons: no runtime object emitted, tree-shakeable,
values are plain strings/numbers usable anywhere, no double-declaration quirks.

```typescript
// ❌ enum — emits JS runtime object, can be a footgun with reverse mapping
export enum UserRole {
  Teacher = 'teacher',
  Student = 'student',
}

// ✅ as const — pure type, no runtime overhead
export const UserRole = {
  Teacher: 'teacher',
  Student: 'student',
} as const

export type UserRole = (typeof UserRole)[keyof typeof UserRole]
// => type UserRole = 'teacher' | 'student'

// Use with @IsIn() for class-validator
@IsIn(Object.values(UserRole))
role: UserRole

// Use with Zod
const schema = z.enum(Object.values(UserRole) as [string, ...string[]])
// or
const schema = z.union([z.literal(UserRole.Teacher), z.literal(UserRole.Student)])
```

## Custom Zod Validation Pipe

```typescript
import { PipeTransform, BadRequestException } from '@nestjs/common'
import { ZodSchema } from 'zod'

export class ZodValidationPipe implements PipeTransform {
  constructor(private schema: ZodSchema) {}

  transform(value: unknown) {
    const result = this.schema.safeParse(value)
    if (!result.success) {
      throw new BadRequestException(result.error.issues)
    }
    return result.data
  }
}

// Usage
@Post()
create(@Body(new ZodValidationPipe(CreateCatSchema)) body: CreateCatDto) { ... }
```

## Guards (Authentication / Authorization)

```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common'
import { Observable } from 'rxjs'

@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const request = context.switchToHttp().getRequest()
    return this.validateRequest(request)
  }

  private validateRequest(request: any): boolean {
    const token = request.headers.authorization?.split(' ')[1]
    return !!token && this.verifyToken(token)
  }
}

// Apply to controller or route
@UseGuards(AuthGuard)
@Get('protected')
getProtected() { ... }

// Global guard (main.ts)
app.useGlobalGuards(new AuthGuard())
```

## JWT Auth Setup

```typescript
// auth.module.ts
@Module({
  imports: [
    UsersModule,
    PassportModule,
    JwtModule.register({
      secret: process.env.JWT_SECRET,
      signOptions: { expiresIn: '7d' },
    }),
  ],
  providers: [AuthService, JwtStrategy],
  exports: [AuthService],
})
export class AuthModule {}

// Controller
@Controller()
export class AppController {
  @UseGuards(LocalAuthGuard)
  @Post('auth/login')
  async login(@Request() req) {
    return this.authService.login(req.user)
  }

  @UseGuards(JwtAuthGuard)
  @Get('profile')
  getProfile(@Request() req) {
    return req.user
  }
}
```

## Exception Filters

```typescript
import { ExceptionFilter, Catch, ArgumentsHost, HttpException } from '@nestjs/common'
import { Request, Response } from 'express'

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp()
    const response = ctx.getResponse<Response>()
    const request = ctx.getRequest<Request>()
    const status = exception.getStatus()

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message: exception.message,
    })
  }
}

// Apply globally
app.useGlobalFilters(new HttpExceptionFilter())
```

## Built-In Exceptions

```typescript
import {
  BadRequestException,      // 400
  UnauthorizedException,    // 401
  ForbiddenException,       // 403
  NotFoundException,        // 404
  ConflictException,        // 409
  UnprocessableEntityException, // 422
  InternalServerErrorException, // 500
} from '@nestjs/common'

throw new NotFoundException('Cat not found')
throw new BadRequestException('Invalid ID format', { cause: new Error() })
throw new ConflictException({ message: 'Email already exists', field: 'email' })
```

## ConfigModule

```typescript
// app.module.ts
import { ConfigModule, ConfigService } from '@nestjs/config'

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,          // available everywhere without importing
      envFilePath: '.env',
      cache: true,
    }),
  ],
})
export class AppModule {}

// In a service
@Injectable()
export class AppService {
  constructor(private configService: ConfigService) {}

  getPort() {
    return this.configService.get<number>('PORT', 3000)
  }

  getDatabaseUrl() {
    return this.configService.getOrThrow<string>('DATABASE_URL')
  }
}
```

## Interceptors

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common'
import { Observable } from 'rxjs'
import { map, tap } from 'rxjs/operators'

// Transform response
@Injectable()
export class TransformInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => ({ success: true, data })) // wrap all responses
    )
  }
}

// Logging interceptor
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const start = Date.now()
    return next.handle().pipe(
      tap(() => console.log(`Request took ${Date.now() - start}ms`))
    )
  }
}

// Apply globally
app.useGlobalInterceptors(new TransformInterceptor())
```

## Bootstrap (main.ts)

```typescript
import { NestFactory } from '@nestjs/core'
import { ValidationPipe } from '@nestjs/common'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)

  app.setGlobalPrefix('api')           // all routes prefixed with /api
  app.enableCors({ origin: process.env.FRONTEND_URL })
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))
  app.useGlobalFilters(new HttpExceptionFilter())

  await app.listen(process.env.PORT ?? 3000)
  console.log(`Server running on port ${process.env.PORT ?? 3000}`)
}
bootstrap()
```

---

## TypeORM Integration

### TypeOrmModule setup

```typescript
// app.module.ts — async config (preferred)
TypeOrmModule.forRootAsync({
  imports: [ConfigModule],
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    type: 'postgres',
    url: config.getOrThrow<string>('DATABASE_URL'),
    entities: [__dirname + '/**/*.entity{.ts,.js}'],
    migrations: [__dirname + '/migrations/*{.ts,.js}'],
    synchronize: false,   // NEVER true in production
    logging: config.get('NODE_ENV') !== 'production',
  }),
})

// feature module — register entities for that module
TypeOrmModule.forFeature([UserEntity, PostEntity])
```

### Repository injection

```typescript
import { InjectRepository } from '@nestjs/typeorm'
import { Repository } from 'typeorm'

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(UserEntity)
    private readonly usersRepo: Repository<UserEntity>,
    private readonly dataSource: DataSource,  // inject for transactions
  ) {}

  findAll(): Promise<UserEntity[]> {
    return this.usersRepo.find()
  }

  findOne(id: string): Promise<UserEntity | null> {
    return this.usersRepo.findOneBy({ id })
  }

  async remove(id: string): Promise<void> {
    await this.usersRepo.delete(id)
  }
}
```

### Entity decorators

```typescript
import {
  Entity, PrimaryGeneratedColumn, Column, CreateDateColumn,
  UpdateDateColumn, Index, ManyToOne, OneToMany, JoinColumn,
} from 'typeorm'

@Entity('users')
@Index(['email'])                              // composite index
export class UserEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column({ unique: true })
  email: string

  @Column({ type: 'varchar', length: 20 })    // explicit type required for nullable union
  role: string

  @Column({ name: 'is_active', default: true })
  isActive: boolean

  @Column({ type: 'text', nullable: true })   // nullable: MUST set explicit type
  bio: string | null

  @Column({ type: 'int', nullable: true })
  age: number | null

  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, unknown> | null

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date

  @OneToMany(() => PostEntity, post => post.author)
  posts: PostEntity[]
}

// RULE: TypeORM cannot infer SQL type from `string | null` or `number | null`.
// Always add explicit `type:` when the column is nullable or has a union type.
```

### Relations

```typescript
// ManyToOne side (owns the FK)
@Entity('posts')
export class PostEntity {
  @Column({ name: 'author_id', type: 'uuid' })
  authorId: string

  @ManyToOne(() => UserEntity, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'author_id' })
  author: UserEntity
}

// OneToOne
@Entity('profiles')
export class ProfileEntity {
  @PrimaryColumn({ name: 'user_id', type: 'uuid' })
  userId: string

  @OneToOne(() => UserEntity)
  @JoinColumn({ name: 'user_id' })
  user: UserEntity
}

// ManyToMany
@Entity('posts')
export class PostEntity {
  @ManyToMany(() => TagEntity)
  @JoinTable()   // only on owning side
  tags: TagEntity[]
}
```

### Transactions — QueryRunner (manual, full control)

```typescript
async createMany(items: CreateItemDto[]) {
  const queryRunner = this.dataSource.createQueryRunner()
  await queryRunner.connect()
  await queryRunner.startTransaction()
  try {
    for (const item of items) {
      const entity = queryRunner.manager.create(ItemEntity, item)
      await queryRunner.manager.save(entity)
    }
    await queryRunner.commitTransaction()
  } catch (err) {
    await queryRunner.rollbackTransaction()
    throw new ConflictException(err)
  } finally {
    await queryRunner.release()  // always release
  }
}
```

### Transactions — callback style (simpler)

```typescript
async createMany(items: CreateItemDto[]) {
  await this.dataSource.transaction(async (manager) => {
    for (const item of items) {
      await manager.save(ItemEntity, item)
    }
  })
}
```

### TypeORM CLI migrations (separate DataSource)

```typescript
// typeorm.config.ts — used by CLI only, NOT by the NestJS app
import 'dotenv/config'
import { DataSource } from 'typeorm'

export default new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  entities: ['src/**/*.entity.ts'],
  migrations: ['src/migrations/*.ts'],
  synchronize: false,
})
```

```json
// package.json scripts
"migration:generate": "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js migration:generate src/migrations/Name -d typeorm.config.ts",
"migration:run":      "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js migration:run -d typeorm.config.ts",
"migration:revert":   "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js migration:revert -d typeorm.config.ts"
```

---

## Namespace Config with `registerAs`

```typescript
// auth/config/jwt.config.ts
import { registerAs } from '@nestjs/config'

export default registerAs('jwt', () => ({
  secret: process.env.JWT_SECRET,
  audience: process.env.JWT_TOKEN_AUDIENCE,
  issuer: process.env.JWT_TOKEN_ISSUER,
  accessTokenTtl: parseInt(process.env.JWT_ACCESS_TOKEN_TTL ?? '3600', 10),
  refreshTokenTtl: parseInt(process.env.JWT_REFRESH_TOKEN_TTL ?? '86400', 10),
}))
```

```typescript
// auth.module.ts — load the namespace config + use with JwtModule
import jwtConfig from './config/jwt.config'
import { ConfigModule } from '@nestjs/config'
import { JwtModule } from '@nestjs/jwt'

@Module({
  imports: [
    ConfigModule.forFeature(jwtConfig),         // load in this module
    JwtModule.registerAsync(jwtConfig.asProvider()), // JwtModule reads from namespace
  ],
})
export class AuthModule {}
```

```typescript
// Inject typed namespace config in a service
import { ConfigType } from '@nestjs/config'
import jwtConfig from '../config/jwt.config'

@Injectable()
export class TokenService {
  constructor(
    @Inject(jwtConfig.KEY)
    private readonly jwtConfiguration: ConfigType<typeof jwtConfig>,
  ) {}

  getSecret() {
    return this.jwtConfiguration.secret // fully typed
  }
}
```

## Env Validation with Joi

```typescript
// config/environment.validation.ts
import * as Joi from 'joi'

export default Joi.object({
  NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
  DATABASE_URL: Joi.string().required(),
  JWT_SECRET: Joi.string().required(),
  JWT_ACCESS_TOKEN_TTL: Joi.number().required(),
})

// app.module.ts
ConfigModule.forRoot({
  isGlobal: true,
  envFilePath: [`.env.${process.env.NODE_ENV}`, '.env'],
  load: [appConfig, databaseConfig],
  validationSchema: environmentValidation,
})
```

---

## Global Guards and Interceptors via DI

Register in `AppModule` providers array — they receive DI injection unlike `app.useGlobal*()`.

```typescript
import { APP_GUARD, APP_INTERCEPTOR } from '@nestjs/core'

@Module({
  providers: [
    { provide: APP_GUARD,       useClass: AuthenticationGuard },
    { provide: APP_INTERCEPTOR, useClass: DataResponseInterceptor },
    AccessTokenGuard, // must be registered so AuthenticationGuard can inject it
  ],
})
export class AppModule {}
```

> **Rule**: `app.useGlobalGuards(new Guard())` does NOT support DI. Use `APP_GUARD` token instead when the guard has
> constructor dependencies.

---

## Auth Pattern — AuthType + Reflector

```typescript
// auth/constants/auth-type.ts
// Prefer `as const` over enum — tree-shakeable, no runtime object emitted, works as value & type
export const AuthType = {
  Bearer: 'Bearer',
  None: 'None',
} as const

export type AuthType = (typeof AuthType)[keyof typeof AuthType]
// => type AuthType = 'Bearer' | 'None'

// auth/decorators/auth.decorator.ts
export const AUTH_TYPE_KEY = 'authType'
export const Auth = (...types: AuthType[]) => SetMetadata(AUTH_TYPE_KEY, types)

// auth/guards/authentication.guard.ts
@Injectable()
export class AuthenticationGuard implements CanActivate {
  private static readonly defaultAuthType: AuthType = AuthType.Bearer

  private readonly authTypeGuardMap: Record<AuthType, CanActivate> = {
    [AuthType.Bearer]: this.accessTokenGuard,
    [AuthType.None]:   { canActivate: () => true },
  }

  constructor(
    private readonly reflector: Reflector,
    private readonly accessTokenGuard: AccessTokenGuard,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const authTypes = this.reflector.getAllAndOverride<AuthType[]>(
      AUTH_TYPE_KEY,
      [context.getHandler(), context.getClass()],
    ) ?? [AuthenticationGuard.defaultAuthType]

    let error = new UnauthorizedException()
    for (const type of authTypes) {
      const canActivate = await Promise.resolve(
        this.authTypeGuardMap[type].canActivate(context),
      ).catch(err => { error = err })
      if (canActivate) return true
    }
    throw error
  }
}

// Usage — mark a route as public
@Auth(AuthType.None)
@Post('login')
login() {}
```

---

## Custom Param Decorator

```typescript
// decorators/active-user.decorator.ts
import { createParamDecorator, ExecutionContext } from '@nestjs/common'

export const REQUEST_USER_KEY = 'user'

export const ActiveUser = createParamDecorator(
  (field: keyof ActiveUserData | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest()
    const user: ActiveUserData = request[REQUEST_USER_KEY]
    return field ? user?.[field] : user
  },
)

// Usage in controller
@Get('profile')
getProfile(@ActiveUser() user: ActiveUserData) { ... }

@Get('id')
getId(@ActiveUser('sub') id: string) { ... }
```

---

## Circular Dependency Resolution with `forwardRef`

```typescript
// Module level
@Module({
  imports: [forwardRef(() => AuthModule)],
  exports: [UsersService],
})
export class UsersModule {}

// Provider level (inject)
@Injectable()
export class AuthService {
  constructor(
    @Inject(forwardRef(() => UsersService))
    private readonly usersService: UsersService,
  ) {}
}
```

> Use `forwardRef` only when two modules genuinely depend on each other. Consider refactoring if it appears often.

---

## File Upload (Multer)

```typescript
// controller
import { FileInterceptor, FilesInterceptor } from '@nestjs/platform-express'
import { UploadedFile, UseInterceptors } from '@nestjs/common'

// Single file
@Post('upload')
@UseInterceptors(FileInterceptor('file'))
uploadFile(@UploadedFile() file: Express.Multer.File) {
  return this.uploadsService.upload(file)
}

// Multiple files
@Post('upload-many')
@UseInterceptors(FilesInterceptor('files', 10))
uploadFiles(@UploadedFiles() files: Express.Multer.File[]) { ... }

// Multiple fields
@Post('upload-fields')
@UseInterceptors(FileFieldsInterceptor([
  { name: 'avatar', maxCount: 1 },
  { name: 'cover',  maxCount: 1 },
]))
uploadFields(@UploadedFiles() files: { avatar?: Express.Multer.File[], cover?: Express.Multer.File[] }) { ... }
```

```typescript
// service — validate MIME type, upload to S3
@Injectable()
export class UploadsService {
  async uploadFile(file: Express.Multer.File) {
    const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowed.includes(file.mimetype)) {
      throw new BadRequestException('Unsupported MIME type')
    }
    // upload to S3 / Supabase Storage, return URL
    const key = await this.s3Provider.upload(file)
    return this.uploadsRepo.save({ name: key, mime: file.mimetype, size: file.size })
  }
}
```

---

## Pagination Pattern

```typescript
// common/pagination/dto/pagination-query.dto.ts
export class PaginationQueryDto {
  @IsOptional() @IsPositive() @Type(() => Number)
  limit?: number = 20

  @IsOptional() @IsPositive() @Type(() => Number)
  page?: number = 1
}

// common/pagination/interfaces/paginated.interface.ts
export interface Paginated<T> {
  data: T[]
  meta: { itemsPerPage: number; totalItems: number; currentPage: number; totalPages: number }
  links: { first: string; last: string; current: string; next: string; previous: string }
}

// common/pagination/providers/pagination.provider.ts
@Injectable()
export class PaginationProvider {
  constructor(@Inject(REQUEST) private readonly request: Request) {}

  async paginate<T extends ObjectLiteral>(
    query: PaginationQueryDto,
    repo: Repository<T>,
  ): Promise<Paginated<T>> {
    const [data, total] = await repo.findAndCount({
      skip: (query.page - 1) * query.limit,
      take: query.limit,
    })
    const totalPages = Math.ceil(total / query.limit)
    const base = `${this.request.protocol}://${this.request.headers.host}${this.request.path}`
    return {
      data,
      meta: { itemsPerPage: query.limit, totalItems: total, currentPage: query.page, totalPages },
      links: {
        first:    `${base}?limit=${query.limit}&page=1`,
        last:     `${base}?limit=${query.limit}&page=${totalPages}`,
        current:  `${base}?limit=${query.limit}&page=${query.page}`,
        next:     `${base}?limit=${query.limit}&page=${Math.min(query.page + 1, totalPages)}`,
        previous: `${base}?limit=${query.limit}&page=${Math.max(query.page - 1, 1)}`,
      },
    }
  }
}

// Register with REQUEST scope (needed for request injection)
@Module({
  providers: [{ provide: PaginationProvider, useClass: PaginationProvider, scope: Scope.REQUEST }],
  exports: [PaginationProvider],
})
export class PaginationModule {}
```

---

## BullMQ (Queue / Background Jobs)

```typescript
pnpm add @nestjs/bullmq bullmq

// app.module.ts
BullModule.forRoot({ connection: { host: 'localhost', port: 6379 } })

// feature module
BullModule.registerQueue({ name: 'session-reminders' })

// producer service
@Injectable()
export class RemindersService {
  constructor(@InjectQueue('session-reminders') private queue: Queue) {}

  async scheduleReminder(sessionId: string, delayMs: number) {
    await this.queue.add(
      'remind',
      { sessionId },
      { delay: delayMs, jobId: `reminder-${sessionId}` },
    )
  }

  async cancelReminder(sessionId: string) {
    const job = await this.queue.getJob(`reminder-${sessionId}`)
    await job?.remove()
  }
}

// processor
@Processor('session-reminders')
export class ReminderProcessor {
  @Process('remind')
  async handle(job: Job<{ sessionId: string }>) {
    const { sessionId } = job.data
    // send notification / email
  }
}
```

---

## Response Transform Interceptor

```typescript
// Wrap all responses with { apiVersion, data }
@Injectable()
export class DataResponseInterceptor implements NestInterceptor {
  constructor(private readonly config: ConfigService) {}

  intercept(ctx: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => ({
        apiVersion: this.config.get('appConfig.apiVersion'),
        data,
      })),
    )
  }
}

// Register globally via DI (supports injection)
{ provide: APP_INTERCEPTOR, useClass: DataResponseInterceptor }
```

---

## Provider Patterns

```typescript
// Abstract base class — strategy pattern for hashing
export abstract class HashingProvider {
  abstract hashPassword(data: string): Promise<string>
  abstract comparePassword(data: string, hash: string): Promise<boolean>
}

// Concrete implementation
@Injectable()
export class BcryptProvider extends HashingProvider {
  async hashPassword(data: string) { return bcrypt.hash(data, 10) }
  async comparePassword(data: string, hash: string) { return bcrypt.compare(data, hash) }
}

// Register with substitution token
{
  provide: HashingProvider,
  useClass: BcryptProvider,
}

// Inject by abstract class token
constructor(private readonly hashingProvider: HashingProvider) {}
```

---

## Middleware

Middleware chạy trước route handler. Có thể dùng class-based (có DI) hoặc functional (không có DI).

```typescript
// Class-based middleware (có thể inject dependencies)
import { Injectable, NestMiddleware } from '@nestjs/common'
import { Request, Response, NextFunction } from 'express'

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`)
    next()
  }
}

// Functional middleware (dùng khi không cần DI — nhẹ hơn)
export function logger(req: Request, res: Response, next: NextFunction) {
  console.log('Request...')
  next()
}
```

```typescript
// Đăng ký middleware trong module — implement NestModule
import { Module, NestModule, MiddlewareConsumer, RequestMethod } from '@nestjs/common'

@Module({ imports: [CatsModule] })
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware)
      .exclude(
        { path: 'cats', method: RequestMethod.GET },
      )
      .forRoutes(CatsController)  // hoặc .forRoutes('cats') hoặc .forRoutes('*')

    // Nhiều middleware cùng lúc
    consumer
      .apply(cors(), helmet(), logger)
      .forRoutes(CatsController)
  }
}

// Global middleware (không có DI — dùng app.use)
const app = await NestFactory.create(AppModule)
app.use(logger)
```

> **Rule**: dùng `app.use()` cho third-party middleware (helmet, cors, compression). Dùng class-based middleware khi cần
> inject service.

---

## Logger (built-in)

```typescript
import { Logger, Injectable } from '@nestjs/common'

@Injectable()
export class CatsService {
  private readonly logger = new Logger(CatsService.name)  // context = class name

  findAll() {
    this.logger.log('Fetching all cats')
    this.logger.debug('Debug info')
    this.logger.warn('Something might be wrong')
    this.logger.error('Something failed', new Error('stack trace').stack)
    this.logger.verbose('Extra verbose info')
    this.logger.fatal('Critical failure')
  }
}

// Disable logging in production / test
const app = await NestFactory.create(AppModule, {
  logger: process.env.NODE_ENV === 'production'
    ? ['log', 'warn', 'error', 'fatal']
    : ['log', 'debug', 'warn', 'error', 'verbose'],
})

// Disable completely
const app = await NestFactory.create(AppModule, { logger: false })
```

---

## Serialization (ClassSerializerInterceptor)

Dùng `class-transformer` để tự động loại bỏ / biến đổi fields khi trả response. Không cần xóa field thủ công trong
service.

```typescript
// entity / response class
import { Exclude, Expose, Transform } from 'class-transformer'

export class UserEntity {
  id: number
  email: string

  @Exclude()               // luôn loại bỏ khỏi response
  password: string

  @Expose()                // chỉ expose khi dùng excludeExtraneousValues: true
  fullName: string

  @Transform(({ value }) => value?.toLowerCase())
  role: string

  constructor(partial: Partial<UserEntity>) {
    Object.assign(this, partial)
  }
}

// Controller — trả về instance của class, không phải plain object
@UseInterceptors(ClassSerializerInterceptor)
@Get(':id')
async findOne(@Param('id') id: string): Promise<UserEntity> {
  const user = await this.usersService.findOne(id)
  return new UserEntity(user)   // PHẢI tạo instance để @Exclude hoạt động
}

// Global (recommended)
{ provide: APP_INTERCEPTOR, useClass: ClassSerializerInterceptor }
```

> **Rule**: `@Exclude()` chỉ hoạt động khi giá trị trả về là **instance của class**, không phải plain object. Luôn
`new UserEntity(data)` trước khi return.

---

## Task Scheduling

```typescript
pnpm add @nestjs/schedule
pnpm add -D @types/cron

// app.module.ts
import { ScheduleModule } from '@nestjs/schedule'
ScheduleModule.forRoot()
```

```typescript
import { Injectable, Logger } from '@nestjs/common'
import { Cron, CronExpression, Interval, Timeout } from '@nestjs/schedule'

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name)

  // Chạy theo cron expression
  @Cron('45 * * * * *')                         // giây phút giờ ngày tháng weekday
  handleEveryMinuteAt45Sec() {
    this.logger.debug('Fires at second 45 of every minute')
  }

  // Dùng CronExpression enum
  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT, {
    name: 'daily-cleanup',
    timeZone: 'Asia/Ho_Chi_Minh',
  })
  dailyCleanup() {}

  // Lặp lại theo interval (milliseconds)
  @Interval(10_000)
  handleEvery10Seconds() {}

  // Chạy một lần sau delay (milliseconds)
  @Timeout(5_000)
  handleAfter5Seconds() {}
}
```

```typescript
// Dynamic jobs — thêm / xóa runtime
import { SchedulerRegistry } from '@nestjs/schedule'
import { CronJob } from 'cron'

@Injectable()
export class DynamicJobsService {
  constructor(private schedulerRegistry: SchedulerRegistry) {}

  addCronJob(name: string, cronTime: string, callback: () => void) {
    const job = new CronJob(cronTime, callback)
    this.schedulerRegistry.addCronJob(name, job)
    job.start()
  }

  deleteCronJob(name: string) {
    this.schedulerRegistry.deleteCronJob(name)
  }
}
```

---

## Caching

```typescript
pnpm add @nestjs/cache-manager cache-manager
# Redis store:
pnpm add cache-manager-ioredis-yet ioredis

// app.module.ts
import { CacheModule } from '@nestjs/cache-manager'

CacheModule.registerAsync({
  isGlobal: true,
  useFactory: () => ({
    ttl: 60_000,    // default TTL ms
    max: 100,       // max items in memory cache
  }),
})

// Redis store
CacheModule.registerAsync({
  isGlobal: true,
  imports: [ConfigModule],
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    store: require('cache-manager-ioredis-yet'),
    host: config.get('REDIS_HOST'),
    port: config.get('REDIS_PORT'),
    ttl: 60_000,
  }),
})
```

```typescript
import { Cache, CACHE_MANAGER } from '@nestjs/cache-manager'
import { Inject } from '@nestjs/common'

@Injectable()
export class AppService {
  constructor(@Inject(CACHE_MANAGER) private cache: Cache) {}

  async getData(key: string) {
    const cached = await this.cache.get<string>(key)
    if (cached) return cached

    const data = await this.fetchFromDB()
    await this.cache.set(key, data, 30_000)  // TTL 30s
    return data
  }

  async invalidate(key: string) {
    await this.cache.del(key)
  }
}

// Auto-cache GET endpoints với CacheInterceptor
@Controller('cats')
@UseInterceptors(CacheInterceptor)
export class CatsController {
  @CacheKey('all-cats')
  @CacheTTL(30_000)
  @Get()
  findAll() { ... }
}
```

---

## Swagger / OpenAPI

```typescript
pnpm add @nestjs/swagger

// main.ts
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger'

const config = new DocumentBuilder()
  .setTitle('Teach Loop API')
  .setDescription('API documentation')
  .setVersion('1.0')
  .addBearerAuth()   // thêm auth header vào Swagger UI
  .build()

const document = SwaggerModule.createDocument(app, config)
SwaggerModule.setup('docs', app, document)  // UI tại /docs, JSON tại /docs-json
```

```typescript
// Decorators trên controller & DTO
import { ApiTags, ApiOperation, ApiResponse, ApiProperty, ApiPropertyOptional, ApiBearerAuth } from '@nestjs/swagger'

@ApiTags('users')          // nhóm endpoint trong Swagger UI
@ApiBearerAuth()           // route cần Bearer token
@Controller('users')
export class UsersController {
  @ApiOperation({ summary: 'Get all users' })
  @ApiResponse({ status: 200, type: [UserEntity] })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @Get()
  findAll() {}
}

// DTO
export class CreateUserDto {
  @ApiProperty({ example: 'John Doe', description: 'Full name' })
  name: string

  @ApiPropertyOptional({ example: 'Teacher', enum: ['teacher', 'student'] })
  role?: string

  @ApiProperty({ minimum: 0, maximum: 120 })
  age: number
}
```

> Nếu dùng Swagger CLI plugin (`@nestjs/swagger/plugin`), có thể bỏ qua `@ApiProperty` trên một số DTO — plugin tự sinh
> metadata từ TypeScript types.

---

## Events (EventEmitter)

Pub/sub nội bộ trong process — giữ các module decoupled.

```typescript
pnpm add @nestjs/event-emitter eventemitter2

// app.module.ts
import { EventEmitterModule } from '@nestjs/event-emitter'
EventEmitterModule.forRoot({
  wildcard: true,   // cho phép 'order.*' pattern
  delimiter: '.',
})
```

```typescript
// Định nghĩa event class (typed payload)
export class OrderCreatedEvent {
  constructor(
    public readonly orderId: string,
    public readonly userId: string,
  ) {}
}

// Emit từ service
import { EventEmitter2 } from '@nestjs/event-emitter'

@Injectable()
export class OrdersService {
  constructor(private eventEmitter: EventEmitter2) {}

  async createOrder(dto: CreateOrderDto) {
    const order = await this.ordersRepo.save(dto)
    this.eventEmitter.emit('order.created', new OrderCreatedEvent(order.id, order.userId))
    return order
  }
}

// Listener — trong bất kỳ @Injectable nào
import { OnEvent } from '@nestjs/event-emitter'

@Injectable()
export class NotificationsListener {
  @OnEvent('order.created')
  handleOrderCreated(event: OrderCreatedEvent) {
    // gửi notification
  }

  @OnEvent('order.*')               // wildcard
  handleAnyOrderEvent(event: any) {}

  @OnEvent('order.created', { async: true })  // async listener
  async handleAsync(event: OrderCreatedEvent) {}
}
```

> Dùng EventEmitter cho side effects trong cùng process (notifications, audit logs). Dùng BullMQ/queue khi cần retry,
> durability, hoặc worker riêng.

---

## HTTP Module (HttpService / Axios)

Dùng khi cần gọi API bên ngoài từ trong NestJS service.

```typescript
pnpm add @nestjs/axios axios

// feature module
import { HttpModule } from '@nestjs/axios'

@Module({
  imports: [
    HttpModule.register({
      timeout: 5000,
      maxRedirects: 3,
      baseURL: 'https://api.example.com',
    }),
    // hoặc async
    HttpModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        baseURL: config.getOrThrow('EXTERNAL_API_URL'),
        headers: { 'X-Api-Key': config.getOrThrow('API_KEY') },
      }),
    }),
  ],
  providers: [ExternalService],
})
export class ExternalModule {}
```

```typescript
import { HttpService } from '@nestjs/axios'
import { firstValueFrom } from 'rxjs'

@Injectable()
export class ExternalService {
  constructor(private readonly httpService: HttpService) {}

  // HttpService trả Observable — dùng firstValueFrom để convert sang Promise
  async fetchUsers(): Promise<User[]> {
    const { data } = await firstValueFrom(
      this.httpService.get<User[]>('/users'),
    )
    return data
  }

  async postData(payload: unknown) {
    const { data } = await firstValueFrom(
      this.httpService.post('/endpoint', payload),
    )
    return data
  }

  // Dùng axiosRef cho raw Axios API
  async rawRequest() {
    const { data } = await this.httpService.axiosRef.get('/path')
    return data
  }
}
```

---

## API Versioning

```typescript
// main.ts
import { VersioningType } from '@nestjs/common'

app.enableVersioning({ type: VersioningType.URI })
// => /v1/cats, /v2/cats

app.enableVersioning({ type: VersioningType.HEADER, header: 'X-API-Version' })
// => header: X-API-Version: 1

app.enableVersioning({ type: VersioningType.MEDIA_TYPE, key: 'v=' })
// => Accept: application/json;v=1
```

```typescript
// Controller level
@Controller({ path: 'cats', version: '1' })
export class CatsV1Controller {}

@Controller({ path: 'cats', version: '2' })
export class CatsV2Controller {}

// Route level — override controller version
@Controller('cats')
export class CatsController {
  @Version('1') @Get()
  findAllV1() { return 'v1' }

  @Version('2') @Get()
  findAllV2() { return 'v2' }

  @Version(VERSION_NEUTRAL) @Get('health')
  health() { return 'ok' }   // không phụ thuộc version
}

// Nhiều version cùng lúc
@Version(['1', '2'])
@Get()
findAll() {}
```

---

## Authorization (RBAC)

```typescript
// decorators/roles.decorator.ts — dùng Reflector.createDecorator (typed, gọn hơn SetMetadata)
import { Reflector } from '@nestjs/core'
export const Roles = Reflector.createDecorator<string[]>()

// Hoặc dùng SetMetadata
export const ROLES_KEY = 'roles'
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles)

// guards/roles.guard.ts
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ])
    if (!requiredRoles) return true

    const { user } = context.switchToHttp().getRequest()
    return requiredRoles.some(role => user?.roles?.includes(role))
  }
}

// Sử dụng
@Controller('admin')
@UseGuards(AuthenticationGuard, RolesGuard)
export class AdminController {
  @Roles(['admin'])
  @Delete(':id')
  remove(@Param('id') id: string) {}
}
```

> **Claim-based / Policy-based**: với phân quyền phức tạp hơn, dùng thư viện `casl` + custom guard thay vì RBAC đơn
> giản.

---

## Encryption & Hashing

### Password hashing (bcrypt / argon2)

```typescript
pnpm add bcrypt && pnpm add -D @types/bcrypt
# hoặc argon2 (mạnh hơn, nhưng cần native build)
pnpm add argon2

// bcrypt
import * as bcrypt from 'bcrypt'

const hash = await bcrypt.hash(password, 10)         // saltRounds = 10
const isMatch = await bcrypt.compare(password, hash)

// argon2
import * as argon2 from 'argon2'

const hash = await argon2.hash(password)
const isMatch = await argon2.verify(hash, password)
```

### Encryption (Node.js built-in crypto)

```typescript
import { createCipheriv, createDecipheriv, randomBytes, scrypt } from 'node:crypto'
import { promisify } from 'node:util'

const ALGORITHM = 'aes-256-ctr'

async function encrypt(text: string, password: string): Promise<{ iv: string; encrypted: string }> {
  const iv = randomBytes(16)
  const key = (await promisify(scrypt)(password, 'salt', 32)) as Buffer
  const cipher = createCipheriv(ALGORITHM, key, iv)
  const encrypted = Buffer.concat([cipher.update(text), cipher.final()])
  return { iv: iv.toString('hex'), encrypted: encrypted.toString('hex') }
}

async function decrypt(encryptedHex: string, ivHex: string, password: string): Promise<string> {
  const key = (await promisify(scrypt)(password, 'salt', 32)) as Buffer
  const decipher = createDecipheriv(ALGORITHM, key, Buffer.from(ivHex, 'hex'))
  const decrypted = Buffer.concat([decipher.update(Buffer.from(encryptedHex, 'hex')), decipher.final()])
  return decrypted.toString()
}
```

### Helmet & CORS (bảo mật HTTP headers)

```typescript
pnpm add helmet

// main.ts
import helmet from 'helmet'
app.use(helmet())   // set security headers (X-Frame-Options, CSP, HSTS, ...)

app.enableCors({
  origin: ['https://app.example.com'],
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  credentials: true,
})
```

---

## Health Checks (@nestjs/terminus)

```typescript
pnpm add @nestjs/terminus

// health/health.module.ts
import { TerminusModule } from '@nestjs/terminus'
import { HttpModule } from '@nestjs/axios'

@Module({
  imports: [TerminusModule, HttpModule],
  controllers: [HealthController],
})
export class HealthModule {}

// health/health.controller.ts
import { Controller, Get } from '@nestjs/common'
import {
  HealthCheckService, HealthCheck,
  TypeOrmHealthIndicator,
  HttpHealthIndicator,
  MemoryHealthIndicator,
  DiskHealthIndicator,
} from '@nestjs/terminus'

@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator,
    private http: HttpHealthIndicator,
    private memory: MemoryHealthIndicator,
    private disk: DiskHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.db.pingCheck('database'),                          // SELECT 1
      () => this.http.pingCheck('external', 'https://example.com'), // HTTP ping
      () => this.memory.checkHeap('memory_heap', 200 * 1024 * 1024), // < 200MB
      () => this.disk.checkStorage('storage', { path: '/', thresholdPercent: 0.9 }),
    ])
  }
}
```

Response format:

```json
{ "status": "ok", "info": { "database": { "status": "up" } }, "error": {}, "details": {} }
```

---

## Server-Sent Events (SSE)

One-way stream từ server → client qua HTTP — nhẹ hơn WebSocket khi không cần bidirectional.

```typescript
import { Sse, MessageEvent } from '@nestjs/common'
import { Observable, interval } from 'rxjs'
import { map } from 'rxjs/operators'

@Controller('events')
export class EventsController {
  @Sse('stream')
  stream(): Observable<MessageEvent> {
    return interval(1000).pipe(
      map(count => ({
        data: { count, timestamp: Date.now() },
        id: String(count),
        type: 'tick',
        retry: 3000,   // ms client waits before reconnect
      })),
    )
  }

  // Real-world: emit từ EventEmitter
  @Sse('notifications')
  notifications(@Query('userId') userId: string): Observable<MessageEvent> {
    return new Observable(subscriber => {
      const handler = (event: NotificationCreatedEvent) => {
        if (event.userId === userId) {
          subscriber.next({ data: event })
        }
      }
      this.eventEmitter.on('notification.created', handler)
      return () => this.eventEmitter.off('notification.created', handler)
    })
  }
}

// Client (browser)
const es = new EventSource('/events/stream')
es.onmessage = ({ data }) => console.log(JSON.parse(data))
es.addEventListener('tick', ({ data }) => console.log(data))
es.onerror = () => es.close()
```

---

## Cookies

```typescript
pnpm add cookie-parser && pnpm add -D @types/cookie-parser

// main.ts
import * as cookieParser from 'cookie-parser'
app.use(cookieParser('optional-secret-for-signed-cookies'))
```

```typescript
import { Res, Req } from '@nestjs/common'
import { Request, Response } from 'express'

@Controller('auth')
export class AuthController {
  @Post('login')
  login(@Res({ passthrough: true }) res: Response) {
    // Set cookie
    res.cookie('refreshToken', token, {
      httpOnly: true,       // JS không đọc được
      secure: true,         // chỉ HTTPS
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days ms
    })
    return { accessToken }
  }

  @Post('refresh')
  refresh(@Req() req: Request) {
    const token = req.cookies['refreshToken']         // unsigned
    const signed = req.signedCookies['refreshToken']  // signed (khi dùng secret)
    return this.authService.refresh(token)
  }

  @Post('logout')
  logout(@Res({ passthrough: true }) res: Response) {
    res.clearCookie('refreshToken')
    return { ok: true }
  }
}
```

> **`passthrough: true`**: bắt buộc khi dùng `@Res()` nhưng vẫn muốn NestJS tự gửi response (không gọi `res.send()` thủ
> công).

---

## Session

```typescript
pnpm add express-session && pnpm add -D @types/express-session
# Redis session store (production):
pnpm add connect-redis ioredis

// main.ts
import * as session from 'express-session'

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 1000 * 60 * 60 * 24 * 7,  // 7 days
  },
  // Redis store
  store: new RedisStore({ client: redisClient }),
}))
```

```typescript
// Đọc / ghi session trong controller
@Controller('auth')
export class AuthController {
  @Post('login')
  login(@Session() session: Record<string, any>, @Body() dto: LoginDto) {
    session.userId = 'abc123'
    session.role = 'admin'
    return { ok: true }
  }

  @Get('me')
  me(@Session() session: Record<string, any>) {
    if (!session.userId) throw new UnauthorizedException()
    return { userId: session.userId }
  }

  @Post('logout')
  logout(@Session() session: Record<string, any>) {
    session.destroy()
    return { ok: true }
  }
}
```

> Prefer JWT / Clerk cho stateless auth. Session phù hợp khi cần server-side invalidation ngay lập tức hoặc làm việc với
> SSR apps.

---

## CQRS

Tách Command (write) khỏi Query (read). Phù hợp khi business logic phức tạp, cần audit trail, hoặc chuẩn bị cho Event
Sourcing.

```typescript
pnpm add @nestjs/cqrs

// module
import { CqrsModule } from '@nestjs/cqrs'
@Module({
  imports: [CqrsModule],
  providers: [CreateOrderHandler, GetOrderHandler, OrderCreatedHandler],
})
export class OrdersModule {}
```

```typescript
// Command — write, có side effect
export class CreateOrderCommand extends Command<{ orderId: string }> {
  constructor(
    public readonly userId: string,
    public readonly items: OrderItem[],
  ) { super() }
}

@CommandHandler(CreateOrderCommand)
export class CreateOrderHandler implements ICommandHandler<CreateOrderCommand> {
  constructor(private repo: OrdersRepository) {}

  async execute(cmd: CreateOrderCommand) {
    const order = await this.repo.create({ userId: cmd.userId, items: cmd.items })
    return { orderId: order.id }
  }
}

// Query — read only, không có side effect
export class GetOrderQuery extends Query<Order> {
  constructor(public readonly orderId: string) { super() }
}

@QueryHandler(GetOrderQuery)
export class GetOrderHandler implements IQueryHandler<GetOrderQuery> {
  constructor(private repo: OrdersRepository) {}

  async execute(query: GetOrderQuery): Promise<Order> {
    return this.repo.findById(query.orderId)
  }
}

// Event — kết quả của command (cho Event Sourcing / decoupled side effects)
export class OrderCreatedEvent {
  constructor(public readonly orderId: string) {}
}

@EventsHandler(OrderCreatedEvent)
export class OrderCreatedHandler implements IEventHandler<OrderCreatedEvent> {
  handle(event: OrderCreatedEvent) {
    // send email, update read model, ...
  }
}

// Dispatch từ controller
@Controller('orders')
export class OrdersController {
  constructor(
    private commandBus: CommandBus,
    private queryBus: QueryBus,
  ) {}

  @Post()
  create(@Body() dto: CreateOrderDto, @ActiveUser('sub') userId: string) {
    return this.commandBus.execute(new CreateOrderCommand(userId, dto.items))
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.queryBus.execute(new GetOrderQuery(id))
  }
}
```

> Không phải mọi endpoint cần CQRS. Dùng khi: domain logic phức tạp, cần tách read/write model, hoặc đang làm Event
> Sourcing. Với CRUD đơn giản, dùng Service trực tiếp.
