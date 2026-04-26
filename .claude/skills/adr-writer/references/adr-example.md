# ADR Example

Reference example of a well-written ADR.

```markdown
# 012: Use of Queues for Asynchronous Messaging Between Order and Downstream Services

## Status
Accepted

## Context
The trading service must inform downstream services (namely the notification and analytics services, for now) about new items available for sale and about all transactions. This can be done through synchronous messaging (using REST) or asynchronous messaging (using queues or topics).

## Decision
We will use queues for asynchronous messaging between the trading and downstream services.

Using queues makes the system more extensible, since each queue can deliver a different kind of message. Furthermore, since the trading service is acutely aware of any and all subscribers, adding a new consumer involves modifying it — which improves the security of the system.

## Consequences

### Positive
- System is more extensible via separate queues per message type
- Security improved — trading service controls subscriber access

### Negative
- Higher degree of coupling between services
- Queuing infrastructure must be provisioned and clustered for HA
- Adding new downstream services requires modifications to trading service

## Governance
- Code reviews on all queue consumer/producer changes
- Infrastructure monitoring for queue health and message delivery

## Notes
- **Original Author:** Architecture Team
- **Approval Date:** 2025-10-22
- **Approved By:** Lead Architect
```
