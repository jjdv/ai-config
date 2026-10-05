---
name: create-plan
description: >-
  Create or update implementation plans for sequential-implementation. Run on
  every plan create or structural update — enforces handoff-ready structure,
  open-only implementation order, fresh-chat entry point, and linked task files.
  Use when drafting a plan, extending phases, re-syncing after completed tasks,
  or before telling the user to run sequential-implementation. Also use for
  planning a website/page-group migration (routes, domains, blocks or page types
  from a reference repo; "plan a migration", "create migration plan", migration
  scope) — load references/migration-workflow.md. After authoring, run
  check-plan on the plan path to confirm READY.
---

# Create Plan

{{block:tool-note}}

Produce and maintain plans structured for **`sequential-implementation`** and **`standard`** delegation.

**Contract:** A plan is **handoff-ready** only when a **fresh chat** can run `/sequential-implementation <plan-path>` with **no prior context** — read plan → follow **Fresh chat handoff** → delegate next open task.

## Execution

Main thread is a supervisor: author and maintain plans via `{{tool:spawn-agent}}({{agent:senior}})`, passing this skill's text, project root and scope. Already running as `senior` → author directly. The subagent cannot ask the user: it returns questions; the supervisor relays them with `{{tool:ask-user}}` and re-spawns with the answers. Task execution later uses `standard`.

**Migration planning** (website/page-group migration, "plan a migration of these pages"): read `references/migration-workflow.md` and follow it; it authors through this skill. Do not load it for other plans.

## Mandatory triggers (run this skill)

Read and follow this skill **before finishing** when **any** of:

| Trigger | Action |
| --- | --- |
| **New plan** | Full **Workflow** + **Handoff readiness checklist** |
| **Plan extended** (new phase/task, parity round, scope change) | **Plan update workflow** + checklist on affected sections |
| **Batch completion** (many tasks marked ✅ outside sequential-implementation) | **Out-of-band completion** |
| **Before** user runs `sequential-implementation`, or its **pre-flight failed** | Run **`check-plan`**; fix gaps with this skill |
| **Conventions/docs changed** after plan was `ready` | Re-run checklist; update **Context references** and task specs |

**After every structural edit** (phases, order, context refs, fresh chat handoff): run the **Handoff readiness checklist** before replying done. If a fresh chat needs history, re-run this skill on the plan — do not patch ad hoc.

## Self-contained entry point

A plan is the **sole starting context** for a fresh chat and throughout execution. It **must** have: **Project root** (absolute git root), **Context references** (every file an implementer needs), **Implementation order** (open task IDs only), **Fresh chat handoff** (numbered steps naming the next task ID, skills, prerequisites), **Plan maintenance**. Detail lives in linked files, not chat history.

**Ready gate:** `status: ready` or `in_progress` only when the **Handoff readiness checklist** passes (`complete`: all tasks ✅ and scoreboard/acceptance met if applicable).

## Alignment with sequential-implementation

| Contract piece | create-plan | sequential-implementation |
| --- | --- | --- |
| Structure | **Required plan structure** | Pre-flight validation |
| Task IDs | One ID = one `standard` spawn | Delegates in **Implementation order** |
| Order | **Open tasks only** | Fails if ✅ IDs listed |
| Progress | **Plan maintenance** | Supervisor updates after each task |
| Autonomy | § **Autonomy & authorization** (when present) | Pauses only on plan **User escalation** |
| Scope | § **Scope boundary** | Agent respects; global → escalate |
| Task-fit | **Task-fit checklist** | Pre-flight + **Oversized tasks** block delegation until split |

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
| **User escalation required** | Non-obvious choices, ties, global/shared scope, Tier D last resort, commit/deploy unless pre-approved |
| **Delegation template** | **Authorization** block copied into every `standard` prompt: project root, allowed operations, forbidden global scope, "do not update the plan", escalation pointer |

Overrides **External environment boundary** for operations pre-approved here (e.g. Sanity MCP import).

### `## Scope boundary` (domain migration plans)

| | |
| --- | --- |
| **Domain scope** | Paths/components autonomous agents may edit (e.g. `blocks/customers/`, domain Sanity schemas) |
| **Global / shared scope** | Theme tokens, `components/ui/`, shared blocks, layout shell — **propose only; user approves before implement** |
| **Promote-to-shared rule** | Domain pattern → global primitive requires user |

Reference project `references/website-structure.md` or equivalent when listing paths.

### Phase retrospectives

On multi-phase plans (analysis → implementation → verify) add **report-only** retro tasks:

| When | Task ID pattern | Output |
| --- | --- | --- |
| After target survey / lock | `N.3` optional | `retro-<phase>.md` |
| After gap analysis, before fixes | `N.4` **recommended** | Replan implementation order |
| After fix slices, before final pass | `N.R` **recommended** | Trim or extend final verify scope |

Sections: **Went well** · **Didn't work** · **Plan changes** · **Policy notes** (if any). Supervisor updates **Implementation order** from the retro before the next delegation.

## Conventions coverage (mandatory for source-editing plans)

Implementers need **repo conventions** and **code quality**, not only task paths. Check `<project-root>/.agents/skills/project-best-practices/SKILL.md` during **Before writing** and **Handoff readiness**.

| Plan touches | **Context references** must include |
| --- | --- |
| Always (repo has the skill) | `project-best-practices/SKILL.md` |
| Blocks, components, placement | `references/placement.md`, `references/website-structure.md` |
| Styling, tokens, SCSS | `references/styling.md` |
| CMS blocks, GROQ, page builders | `references/cms-blocks.md` |
| Sanity schemas, Studio, CMS content | `sanity-best-practices` + `sanity-data-handling` (per project-best-practices § Sanity) |

List only refs the plan needs, but **never omit** one when any open task matches the row; note task IDs per ref in the Purpose column when helpful.

Plans that change source must call out the **code** user rule in **Fresh chat handoff** (apply + run its checklist before marking tasks done). It covers general quality (naming, structure, KISS/DRY/SOLID-lite); **project-best-practices** covers repo placement and architecture — both apply when present.

## Handoff readiness checklist

Run **after every create or structural update** and before `status: ready` / recommending `sequential-implementation`.

| Check | Pass when |
| --- | --- |
| **Project root** | `**Project root:**` line with absolute path |
| **Header next task** | `**Last updated:**` includes `(next: **<id>**)` matching first open task |
| **Implementation order** | Lists **only** task IDs that still need work — **no** `✅ Complete` IDs |
| **Phase table vs order** | Every ID in **Implementation order** appears in **Phases**; completed tasks stay in **Phases** with `✅` |
| **Fresh chat handoff** | Section present; step names **next task ID**; lists skills (e.g. `improve-parity`, `project-best-practices`) and **code** user rule when plan edits source |
| **Project conventions** | When `project-best-practices` exists: SKILL.md + task-relevant `references/` and Sanity siblings in **Context references** per **Conventions coverage** |
| **Code quality** | **Fresh chat handoff** requires **code** user rule checklist for source-editing tasks |
| **Single entry point** | Handoff includes exact `sequential-implementation` invocation with plan path |
| **Context references** | Every linked path exists; purposes accurate (no stale "to update" for done work) |
| **Initiative refs** | `.local/<slug>/decisions.md` and `architecture.md` exist when referenced |
| **Task files** | Every linked `.local/<slug>/tasks/<id>.md` exists for non-`—` Details rows |
| **Plan folder** | Supporting files under `.local/<slug>/`; entry point at `.local/<slug>-plan.md` — no shared flat `.local/tasks/` |
| **Task-fit** | Every **open** task passes **Task-fit checklist**; no mega-tasks or investigate+implement bundles |
| **Target vs code** | Migration/refactor plans: banner under title (**target** docs vs **current** code) wherever docs ≠ code; canonical specs in **Context references**; prefer verify tasks over duplicate doc writes when docs already landed |
| **Out-of-band** | Done work removed from **Implementation order**; task files `**Status:**` synced |
| **Open questions** | **Blocks** column empty or only truly blocked IDs |
| **Operator handoff** | External steps (import, deploy) in **Operator handoff** — not plan tasks unless user requested or **Autonomy** pre-approves |
| **Autonomy** (parity/migration) | § **Autonomy & authorization** present when plan claims autonomous execution; escalation rules explicit |
| **Scope boundary** (domain migration) | Domain vs global/shared paths listed when edits touch theme or shared architecture |
| **Plan lineage** | Child plan linked from parent when parent marked complete with open follow-on |

**Report:** list failed checks and fix them in the plan before marking done.

## Out-of-band completion

When work finishes outside sequential-implementation:

1. Mark task `✅` in **Phases** + task file `**Status:**`.
2. **Remove** the ID from **Implementation order** (no "skip" comments).
3. Update **Context references** purposes; rewrite later task specs if outcomes changed.
4. Re-run **Handoff readiness checklist**.

## Plan update workflow (extend / re-sync)

1. Read the current plan end-to-end.
2. Add phase/task rows in **Phases**; create `.local/<slug>/tasks/<id>.md` for non-trivial work.
3. Append **only new open IDs** to **Implementation order**.
4. Update **Progress summary**, header `(next: …)`, **Context references**, **Fresh chat handoff** for the new next task.
5. Parity/migration: add scoreboard or invocation spec inline, or link `improve-parity`.
6. Run **Handoff readiness checklist**; bump `last_updated` and `version` if structure changed materially.

## Before writing (new plan)

1. Confirm **project root** (git root).
2. Gather scope, constraints, success criteria.
3. Separate task details from durable knowledge (**documentation** skill).
4. Confirm external-environment requests (**External environment boundary**).

## External environment boundary (mandatory)

No tasks mutating GitHub, remote deploy, hosted datasets, etc. unless the user **explicitly** asked **or** plan § **Autonomy & authorization** pre-approves them (e.g. CMS import via MCP/CLI). Prefer **Operator handoff** + runbook when autonomy is silent.

## Plan directory layout (mandatory)

**Every plan gets a dedicated support folder; the entry point stays at `.local/` root.** Task IDs live only inside that folder so they never collide across plans.

```
.local/
  <slug>-plan.md           # Main plan — sole entry point for sequential-implementation
  <slug>/
    decisions.md            # Locked decisions (optional but recommended)
    architecture.md         # Target layout, inventory (optional)
    tasks/
      1.1.md
```

| Content | Path |
|---------|------|
| Main plan (lean **entry point**: phases, task index, progress) | `.local/<slug>-plan.md` — slug is short kebab-case (e.g. `date-input-migration`) |
| Task details (large or multi-file specs) | `.local/<slug>/tasks/<task-id>.md` — **never** a repo-wide `.local/tasks/` |
| Initiative reference (short-term decisions, design targets, runbooks) | `.local/<slug>/decisions.md`, `architecture.md`, … |
| Long-term agent knowledge (stable architecture, conventions) | `.context/` (+ `index.md`) |
| Long-term human docs | `docs/` (+ `README.md`) |

Follow the **`documentation`** skill. Link tasks from the plan as `[1.1.md](<slug>/tasks/1.1.md)`. Legacy plans with `plan.md` inside `<slug>/` or flat `.local/tasks/`: migrate when touching them. Create `.local/<slug>/` and `tasks/` when authoring; write `.local/<slug>-plan.md` last; add `.local/` to `.gitignore` when not already ignored.

**Content placement:** the plan or task file holds only what the executor needs for that task. Locked decisions, design targets, epic architecture, and background repeated across tasks → one `.local/<slug>/` file linked from each task; stable conventions → `.context/`; durable human reference → `docs/`.

## Task sizing and task-fit (mandatory)

**One task ID = one `standard` spawn** (foreground), finishable in a **single subagent session** with one primary verification path — not an epic, not a sequence of follow-up spawns. When drafting or extending a plan (and after scope grows mid-initiative), apply the checklist to **each open task** (read its linked task file). **Fail any row → split** (e.g. `3.2` → `3.2` + `3.3`) and update **Implementation order**.

| # | Criterion | Pass when | Fail → split when |
| --- | --- | --- | --- |
| 1 | **One outcome** | Summary is one concrete deliverable a reviewer can sign off | Summary joins unrelated outcomes with "and" (tokens **and** layout **and** CMS seed **and** parity) |
| 2 | **One session** | One `standard` spawn, no planned follow-up for the same ID | Needs multiple runs, or supervisor already expects a follow-up |
| 3 | **Bounded scope** | ≤8 primary paths, or one cohesive subsystem | >8 primary paths, or 3+ **unrelated** subsystems (Studio schema + React layout + MCP import) |
| 4 | **Acceptance cap** | ≤7 criteria, all serving the same outcome | >7 criteria, or criteria belonging to separate tasks |
| 5 | **Single verify track** | One primary **Verification** command or manual check | Multiple independent tracks (full parity suite **and** CMS import **and** schema deploy) |
| 6 | **No investigate + build** | Implementation only, or analysis is a separate report-only ID | Same ID mixes spike/audit/gap analysis with production code changes |
| 7 | **Sequenced deps only** | Depends only on prior tasks already sequenced; **Out of scope** defers adjacent work | Acceptance requires a later ID's work, or overlaps another open task |
| 8 | **Vertical slice OK** | Multi-file edits are one GROQ→props→UI slice, token+SCSS for one surface, or a deletion sweep | Unrelated packages or layers bundled without a single user-visible slice |

**Split:** schema + React UI + CMS seed + visual parity verify; phase umbrellas ("implement footer", "fix customers parity"); research + fix in one ID; global shared refactor + feature work (unless § **Scope boundary** pre-approves).
**Keep together:** one vertical slice (GROQ → normalize → props → component); token palette + SCSS map for one chrome surface; cleanup/deletion grep + build for one retirement manifest; CMS content patch (OAuth MCP) kept separate from code layout.

**Splitting procedure:** add new rows in **Phases** (+ task files for non-trivial splits); move scope, acceptance and verify from the oversized task and tighten **Out of scope** on each; insert new IDs in **Implementation order** in dependency order (remove or replace the oversized ID); update **Fresh chat handoff** `(next: …)` and **Context references**; re-run the checklist.

## Required plan structure

Every plan **must** include:

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
| `.local/<slug>/decisions.md` | Locked decisions |
| `.local/<slug>/architecture.md` | Target layout, file inventory, retirement manifest |
| `.local/<slug>/tasks/<id>.md` | Per-task specs (list every task file) |
| `.agents/skills/project-best-practices/SKILL.md` | Mandatory when present under project root |
| `.agents/skills/project-best-practices/references/*.md` | Task-relevant refs (placement, styling, cms-blocks, website-structure, …) |
| `.agents/skills/sanity-best-practices/SKILL.md` | When plan has Sanity schema/GROQ/Studio tasks |
| `.agents/skills/sanity-data-handling/SKILL.md` | When plan patches or imports CMS content |
| *convention / docs paths* | Canonical spec — note **target** vs **current** if code lags |

Use accurate purpose text (date, "target architecture", "legacy — replace in task X").

## Implementation order

1. `2.1`   ← open tasks only; re-sync removes ✅ IDs

## Phases

### Phase 1 — <name>

| Task ID | Summary | Status | Details |
|---------|---------|--------|---------|
| 1.1 | One-line outcome | ⬜ | [1.1.md](<slug>/tasks/1.1.md) or — |

Use `—` in Details when the summary is sufficient (no task file).

### Phase 2 — <name>

…

## Open questions
…

## Operator handoff (not plan tasks)
…

## Plan maintenance
…

### After each task

1. Set the task row in **Phases** to `✅ Complete` (or `⏸ Blocked` with reason).
2. If the task has a linked task file, update its `**Status:**` line to match.
3. Recompute **Progress summary** phase rows (`✅` all complete; `🔄` any in progress; `⬜` otherwise).
4. Update header `**Last updated:**` and frontmatter `last_updated` (today's date).
5. Set frontmatter `status: in_progress` on first completed task; `status: complete` when all tasks are `✅`.
6. Resolve or add **Open questions** if the task surfaced new blockers or decisions.
7. Add newly created files that future tasks need to **Context references** immediately.

### During execution

- Do **not** start the next task until the plan is updated.
- Subagents do **not** edit the plan — the supervisor or implementing agent does.
- Prefer updating the plan over leaving progress in chat only.

### Fresh chat handoff

**Single entry point:**

/sequential-implementation <project-root>/.local/<slug>-plan.md

1. **Project root:** …
2. Read this plan (Progress summary, Context references, scoreboard if any).
3. Load `.agents/skills/project-best-practices/SKILL.md` when under `.agents/`; open task-relevant `references/` from Context references.
4. Apply **code** user rule for source-editing tasks — run its checklist before marking each task done.
5. Load initiative refs from Context references.
6. **Next task:** `<id>` only — open `.local/<slug>/tasks/<id>.md`.
7. Load task-specific skills listed in task spec or phase (e.g. `{{path:skills}}/improve-parity/SKILL.md`, `sanity-best-practices`, `sanity-data-handling`).
8. Delegate `standard` with **Conventions** (project-best-practices + **code** rule) + plan **Authorization** when § Autonomy present; supervisor updates plan after each task.
9. **Continue autonomously** through **Implementation order**; pause only on plan § **User escalation required** (not fixed task IDs).
10. Prerequisites: …
```

Adjust steps for the initiative; **never** omit the single entry point or next task ID.

## Task file template (`.local/<slug>/tasks/<task-id>.md`)

```markdown
## Goal

One paragraph — concrete outcome.

## Scope

- In scope: …
- Out of scope: … (include boundaries vs adjacent tasks when paths may overlap)

## Context

- Plan: `../../<slug>-plan.md` (from `tasks/`; or `../<slug>-plan.md` from `.local/` siblings)
- Background: `../decisions.md`, `../architecture.md`, or `../../.context/…` (long-term only)

## Acceptance criteria

- [ ] …
- [ ] Code complies with project-best-practices (when present) and passes **code** user rule checklist for touched source files

## Verification

Command or manual check the subagent should run (e.g. `pnpm test packages/foo`, lint, or visual check).

## Notes

Primary file or dir hints; sequencing notes only when reordering **Implementation order** is insufficient.
```

## Workflow (new plan)

1. Draft phases/tasks; agree order if ambiguous.
2. Check `project-best-practices`; map open tasks to **Conventions coverage** refs.
3. Write `.local/<slug>/` decisions/architecture as needed; durable conventions to agent `references/` or `docs/` when the initiative defines long-term rules.
4. Write task files for non-trivial tasks (paths, **Out of scope**, **Verification** when not obvious).
5. Run **Task-fit checklist** on every open task; split until all pass.
6. Write `.local/<slug>-plan.md` last.
7. **Handoff readiness checklist** — fix all failures (or run **`check-plan`**).
8. Tell the user: `/check-plan <plan-path>` then `/sequential-implementation <plan-path>` in a fresh chat.

## Authoring rules

1. **Task IDs:** `<phase>.<sequence>` (e.g. `2.3`), unique across the plan; phases are labels, never umbrella tasks.
2. **One spawn per task**, independently delegatable — see **Task sizing**.
3. **Implementation order = open tasks only** — re-sync when tasks complete.
4. **Progress:** the plan owns the summary table and per-task status columns (single source of truth).
5. **Lean plan:** specs live in linked files; the plan is the **index** — never orphan detail outside **Context references** or task links.
6. **Self-contained:** **Context references** enumerates all files for a fresh chat; **Plan maintenance** keeps progress current; **Fresh chat handoff** is required.
7. **External environments:** no PR/deploy/import/hosting/commit tasks by default (not even "ship"/"done" phases); hand off to the user in decisions or runbook text and use local verify. Exceptions per **External environment boundary**.
8. **Re-sync before handoff:** if conventions or docs changed after drafting, update the plan before telling the user to run `sequential-implementation`; re-run the checklist after any structural edit.
9. **Ready gate:** `status: ready` only when the checklist passes and no open question blocks specific tasks (list them in **Open questions** with **Blocks**).
10. **Conventions coverage:** source-editing plans list project-best-practices (+ task-relevant references and Sanity siblings) and the **code** user rule in **Fresh chat handoff**.
11. **Task-fit:** no open task fails the checklist — split first.

## Do not

- Put task files in a shared `.local/tasks/`, or the main plan inside `.local/<slug>/`.
- Leave `✅ Complete` IDs in **Implementation order**, or a handoff saying "start at 1.1" when only `8.1` is open.
- Mark ready without the checklist.
- Embed full product briefs in the plan when `.local/<slug>/` is more appropriate.
- Leave implementation-relevant files unlisted in **Context references**, or use "to update" purposes for finished work.
- Create tasks without IDs, or a plan without **Implementation order**.
- Write tasks whose acceptance criteria require another open task — reorder or split.
- Merge investigation and implementation when exploration scope is unclear.
