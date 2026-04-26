---
library: zod v4
package: "zod"
context7_library_id: /colinhacks/zod
synced_version: v4.0.1
project_version: v4.3.6
declared_range: ^4.3.6
benchmark_score: 88.68
source_reputation: High
last_synced: 2026-03-21
coverage: primitives, objects, arrays, unions, transforms, safeParse, infer, v4 new features, breaking changes from v3
---

# Zod v4

TypeScript-first schema validation. Project uses v4.3.6 (released mid-2025). Import as `import { z } from 'zod'`.

## Breaking Changes from v3

| v3                   | v4                      |
|----------------------|-------------------------|
| `z.string().email()` | `z.email()` (top-level) |
| `z.string().url()`   | `z.url()` (top-level)   |
| `z.string().uuid()`  | `z.uuid()` (top-level)  |
| `error.errors`       | `error.issues`          |
| `z.ZodError`         | `z.ZodError` (same)     |
| `z.optional(schema)` | same                    |

## Primitives

```ts
import { z } from 'zod'

z.string()
z.number()
z.boolean()
z.bigint()
z.date()
z.undefined()
z.null()
z.any()
z.unknown()
z.never()
z.void()
```

## Top-Level Format Validators (New in v4)

```ts
// These are now top-level instead of z.string().email()
z.email()        // email address
z.url()          // any URL
z.httpUrl()      // http/https only
z.uuid()
z.nanoid()
z.cuid()
z.ulid()
z.ipv4()
z.ipv6()
z.jwt()
z.base64()
z.iso.date()     // "2024-01-15"
z.iso.time()     // "14:30:00"
z.iso.datetime() // "2024-01-15T14:30:00Z"
```

## String Validations

```ts
z.string().min(3)
z.string().max(100)
z.string().length(10)
z.string().includes('@')
z.string().startsWith('https')
z.string().endsWith('.pdf')
z.string().regex(/^[a-z0-9-]+$/)
z.string().trim()
z.string().toLowerCase()
z.string().toUpperCase()
```

## Number Validations

```ts
z.number().min(0)
z.number().max(100)
z.number().int()         // must be integer
z.number().positive()    // > 0
z.number().nonnegative() // >= 0
z.number().negative()    // < 0
z.number().finite()
z.number().multipleOf(5)
```

## Object Schema

```ts
const UserSchema = z.object({
  id: z.string(),
  email: z.email(),
  name: z.string().min(1),
  age: z.number().int().min(0).optional(),
  role: z.enum(['admin', 'user', 'guest']).default('user'),
})

type User = z.infer<typeof UserSchema>
// { id: string; email: string; name: string; age?: number; role: 'admin'|'user'|'guest' }
```

## Optional, Nullable, Default

```ts
z.string().optional()     // string | undefined
z.string().nullable()     // string | null
z.string().nullish()      // string | null | undefined
z.string().default('N/A') // fills undefined with 'N/A'
```

## Array

```ts
z.array(z.string())
z.array(z.string()).min(1)
z.array(z.string()).max(10)
z.array(z.string()).length(5)
z.string().array()  // shorthand
```

## Union & Discriminated Union

```ts
// Union
const StringOrNumber = z.union([z.string(), z.number()])

// Discriminated union (faster, better errors)
const ShapeSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('circle'), radius: z.number() }),
  z.object({ type: z.literal('rect'), width: z.number(), height: z.number() }),
])
```

## Transform

```ts
const TrimmedEmail = z.string().trim().toLowerCase().email()

const NumberFromString = z.string().transform((val) => Number(val))

// Refine (custom validation)
const PositiveNumber = z.number().refine(
  (n) => n > 0,
  { message: 'Must be positive' }
)
```

## Parse vs safeParse

```ts
// parse — throws ZodError on failure
const user = UserSchema.parse(rawData)

// safeParse — returns result object (preferred)
const result = UserSchema.safeParse(rawData)
if (!result.success) {
  console.log(result.error.issues)  // v4: .issues not .errors
} else {
  const user = result.data
}

// Async
const result = await UserSchema.safeParseAsync(rawData)
```

## Error Handling (v4 uses .issues)

```ts
try {
  UserSchema.parse(data)
} catch (err) {
  if (err instanceof z.ZodError) {
    err.issues.forEach(issue => {
      console.log(issue.path, issue.message, issue.code)
    })
  }
}
```

## Record, Map, Set

```ts
z.record(z.string(), z.number())  // { [key: string]: number }
z.map(z.string(), z.date())
z.set(z.string())
```

## With NestJS Pipes

```ts
// Zod validation pipe (NestJS)
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
create(@Body(new ZodValidationPipe(CreateUserSchema)) body: CreateUserDto) { ... }
```

## With TanStack Form

```ts
const form = useForm({
  defaultValues: { email: '', age: 0 },
  validators: {
    onChange: ({ value }) => {
      const result = schema.safeParse(value)
      if (!result.success) {
        return {
          fields: Object.fromEntries(
            result.error.issues.map(i => [i.path[0], i.message])
          ),
        }
      }
      return undefined
    },
  },
})
```

## Branded Types

```ts
const UserId = z.string().brand<'UserId'>()
type UserId = z.infer<typeof UserId>  // string & { __brand: 'UserId' }

const id = UserId.parse('abc-123')  // UserId type

// Control brand direction (v4.2+)
z.string().brand<'Cat', 'out'>()    // output branded (default)
z.string().brand<'Cat', 'in'>()     // input branded
z.string().brand<'Cat', 'inout'>()  // both
```
