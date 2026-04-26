# The Entity Trap & Component Naming

## The Entity Trap

Grouping all actions related to a single data entity into one large component.

### Example (BAD)
`Bid Manager` — responsible for: accepting bids, displaying winners, auditing bids, determining winners, notifying users, generating reports. All in one place.

### Problems
1. **Vague naming:** "Bid Manager" doesn't tell you what the component actually does
2. **Too many responsibilities:** Becomes a dumping ground — bloated, hard to maintain, hard to scale, hard to make fault-tolerant

## Red Flag Words

These words in component names often signal the Entity Trap:
- Manager, Supervisor, Handler, Controller
- Agent, Service, Engine, Mediator
- Coordinator, Orchestrator, Processor
- Utility, Worker

## When It's OK

Not a hard rule. `Reference Data Manager` (managing country codes, etc.) is specific and acceptable. The trap is when names like `Order Manager` are too broad and don't describe specific behavior.

## Good Naming Patterns

| Bad | Good | Why |
|-----|------|-----|
| Bid Manager | Bid Capture | Specifically describes accepting bids |
| Bid Manager | Bid Tracker | Specifically describes tracking bid history |
| Bid Manager | Bid Streamer | Specifically describes streaming bids to viewers |
| Order Manager | Order Placement | Specifically describes placing orders |
| User Service | Bidder Registration | Specifically describes user registration for bidders |

## Naming Test

Ask: "Can someone read this name and know exactly what the component does without asking?" If no, the name is too vague.
