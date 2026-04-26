# Performance Reference

## Table of contents

- §1 Measuring Performance
- §2 Bundle Optimization
- §3 Rendering Performance
- §4 Image & Media Optimization
- §5 Data Fetching Optimization
- §6 CSS Performance

---

## §1 Measuring Performance

### Core Web Vitals targets

| Metric  | Good    | Needs Improvement | Poor    | What it measures                    |
|---------|---------|-------------------|---------|-------------------------------------|
| **LCP** | < 2.5s  | 2.5–4.0s          | > 4.0s  | Largest visible element load time   |
| **INP** | < 200ms | 200–500ms         | > 500ms | Responsiveness to user interactions |
| **CLS** | < 0.1   | 0.1–0.25          | > 0.25  | Visual stability (layout shifts)    |

### Profiling tools

**Development:**

- React DevTools Profiler — Render counts, commit durations, component tree timing
- `why-did-you-render` — Detects avoidable re-renders
- Chrome DevTools Performance tab — JS execution, layout, paint, compositing
- **React 19.2 Performance Tracks** — Custom Chrome DevTools tracks:
    - Scheduler track: shows priorities (blocking vs transition), render phases, event timing
    - Components track: shows component mount/render/effect timing per component

**Audit:**

- Lighthouse — Core Web Vitals, accessibility, best practices score
- PageSpeed Insights — Real-user data (CrUX) + lab data
- WebPageTest — Waterfall analysis, filmstrip comparison

**Production monitoring:**

- `web-vitals` library — Track real-user Core Web Vitals
- Sentry Performance — Transaction tracing, slow component detection
- Vercel Analytics / DataDog RUM — Dashboard with CWV trends

### Profile before optimizing

```tsx
// Add web-vitals tracking to production
import { onCLS, onINP, onLCP } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  // Send to your analytics endpoint
  fetch('/api/vitals', {
    method: 'POST',
    body: JSON.stringify({ name: metric.name, value: metric.value }),
  });
}

onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onLCP(sendToAnalytics);
```

---

## §2 Bundle Optimization

### Code splitting

```tsx
// Route-level splitting (automatic in Next.js)
// Each page.tsx is its own chunk

// Component-level splitting (for heavy components)
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));
const RichTextEditor = lazy(() => import('./RichTextEditor'));

function Dashboard() {
  return (
    <div>
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart data={data} />
      </Suspense>
      <Suspense fallback={<EditorSkeleton />}>
        <RichTextEditor />
      </Suspense>
    </div>
  );
}
```

### Dynamic imports for conditional features

```tsx
// Only load when user needs it
async function handleExport() {
  const { exportToPDF } = await import('@/lib/pdf-export');
  await exportToPDF(data);
}

// Conditional component loading
function AdminPanel() {
  const isAdmin = useUser().role === 'admin';
  const AdminTools = isAdmin
    ? lazy(() => import('./AdminTools'))
    : () => null;

  return (
    <Suspense fallback={null}>
      <AdminTools />
    </Suspense>
  );
}
```

### Bundle analysis

```bash
# Next.js
npm install @next/bundle-analyzer
# In next.config.js:
# const withBundleAnalyzer = require('@next/bundle-analyzer')({ enabled: process.env.ANALYZE === 'true' });
ANALYZE=true npm run build

# Generic
npx source-map-explorer 'dist/**/*.js'
```

### Tree shaking tips

- Use ESM imports (`import { map } from 'lodash-es'` not `import _ from 'lodash'`)
- Barrel files (index.ts) can prevent tree shaking — import directly when bundle size matters
- Check with `import-cost` VSCode extension for per-import size
- Replace heavy libraries: `moment` → `date-fns` or `dayjs`, `lodash` → `lodash-es` or native

---

## §3 Rendering Performance

### React Compiler (React 19+)

React Compiler automatically memoizes components and values. If on React 19+:

- Remove most manual `useMemo`, `useCallback`, `React.memo`
- The compiler applies optimizations at build time where safe
- Still need manual optimization for: very expensive computations, referential identity for external libs

### When NOT on React 19 — manual optimization

```tsx
// React.memo — prevent re-render when props haven't changed
const ExpensiveList = React.memo(function ExpensiveList({ items }: { items: Item[] }) {
  return items.map((item) => <ExpensiveItem key={item.id} item={item} />);
});

// useMemo — cache expensive computation
function Dashboard({ data }: { data: DataPoint[] }) {
  const aggregatedData = useMemo(
    () => data.reduce((acc, point) => /* expensive calculation */, {}),
    [data] // Only recompute when data changes
  );
  return <Chart data={aggregatedData} />;
}

// useCallback — stable function reference for child components
function Parent() {
  const handleClick = useCallback((id: string) => {
    // handle click
  }, []);

  return <ChildList onClick={handleClick} />;
}
```

### Virtual scrolling for large lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60, // Estimated row height
    overscan: 5, // Render 5 extra items above/below viewport
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <ItemRow item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Avoiding common re-render traps

```tsx
// Bad — new object on every render
<Component style={{ color: 'red' }} />        // new ref every render
<Component items={data.filter(x => x.active)} /> // new array every render
<Component onClick={() => handleClick(id)} />  // new function every render

// Good — stable references
const style = useMemo(() => ({ color: 'red' }), []);
const activeItems = useMemo(() => data.filter(x => x.active), [data]);
const handleItemClick = useCallback((id: string) => handleClick(id), []);
```

### Debounce expensive operations

```tsx
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  // Only fetch when debounced value changes — not on every keystroke
  const { data } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => api.search(debouncedQuery),
    enabled: debouncedQuery.length > 2,
  });

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

---

## §4 Image & Media Optimization

### Next.js Image component

```tsx
import Image from 'next/image';

// Remote image — requires next.config.js domains config
<Image
  src="https://cdn.example.com/hero.jpg"
  alt="Hero banner"
  width={1200}
  height={600}
  priority              // Above-the-fold: skip lazy loading, preload
  sizes="(max-width: 768px) 100vw, 1200px"
  className="rounded-lg"
/>

// Below-fold image — lazy loaded by default
<Image
  src="/product-photo.jpg"
  alt="Product"
  width={400}
  height={400}
  placeholder="blur"    // Show blur placeholder while loading
  blurDataURL="data:image/..."
/>
```

### Image optimization checklist

- **Format**: WebP/AVIF auto-conversion (Next.js Image does this)
- **Sizes**: `sizes` attribute for responsive images — prevents downloading oversized images
- **Priority**: `priority` prop for LCP image (hero, above-fold)
- **Dimensions**: Always set width + height or use `fill` with a sized container — prevents CLS
- **Lazy loading**: Default for below-fold (browser `loading="lazy"`)
- **Placeholder**: Blur or color placeholder for perceived performance
- **CDN**: Serve from edge (Vercel, Cloudinary, Imgix)

---

## §5 Data Fetching Optimization

### Avoid waterfalls

```tsx
// Bad — sequential fetching (waterfall)
async function Page() {
  const user = await getUser();        // 200ms
  const posts = await getPosts(user.id); // 300ms — waits for user
  const comments = await getComments(posts[0].id); // 200ms — waits for posts
  // Total: ~700ms sequential
}

// Good — parallel where possible
async function Page() {
  const user = await getUser(); // Need user first for dependent queries
  const [posts, notifications] = await Promise.all([
    getPosts(user.id),
    getNotifications(user.id),
  ]); // Both fetch in parallel: ~300ms instead of 500ms
}

// Best — streaming with Suspense
async function Page() {
  const user = await getUser(); // Fast, render immediately
  return (
    <>
      <UserHeader user={user} />
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList userId={user.id} /> {/* Streams when ready */}
      </Suspense>
      <Suspense fallback={<NotifSkeleton />}>
        <Notifications userId={user.id} /> {/* Streams independently */}
      </Suspense>
    </>
  );
}
```

### TanStack Query staleTime tuning

```tsx
// Rarely changes (user profile, settings) — cache longer
useQuery({ queryKey: ['user'], queryFn: getUser, staleTime: 10 * 60 * 1000 }); // 10 min

// Changes frequently (feed, notifications) — shorter cache
useQuery({ queryKey: ['feed'], queryFn: getFeed, staleTime: 30 * 1000 }); // 30 sec

// Real-time data — always fresh
useQuery({ queryKey: ['stock', ticker], queryFn: () => getStock(ticker), staleTime: 0 });
```

### Prefetching strategies

- **On hover**: Prefetch the destination page data when user hovers a link
- **On route transition**: Use Next.js `<Link prefetch>` (default behavior)
- **On visibility**: Prefetch when a section scrolls into view
- **On idle**: Use `requestIdleCallback` to prefetch anticipated data

---

## §6 CSS Performance

### Tailwind CSS (recommended — zero runtime)

- PurgeCSS built-in — only ships used classes
- No runtime CSS-in-JS overhead
- Works perfectly with Server Components
- Combine with `clsx` or `cn()` for conditional classes:

```tsx
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage
<button className={cn(
  'px-4 py-2 rounded-md font-medium',
  variant === 'primary' && 'bg-blue-600 text-white',
  variant === 'ghost' && 'bg-transparent text-gray-700',
  disabled && 'opacity-50 cursor-not-allowed',
)} />
```

### CSS-in-JS considerations

- **Styled Components / Emotion**: Runtime overhead, NOT compatible with Server Components (requires `'use client'`)
- **Vanilla Extract**: Zero-runtime CSS-in-JS, works with RSC, great for design tokens
- **CSS Modules**: Zero runtime, scoped styles, works everywhere

**Rule**: For new projects, use Tailwind CSS. If you need a token system, Tailwind config handles it. If you need more,
CSS Modules + CSS Variables or Vanilla Extract.

### Critical CSS

Next.js automatically inlines critical CSS for the initial render. For custom setups:

- Extract above-the-fold CSS
- Inline in `<head>`
- Load remaining CSS asynchronously
