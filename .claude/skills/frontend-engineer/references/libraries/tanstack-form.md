---
library: tanstack form
package: "@tanstack/react-form"
context7_library_id: /tanstack/form
synced_version: v1.11.0
project_version: latest
declared_range: latest
benchmark_score: 81.02
source_reputation: High
last_synced: 2026-03-21
coverage: useForm, form.Field, validators, async validation, form-level validation, cross-field validation, submission
---

# TanStack Form

Headless, type-safe form state management. No default UI — pairs with shadcn/ui or any component library.

## Basic Form

```tsx
import { useForm } from '@tanstack/react-form'

function SignupForm() {
  const form = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
    onSubmit: async ({ value }) => {
      await api.signup(value)
    },
  })

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        form.handleSubmit()
      }}
    >
      <form.Field
        name="email"
        validators={{
          onChange: ({ value }) =>
            !value ? 'Required' : !value.includes('@') ? 'Invalid email' : undefined,
        }}
        children={(field) => (
          <div>
            <input
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
            />
            {field.state.meta.errors.map((e, i) => (
              <span key={i} className="text-red-500">{e}</span>
            ))}
          </div>
        )}
      />

      <form.Subscribe
        selector={(state) => [state.canSubmit, state.isSubmitting]}
        children={([canSubmit, isSubmitting]) => (
          <button type="submit" disabled={!canSubmit || isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        )}
      />
    </form>
  )
}
```

## Field Validators

```tsx
<form.Field
  name="username"
  validators={{
    // Sync on change
    onChange: ({ value }) => {
      if (!value) return 'Required'
      if (value.length < 3) return 'Min 3 characters'
      if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Alphanumeric only'
      return undefined
    },
    // Async with debounce
    onChangeAsync: async ({ value, signal }) => {
      const res = await fetch(`/api/check-username?u=${value}`, { signal })
      const { available } = await res.json()
      return available ? undefined : 'Username taken'
    },
    onChangeAsyncDebounceMs: 500,
    // On blur
    onBlur: ({ value }) => (value.length > 20 ? 'Too long' : undefined),
  }}
  children={(field) => (
    <div>
      <input
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
      />
      {field.state.meta.isValidating && <span>Checking...</span>}
      {field.state.meta.errors.map((e, i) => <span key={i}>{e}</span>)}
    </div>
  )}
/>
```

## Form-Level Validation (cross-field)

```tsx
const form = useForm({
  defaultValues: { password: '', confirmPassword: '' },
  validators: {
    onChange: ({ value }) => {
      if (value.password !== value.confirmPassword) {
        return {
          form: 'Passwords must match',
          fields: { confirmPassword: 'Does not match password' },
        }
      }
      return undefined
    },
  },
  onSubmit: async ({ value }) => { /* ... */ },
})
```

## Linked Field Re-validation

```tsx
<form.Field
  name="confirmPassword"
  validators={{
    onChangeListenTo: ['password'],  // re-validates when password changes
    onChange: ({ value, fieldApi }) => {
      const password = fieldApi.form.getFieldValue('password')
      return value !== password ? 'Passwords do not match' : undefined
    },
  }}
  children={(field) => (
    <input
      type="password"
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
/>
```

## Field Meta State

```tsx
field.state.meta.errors        // string[] of current errors
field.state.meta.isValidating  // boolean - async validation in progress
field.state.meta.isDirty       // boolean - value changed from default
field.state.meta.isTouched     // boolean - field was focused+blurred
field.state.meta.isValid       // boolean
```

## Form State Subscription

```tsx
// Subscribe to specific state slices for performance
<form.Subscribe
  selector={(state) => state.isSubmitting}
  children={(isSubmitting) => (
    <button disabled={isSubmitting}>Submit</button>
  )}
/>

// Access full form state
const canSubmit = form.state.canSubmit
const isSubmitting = form.state.isSubmitting
const values = form.state.values
```

## With Zod Schema Validation

```tsx
import { useForm } from '@tanstack/react-form'
import { z } from 'zod'

const schema = z.object({
  email: z.email(),
  age: z.number().min(13),
})

const form = useForm({
  defaultValues: { email: '', age: 0 },
  validators: {
    onChange: ({ value }) => {
      const result = schema.safeParse(value)
      if (!result.success) {
        // Map zod errors to field errors
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

## Server-Side Errors (from API)

```tsx
const form = useForm({
  defaultValues: { username: '' },
  onSubmit: async ({ value, formApi }) => {
    try {
      await api.createUser(value)
    } catch (err) {
      if (err.field) {
        formApi.setFieldMeta(err.field, (meta) => ({
          ...meta,
          errors: [err.message],
        }))
      }
    }
  },
})
```
