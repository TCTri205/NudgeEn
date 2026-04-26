# ADR Template

Use this template when creating new ADRs.

```markdown
# {NNN}: {Title — use nouns, concise, describes what the decision covers}

## Status
{RFC | Proposed | Accepted | Superseded}

{If RFC: "Comments requested by: {YYYY-MM-DD}"}
{If Superseded: "Superseded by [ADR-{NNN}: {Title}](./{nnn}-{slug}.md)"}

## Context
{Explain the problem, challenge, or opportunity prompting this decision.
Include:
- Technical environment and constraints
- Non-technical factors (budget, team skills, regulatory, political)
- What triggered the need for a decision now

Do NOT list alternatives here — keep this section focused on the "why."}

## Decision
{State the decision in active, authoritative voice: "We will..."}

{Justify why this option was chosen over alternatives.
Address the key question: "Why is this the best choice given our context?"
Maintain objective, fact-based tone — no personal opinions.}

## Consequences

{Document trade-offs and impacts:}

### Positive
- {Benefit 1}
- {Benefit 2}

### Negative
- {Drawback or risk 1}
- {Drawback or risk 2}

### Neutral
- {Side effect or implication that is neither clearly positive nor negative}

{Consider impact on: implementing team, infrastructure, cross-cutting concerns,
time/budget, and irreversible limitations ("one-way doors").}

## Governance
{How will correct implementation be ensured?}
- {Short-term: e.g., code reviews, pair programming}
- {Long-term: e.g., automated fitness functions, architectural tests}

## Notes
- **Original Author:** {Name}
- **Approval Date:** {YYYY-MM-DD}
- **Approved By:** {Name/Role}
- **Last Modified Date:** {YYYY-MM-DD}
- **Modified By:** {Name}
- **Last Modification:** {Brief description}
```

## Superseding Template Addition

When an ADR supersedes another, add this line to the NEW ADR's Context section:

```markdown
This decision supersedes [ADR-{NNN}: {Title}](./{nnn}-{slug}.md) because {reason for change}.
```

And update the OLD ADR's Status section to:

```markdown
## Status
Superseded by [ADR-{NNN}: {Title}](./{nnn}-{slug}.md) on {YYYY-MM-DD}
```
