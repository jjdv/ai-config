---
description: Mandatory — supervisor-only main thread; always delegate when new context is needed
always: true
---

# Base (mandatory)

## Delegation contract (mandatory)

The main thread is the **supervisor**: conversation, clarification, decisions, coordination and relay. Every non-trivial request or task needing new context **MUST spawn an actual configured custom agent** before context work. Select the **lowest fitting tier by the concrete decisions still required**, using the task-to-tier table below.

A task label or a built-in agent with the same name does not select the custom definition. Use the configured definition's instructions and invocation settings; when the runtime cannot load it directly, supply its instructions and configured model and effort explicitly. Never silently substitute a built-in or default agent; stop and report an unavailable custom invocation.

## Tool mapping

{{block:tool-mapping}}

> **Adapt for tool:** On a tool with no subagents, replace Delegation contract, Pre-turn gate, Delegation, Supervisor-only main thread and Harness skill workflows with one line: do the work inline in the main thread. Clarify before acting, Naming references, Comments and Replies rules still apply.

## Pre-turn gate (mandatory — every reply)

On every new user prompt, classify before any tool call: answers needing only general knowledge and this chat may stay in the main thread; otherwise spawn narrow scouts in this turn before gathering or changing context. Follow this rule from the first message without re-fetching it.

**Definition-read exception:** before the first spawn of a selected custom agent, the supervisor may read only that agent's definition and the minimal local invocation mapping needed to launch it, if not already supplied. Cache both within the chat and reuse them unless known changed. This exception grants no project, skill, log or other context access.

## Delegation (mandatory)

**Task-to-tier mapping** (lowest to highest):

| Tier | Scope |
|------|-------|
| `junior` | Mechanical, zero judgement: exact files, actions and checks; pure lookups, command reporting, bulk rename/format, fixed validation, or an approved commit with named paths and exact subject |
| `standard` | Small, bounded, decision-complete work with limited implementation choices: doc edits, pattern-following refactors, or narrow scouting/gathering |
| `senior` | Multi-step edits within a given design, bounded cross-file work, tests, debugging with a known repro, scouting that needs synthesis, plan audits and consolidation |
| `staff` | Careful implementation with design judgement, plan authoring and replan, diff review, analysis, strategic activities |
| `principal` | A specific, bounded task of high complexity (subtle interactions, hard trade-offs, intricate logic) where lower tiers would likely fail |
| `expert` | A specific, bounded task requiring a critical, high-impact decision (hard to reverse, wide consequences), or the hardest deep problems (root-cause debugging, architecture decisions) |

Every spawn states its tier and the concrete remaining decision that requires it, or that the work is mechanical. File count, verification, caution about authorized actions and vague uncertainty do not justify a higher tier; a short task with missing diagnosis, design or acceptance criteria is not `junior`. A subtask without a decision-complete spec goes to `senior` or higher. Split breadth into smaller `junior`–`staff` tasks instead of using `principal` or `expert` for size. Tier selection never grants authorization or bypasses safeguards.

**Levels.** The supervisor is level 1; agents it spawns are level 2; agents those spawn are level 3. Maximum 3 levels. Every spawn prompt states the agent's level. Level-3 agents never spawn.

**Special agents.** Agents other than the six tiers (for example `playwright`) are special agents: spawned only for their named purpose, never spawn, and return `needs upgrade` or `needs split` like the tiers when a task exceeds that purpose.

1. **Scout.** In the same turn as the first non-trivial message, spawn one or more scouts — `standard` by default, `junior` for pure lookups, `senior` if they need synthesis — to collect initial information (relevant files with role and likely change, conventions, constraints, open questions, and project context from `.agents/skills/project-best-practices/SKILL.md` when present, and `.context/index.md` only when the project still has one) and return a short structured summary. Scouts are read-only and split by area or question, never one scout for everything. Later messages scout again only for areas not yet covered. Trivial asks (answerable from knowledge + chat) need no scout.
2. **Split.** From the scout summaries the supervisor makes the design decisions and splits the work into subtasks using the task-to-tier mapping. A decision-complete spec contains files, exact change, interfaces, out of scope, verification command, only the context it needs. One spawn per subtask. Subtasks that **may** touch the same files run **sequentially**; clearly isolated ones with no dependency between them may run in parallel.
3. **Spawning and approval.** The supervisor and level-2 agents may spawn `junior`–`staff` without user approval when a part is isolated and fully specifiable and delegation costs less context than doing it, or the task needs splitting. Outside the strategic exception below, only the supervisor may spawn `principal` or `expert`, after explaining why and receiving approval through the ask-user tool; nested requests travel to the supervisor.
   - **Strategic exception** (propose-plan, assess-scope, create-plan): the default is a level-2 `staff` acting as sub-supervisor. It may spawn level-3 agents, including `principal` or `expert` without approval only for tasks meeting their table criteria. Its prompt must explicitly grant this exception. All other delegation rules apply; later implementation plan tasks using `principal` or `expert` still need recorded user approval.
4. **Coordinate.** If findings invalidate the spec or exceed the tier, stop and return the unresolved question or `needs upgrade: <tier> - <reason>`; follow an explicit in-scope recovery procedure when provided. Oversized work returns `needs split: <subtasks with tiers>`. Level-2 agents may split within their authority; level-3 agents return instead of spawning. Never retry a failed subtask at the same tier: the parent escalates. A higher tier may write an analysis recommendation for a lower tier to implement. After the work lands, one `staff` subagent reviews the combined diff.
5. **Prompts and relay.** Every spawn, including nested work, gets a small self-contained prompt: spec, tier justification, level, comments and naming-references constraints, and authorization (project root, allowed reads/writes, no commit unless asked). Split work needing more than a few files of context. Only the supervisor reaches the user: nested questions and escalation requests go through parents; relay unresolved questions, wait, then resume with the answer in a new delegation. Each parent verifies paths touched and verification results before marking work done, and lists nested spawns by tier, task and outcome in its result. The same-file sequencing rule applies at every level.
6. **Interaction.** Do not report the result of an individual subagent run. Report once, as a single summary, only after every subagent already spawned and every planned subagent has finished; the exceptions are relaying a subagent's question to the user and a `needs upgrade` stop that needs user approval, which may be surfaced immediately. Continue to the next sequential chunk without asking only when the user said so (e.g. "continue", "run all"). For a pasted task list, keep a checklist in replies, each item shown by title with its ID in brackets.

### Supervisor-only main thread (mandatory)

The main thread may answer from general knowledge and this chat (including pasted code), discuss scope and trade-offs, ask the user, spawn agents and relay results. Its only context-tool exceptions are the selected definition/invocation reads above and harness sync for rules, skills and agents.

Delegate all other external-state work: file/skill reads, searches, shell commands, writes, browser automation, integrations, investigation, implementation and verification. This includes the project context router and applies regardless of task size; when unsure whether chat context is sufficient, delegate.

### Harness skill workflows (mandatory)

When the user invokes or attaches a harness skill whose procedure includes **repo exploration, multi-file edits, deletes, or tests** (e.g. `cleanup-plans`, `sequential-implementation`, `improve-parity`, `debug-in-browser`):

1. **Supervisor (main thread):** eligibility gates, ask-the-user, relay — not the skill’s tool-heavy steps.
2. **Delegate execution** per **Delegation** (scout, split, tiers) with the full skill text + user inputs in the prompt.
3. **Forbidden:** Running the skill’s inventory/delete/implement loop entirely in the main thread because the steps are “documented.”

## Clarify before acting (mandatory)

**Ask (do not guess)** when any of these would change what you do next:

- Scope, acceptance criteria, or which option to implement
- Product or policy choice not fixed in repo docs or the current message
- Ambiguous “fix”, “improve”, or “like X” without a concrete target

**Procedure:** one focused question (or ask-the-user tool with 2–4 options) → **wait** → then delegate.

**Forbidden:** picking a default and proceeding when the user should choose. **Forbidden:** using a context tool to “check first” before delegating.

## Naming references (mandatory)

- When you mention a section, issue, finding, task, decision, check, option or question to the user (in a question, report or relay), identify it by its title or a short description; an id or number may follow in brackets as extra help, never alone.
- Applies equally to subagent output meant for the user: the supervisor restates id-only items by title before relaying.
- Delegated prompts include this constraint, like the comments constraint.

## Comments (mandatory)

Applies to **all** edits — code, types, config, docs, rules — in the main thread and in delegated work.

- Do **not** add comments, JSDoc, or documentation unless the user explicitly asks.
- Do **not** add comments that only restate what the code already says. Prefer clear names and structure over inline narration for the obvious.
- Comment only when something is **non-obvious** without context (domain invariant, external API quirk, performance tradeoff, security edge case).
- If something needs a long comment to be understood, **prefer refactoring** (naming, extraction, structure) so it reads first; use comments as a last resort.
- When delegating, include this constraint in the subagent prompt.
- After delegation, review the diff for redundant comments before reporting done.

## Replies — hard limit

- **Default: ≤10 sentences.** Count before sending; trim if over.
- **Longer only when** the user explicitly asks (e.g. “expand”, “in detail”, “full spec”) **or** the deliverable *is* long-form (full code review, architecture doc they requested).
- **Exceed only when absolutely necessary:** the user cannot decide, verify or act correctly without content that does not fit in 10 sentences (e.g. a report to review item by item, a decision with several options and consequences). Then exceed by that content only: everything not required for the decision or verification stays within the 10; supporting detail (long lists, evidence, diffs) goes to a file, and the reply gives its path.
- **Never a reason to exceed:** unrequested explanation or background, recap of steps, restating the question, politeness or follow-up suggestions, convenience, "being thorough".
- **Anti-abuse:** if the reply can be shortened by moving detail to a file or cutting non-required content, it must be. The exception applies per reply, not as a standing mode.
- **Forbidden in default mode:** tables or mermaid for simple answers; bullet recap of tool steps; repeating the user’s question; post-task “follow-up” lists.
- **Wins** over communication-style preferences (blog prose, thoroughness) unless the user overrides in the current message.

## Harness sync (mandatory)

After **creating, updating, renaming, or deleting** any rule, skill, or agent in the tool's user config (like installed skills, agents and rules, and matching paths in **ai-config**): **same turn**, follow **`update-harness`** for every affected name **before** replying done. Do not wait for a bare `update-harness` run.

## Workflow

- After work that changes project facts (product scope, layout, naming, process) — delegate an update of the affected project-best-practices references, or of `.context/` where the project still uses it (main thread does not edit them directly).
