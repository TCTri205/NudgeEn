# Architecture Characteristics Catalog

Based on Mark Richards' Architecture Characteristics Worksheet (DeveloperToArchitect.com, March 2024) and "Software Architecture" reference material.

## Common Architecture Characteristics

| Characteristic | Definition | Related |
|---|---|---|
| **performance** | Time it takes for system to process a business request | a |
| **responsiveness** | Time it takes to get a response to the user | a |
| **availability** | Uptime of a system; usually measured in 9's (e.g., 99.9%) | b |
| **fault tolerance** | When fatal errors occur, other parts of system continue to function | b |
| **scalability** | System capacity and growth over time; as users/requests increase, responsiveness, performance, and error rates remain constant | c |
| **elasticity** | System can expand and respond quickly to unexpected or anticipated extreme loads (e.g., 20 to 250,000 users instantly) | c |
| **data integrity** | Data across the system is correct and there is no data loss | d |
| **data consistency** | Data across the system is in sync and consistent across databases and tables | d |
| **adaptability** | Ease in which system can adapt to changes in environment and functionality | e |
| **extensibility** | Ease in which system can be extended with additional features and functionality | e |
| **concurrency** | Ability to process simultaneous requests, usually in the same order received; implied when scalability and elasticity are supported | |
| **interoperability** | Ability to interface and interact with other systems to complete a business request | |
| **deployability** | Amount of ceremony involved with releasing software, frequency of releases, and overall risk of deployment | |
| **testability** | Ease of and completeness of testing | |
| **abstraction** | Level at which parts of system are isolated from other parts (internal and external interactions) | |
| **workflow** | Ability to manage complex workflows requiring multiple parts (services) to complete a business request | |
| **configurability** | Ability to support multiple configurations, custom on-demand configurations and configuration updates | |
| **recoverability** | Ability to start where it left off in the event of a system crash | |

**Related pairs (a/b):** Some systems only need one, others may need both.

## Implicit Characteristics (Always Considered)

| Characteristic | Definition |
|---|---|
| **feasibility (cost/time)** | Taking into account timeframes, budgets, and developer skills when making architectural choices; tight timeframes and budgets make this a driving characteristic |
| **security** | Ability to restrict access to sensitive information or functionality |
| **maintainability** | Level of effort required to locate and apply changes to the system |
| **observability** | Ability to make available and stream metrics such as overall health, uptime, response times, performance, etc. |

Implicit characteristics become **driving** characteristics if they are critical concerns.

## Composite Architecture Characteristics

| Composite | Components |
|---|---|
| **agility** | maintainability + testability + deployability |
| **reliability** | availability + testability + data integrity + data consistency + fault tolerance |

## Category Groupings (from reference material)

### Process Characteristics
modularity, testability, agility, deployability, decouple-ability, extensibility

### Structural Characteristics
security, maintainability, extensibility, portability, localization

### Operational Characteristics
scalability, recoverability, robustness, performance, reliability/safety, availability

### Cross-cutting Characteristics
security, legal, authentication/authorization, privacy, accessibility, usability

## Guiding Questions by Category

### Operational
- How many concurrent users are expected? Peak vs average?
- What uptime SLA is required? (99.9%? 99.99%?)
- Is traffic steady or bursty? (e.g., seasonal spikes, flash sales)
- How fast must the system respond? (ms? seconds?)
- What happens if the system goes down? Business impact?

### Structural
- How frequently will new features be added?
- How many external systems need integration?
- How large is the development team? Multiple teams?
- How often will the system be deployed?
- Is the codebase expected to grow significantly?

### Cross-cutting
- Does the system handle sensitive/personal data?
- Are there compliance requirements? (GDPR, HIPAA, PCI-DSS, SOC2)
- Does it need to work across regions/languages?
- Who are the end users? Technical sophistication?
- Are there legal/regulatory constraints?

### Environment & Feasibility
- Startup (agility-first) or enterprise (stability-first)?
- Budget and timeline constraints?
- Team expertise — what technologies are they comfortable with?
- Existing infrastructure that must be leveraged?

## Custom Characteristics

If no existing characteristic fits, create a custom one:
- Name MUST end in `-ility` (e.g., `auditability`, `portability`, `learnability`)
- Provide a clear, one-sentence definition following the pattern: "The ability/ease/level of [what the system can do]"
- Assign to the most appropriate category
- Document why existing characteristics don't cover this concern

### Examples of Custom Characteristics
| Characteristic | Definition | Category |
|---|---|---|
| **auditability** | The ability to trace and record all system actions for compliance review | Cross-cutting |
| **portability** | The ease in which the system can be moved to a different environment or platform | Structural |
| **learnability** | The ease in which new developers can understand and contribute to the system | Process |
| **debuggability** | The ease in which issues can be identified and diagnosed in production | Operational |
| **reproducibility** | The ability to consistently reproduce system behavior across environments | Process |
