---
name: create-plan
description: >-
  Create or update implementation plans for sequential-implementation: small
  tasks (one outcome, bounded scope, acceptance check) with a decided Agent each,
  a Decisions section for cross-task choices, notes/ for scout findings, and
  check-plan as the single owner of readiness rules (read before authoring, run
  as the final audit until READY). Authoring is delegated (scouts at the lowest
  fitting tier, senior author). Includes replan mode when sequential-implementation reports a plan
  issue. Use when drafting a plan, extending phases, re-syncing after completed
  tasks, replanning, or before telling the user to run sequential-implementation.
  Author plans to minimize user manual work and execution-time gates (gate budget,
  batched authoring questions, chat-first handoffs aligned with sequential-implementation).
  Also use for planning a website/page-group migration (routes, domains, blocks
  or page types from a reference repo; "plan a migration", "create migration
  plan", migration scope) — load references/migration-workflow.md.
---

# Create Plan

{{block:tool-note}}

Produce and maintain plans structured for **`sequential-implementation`**. A task is **small**: one outcome, bounded scope, an acceptance check, references to cross-task decisions and notes, and a decided Agent (the lowest tier whose scope fits, per the Delegation scope table). Tasks are not decision-complete specs: the supervisor running the plan writes the spec for each task at run time from the task, the **Decisions** section and the notes. Plan effort goes into making tasks small enough for low-tier Agents. A task whose spec cannot be written at run time from the task, the **Decisions** and the notes is a plan issue (**Replan mode**), not something the executor guesses.

**Contract:** A plan is **handoff-ready** only when `check-plan` returns `READY`, i.e. a **fresh chat** can run `{{tool:skill-prefix}}sequential-implementation <plan-path>` with **no prior context**.

## Readiness: check-plan is the single owner

`check-plan` owns every readiness rule (structure, linked artifacts, task fit, agents, notes, conditional and convention checks). This skill does not restate them.

- **Before authoring:** read `{{path:skills}}/check-plan/SKILL.md` and author so that every check passes.
- **At the end:** run `check-plan` as an audit (Workflow step 7) and fix reported gaps until `READY`.

## Execution

Main thread is a supervisor; plan authoring is delegated:

1. **Scouts:** `{{tool:spawn-agent}}` at the lowest tier per the Delegation scope table (`{{agent:standard}}` for narrow scouting), split by area (code, docs, conventions, external sources). Scouts are read-only for the repo; their only write is their own notes file under `.local/<slug>/notes/`, named in the authorization block of the spawn prompt.
2. **Author:** `{{tool:spawn-agent}}({{agent:senior}})` writes the plan, passing this skill's text, `check-plan`'s SKILL.md path, project root, scope, the brief path (when present) and the note paths. The author is the sub-supervisor for the activity: the spawn prompt explicitly grants it to spawn `junior` through `senior` without user approval for scouting and authoring subtasks, and `staff` through `expert` only for advisory analysis per the Delegation scope table, never for size or implementation.
3. **Questions:** a subagent cannot ask the user. It returns questions and proposed `principal` or `expert` Agents; the supervisor batches them into as few `{{tool:ask-user}}` rounds as possible (see **User-facing wording**), then re-spawns the author with the answers.
4. **Audit:** the supervisor runs the `check-plan` audit after the author returns (Workflow step 7).

Task execution later uses each task's **Agent**.

**User-facing wording:** Plan and task files keep ids for tracking; **chat** matches `sequential-implementation` (**User-facing reports**, **User actions**, **User-reported results**):

- **Reports and questions:** name tasks, decisions, sections and findings by title or short plain-language description; id in brackets only when titles need disambiguation (e.g. `Cache invalidation [D2]`, `Add cache layer [2.1]`), never by id alone. Question wording follows the `ask-questions` skill.
- **When the user must act:** **Operator handoff** and runbook text must be paste-ready for the executor as step-by-step chat instructions (what to do, in order, plus a one-line why). State that the user may **reply in chat only**; the executor updates the plan. The user is never required to edit plan or task files or to mirror **Implementation order**, **Agent approvals**, **Open questions**, or task **Status**.
- **Authoring:** batch open product or policy choices into one `{{tool:ask-user}}` round when possible; do not structure the plan so the user must confirm each phase or approve `staff`/`standard` work task by task.

**Migration planning** (website/page-group migration, "plan a migration of these pages"): read `references/migration-workflow.md` and follow it; it authors through this skill. Do not load it for other plans.

## Mandatory triggers (run this skill)

Read and follow this skill **before finishing** when **any** of:

| Trigger | Action |
| --- | --- |
| **New plan** | **Workflow (new plan)** |
| **Plan extended** (new phase/task, parity round, scope change) | **Plan update workflow**, then the audit |
| **Batch completion** (many tasks marked ✅ outside sequential-implementation) | **Out-of-band completion** |
| **Plan issue reported** by `sequential-implementation` | **Replan mode** |
| **Pre-flight failed** (`check-plan` not `READY`) | Fix the reported gaps with this skill, then re-run the audit |
| **Conventions/docs changed** after plan was `ready` | Update **Context references** and affected tasks, then the audit |

**After every structural edit** (phases, order, decisions, context refs, fresh chat handoff): re-run the audit before replying done.

## Self-contained entry point

A plan is the **sole starting context** for a fresh chat and throughout execution. Detail lives in linked files, not chat history. Required sections are listed in **Required plan structure**.

**Ready gate:** `status: ready` or `in_progress` only after the audit returns `READY` (`complete`: all tasks ✅ and scoreboard/acceptance met if applicable).

## Alignment with sequential-implementation

| Contract piece | create-plan | sequential-implementation |
| --- | --- | --- |
| Structure | **Required plan structure** | Pre-flight (`check-plan`) |
| Task | Small task: goal, scope, acceptance, Decisions refs, notes, Agent | Supervisor writes the spec at run time and delegates to the task's Agent |
| Agent | **Agents** | Runs each task with its Agent; reports plan issues |
| Order | **Open tasks only** | Fails if ✅ IDs listed |
| Progress | **Plan maintenance** | Supervisor updates after each task |
| Plan issue | **Replan mode** | Reports the issue and stops the affected tasks |
| Autonomy | § **Autonomy & authorization** (when present) | Pauses only on plan **User escalation** |
| Scope | § **Scope boundary** | Agent respects; unapproved shared changes or scope expansion → escalate |
| User manual work / gates | **Gate budget (authoring)**; minimal **Open questions**; **Operator handoff** for rare milestones; § **User escalation required** | **User-facing reports**, **User actions**, **User-reported results**; supervisor updates plan from chat |

## Gate budget (authoring)

Minimize how often execution pauses for the user and how much they do outside the agent loop.

| Lever | Use |
| --- | --- |
| **Decisions + brief** | Resolve cross-task choices at authoring (scouts, brief, **Decisions**); split so `senior`/`standard` agents run without per-task approval. |
| **Autonomy & authorization** | When multi-session work justifies it, pre-approve safe ops (dev server, read-only prod compare, plan-scoped edits) so routine environment use does not pause the run. |
| **Operator handoff** | Explicit user steps only for rare milestones: deploy, prod credentials, irreversible external effects, only when authority, access or an unresolved product/policy decision prevents executor action; group compatible milestones and keep locally runnable checks with the executor. |
| **Open questions** | Few rows; **Blocks** only tasks that truly cannot proceed; resolve at authoring when scouts or the brief can settle them. |
| **Agent approvals** | Only `principal` or `expert`; no user gates for lower tiers. |
| **Fresh chat handoff** | **Continue autonomously** through **Implementation order**; repair plan issues automatically; pause only for unresolved user input under § **User escalation required** or missing `principal`/`expert` approval. |

Group independent knowable questions into one round; do not group dependent decisions or bypass required authorization. Honor confirmed scope and existing approvals, including specific shared paths/actions. The executor owns bookkeeping and accepts chat-only results. `check-plan` audits these requirements under **User work and execution gates**.

Do not author optional per-phase confirm tasks, redundant approval rows, or handoff bullets that tell the user to maintain plan progress.

## Plan lineage (parent → child)

When a plan's goal **shipped** but follow-on work remains (e.g. migration shell complete, parity continues):

1. Mark parent `status: complete`; remove open IDs from **Implementation order**; cancel or supersede closure tasks that no longer match intent (note in phase table).
2. Create **child plan** (e.g. `<domain>-parity-plan.md`) linked from parent **Context references**; child references parent artifacts — do not duplicate history.
3. Update the parent index (e.g. `existing-website-migration-plan.md`) entry point to the child.

## Optional sections (migration / parity plans)

Add when the plan needs autonomous multi-session execution or domain-vs-global boundaries. **Patterns only** — thresholds and paths live in the plan.

### `## Autonomy & authorization`

| Subsection | Purpose |
| --- | --- |
| **User intent** | Autonomous within domain scope; escalate only per rules below |
| **Pre-approved operations** | Dev server, Playwright/parity scripts, prod compare (read-only), plan-scoped edits, plan-authorized CMS import, etc. |
| **Auto-decisions** | When the supervisor/subagent proceeds without user (clear majority target, S/M gap fixes in domain scope) |
| **User escalation required** | Non-obvious product/policy choices, ties with global impact, unapproved global/shared changes or scope expansion (honor specific paths/actions already approved in **Scope boundary**), Tier D last resort, commit/deploy/credentials unless pre-approved here; `principal`/`expert` only per **Agent approvals** — not routine `senior`/`standard` work or per-phase check-ins |
| **Delegation template** | **Authorization** block copied into every task prompt: project root, allowed operations, unapproved shared changes and scope expansion, "do not update the plan", escalation pointer |

Overrides **External environment boundary** for operations pre-approved here (e.g. a plan-authorized CMS import).

### `## Scope boundary` (domain migration plans)

Required when the plan changes shared or root configuration (check-plan D2); otherwise optional.

| | |
| --- | --- |
| **Domain scope** | Paths/components autonomous agents may edit (e.g. one domain's block directory, its CMS schemas) |
| **Global / shared scope** | Theme tokens, `components/ui/`, shared blocks, layout shell — execute specifically approved paths/actions; propose unapproved changes for user approval |
| **Promote-to-shared rule** | Domain pattern → global primitive requires user approval unless the specific shared change is already approved |

Read the project's own structure reference (`.agents/skills/project-best-practices/references/<topic>.md`, or the project-best-practices router) when listing paths and it exists.

### Phase retrospectives

On multi-phase plans (analysis → implementation → verify) add **report-only** retro tasks:

| When | Task ID pattern | Output |
| --- | --- | --- |
| After target survey / lock | `N.3` optional | `notes/retro-<phase>.md` (Notes out) |
| After gap analysis, before fixes | `N.4` **recommended** | Replan implementation order |
| After fix slices, before final pass | `N.R` **recommended** | Trim or extend final verify scope |

Sections: **Went well** · **Didn't work** · **Plan changes** · **Policy notes** (if any). Plan changes from a retro go through **Replan mode** before the next delegation.

## Conventions coverage (source-editing plans)

Implementers need **repo conventions** and **code quality**, not only task paths. During **Before writing**, check `<project-root>/.agents/skills/project-best-practices/SKILL.md`. When it exists, list it in **Context references** together with the task-relevant `references/<topic>.md` files and the sibling skills its router names for the plan's task types; note task IDs per ref in the Purpose column when helpful. Source-editing plans call out the **code** user rule in **Fresh chat handoff**. `check-plan` E1–E4 verify this.

## Out-of-band completion

When work finishes outside sequential-implementation:

1. Mark task `✅` in **Phases** + task file `**Status:**`.
2. **Remove** the ID from **Implementation order** (no "skip" comments).
3. Update **Context references** purposes; revise open tasks if outcomes changed.
4. Run the audit.

## Plan update workflow (extend / re-sync)

1. Read the current plan end-to-end.
2. Add phase/task rows in **Phases**; create `.local/<slug>/tasks/<id>.md` for each task (see **Authoring tasks**); add new cross-task choices to **Decisions**.
3. Add scout tasks where new work depends on discovery.
4. Append **only new open IDs** to **Implementation order**.
5. Update **Progress summary**, header `(next: …)`, **Context references**, **Fresh chat handoff** for the new next task.
6. Parity/migration: add scoreboard or invocation spec inline, or link `improve-parity`.
7. Bump `last_updated` and `version` if structure changed materially; run the audit.

## Replan mode

Triggered when `sequential-implementation` reports a plan issue (task ID, what failed or does not fit). The supervisor spawns `{{tool:spawn-agent}}({{agent:senior}})` with this skill, `check-plan`'s SKILL.md path, the plan path, the issue report and, when the replan follows an audit, the **complete** `check-plan` Findings table (every row, fails and warns). The replan agent assesses the problematic task and its impact on the following tasks, then may edit the plan within these limits:

- Edits only tasks **not yet done**. Completed tasks are never rewritten; add a corrective task instead.
- Stays within the plan's original goal and scope.
- Does not reverse **Decisions** the user approved.
- Does not assign `principal` or `expert` without recorded user approval.
- Appends a **Change log** entry: date, task IDs, what changed, why.

A change beyond these limits (goal or scope change, reversing an approved decision, an unapproved `principal` or `expert` assignment, rewriting completed work) needs user approval via `{{tool:ask-user}}` before the plan is edited; the agent returns it as a question. Upgrades within `junior` through `senior` need no extra user approval: select the lowest fitting tier and update the recorded **Agent** before execution. Existing recorded `principal`/`expert` approval persists when it covers the assignment.

The replan agent fixes **every** finding in one pass: it works through the whole Findings table, never stops after the first fix, and reports any finding it could not fix with the reason (a finding that needs user approval is returned as a question). After editing, the agent reports what changed, finding by finding, and returns. It does not run the `check-plan` audit, spawn any auditor, or wait for a verdict. The supervisor runs the audit (Workflow step 7) in the foreground so `sequential-implementation` can resume on `READY`.

## Before writing (new plan)

1. Confirm **project root** (git root).
2. Gather scope, constraints, success criteria; read the brief at `.local/<slug>/brief.md` when `propose-plan` produced one and treat its decisions as locked.
3. Separate task details from durable knowledge (**documentation** skill).
4. Confirm external-environment requests (**External environment boundary**).

## External environment boundary (mandatory)

No tasks mutating GitHub, remote deploy, hosted datasets, etc. unless the user **explicitly** asked **or** plan § **Autonomy & authorization** pre-approves them (e.g. a hosted-CMS import). Prefer **Operator handoff** + runbook when autonomy is silent.

## Plan directory layout (mandatory)

**Every plan gets a dedicated support folder; the entry point stays at `.local/` root.** Task IDs live only inside that folder so they never collide across plans.

```
.local/
  <slug>-plan.md           # Main plan — sole entry point for sequential-implementation
  <slug>/
    brief.md                # Plan brief from propose-plan (when present)
    architecture.md         # Target layout, inventory (optional)
    notes/                  # Scout findings and analysis recommendations
      <name>.md
    tasks/
      1.1.md
```

| Content | Path |
|---------|------|
| Main plan (lean **entry point**: phases, task index, decisions, progress) | `.local/<slug>-plan.md` — slug is short kebab-case (e.g. `date-input-migration`) |
| Plan brief handed off by `propose-plan` | `.local/<slug>/brief.md` |
| Task files | `.local/<slug>/tasks/<task-id>.md` — **never** a repo-wide `.local/tasks/` |
| Scout findings, analysis recommendations | `.local/<slug>/notes/<name>.md` |
| Initiative reference (design targets, runbooks) | `.local/<slug>/architecture.md`, … |
| Long-term agent knowledge (stable architecture, conventions) | `.context/` (+ `index.md`) |
| Long-term human docs | `docs/` (+ `README.md`) |

Follow the **`documentation`** skill. Link tasks from the plan as `[1.1.md](<slug>/tasks/1.1.md)`. Legacy plans with `plan.md` inside `<slug>/` or flat `.local/tasks/`: migrate when touching them. Create `.local/<slug>/` with `tasks/` and `notes/` when authoring; write `.local/<slug>-plan.md` last; add `.local/` to `.gitignore` when not already ignored.

**Content placement:** the plan or task file holds only what the executor needs for that task. Cross-task choices → the plan's **Decisions** section; discovery output → `notes/`; stable conventions → `.context/`; durable human reference → `docs/`.

## Authoring tasks

**Task size.** A task is one outcome a reviewer can sign off, finishable in one spawn of its Agent, with one primary verification. `check-plan` C1–C8 define the bar (including scope and acceptance limits); they are not restated here. To get there:

- **Split** by vertical slice and by dependency: schema, React UI, CMS seed and visual parity are separate tasks; phase umbrellas ("implement footer", "fix checkout parity"), research + fix in one ID and global shared refactor + feature work (unless § **Scope boundary** pre-approves) are always split.
- **Keep together:** one vertical slice (data query → normalize → props → component); token palette + style map for one surface; cleanup/deletion search + build for one retirement manifest. Content changes in a hosted environment stay separate from code layout.
- A task states what it delivers and how to check it, not how to build it. Do not pre-write file-by-file change lists; the executing supervisor derives them from the task, **Decisions** and notes.
- **Splitting procedure:** add rows in **Phases** (+ task files); move scope and acceptance from the oversized task and tighten **Out of scope** on each; insert new IDs in **Implementation order** in dependency order; update **Fresh chat handoff** `(next: …)` and **Context references**.

**Decisions.** Put a choice in `## Decisions` (ID `D1`, `D2`, …) when more than one task depends on it or when getting it wrong breaks a later task: interfaces and signatures, data shapes, ordering, naming, placement. A choice local to one task stays in that task's Scope. Never leave a design choice for the executor to make: settle it in **Decisions**, or in the brief, or ask the user in a batched authoring round — not as a per-task execution gate unless it truly blocks only that task. Tasks cite decisions by ID.

**Scout tasks.** When later work depends on discovery (inventory, gap analysis, API survey), add a report-only scout task (lowest tier per the Delegation scope table) whose `Notes out` is a file under `notes/`, and have the later tasks list it in `Notes in`. Place the scout earlier in **Implementation order**. A scout task never also implements. Discovery done while authoring goes to `notes/` too, and tasks reference it in `Notes in`.

**Agents.** Each implementation task has an **Agent** in the **Phases** table: the lowest tier from `junior` to `senior` whose scope fits, per the Delegation scope table; no user approval needed. Use `staff`, `principal`, or `expert` only for tasks whose sole deliverable is a recommendation or analysis (not product changes). If a task needs advisory depth beyond `senior` after splitting, honor applicable recorded approval for `principal` or `expert`; otherwise ask the user with `{{tool:ask-user}}` (see **User-facing wording**): propose `principal` or `expert` with a brief justification that cites one criterion from the Delegation scope table. Size or breadth is never a justification; split further instead. Once agreed, write the Agent into the task row **and** a row in `## Agent approvals`. If the user declines, keep `senior` (or lower) and split further.

## Required plan structure

```markdown
---
plan: true
version: 1
status: ready | in_progress | complete
last_updated: YYYY-MM-DD
---

# <Title>

**Status:** … · **Last updated:** YYYY-MM-DD (next: **<open-task-id>**)

**Project root:** `/absolute/path/to/repo`

## Progress summary
…

## Context references

Complete manifest — every file to consult during this initiative. Group by kind; **omit nothing** an implementer would need from a prior chat.

| File | Purpose |
|------|---------|
| `.local/<slug>-plan.md` | Main plan (entry point for sequential-implementation) |
| `.local/<slug>/brief.md` | Plan brief from propose-plan; locked decisions and rationale |
| `.local/<slug>/architecture.md` | Target layout, file inventory, retirement manifest |
| `.local/<slug>/notes/<name>.md` | Scout findings and analysis recommendations (list every note) |
| `.local/<slug>/tasks/<id>.md` | Per-task files (list every task file) |
| `.agents/skills/project-best-practices/SKILL.md` | Mandatory when present under project root |
| `.agents/skills/project-best-practices/references/*.md` | Task-relevant refs |
| *sibling skills named by project-best-practices* | Per task type, when the plan has such tasks |
| *convention / docs paths* | Canonical spec — note **target** vs **current** if code lags |

Use accurate purpose text (date, "target architecture", "legacy — replace in task X"). A file that a task will create starts its purpose with `Target (task <id>):`; check-plan skips it while the file is missing and warns only when that task is next open (B7).

## Decisions

Cross-task decisions (interfaces, data shapes, ordering, naming). Tasks reference these by ID.

| ID | Decision | Affects |
|----|----------|---------|
| D1 | … | 1.2, 2.1 |

## Implementation order

1. `2.1`   ← open tasks only; re-sync removes ✅ IDs

## Phases

### Phase 1 — <name>

| Task ID | Summary | Agent | Status | Details |
|---------|---------|-------|--------|---------|
| 1.1 | One-line outcome | standard | ⬜ | [1.1.md](<slug>/tasks/1.1.md) |

`Decisions`, `Notes in` and `Notes out` of each task live in its task file; any task that has them uses a task file (Details `—` only for a task with none). Status values: `⬜`, `🔄`, `✅ Complete`, `⏸ Blocked`, `🚫 Superseded` (kept in **Phases**, never in **Implementation order**).

### Phase 2 — <name>

…

## Agent approvals

Only for tasks whose Agent is `principal` or `expert`; omit rows otherwise. Each justification cites a criterion from the Delegation scope table, never size.

| Task ID | Agent | Justification | Agreed by user |
|---------|-------|---------------|----------------|
| 2.4 | principal | … | YYYY-MM-DD |

## Open questions

| Question | Owner | Blocks |
|----------|-------|--------|
| … | user | — |

Blocks lists only task IDs that are `⏸` pending the answer, otherwise `—`. Author at most a few rows; prefer **Decisions**, `notes/`, or batched authoring questions over a large blocking table. Do not use **Open questions** for non-blocking curiosity.

## Operator handoff (not plan tasks)

Manual steps that are **not** plan tasks: deploy, credentials, one-off external console work, or other milestones execution cannot perform under **Autonomy & authorization** or **External environment boundary**. Group compatible milestones; justify each unavoidable gate by authority, access or an unresolved product/policy decision. Write numbered, chat-ready steps naming each milestone by title, with enough context and a one-line why; state the user may report outcomes in chat and the executor updates the plan. Do not duplicate **Phases** tasks; do not instruct the user to edit the plan for progress or **Agent approvals**.

…

## Change log

Replans only (see **Replan mode**). A row whose change a later row reverses or replaces gets `Superseded by <date>` appended to its Change cell (check-plan A16).

| Date | Task IDs | Change | Why |
|------|----------|--------|-----|

## Plan maintenance
…

### After each task

1. Set the task row in **Phases** to `✅ Complete` (or `⏸ Blocked` with reason).
2. If the task has a linked task file, update its `**Status:**` line to match.
3. Recompute **Progress summary** phase rows (`✅` all complete; `🔄` any in progress; `⬜` otherwise).
4. Update header `**Last updated:**` and frontmatter `last_updated` (today's date).
5. Set frontmatter `status: in_progress` on first completed task; `status: complete` when all tasks are `✅`.
6. Resolve or add **Open questions** if the task surfaced new blockers or decisions.
7. Add newly created files (including notes) that future tasks need to **Context references** immediately.

### During execution

- Do **not** start the next task until the plan is updated.
- Subagents do **not** edit the plan — the supervisor does.
- Prefer updating the plan over leaving progress in chat only.
- A plan issue (task cannot be done as written, wrong order, missing decision) goes back through **Replan mode**; do not patch around it in the task prompt.

### Fresh chat handoff

**Single entry point:**

{{tool:skill-prefix}}sequential-implementation <project-root>/.local/<slug>-plan.md

1. **Project root:** …
2. Read this plan (Progress summary, Decisions, Context references, scoreboard if any).
3. Load `.agents/skills/project-best-practices/SKILL.md` when under `.agents/`; open task-relevant `references/` from Context references.
4. Apply **code** user rule for source-editing tasks — run its checklist before marking each task done.
5. Load initiative refs (brief, architecture) from Context references.
6. **Next task:** <task title> [<id>] — open `.local/<slug>/tasks/<id>.md`.
7. Load task-specific skills listed in the task or phase (e.g. `{{path:skills}}/improve-parity/SKILL.md`, sibling skills named by project-best-practices).
8. For each task, write its spec from the task, the **Decisions** it cites and its `Notes in`; delegate to its **Agent** with **Conventions** (project-best-practices + **code** rule) + plan **Authorization** when § Autonomy present; supervisor updates plan after each task.
9. **Continue autonomously** through **Implementation order**; pause only on plan § **User escalation required**, a missing `principal`/`expert` approval or other user-dependent blocker; repair plan issues automatically via **Replan mode** — not after each phase or task by default.
10. When pausing for user action, relay per **User-facing wording** (executor uses `sequential-implementation` **User actions** and **User-reported results**).
11. Prerequisites: …
```

Adjust steps for the initiative; **never** omit the single entry point or next task ID.

## Task file template (`.local/<slug>/tasks/<task-id>.md`)

```markdown
**Status:** ⬜

## Goal

One paragraph — one concrete outcome.

## Scope

- Areas: expected files or directories
- In scope: …
- Out of scope: … (include boundaries vs adjacent tasks when paths may overlap)

## References

- Decisions: D1, D3
- Notes in: `../notes/<name>.md` (existing, or produced by an earlier task's Notes out)
- Notes out: `../notes/<name>.md` (scout and analysis tasks only)

## Acceptance

- [ ] … (all serving the goal)

## Verification

Exact command or manual check and its expected result (e.g. the package's test command passes, lint clean, or visual check).

## Context

- Plan: `../../<slug>-plan.md`
- Background: `../architecture.md`, `../brief.md`, or `../../.context/…` (long-term only)
```

Omit a References line that has no entries. The `Decisions` line holds only comma-separated IDs from the plan's **Decisions** section, with no other text (check-plan parses it).

## Workflow (new plan)

1. Confirm project root, scope, constraints and the brief (if any); read `check-plan`'s SKILL.md.
2. Check `project-best-practices`; map open work to **Conventions coverage** refs.
3. Spawn scouts by area at the lowest tier per the Delegation scope table; each writes only its own notes file under `.local/<slug>/notes/` (named in its authorization block) and returns a short summary.
4. Spawn the `senior` author (see **Execution**) with the notes and brief: it drafts phases, small tasks, **Decisions**, scout tasks and Agents (lowest fitting tier per the Delegation scope table), and returns proposals for any `principal` or `expert` Agent.
5. Relay batched questions and Agent proposals with `{{tool:ask-user}}` (see **User-facing wording**); record agreed Agents in the task rows and **Agent approvals**; re-spawn the author with the answers.
6. The author creates `.local/<slug>/` (`tasks/`, `notes/`), the task files, then `.local/<slug>-plan.md` last.
7. **Audit:** spawn `{{tool:spawn-agent}}({{agent:senior}})` as a read-only auditor given `{{path:skills}}/check-plan/SKILL.md` and the plan path; it returns the `check-plan` report. If not `READY`, re-spawn the author with the complete Findings table (every fail and warn row) so it fixes all of them in one pass, and repeat until `READY`. If the same failure recurs unchanged with no progress, stop and explain the blocker rather than looping; ask only for genuinely user-dependent decisions or authorization.
8. Tell the user the plan path and `{{tool:skill-prefix}}sequential-implementation <plan-path>` for a fresh chat.

## Authoring rules

1. **Task IDs:** `<phase>.<sequence>` (e.g. `2.3`), unique across the plan; phases are labels, never umbrella tasks.
2. **Small tasks:** one spawn per task, at the lowest tier whose scope fits; `principal` or `expert` only with a recorded approval — see **Authoring tasks**.
3. **Implementation order = open tasks only** — re-sync when tasks complete.
4. **Progress:** the plan owns the summary table and per-task status columns (single source of truth).
5. **Lean plan:** the plan is the **index**; cross-task choices live in **Decisions**, discovery in `notes/`; never orphan detail outside **Context references** or task links.
6. **Self-contained:** **Context references** enumerates all files for a fresh chat; **Plan maintenance** keeps progress current; **Fresh chat handoff** is required.
7. **External environments:** no PR/deploy/import/hosting/commit tasks by default (not even "ship"/"done" phases); hand off to the user in the runbook text and use local verify. Exceptions per **External environment boundary**.
8. **Re-sync before handoff:** if conventions or docs changed after drafting, update the plan and re-run the audit.
9. **Ready gate:** `status: ready` only after the audit returns `READY`.
10. **Conventions coverage:** source-editing plans list project-best-practices (+ task-relevant references and the sibling skills its router names) and the **code** user rule in **Fresh chat handoff**.
11. **Gate budget:** follow **Gate budget (authoring)**; prefer autonomy and **Decisions** over execution-time pauses.
12. **Open questions:** minimize rows and blocked surface; resolve at authoring when scouts or the brief can settle them.
13. **User plan edits:** execution never requires the user to edit plan or task files; the supervisor updates the plan from chat per **User-facing wording**.

## Do not

- Put task files in a shared `.local/tasks/`, or the main plan inside `.local/<slug>/`.
- Duplicate `check-plan`'s checklist in the plan or in this skill; mark ready without a `READY` audit.
- Assign `principal` or `expert` without a recorded user approval, or rewrite a completed task during a replan.
- Leave a design choice for the executor, or a cross-task choice outside **Decisions**.
- Merge investigation and implementation; put discovery in a task body instead of a scout task with `Notes out`.
- Leave `✅ Complete` IDs in **Implementation order**, or a handoff saying "start at 1.1" when only `8.1` is open.
- Leave implementation-relevant files unlisted in **Context references**, or use "to update" purposes for finished work.
- Write tasks whose acceptance requires another open task — reorder or split.
- Require the user to edit plan or task files during execution, or to mirror **Implementation order** / task **Status** manually.
- Scatter micro-approvals across tasks when one **Decisions** row or one batched authoring question suffices.
- Add per-phase confirm tasks or optional approval rows for `senior`/`standard` work.
- Structure **Fresh chat handoff** or tasks so execution must pause after each phase unless § **User escalation required** applies.
- Load **Open questions** with non-blocking items; use `notes/` or **Decisions** instead.
