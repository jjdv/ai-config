---
name: propose-plan
description: >-
  Elaborate an initial idea into a decision-complete plan brief covering
  architecture, data structures, UX, UI, performance, security and other
  relevant aspects. Settles decisions level by level (product and system shape,
  architecture, design detail), researching each level with tiered subagents
  once the level above is settled, asks the user to decide every open direction
  with ask-questions (each with a recommendation), records decisions in a
  brief, then hands off to create-plan. Use when the user has an idea, feature
  or initiative that needs shaping before a plan is written, or asks to
  propose, design or elaborate a plan.
---

# Propose plan

{{block:tool-note}}

Turn an idea into a **plan brief**: every key detail specified, every key decision made by the user, every key open question closed. The last step runs `create-plan` on that brief.

## Levels and aspects

Level definitions, the placement rule and the aspect catalogue are in `references/levels-and-aspects.md`; read it before phase 2.

Asking by level:

| Level | Asking |
| --- | --- |
| 1. Product and system shape | Ask decisions with directions of similar value |
| 2. Architecture | Ask decisions with directions of similar value |
| 3. Design detail | Rarely constrains other aspects: record as **proposed** with a recommendation, ask only contentious ones |

## Roles

| Who | Does |
| --- | --- |
| Main thread (supervisor) | Dialogue with the user, `ask-questions` rounds, relay, choosing tiers, deciding parallel vs sequential, spawning |
| `standard` | Process management (brief file upkeep, decision log, consolidation, status), data gathering from the codebase, docs and the internet, fact sheets for higher tiers |
| `principal`, `expert` | Key thinking: investigation, option analysis, solution proposals, risk and trade-off judgment. Consume `standard` fact sheets instead of gathering data themselves |
| `senior` | Aspects of moderate complexity that do not need the top tiers |

Subagents cannot ask the user: they return **draft questions** (decision, context, options, recommendation). The main thread asks them and relays answers in the next spawn.

## Tier selection

Pick per aspect and level from importance, complexity and blast radius, not once per run. A `minor` aspect gets no own gather or thinker: fold it into the closest related aspect's thinker.

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
- Levels decide order: settle a level before researching the next. Within a level, gather tasks run in one parallel wave, then thinkers for independent aspects in one parallel wave; aspect dependencies decide order: upstream aspects (for example data model) before downstream ones when the answer changes the options.

## Phases

### 1. Intake

1. Restate the idea in one paragraph and fix the **project root**.
2. Spawn one `standard` to survey the project context (conventions, existing architecture, relevant code, prior decisions) and return a fact sheet with proposed `<slug>`.
3. Ask only what blocks decomposition (goal, success criteria, hard constraints, out of scope) with `ask-questions`.

### 2. Aspect decomposition

1. Spawn `standard` (or use the fact sheet) to list candidate aspects from the catalogue in the reference.
2. Drop aspects the idea does not touch, recording each with a reason as the reference defines.
3. For each kept aspect set importance, complexity, tier and dependencies, as the reference defines.
4. Confirm the aspect list (drops, importance, tiers) with one `ask-questions` question before scanning; recommended option: proceed as listed.

### 3. Shallow scan and level assignment

1. Spawn `standard` in parallel per aspect (or one for all small ones) for a shallow scan only: open decisions, dependencies on other aspects, no options analysis.
2. Assign every open decision to a level by the placement rule and record the map (aspect, decision, level, dependencies) in the brief.
3. Start at Level 1. Phases 4 and 5 repeat per level, top-down.

### 4. Proposal per level

1. Spawn `standard` gather tasks for the level's aspects in parallel. A failed or thin sheet is re-gathered, not guessed.
2. Spawn one thinker per aspect with decisions at this level (parallel where independent), passing: idea, project root, relevant fact sheets, decisions already made, the aspect's scope limited to this level.
3. Each thinker returns, in the **proposal format** below, either a single justified decision or **directions of similar value** with a recommendation.
4. A decision with one clearly dominant direction is recorded as **proposed** and listed for confirmation, not asked as an open question. Level 3 decisions default to this.
5. A new aspect reported by a thinker goes through phase 2 step 3 and a shallow scan (phase 3); its decisions are assigned to levels. It is handled at the current level only for decisions assigned to that level; the others are deferred to their level.

Proposal format returned by a thinker:

```
Aspect: <name>
Level: <1 | 2 | 3>
Findings: <facts that drive the choice, with sources>
Proposal: <the recommended design, concrete enough to plan from>
Directions (only when similar value):
  - <id> <option>: <benefit> / <cost> / <risk>
Recommendation: <direction id or the proposal>, <reason in one sentence>
Questions: <decision | context | options | recommended option>
Cross-aspect impact: <aspects affected, level reassignments, new aspects missing from the list>
Gather requests: <what is missing>
```

### 5. Ask-questions rounds

1. Ask one level at a time, aspect by aspect within the level, upstream aspects first. Follow `ask-questions` batching: one question for a single decision, up to 4 related questions per call, unrelated decisions in separate rounds.
2. Every question carries a **recommended option**, listed first and marked, with the reason it is recommended.
3. Ask only decisions where directions have similar value; do not ask what a dominant direction settles.
4. After each round, spawn `standard` to record answers in the brief's decision log. An answer that changes a downstream aspect or a level assignment re-spawns the affected thinkers with the decision. Reopen an already-settled level only if the answer changes its decisions, and re-think downstream aspects.
5. Repeat until the level has no open direction or open question, then return to phase 4 for the next level. After Level 3, no level has open items.

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

## Level map
| Aspect | Decision | Level | Dependencies |
| --- | --- | --- | --- |
| data | storage choice | 2 | none |

## Decision log
| ID | Level | Aspect | Decision | Alternatives rejected | Reason | Source |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | 2 | data | chosen option | other options | why | user / proposed-confirmed |

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

- Every decision has a level and was settled after the level above.
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
- Asking Level 3 detail that does not constrain other aspects instead of recording it as proposed.
- Two agents writing the brief at once.
- Running `create-plan` before the brief is `approved`.
- Guessing a product or policy choice instead of asking.
