---
name: propose-plan
description: >-
  Elaborate an initial idea into a decision-complete plan brief covering
  architecture, data structures, UX, UI, performance, security and other
  relevant aspects. Researches in parallel with tiered subagents, asks the user
  to decide every open direction with ask-questions (each with a recommendation),
  records decisions in a brief, then hands off to create-plan. Use when the user
  has an idea, feature or initiative that needs shaping before a plan is written,
  or asks to propose, design or elaborate a plan.
---

# Propose plan

{{block:tool-note}}

Turn an idea into a **plan brief**: every key detail specified, every key decision made by the user, every key open question closed. The last step runs `create-plan` on that brief.

## Roles

| Who | Does |
| --- | --- |
| Main thread (supervisor) | Dialogue with the user, `ask-questions` rounds, relay, choosing tiers, deciding parallel vs sequential, spawning |
| `standard` | Process management (brief file upkeep, decision log, consolidation, status), data gathering from the codebase, docs and the internet, fact sheets for higher tiers |
| `principal`, `expert` | Key thinking: investigation, option analysis, solution proposals, risk and trade-off judgment. Consume `standard` fact sheets instead of gathering data themselves |
| `senior` | Aspects of moderate complexity that do not need the top tiers |

Subagents cannot ask the user: they return **draft questions** (decision, context, options, recommendation). The main thread asks them and relays answers in the next spawn.

## Tier selection

Pick per aspect from importance, complexity and blast radius, not once per run. A `minor` aspect gets no own gather or thinker: fold it into the closest related aspect's thinker.

| Work | Tier |
| --- | --- |
| Reading code, docs, web sources; inventories; fact sheets; brief upkeep; consolidation; status | `standard` |
| Well-understood aspect, one clear option space | `senior` |
| Cross-cutting aspect, several viable architectures, non-obvious trade-offs | `principal` |
| Hardest or highest-risk aspect (core architecture, security model, data model migration, performance-critical paths), or review of the consolidated brief | `expert` |

Default for key thinking: `expert` or `principal`. Never spend a high tier on data gathering.

## Splitting for cost

Every investigation is split into two stages:

1. **Gather** (`standard`): a bounded fact sheet with sources and paths. Facts only, no recommendations.
2. **Think** (`principal` or `expert`): receives the fact sheets in its prompt and returns options with a recommendation per direction.

A thinking agent that needs more data returns a **gather request**; the main thread spawns `standard` and re-spawns the thinker with the result.

## Parallelism

Look for parallel work at every phase, then decide per set of tasks:

- **Parallel** (same turn, several spawns): independent aspects, independent gather tasks, read-only investigations, anything with no shared written files and no data dependency.
- **Sequential**: tasks that may write the same files (the brief is written only by one `standard` at a time), and a thinker that depends on a gather or on another aspect's decision.
- Aspect dependencies decide order: decide upstream aspects (for example data model) before downstream ones (API, UI, performance) when the answer changes the options.

Gather tasks for all aspects run in one parallel wave; thinkers for independent aspects run in one parallel wave.

## Phases

### 1. Intake

1. Restate the idea in one paragraph and fix the **project root**.
2. Spawn one `standard` to survey the project context (conventions, existing architecture, relevant code, prior decisions) and return a fact sheet with proposed `<slug>`.
3. Ask only what blocks decomposition (goal, success criteria, hard constraints, out of scope) with `ask-questions`.

### 2. Aspect decomposition

1. Spawn `standard` (or use the fact sheet) to list candidate aspects. Always consider: architecture (implementation, process), data structures, UX, UI, performance, security, plus those the idea implies: integrations, migration and rollout, testing and verification, observability, accessibility, cost, compliance, failure modes, and any domain-specific aspect outside this set.
2. Drop aspects the idea does not touch; record dropped ones with a one-line reason.
3. For each kept aspect set: importance (`core`, `supporting`, `minor`), complexity, tier, dependencies on other aspects, gather tasks needed.
4. Confirm the aspect list (drops, importance, tiers) with one `ask-questions` question before fanning out; recommended option: proceed as listed.

### 3. Research fan-out

1. Spawn all independent gather tasks as `standard` in parallel.
2. Collect fact sheets. A failed or thin sheet is re-gathered, not guessed.

### 4. Proposal per aspect

1. Spawn one thinker per aspect (parallel where independent), passing: idea, project root, relevant fact sheets, decisions already made, the aspect's scope.
2. Each thinker returns, in the **proposal format** below, either a single justified decision or **directions of similar value** with a recommendation.
3. A decision with one clearly dominant direction is recorded as **proposed** and listed for confirmation, not asked as an open question.
4. A new aspect reported by a thinker goes through phase 2 step 3, then phases 3 and 4.

Proposal format returned by a thinker:

```
Aspect: <name>
Findings: <facts that drive the choice, with sources>
Proposal: <the recommended design, concrete enough to plan from>
Directions (only when similar value):
  - <id> <option>: <benefit> / <cost> / <risk>
Recommendation: <direction id or the proposal>, <reason in one sentence>
Questions: <decision | context | options | recommended option>
Cross-aspect impact: <aspects affected, including new aspects missing from the list>
Gather requests: <what is missing>
```

### 5. Ask-questions rounds

1. Group draft questions by aspect and dependency. Run `ask-questions` rounds in dependency order: upstream decisions first.
2. Every question carries a **recommended option**, listed first and marked, with the reason it is recommended.
3. Ask only decisions where directions have similar value; do not ask what a dominant direction settles.
4. After each round, spawn `standard` to record answers in the brief's decision log. Answers that change a downstream aspect re-spawn its thinker with the decision.
5. Repeat until no aspect has an open direction or open question.

### 6. Consolidation

1. Spawn `standard` to merge all decisions into the brief and run a consistency pass: contradictions, uncovered requirements, decisions without owner aspect, open questions left.
2. For a large or high-risk idea, spawn `expert` to review the consolidated brief against the goal and the checklist below; its findings go back through phase 5.
3. Present the user a short summary of the decided design and any residual risks. Wait for approval or changes.

### 7. Handoff to create-plan

1. Brief status is `approved`. Brief path: `<project-root>/.local/<slug>/brief.md`.
2. Run `create-plan` with the project root, slug, brief path and the instruction to treat the brief as locked decisions: list it in Context references, keep every decision in the plan or its task files, and carry open items into Open questions only if the user deferred them.
3. After `create-plan` finishes, report the plan path and the single next command.

## Plan brief format

One file, `<project-root>/.local/<slug>/brief.md`, written and updated only by `standard`. Add `.local/` to the project's ignore file when missing.

```markdown
---
brief: true
status: draft | approved
slug: <slug>
last_updated: YYYY-MM-DD
---

# <Idea title>

**Project root:** `/absolute/path`

## Goal and scope
Goal, success criteria, constraints, out of scope.

## Aspects
| Aspect | Tier used | Status | Summary |
| --- | --- | --- | --- |
| architecture | expert | decided | one line |

## Decision log
| ID | Aspect | Decision | Alternatives rejected | Reason | Source |
| --- | --- | --- | --- | --- | --- |
| D1 | data | chosen option | other options | why | user / proposed-confirmed |

## Design by aspect
### <aspect>
Concrete design: components, flows, data structures and schemas, UX flows, UI elements and states, performance budgets, threat model and controls, as relevant. Implementation-ready detail, no open choices.

## Dependencies and sequencing hints
Ordering constraints between parts, parallelizable parts, external prerequisites.

## Verification and acceptance
How each success criterion is verified.

## Risks and mitigations

## Open questions
Only items the user explicitly deferred, each with owner and blocking task area. Empty otherwise.

## Evidence
Fact-sheet summaries with paths and sources.
```

Decision `Source` is `user` when the user chose, `proposed-confirmed` when the user approved a dominant proposal.

## Completeness checklist

Before status `approved`:

- Every kept aspect has a decided design and at least one decision-log row or a stated no-decision reason.
- No open direction of similar value remains.
- Every user question had a recommendation and a recorded answer.
- Goal, success criteria and out of scope are explicit.
- Security, performance and failure modes are addressed or dropped with a reason.
- Verification covers every success criterion.
- No contradiction between aspects.

## Spawning

{{block:spawn-rule}}

```text
{{tool:spawn-agent}}(
  {{agent:standard}},
  run_in_background=false,
  description="gather: <aspect>",
  prompt="…"
)
```

- Self-contained prompts: idea, project root, aspect scope, inputs, return format. State what is out of scope and that the agent only reads unless it is the brief writer.
- Thinker prompts include the fact sheets, decisions so far and the proposal format.
- Brief writer prompts include an Authorization block: project root, may write only `.local/<slug>/`, no commit.
- Parallel spawns go in the same turn; wait for the whole wave before the next phase.
- Do not dump raw subagent output into chat; relay only what the user must decide or verify.

## Anti-patterns

- Gathering data in the main thread or with a high tier.
- Asking a question without a recommendation, or one whose options are not of similar value.
- Asking aspects in parallel rounds when a downstream answer depends on an upstream one.
- Two agents writing the brief at once.
- Running `create-plan` before the brief is `approved`.
- Guessing a product or policy choice instead of asking.
