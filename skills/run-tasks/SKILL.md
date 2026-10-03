---
name: run-tasks
description: >-
  Split a large goal or task list into composer-sized subtasks and delegate each
  to a dedicated composer subagent — sequentially when scope overlaps, in parallel
  when completely separate. Use when the user asks to run tasks, execute a backlog,
  batch work via subagents, or /run-tasks. Not for formal .local plan files —
  use sequential-implementation instead.
disable-model-invocation: true
---

# Run tasks

> **Tool mapping (Cursor / Claude Code):** subagent spawn `Task(subagent_type=…, model=…)` → `Agent(subagent_type=…)`; `AskQuestion` → `AskUserQuestion`; `@Browser` / `cursor-ide-browser` → Claude browser tools; `Write`/`StrReplace`/`Shell` → `Write`/`Edit`/`Bash`. The `composer` agent exists in both tools (Cursor runs `composer-2.5` — always pass `model="composer-2.5"`; in Claude Code it is pinned to `sonnet` — do not pass `model`). User skills live in `~/.agents/skills/` (Cursor) or `~/.claude/skills/` (Claude Code).

Act as **supervisor**: decompose work into **one composer spawn per subtask**, then delegate. Do not implement task work in the main thread unless the user explicitly overrides.

## When to use

- User gives a **task list**, backlog, or bullet checklist to execute
- One **large goal** that needs splitting before delegation
- User says **run tasks**, **execute these**, **batch via subagents**, or `/run-tasks`
- Ad-hoc multi-step work **without** a formal `.local/*-plan.md` file

## When not to use

| Situation | Use instead |
| --- | --- |
| Formal plan at `.local/<slug>-plan.md` with task IDs | **`sequential-implementation`** |
| Open-ended chat; user steers every chunk | **`long-chat-mode`** |
| Need a durable plan file first | **`create-plan`** → then **`sequential-implementation`** |

## Workflow

```
intake → decompose → schedule (parallel vs sequential) → composer per subtask → report → next batch or stop
```

### 1 — Intake

Accept input as:

- Pasted bullet/numbered list
- Inline goals in the user message
- A short prose description of a large task

If scope or acceptance criteria are ambiguous, ask **one** focused question before decomposing.

### 2 — Decompose (mandatory)

Split until **every** subtask fits **one** `composer` spawn. Apply the **Composer-fit checklist** in **`create-plan`** (read that section when splitting — do not delegate oversized chunks).

Quick fail signals → split further:

- Multiple unrelated outcomes joined with "and"
- Investigate/spike **and** implementation in one chunk
- >8 primary paths or 3+ unrelated subsystems
- Later subtask depends on an earlier subtask's output

Assign each subtask a short **ID** (`T1`, `T2`, … or reuse plan IDs if pasted from a plan).

Present the split to the user when non-obvious (brief numbered list).

### 3 — Schedule parallel vs sequential

| Mode | When |
| --- | --- |
| **Sequential** (default) | Subtasks **may** touch the same files/dirs/modules; explicit dependency (B needs A); uncertain overlap |
| **Parallel** (same turn) | **No** path overlap, **no** cross-task dependency, conflicting edits unlikely |

When in doubt → **sequential**.

**Dependency batches:** group subtasks into waves. Run all tasks in a wave in parallel only when every pair in that wave is safe; wait for the wave to finish before the next.

### 4 — Delegate each subtask

Every subtask → **one** `composer` spawn:

```text
Task(
  subagent_type="composer",
  model="composer-2.5",
  run_in_background=false,
  description="…",
  prompt="…"
)
```

**Model (mandatory):** always `model="composer-2.5"`. Never fast variants; never omit `model`.

**Parallel spawns:** launch all tasks in the same wave in **one** parent message (multiple `Task` calls). **Sequential:** wait for completion before the next spawn.

### 5 — Prompt template

Each `prompt` is self-contained — subagents do not see the parent chat.

```markdown
## Subtask

ID: <T1>
Title: <one-line summary>
Goal: <what done looks like>
In scope: <paths, surfaces, behaviors>
Out of scope: <explicit boundaries>
Acceptance: <checklist>
Prior results: <summary from completed deps, if any>

## Authorization

**Project root:** `/absolute/path/to/repo`

The user approved this subtask. You may read and write any file under the project root without per-file permission. Do not edit outside this tree. Do not commit unless asked.

## Conventions

<Only when `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists: mandatory read and comply; include task-relevant references/.context paths from the user message.>

## Return

Summary, paths touched, verification run, blockers, and **explicit questions for the user** if blocked.
```

### 6 — After each subtask (or wave)

1. Verify deliverables — do not assume success from the spawn alone.
2. Mark the subtask done in the **task list** you maintain in replies.
3. Surface subagent **questions** to the user; wait for answers before dependent work.
4. Decide next action (see **Continuation**).

## Task list tracking

Maintain a lightweight checklist in your replies — no plan file required unless the user asks.

```markdown
## Tasks

- [x] T1 — …
- [ ] T2 — …
- [ ] T3 — …
```

Update after every completed subtask or wave.

## Continuation

| User said | Supervisor behavior |
| --- | --- |
| Nothing / single task | Run only the requested scope; report and stop |
| "Run all" / "continue through the list" / "don't stop between tasks" | After each sequential subtask (or wave), **immediately** start the next — no "shall I continue?" |
| "Stop after T2" | Hard stop after that ID |
| Changes scope mid-flight | Re-decompose; adjust remaining schedule |

**Default when running a list:** continue through remaining subtasks in schedule order unless a **stop condition** applies.

### Stop conditions

- User input required (product choice, unclear acceptance)
- Unresolvable blocker after relaying to the user
- All subtasks complete
- User explicitly limited scope

**Not** a stop condition: one subtask succeeded with no blockers while "run all" is active.

## Subagent ↔ user relay

Subagents cannot talk to the user. You are the only bridge.

1. Surface questions clearly — say what decision is needed.
2. **Wait** for the answer; do not guess policy or product choices.
3. Resume with a **new** spawn that includes the user's answer.

## Relation to other skills

| Skill | Role |
| --- | --- |
| **`create-plan`** | Composer-fit rules and task sizing — read when decomposing |
| **`sequential-implementation`** | Formal plan files with IDs, linked task specs, plan maintenance |
| **`long-chat-mode`** | Interactive supervisor; pauses between chunks by default |

`run-tasks` is the **lightweight** path: task lists and large goals without plan-file ceremony.

## Anti-patterns

- One mega `composer` prompt for an entire multi-area goal
- Parallel spawns when subtasks may edit the same files
- Delegating a subtask that fails **Composer-fit** without splitting first
- Implementing subtask work in the main thread
- Omitting `model="composer-2.5"` or using fast composer variants
- Asking "continue?" after each task when the user said run all
- Using `run-tasks` for `.local/*-plan.md` execution (use **`sequential-implementation`**)
- Answering subagent product questions without asking the user

## Example invocations

> /run-tasks — fix these three unrelated bugs: [list]

> /run-tasks — implement auth middleware + add login page + write tests *(split → sequential if shared auth module)*

> /run-tasks — update README in repo A and bump version in repo B *(parallel if truly isolated)*
