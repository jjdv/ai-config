---
name: sequential-implementation
description: >-
  Execute a plan sequentially as a thin executor, running one task at a time
  with the task's agent. Supports .local plan files (with create-plan structure)
  or plans pasted in the prompt. Use when the user asks to implement, execute,
  or continue a plan step-by-step.
disable-model-invocation: true
---

# Sequential implementation

{{block:tool-note}}

Act as a **thin executor**: do not implement task work yourself unless the user explicitly overrides. Run each task with the task's **Agent** (default `standard`), then **update progress as the last action** before starting the next task.

**Keep going through open tasks** until a stop condition applies — do not stop after each task to ask whether to continue.

## Plan source

| Mode | When | Source |
| --- | --- | --- |
| **File** | User gives a plan path (e.g. `.local/date-input-migration-plan.md`) | Read from disk; validate structure (see Pre-flight) |
| **Pasted** | User pastes plan in the prompt | Use only what is pasted; do not read plan files unless re-pasted |

For file-based plans that fail validation, **re-sync with `create-plan`** or run **`check-plan`** on the plan path — do not improvise structure. If the supervisor cannot fix without user input, report gap list from checklist.

## Pre-flight validation (file-based plans)

Read the plan. **Do not delegate** until all checks pass. Prefer running **`check-plan <plan-path>`** first; its checklist matches pre-flight below.

| Check | Requirement |
| --- | --- |
| Plan exists | File readable at given path under project root |
| Frontmatter | `plan: true` and `version` present |
| Progress summary | Table with phases and status |
| Phases | At least one `### Phase N` with a task table |
| Task IDs | Every task has `<phase>.<sequence>` ID |
| Implementation order | Numbered list of task IDs |
| Task detail links | Linked `.local/<slug>/tasks/<id>.md` files exist when Details column is not `—` (paths relative to plan folder or absolute from repo root) |
| Plan folder | Entry point at `.local/<slug>-plan.md`; supporting files under `.local/<slug>/tasks/` — flag flat `.local/tasks/` as legacy/collision risk |
| Initiative refs | Linked `.local/<initiative>/` files exist when plan references them |
| Runnable next task | At least one task not `✅ Complete` in **Implementation order**, or report plan complete |
| Order hygiene | **Implementation order** lists **only** open task IDs — if any `✅` ID remains, re-sync plan per **`create-plan`** checklist before delegating |
| Context references | Linked paths exist; purposes match disk (flag stale “to update” or missing target/current banner on migrations) |
| Plan maintenance | **Plan maintenance** section present with per-task update rules |
| Task-fit | **Next open task** (and linked task spec) passes **Task-fit checklist** in **`create-plan`** — see **Oversized tasks** below |
| Agent | Each open task has an Agent (absent = `standard`); every non-`standard` Agent has a user-agreed row in **Agent approvals** — otherwise do not delegate it, report and require **`create-plan`** |

Flag **blocked** tasks (⏸ or open question blocking that ID) to the user before delegating.

### Oversized tasks (mandatory)

Before **every** delegation, evaluate the **next open task** against the **Task-fit checklist** in **`create-plan`** (read task spec when linked).

| Result | Supervisor action |
| --- | --- |
| **Pass** | Delegate to the task's Agent as usual |
| **Fail** | **Do not delegate.** Report failing criteria and task ID(s). Require **`create-plan`** (or user-approved split): new task IDs, updated **Implementation order**, task files, **Fresh chat handoff**. Re-run **`check-plan`** before resuming |
| **Borderline** (one criterion marginal) | Prefer split if marginal on **One session** or **Bounded scope**; otherwise delegate and watch for follow-up spawn — if follow-up needed for same ID, treat as fail and split before next plan task |

If the task's Agent **cannot finish** the task without a follow-up for the **same ID** (not lint/typecheck fix, and not the single escalation below), stop after that task, mark plan for **create-plan** split, and do not continue **Implementation order** until the plan is re-synced.

Pasted plans without task files: apply the same checklist from inline task text in the plan.

### Project conventions (conditional)

Resolve **project root** from the plan (`**Project root:**` line, plan path parent, or workspace). Then check whether this file exists:

`<project-root>/.agents/skills/project-best-practices/SKILL.md`

| Exists | Supervisor | Implementation `prompt` |
| --- | --- | --- |
| **Yes** | Treat **project-best-practices** as mandatory for every delegation. All code for that repo **must comply** with the skill (placement, naming, styling, CMS/blocks, and anything else it requires). Reject a “done” that ignores it — follow-up implementation spawn before the next plan task. | Include a **Conventions** block (see delegation template). Require the task's agent to **write code in compliance**, not only to read the skill. |
| **No** | Do not mention project-best-practices | Omit **Conventions** — use `.context/` paths only if the plan lists them |

This check is **per project root**, not global. Plans under `.local/` are project-specific; the global **sequential-implementation** skill stays conditional on `.agents/` in that root. Do not invent a stand-in skill when the file is missing.

### Code quality (`code` user rule)

When a task edits **source files** (any language the **code** user rule covers), the **Conventions** block must also require the **code** user rule checklist before marking done: intention-revealing names, small units, KISS/DRY/SOLID-lite, Don't Make Me Think, and project conventions (project-best-practices when present). The supervisor verifies source diffs for drive-by churn and obvious rule violations — not only architectural compliance.

For **pasted** plans: if progress tracking is missing, add it before starting (see Plan templates).

## Progress tracking

Progress lives **in the plan file** (file mode) or **in the plan text you maintain in replies** (pasted mode).

1. Check whether progress tracking exists (checkboxes, status column, or equivalent).
2. If missing, **add it** before starting — pick the smallest template below that fits.
3. After each task, **update the plan** (file on disk or full updated plan in your reply).
4. Never rely on out-of-band status; the plan is the source of truth.

Follow the plan's **Plan maintenance** section when present. Default checklist after each task:

1. Set task row in **Phases** to `✅ Complete` (or `⏸ Blocked` with reason).
2. Sync linked `.local/<slug>/tasks/<id>.md` `**Status:**` line if present (derive `<slug>` from plan filename `<slug>-plan.md` or frontmatter `slug`).
3. Recompute **Progress summary** phase rows.
4. Update header `**Last updated:**` and frontmatter `last_updated`.
5. Set frontmatter `status: in_progress` on first completion; `status: complete` when all tasks done.
6. Update **Open questions**; add new rows to **Context references** if the task created files future work needs.

**Never** start the next delegation before the plan is updated.

## Delegating tasks

Run every task with the **Agent** in its **Phases** row (default `standard`). Never pick a heavier agent yourself:

```text
{{tool:spawn-agent}}(
  <the task's Agent>,
  run_in_background=false,
  description="…",
  prompt="…"
)
```

### Model (mandatory)

{{block:spawn-rule}}

### Spawn hygiene

- **`run_in_background: false`** — always foreground; avoids extra per-edit approval churn.
- Put task-specific instructions in `prompt` — subagents do not see the parent chat.
- Keep `prompt` self-contained and small: pass only the task spec (or its path), the Authorization and Conventions blocks, and the paths the task needs — never the plan body, chat history or other tasks' details. Require a short return: success/failure, key paths, verification run, blockers, and whether user input or a follow-up is needed.
- After the subagent finishes, verify deliverables; do not assume success from the spawn alone. Review the diff for redundant comments (comments that restate the code) and have them removed before marking the task done. When `project-best-practices` exists, verify the diff complies with it. When the task touched source files, spot-check the **code** user rule checklist (naming, unit size, no unrelated churn).

### Escalation

- A `standard` task that fails (verification fails, acceptance unmet, or the agent reports it cannot proceed) is re-run **once** as `senior`, with the task spec, the failure report and the paths involved.
- A task whose approved Agent is already `senior` or heavier is not re-run automatically.
- Any further escalation (`senior` failure, or moving to `principal`/`expert`) needs the user's approval after a brief justification — pause per the decision rule below.
- If the re-run still needs a follow-up for the same ID, treat the task as oversized per **Oversized tasks**.

### File-based delegation prompt

Include only what the subagent needs. Run the **project conventions** check before building the prompt.

```markdown
Task ID: <id>
Title: <summary from plan>
Plan: <path to plan> (read-only — do not edit)
Task spec: <path to .local/<slug>/tasks/<id>.md if linked, else inline summary>
Reference: <paths to .local/<slug>/ decisions, architecture, etc. if task-relevant>
Conventions: <only when `.agents/skills/project-best-practices/SKILL.md` exists under project root — mandatory read `.agents/skills/project-best-practices/SKILL.md` first; then open task-relevant `references/` and `docs/` paths from the task spec and plan Context references (e.g. `references/cms-blocks.md`, `references/website-structure.md`, `references/styling.md`, `references/placement.md`). For Sanity work, also load sibling skills listed in that SKILL.md. **Write all code in compliance with that skill**; treating it as optional reading is a failed task. When editing source files, also apply the **code** user rule and run its checklist before marking done.>
Context: <paths to `.context/` files when the plan lists them — omit when none>
Acceptance criteria: <from task file or infer from summary>
Out of scope: <explicit boundaries>
Comments: add no comments or doc comments unless the task spec requires them; none that restate the code.
Return: summary, artifacts (paths/diffs), blockers
Do not update the plan — the supervisor updates it after you finish.
```

### Authorization block (every prompt)

**Every `prompt` must include** an `## Authorization` block (copy/adapt):

```markdown
## Authorization

**Project root:** `/absolute/path/to/repo`

The user already approved this implementation task. You may **read and write any file under the project root** (source, tests, `.local/` plan docs, READMEs) without asking for per-file permission. Do not edit outside this tree. Do not commit unless asked.
```

When the plan has § **Autonomy & authorization**, copy that plan’s **Authorization** block instead of this generic one (pre-approved ops, scope boundary, escalation rules).

After a successful task with no stop condition, **delegate the next open plan task immediately** in the same turn when possible — do not end with "shall I continue?" or wait for confirmation.

## After a task completes

When a task finishes, decide the next action using **only** the result — never habitually pause after one task.

### Decision rule (apply in order)

1. **Pause** — if **any extra input from the user** is required per the plan § **User escalation required** (or subagent `ESCALATE` / `ESCALATE: global-scope`). **Not** because a task title says “user gate” when plan auto-decisions apply.
2. **Escalate or follow up** — if the task failed, apply **Escalation** (one `senior` re-run of a failed `standard` task, no user input needed). If a **follow-up** is needed that does **not** require user input (e.g. fix typecheck/lint from the same task), run a separate subagent with the task's Agent, then re-apply this decision rule.
3. **Next plan task** — **otherwise**, go to the **next open task** in the plan. This is the **default** when the task succeeded with no blockers.

Walk tasks in plan order; the first still-open item is always next.

### Stop conditions (only reasons to pause)

- User input required (including approval for escalation beyond the single `senior` re-run)
- Subagent reports an unresolvable blocker without user action
- All plan tasks are complete
- The user **explicitly** limited scope (e.g. "only T01", "stop after this task")

**Not** a stop condition: one task completed successfully with no blockers.

### Anti-patterns (forbidden)

- Asking "Want me to continue with T02?" after T01 succeeded
- Stopping because the pasted plan says "one task per session" — when **this skill** is active, **these continuation rules override** unless the user also said to limit scope
- Starting the next plan task in the parent context instead of delegating to its Agent
- Spawning subagents in any way that breaks the model rule above
- Choosing a non-`standard` Agent not recorded in the plan, or escalating beyond the single `senior` re-run without user approval
- Passing the full plan or chat history into a task prompt
- Omitting the **Conventions** block when `project-best-practices` exists in the project's `.agents/skills/`
- Shipping code that does not **comply** with `project-best-practices` when that skill exists in the project root
- Shipping source edits without applying the **code** user rule checklist when the task touched source files
- Delegating an oversized task instead of pausing for **`create-plan`** split
- Continuing **Implementation order** after a task needed a second implementation spawn for the same ID without re-splitting the plan
- Omitting the plan **Authorization** block when § Autonomy is present

## Supervisor loop

Repeat until a stop condition applies:

```
pick next task → build prompt → run task's Agent → review result (diff, redundant comments) → update plan → (pause | escalate/follow-up | next task)
```

- **Sequential only** — one task at a time unless the user explicitly requests parallel runs.
- **No plan edits by subagent** — only the supervisor updates the plan.
- **Preserve parent context** — rely on subagent summaries, not full task file dumps.

Brief the user on progress after each task.

## Subagent ↔ user relay

Subagents cannot talk to the user directly. The **supervisor** (you) is the only bridge.

### When a subagent returns questions

1. **Surface** the question(s) to the user — what decision is needed.
2. **Wait** for the user's answer. Do not guess product or policy choices.
3. **Resume** with a new delegation to the task's Agent that includes the user's answer.
4. Mark the plan task `⏸ Blocked` with the question in **Open questions** until answered (file mode).

### When you need user input (supervisor)

- Ask before delegating if ambiguity would change the task outcome.
- During auto-continuation, **pause the plan** (decision rule bullet 1) when user input is required — including questions relayed from a subagent.

### When the user answers mid-plan

- Update **Open questions** and unblock the affected task row before the next delegation.

## When the plan is not ready

Reply with a short gap list, for example:

- Missing `Implementation order`
- Task `2.3` links to `tasks/2.3.md` but file not found under the plan folder (expected `.local/<slug>/tasks/2.3.md`)
- No task IDs in phase tables

Suggest: *Restructure with `create-plan`, run `check-plan` on the plan path, then re-run with the plan path.*

## Plan templates

Use or adapt when adding missing progress tracking to pasted plans.

### Template A — linear checklist

```markdown
# [Plan title]

**Last updated:** YYYY-MM-DD (next: **T02**)

## Tasks (in order)

| ID | Task | Status |
|----|------|--------|
| T01 | … | [x] |
| T02 | … | [ ] |
```

### Template B — scoped plan with progress table

```markdown
# [Plan title]

**Last updated:** YYYY-MM-DD (next: **S2-T01**)

## Progress

| Order | Scope | Theme | Open | Done | Next open | Tasks |
|------:|-------|-------|------|------|-----------|-------|
| 1 | S1 | … | 0 | 3 | — | T01 [x], T02 [x] |
| 2 | S2 | … | 2 | 0 | S2-T01 | T01 [ ], T02 [ ] |
```

### Template C — single task block

```markdown
# [Plan title]

**Last updated:** YYYY-MM-DD

## Current task

**ID:** T01 · **Status:** [ ] in progress | [x] done

### Goal
…

### Acceptance
- [ ] …
```

When extending Template C into a multi-task plan, migrate to Template A or B before starting T02.

## Example invocation (user)

> Run sequential implementation on `.local/date-input-migration-plan.md`

> Implement this plan step by step: [pasted plan]
