# Component Identification Approaches

## Workflow Approach

Identify components by tracing major user journeys through the system.

### Process
1. Map out the major processing steps of a workflow
2. Add detail progressively
3. Model several different user workflows to discover more components
4. Group related steps into logical components

### Key insight
Not always 1:1 mapping. Several workflow steps may point to the same component if their functionalities are closely related.

### Example: Construction Worker Assignment System
Goal: Assign construction workers to different construction sites.
1. Maintain a list of workers (skills, locations) → `Worker Management`
2. Create new projects, define work sites → `Project Management`
3. Schedule start/end dates → `Project Scheduling`
4. Assign available workers based on skills/location → `Worker Assignment`
5. Release workers from completed projects → `Worker Assignment` (same component, related function)

Steps 4 and 5 map to the same component because assigning and releasing workers are closely related responsibilities.

## Actor/Action Approach

Identify components by listing actors and their primary actions. Similar to Event Storming but simpler — only identifies actor + domain event.

### Process
1. Identify actors (different users or roles)
2. Identify primary actions each actor takes (not exhaustive — focus on main actions)
3. Assign each action to a new or existing logical component

### Example: Online Auction System
| Actor | Action | Component |
|-------|--------|-----------|
| Bidder | Register account | `Bidder Registration` |
| Bidder | Sign on | `Bidder Sign-on` |
| Bidder | Search auctions | `Auction Search` |
| Bidder | View auction | `Auction Viewer` |
| Bidder | Place bid | `Bid Capture` |
| Auctioneer | Schedule auction | `Auction Scheduler` |
| Auctioneer | Maintain auction | `Auction Maintenance` |

## Combining Both

Start with Actor/Action to identify all actions, then use Workflow to arrange actions in likely execution order. This often reveals missing components (e.g., a notification step that no actor explicitly triggers but the system needs).

## Output Template

Present identified components as:

```
| # | Component Name | Description | Discovered Via |
|---|---------------|-------------|----------------|
| 1 | Bid Capture | Accepts and processes bids from online users | Actor/Action: Bidder → Place bid |
| 2 | Auction Scheduler | Manages auction timing and scheduling | Workflow: step 3 |
```

Include a simple dependency diagram showing component relationships.
