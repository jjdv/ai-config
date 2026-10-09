---
name: assess-scope
description: >-
  Analyze an existing feature or code scope across aspects (architecture, data,
  UX, UI, performance, security and others) and levels (product and system
  shape, architecture, design detail), report evidence-backed findings and,
  where warranted, propose improvements. Fully read-only: writes no files,
  everything is delivered in chat; findings and agreed improvements are consumed
  by create-plan from the conversation. Use when the user asks
  to assess, audit, analyze or evaluate an existing feature or module, find what
  to improve in it, or review its design rather than a diff.
---

# Assess scope

{{block:tool-note}}

Turn an existing scope into a **findings report**: the as-built picture recovered first, then every aspect assessed level by level, each finding backed by evidence, improvements proposed only where warranted. **Read-only guarantee:** the assessment creates, edits or deletes no file anywhere, notes included. All communication happens in chat and all context stays in the chat history. Fixes are handed to `create-plan`, which takes the findings and agreements from the conversation.

Not a diff-focused review and not `propose-plan` (greenfield decisions).

## Levels and aspects

Shared with `propose-plan`: read `{{path:skills}}/propose-plan/references/levels-and-aspects.md` for level definitions, the placement rule (a finding belongs to the highest level at which it constrains other aspects) and the aspect catalogue.

Questions per level:

| Level | Asks |
| --- | --- |
| 1. Product and system shape | Is the scope right? Do boundaries and user-facing flows fit the purpose? |
| 2. Architecture | Do components, data model, interfaces and cross-cutting strategies (security, performance, failure behaviour) hold up? |
| 3. Design detail | Is the implementation or UI detail sound, consistent and verifiable? |

Levels are assessed top-down. Deep analysis for a level starts only after the level above is settled; its findings inform the next.

## Roles, tiers, parallelism

Roles, tier selection, gather/think splitting, parallelism and spawning follow `{{path:skills}}/propose-plan/SKILL.md` (Roles, Tier selection, Splitting for cost, Parallelism, Spawning), with these changes:

- Every agent is read-only and writes no files; subagents return results to the supervisor, who keeps them in the conversation.
- Gather means reading the as-built code, docs and tests; think means judging it against the aspect and level.
- Subagents return **findings** in the format below and **draft questions** (decision, context, options, recommendation); they never ask the user.

## Phases

### 1. Intake

1. Restate the scope in one paragraph and fix the **project root**.
2. Ask only what blocks the assessment with `ask-questions`: what the scope is, what prompted the assessment, what is out of scope.
3. Spawn one `standard` per area of the scope for a read-only survey (Authorization block: project root, read-only, no writes, no commit): project conventions, prior decisions.

### 2. As-built recovery

1. Spawn `standard` scouts in parallel, one per area, returning a fact sheet: what it does, boundaries, components, data, interfaces, flows, tests, with `file:line` paths. Facts only, no judgment.
2. A failed or thin sheet is re-gathered, not guessed.
3. Spawn one `standard` to merge the sheets into a single as-built picture. No assessment starts before it exists.

### 3. Aspect decomposition

1. Take candidate aspects from the catalogue and the as-built picture.
2. Drop untouched aspects with a one-line reason; set importance, complexity, tier and dependencies for the rest.
3. Confirm the list (drops, importance, tiers) with one `ask-questions` question; recommended option: proceed as listed.

### 4. Assessment per level

Repeat per level, top-down.

1. Spawn `standard` gather tasks for the level's aspects in parallel (extra evidence beyond the as-built picture only).
2. Spawn one thinker per aspect with items at this level (parallel where independent), passing: scope, project root, as-built picture, fact sheets, findings and decisions from higher levels, the aspect's scope limited to this level. A `minor` aspect is folded into the closest related aspect's thinker.
3. Each thinker returns findings in the **finding format** below. A finding with no problem is not reported; a problem with one clearly dominant improvement records it as **proposed**, not asked.
4. A new aspect reported by a thinker goes through phase 3 step 2 and is assessed at its levels.
5. Genuine forks in the improvement direction (directions of similar value) are asked with `ask-questions` following the `propose-plan` rules: one level at a time, aspect by aspect, upstream first, up to 4 related questions per call, a recommended option listed first with its reason. Level 3 improvements default to proposed.
6. After each round, the supervisor restates the answers in chat as agreed decisions. An answer that changes a downstream finding or a level assignment re-spawns the affected thinkers.

Finding format returned by a thinker:

```
Id: <aspect-prefix>-<n>
Level: <1 | 2 | 3>
Aspect: <name>
Severity: <critical | high | medium | low | info>
Evidence: <what was observed, with file:line>
Impact: <consequence for users, maintainers, performance, security>
Improvement (only when warranted): <concrete change>, effort <S|M|L>, risk <low|medium|high>
Directions (only when similar value):
  - <id> <option>: <benefit> / <cost> / <risk>
Recommendation: <direction id or the improvement>, <reason in one sentence>
Questions: <decision | context | options | recommended option>
Cross-aspect impact: <aspects affected, level reassignments, new aspects missing from the list>
Gather requests: <what is missing>
```

### 5. Consolidation

1. Spawn `standard` to merge findings into the report content and run a consistency pass: duplicates, contradictions, findings without evidence, severity ranking, uncovered aspects, open questions left.
2. For a large or high-risk scope, spawn `expert` to review the consolidated report against the checklist below; its findings go back through phase 4.
3. Present the findings report in chat, with a short summary of the main findings and agreed improvements. Wait for approval or changes.

### 6. Handoff

1. Report status is `approved`.
2. When improvements were agreed, present the agreed-improvements summary in chat in the `propose-plan` brief structure (Plan brief format section there): Goal and scope from the assessment, a Level map, a Decision log with a Level column (one row per agreed improvement, Source `user` or `proposed-confirmed`) and the supporting finding ids and evidence.
3. Subagents cannot persist anything, so the supervisor keeps findings and agreed decisions complete and self-contained in chat: id, level, aspect, severity, evidence `file:line`, agreed direction. `create-plan` consumes them from the conversation.
4. On request or when improvements were agreed, point the user to `create-plan`, which takes the findings and agreements from this conversation as locked decisions. This skill does not invoke it. Without agreed improvements, stop after the report.

## Report format

Delivered as chat messages only; no file is written.

```markdown
# <Scope title>

**Project root:** `/absolute/path`
**Status:** draft | approved

## Scope and trigger
What was assessed, what prompted it, out of scope.

## As-built summary
What it does, boundaries, components, flows.

## Aspects
| Aspect | Importance | Tier used | Status | Summary |
| --- | --- | --- | --- | --- |

## Findings
| ID | Level | Aspect | Severity | Finding | Evidence | Impact | Improvement | Effort / risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Agreed improvements
| ID | Level | Aspect | Improvement | Alternatives rejected | Reason | Source |
| --- | --- | --- | --- | --- | --- | --- |

## Dropped aspects
Aspect and one-line reason.

## Risks and open questions
Only items the user explicitly deferred.

## Evidence
Fact-sheet summaries with paths.
```

## Completeness checklist

Before status `approved`:

- The as-built picture was recovered before any judgment.
- Every kept aspect is assessed at each of its levels or has a stated no-finding reason.
- Every finding has a level, severity and `file:line` evidence, and was assessed after the level above.
- Every proposed improvement has effort and risk and answers a stated impact.
- No open direction of similar value remains; every user question had a recommendation and a recorded answer.
- No duplicate or contradictory findings; severities ranked consistently.
- No file was created, edited or deleted anywhere.
- Findings and agreed decisions are complete and self-contained in chat.

## Spawning

Prompts follow `propose-plan` Spawning, plus:

- Every prompt carries the constraint: add no comments, JSDoc or documentation.
- Every prompt carries an Authorization block. Every agent: project root, **read-only**, no writes of any kind, no commit.
- Thinker prompts include the as-built picture, fact sheets, higher-level findings and decisions, and the finding format.

## Anti-patterns

- Writing, editing or deleting any file, including notes, or letting a subagent do so.
- Judging before the as-built picture is recovered.
- A finding without `file:line` evidence.
- Asking lower-level questions before the level above is settled.
- Proposing improvements for non-issues, or reporting style preferences as findings.
- Asking a question without a recommendation, or one whose options are not of similar value.
- Invoking `create-plan` from this skill, or pointing to it before the report is `approved`.
- Leaving findings or agreed decisions incomplete in chat.
- Gathering data in the main thread or with a high tier.
