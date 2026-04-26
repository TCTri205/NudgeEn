# Component Coupling & Law of Demeter

## Coupling Types

### Afferent Coupling (CA)
Total **incoming** dependencies — how many components depend on this one.

Example: `Bidder Profile` is used by `Auction Registration` and `Automatic Payment` → CA = 2

### Efferent Coupling (CE)
Total **outgoing** dependencies — how many components this one depends on.

Example: `Bid Capture` sends to `Bid Streamer` and `Bid Tracker` → CE = 2

### Total Coupling (CT)
CT = CA + CE. Lower is generally better for individual components, but total system coupling stays constant — you're redistributing, not eliminating.

## Coupling Analysis Table Template

```
| Component | CA | CE | CT | Assessment |
|-----------|----|----|-----|------------|
| Order Placement | 1 | 4 | 5 | HIGH — knows too much |
| Email Notification | 1 | 0 | 1 | Good |
| Item Pricing | 0 | 1 | 1 | Good |
```

## Tight vs Loose Coupling Trade-offs

| Aspect | Tightly Coupled | Loosely Coupled |
|--------|----------------|-----------------|
| Workflow | Centralized hub knows all steps | Distributed; each component knows only next step |
| Benefit | Easy to understand entire flow | Low risk; change in one component unlikely to break others |
| Drawback | High risk; change in any dependency can break the hub | Harder to trace full workflow |

## Law of Demeter (Principle of Least Knowledge)

A component should have minimal knowledge about other components' internals.

### Rebalancing Example
**Before:** `Order Placement` (CT=5) knows about decrementing inventory, checking stock, ordering more, setting prices, notifying customers.

**After:** Move "stock low? order more" knowledge to `Inventory Management` (where it belongs). `Order Placement` drops to CT=3, `Inventory Management` gains CE. Total system coupling unchanged (CT=9), but knowledge is where it should be.

### When to Rebalance
- A component has CE > 3 (knows about too many others)
- A component contains knowledge that belongs to another component's domain
- Changing one component frequently breaks another
