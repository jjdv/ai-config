# Levels and aspects

Shared by `propose-plan` (decisions on a planned design) and `assess-scope` (findings on an existing scope). An **item** below is a decision or a finding.

## Levels

Levels are abstraction depth, not aspects: an aspect can have items at more than one level. An item belongs to the **highest level at which it constrains other aspects**; UX scope and flows constrain architecture (Level 1), visual and interaction detail does not (Level 3).

| Level | Holds |
| --- | --- |
| 1. Product and system shape | Goals, scope, success criteria, user-facing capabilities and main flows, system boundaries, major trade-offs |
| 2. Architecture | Components and responsibilities, data model, interfaces and integrations, technology choices, cross-cutting strategies (security, performance, error handling, failure behaviour) |
| 3. Design detail | UI and interaction details, schemas and field-level choices, implementation detail, performance tuning |

Levels are worked top-down. Deep research and thinking for a level starts only after the level above is settled.

## Aspects

Always consider: architecture (implementation, process), data structures, UX, UI, performance, security. Add those the scope implies: integrations, migration and rollout, testing and verification, observability, accessibility, cost, compliance, failure modes, and any domain-specific aspect outside this set.

For each kept aspect set: importance (`core`, `supporting`, `minor`), complexity, tier, dependencies on other aspects. Drop aspects the scope does not touch and record each with a one-line reason.
