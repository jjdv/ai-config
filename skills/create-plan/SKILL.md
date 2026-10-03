---
name: create-plan
description: >-
  Create or update implementation plans for sequential-implementation. Run on
  every plan create or structural update — enforces handoff-ready structure,
  open-only implementation order, fresh-chat entry point, and linked task files.
  Use when drafting a plan, extending phases, re-syncing after completed tasks,
  or before telling the user to run sequential-implementation. After authoring,
  run check-plan on the plan path to confirm READY.
---

# Create Plan

{{tool_mapping_note}}

Produce and maintain plans structured for **`sequential-implementation`** and **`{{impl_agent_name}}`** delegation.

**Contract:** A plan is **handoff-ready** only when a **fresh chat** can run `/sequential-implementation <plan-path>` with **no prior context** — read plan → follow **Fresh chat handoff** → delegate next open task.

## Mandatory triggers (run this skill)

Read and follow this skill **before finishing** when **any** of:

| Trigger | Action |
| --- | --- |
| **New plan** | Full **Workflow** + **Handoff readiness checklist** |
| **Plan extended** (new phase/task, parity round, scope change) | **Plan update workflow** + checklist on affected sections |
| **Batch completion** (many tasks marked ✅ outside sequential-implementation) | **Out-of-band completion** + prune **Implementation order** |
| **Before** user runs `sequential-implementation` | Run **`check-plan`** on the plan path; fix gaps with this skill |
| **sequential-implementation pre-flight failed** | Re-sync per checklist — or run **`check-plan`** and fix reported fails |
| **Conventions/docs changed** after plan was `ready` | Re-run checklist; update **Context references** and task specs |

**After every plan file edit** that touches structure (phases, order, context refs, fresh chat handoff): run the **Handoff readiness checklist** before replying done.

`sequential-implementation` **authors** execution; **this skill** **authors and maintains** plan shape.

## Self-contained entry point

A plan must work as the **sole starting context** at start and throughout execution. It **must**:

1. **`**Project root:**`** absolute path to git root.
2. **Context references** — every file an implementer needs (initiative refs, task specs, skills, `docs/`, sibling repos).
3. **Implementation order** — **only open task IDs** (see checklist).
4. **Fresh chat handoff** — numbered steps naming **next task ID**, required skills, prerequisites.
5. **Plan maintenance** — how to update progress after each task.

Detail lives in linked files — not chat history.

**Ready gate:** `status: ready` or `in_progress` only when **Handoff readiness checklist** passes (for `complete`, all tasks ✅ and scoreboard/acceptance met if applicable).

## Alignment with sequential-implementation

| Contract piece | create-plan | sequential-implementation |
| --- | --- | --- |
| Plan structure | **Required plan structure** | Pre-flight validation |
| Task IDs | One ID = one `{{impl_agent_name}}` spawn | Delegates in **Implementation order** |
| Implementation order | **Open tasks only** | Order hygiene — fails if ✅ IDs listed |
| Progress | **Plan maintenance** | Supervisor updates after each task |
| Fresh chat | **Fresh chat handoff** section | Reads plan only |
| Autonomy | Plan § **Autonomy & authorization** (when present) | Pause only on plan **User escalation** — not fixed task IDs |
| Scope | Plan § **Scope boundary** (domain vs global) | Agent respects; global → escalate |
| Task-fit | **Task-fit checklist** per open task | Pre-flight + **Oversized tasks** — blocks delegation until split |

If pre-flight fails or a fresh chat needs history, **re-run this skill** on the plan — do not patch ad hoc.

## Plan lineage (parent → child)

When a plan’s goal is **shipped** but follow-on work remains (e.g. migration shell complete, parity continues):

1. Mark parent `status: complete`; remove open IDs from **Implementation order**.
2. Cancel or supersede closure tasks that no longer match intent (note in phase table).
3. Create **child plan** (e.g. `<domain>-parity-plan.md`) with link from parent **Context references**.
4. Child references parent artifacts (audits, architecture) — do not duplicate history.
5. Update parent index (e.g. `existing-website-migration-plan.md`) entry point to child.

## Optional sections (migration / parity plans)

Add when the plan needs autonomous multi-session execution or domain-vs-global boundaries. **Patterns only** — thresholds and paths live in the plan, not in this skill.

### `## Autonomy & authorization`

| Subsection | Purpose |
| --- | --- |
| **User intent** | Autonomous within domain scope; escalate only per rules below |
| **Pre-approved operations** | Dev server, Playwright/parity scripts, prod compare (read-only), plan-scoped edits, plan-authorized CMS import, etc. |
| **Auto-decisions** | When supervisor/implementation subagent proceeds without user (e.g. clear majority target, S/M gap fixes in domain scope) |
| **User escalation required** | Non-obvious choices, ties, global/shared scope, Tier D last resort, commit/deploy unless pre-approved |
| **Delegation template** | **Authorization** block copied into every `{{impl_agent_name}}` prompt |

Override **External environment boundary** below when the user pre-approves operations in this section (e.g. Sanity MCP import).

### `## Scope boundary` (domain migration plans)

| | |
| --- | --- |
| **Domain scope** | Paths/components autonomous agents may edit (e.g. `blocks/customers/`, domain Sanity schemas) |
| **Global / shared scope** | Theme tokens, `components/ui/`, shared blocks, layout shell — **propose only; user approves before implement** |
| **Promote-to-shared rule** | Domain pattern → global primitive requires user |

Reference project `references/website-structure.md` or equivalent when listing paths.

### Phase retrospectives

On multi-phase plans with analysis → implementation → verify, add **report-only** retro tasks after major transitions:

| When | Task ID pattern | Output |
| --- | --- | --- |
| After target survey / lock | `N.3` optional | `retro-<phase>.md` |
| After gap analysis, before fixes | `N.4` **recommended** | Replan implementation order |
| After fix slices, before final pass | `N.R` **recommended** | Trim or extend final verify scope |

Retro deliverable sections: **Went well** · **Didn't work** · **Plan changes** · **Policy notes** (if any). Supervisor updates **Implementation order** from retro before next delegation.

## Conventions coverage (mandatory for source-editing plans)

When the plan's tasks edit **source files**, ensure implementers get both **repo conventions** and **code quality** — not only task-specific paths.

### When `project-best-practices` exists

Check `<project-root>/.agents/skills/project-best-practices/SKILL.md` during **Before writing** and **Handoff readiness**.

| Plan touches | **Context references** must include |
| --- | --- |
| Always (repo has the skill) | `project-best-practices/SKILL.md` |
| Blocks, components, placement | `references/placement.md`, `references/website-structure.md` |
| Styling, tokens, SCSS | `references/styling.md` |
| CMS blocks, GROQ, page builders | `references/cms-blocks.md` |
| Sanity schemas, Studio, CMS content | `sanity-best-practices` + `sanity-data-handling` (per project-best-practices § Sanity) |

List only refs the plan actually needs — but **do not omit** a ref when any open task matches the row. Note which task IDs use each ref in the Purpose column when helpful.

### `code` user rule (all source edits)

Plans that change source must call out the **code** user rule in **Fresh chat handoff** (apply + run checklist before marking tasks done). The rule covers general quality (naming, structure, KISS/DRY/SOLID-lite); **project-best-practices** covers repo-specific placement and architecture — both apply when present.

## Handoff readiness checklist

Run **after every create or structural update** and before `status: ready` / recommending `sequential-implementation`.

| Check | Pass when |
| --- | --- |
| **Project root** | `**Project root:**` line with absolute path |
| **Header next task** | `**Last updated:**` includes `(next: **<id>**)` matching first open task |
| **Implementation order** | Lists **only** task IDs that still need work — **no** `✅ Complete` IDs |
| **Phase table vs order** | Every ID in **Implementation order** appears in **Phases**; completed tasks stay in **Phases** with `✅` |
| **Fresh chat handoff** | Section present; step names **next task ID**; lists skills (e.g. `improve-parity`, `project-best-practices`) and **code** user rule when plan edits source |
| **Project conventions** | When `project-best-practices` exists: SKILL.md in **Context references**; task-relevant `references/` and Sanity siblings listed per **Conventions coverage** |
| **Code quality** | **Fresh chat handoff** requires **code** user rule checklist for source-editing tasks |
| **Single entry point** | Handoff includes exact `sequential-implementation` invocation with plan path |
| **Context references** | Every linked path exists; purposes accurate (no stale “to update” for done work) |
| **Initiative refs** | `.local/<slug>/decisions.md` and `architecture.md` exist when referenced |
| **Task files** | Every linked `.local/<slug>/tasks/<id>.md` exists for non-`—` Details rows |
| **Plan folder** | Supporting files under `.local/<slug>/`; entry point at `.local/<slug>-plan.md` — no shared flat `.local/tasks/` |
| **Task-fit** | Every **open** task passes **Task-fit checklist** (§ below); no mega-tasks or investigate+implement bundles |
| **Target vs code** | Migration/refactor plans banner or note where docs ≠ code |
| **Out-of-band** | Done work removed from **Implementation order**; task files `**Status:**` synced |
| **Open questions** | **Blocks** column empty or only truly blocked IDs |
| **Operator handoff** | External steps (import, deploy) in **Operator handoff** — not hidden plan tasks unless user requested or **Autonomy** pre-approves |
| **Autonomy** (parity/migration) | § **Autonomy & authorization** present when plan claims autonomous execution; escalation rules explicit |
| **Scope boundary** (domain migration) | Domain vs global/shared paths listed when edits touch theme or shared architecture |
| **Plan lineage** | Child plan linked from parent when parent marked complete with open follow-on |

**Report:** List any failed checks and fix them in the plan before marking done.

## Out-of-band completion

When work finishes outside sequential-implementation:

1. Mark task `✅` in **Phases** + task file `**Status:**`.
2. **Remove** ID from **Implementation order** (do not leave with “skip” comments — remove the line).
3. Update **Context references** purposes.
4. Rewrite later task specs if outcomes changed.
5. Re-run **Handoff readiness checklist**.

## Plan update workflow (extend / re-sync)

When adding a phase, parity round, or new tasks to an existing plan:

1. Read current plan end-to-end.
2. Add phase row + task row(s) in **Phases**; create `.local/<slug>/tasks/<id>.md` for non-trivial work.
3. Append **only new open IDs** to **Implementation order** (never re-add completed IDs).
4. Update **Progress summary**, header `(next: …)`, **Context references**.
5. If parity/migration: add scoreboard or invocation spec inline or link skill (`improve-parity`).
6. Update **Fresh chat handoff** for the new next task.
7. Run **Handoff readiness checklist**; bump `last_updated` and `version` if structure changed materially.

## Target vs current state (migration plans)

- Banner under title: **target** (docs) vs **current** (code).
- Canonical specs in **Context references**.
- Prefer verify tasks over duplicate doc writes when docs already landed.

## Before writing (new plan)

1. Confirm **project root** (git root).
2. Gather scope, constraints, success criteria.
3. Separate task details from durable knowledge (**documentation** skill).
4. Confirm external-environment requests (**External environment boundary**).

## External environment boundary (mandatory)

No tasks mutating GitHub, remote deploy, hosted datasets, etc. unless the user **explicitly** asked **or** the plan § **Autonomy & authorization** pre-approves them (e.g. CMS import via MCP/CLI). Prefer **Operator handoff** + runbook when autonomy is silent.

## Plan directory layout (mandatory)

**Every plan gets a dedicated support folder; the entry point stays at `.local/` root.** Task IDs (`1.1`, `2.3`, …) live only inside that folder so they never collide across plans.

```
.local/
  <slug>-plan.md           # Main plan — sole entry point for sequential-implementation
  <slug>/
    decisions.md            # Locked decisions (optional but recommended)
    architecture.md         # Target layout, inventory (optional)
    tasks/
      1.1.md
      2.1.md
```

| Rule | Detail |
|------|--------|
| **Slug** | Short kebab-case name (e.g. `date-input-migration`, `session-context-perf`) |
| **Entry point** | `.local/<slug>-plan.md` — pass this path to `sequential-implementation` |
| **Support folder** | `.local/<slug>/` — decisions, architecture, `tasks/`, runbooks; **not** the main plan file |
| **Task files** | `.local/<slug>/tasks/<task-id>.md` only — **never** a repo-wide `.local/tasks/` |
| **Phase links** | From the main plan, link tasks as `[1.1.md](<slug>/tasks/1.1.md)` |
| **Legacy** | Plans with `plan.md` inside `<slug>/` or flat `.local/tasks/` — migrate when touching the plan |

## Output locations

Follow the **`documentation`** skill. For plans:

| Content | Path | Purpose |
|---------|------|---------|
| Main plan | `.local/<slug>-plan.md` | Phases, task index, progress — keep lean; **entry point** |
| Task details | `.local/<slug>/tasks/<task-id>.md` | Large or multi-file task specs |
| Initiative reference | `.local/<slug>/decisions.md`, `architecture.md`, … | Short-term decisions, design targets |
| Long-term agent knowledge | `.context/` (+ `index.md`) | Stable architecture, conventions — not epic-specific |
| Long-term human docs | `docs/` (+ `README.md`) | Durable documentation for people |

Create `.local/<slug>/` and `.local/<slug>/tasks/` when authoring a new plan; write `.local/<slug>-plan.md` last. Add `.local/` to `.gitignore` when the repo does not already ignore it.

## Content placement

Put in the **plan or task file** only what the executor needs for that task.

Move elsewhere:

- Locked decisions, design targets, epic-specific architecture → `.local/<slug>/` (link from plan)
- Stable project conventions agents reuse → `.context/` (update `index.md`)
- Durable human reference → `docs/` (update `README.md`)
- Repeated background duplicated across tasks → one `.local/<slug>/` or `.context/` file, link from each task

## Task sizing (mandatory)

**One task ID = one `{{impl_agent_name}}` spawn** ({{#cursor}}`model="{{impl_agent_model}}"`, {{/cursor}}foreground). A task must be finishable in a **single subagent session** with one primary verification path — not a multi-hour epic, not a sequence of follow-up spawns.

When drafting or extending a plan, **split until every open task passes** the checklist below. Re-run after scope grows mid-initiative.

## Task-fit checklist (mandatory per open task)

Apply to **each open task** (read linked `.local/<slug>/tasks/<id>.md` when present). **Fail any row → split** the task into new IDs (e.g. `3.2` → `3.2` + `3.3`) and update **Implementation order**.

| # | Criterion | Pass when | Fail → split when |
| --- | --- | --- | --- |
| 1 | **One outcome** | Summary is one concrete deliverable a reviewer can sign off | Summary joins unrelated outcomes with “and” (e.g. tokens **and** layout **and** CMS seed **and** parity) |
| 2 | **One session** | Reasonable for one `{{impl_agent_name}}` spawn without a planned follow-up spawn to finish the same ID | Would need multiple implementation runs, or supervisor already expects a follow-up for the same ID |
| 3 | **Bounded scope** | ≤8 primary paths in **In scope** / task spec, or one cohesive subsystem (e.g. all under `SanityCmsService` footer paths) | >8 primary paths, or 3+ **unrelated** subsystems (e.g. Studio schema + React layout + MCP content import) |
| 4 | **Acceptance cap** | ≤7 acceptance criteria, all serving the same outcome | >7 criteria, or criteria that clearly belong in separate tasks |
| 5 | **Single verify track** | One primary **Verification** command or one manual check path | Multiple independent verify tracks (e.g. full parity suite **and** CMS import **and** schema deploy) |
| 6 | **No investigate + build** | Implementation only, or analysis is a separate report-only task ID | Same ID mixes spike/audit/gap analysis with production code changes |
| 7 | **Sequenced deps only** | Depends on prior tasks only where **Implementation order** already sequences them; **Out of scope** defers adjacent work | Acceptance requires unfinished work from a later ID, or overlaps another open task's scope |
| 8 | **Vertical slice OK** | Multi-file / multi-package edits are one GROQ→props→UI slice, token+SCSS for one surface, or deletion sweep | Unrelated packages or layers bundled without a single user-visible slice |

### When to split (patterns)

**Split** into separate task IDs:

- Schema + React UI + CMS seed + visual parity verify
- Phase umbrella (“implement footer”, “fix customers parity”)
- Research task + fix task in one ID
- Global shared refactor + feature work (unless plan § **Scope boundary** pre-approves)

**Keep together**:

- One vertical slice (GROQ → normalize → props → component)
- Token palette + SCSS map for the same chrome surface
- Cleanup/deletion grep + build for one retirement manifest
- CMS content patch only (OAuth MCP) separate from code layout

### Splitting procedure

1. Add new rows in **Phases** with new IDs; create `.local/<slug>/tasks/<id>.md` for non-trivial splits.
2. Move scope, acceptance, and verify from the oversized task into new tasks; tighten **Out of scope** on each.
3. Insert new IDs in **Implementation order** in dependency order; remove the oversized ID or replace with the first slice.
4. Update **Fresh chat handoff** `(next: …)` and **Context references** if new artifacts appear.
5. Re-run **Handoff readiness checklist**.

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

Use accurate purpose text (date, “target architecture”, “legacy — replace in task X”) — not unverified “to update”.

Tasks with `—` in **Phases** rely on initiative refs above, not extra task files.

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
2. If the task has a linked `.local/<slug>/tasks/<id>.md`, update its `**Status:**` line to match.
3. Recompute **Progress summary** phase rows (`✅` when all phase tasks complete; `🔄` when any in progress; `⬜` otherwise).
4. Update header `**Last updated:**` and frontmatter `last_updated` (today's date).
5. Set frontmatter `status: in_progress` on first completed task; `status: complete` when all tasks are `✅`.
6. Resolve or add **Open questions** if the task surfaced new blockers or decisions.
7. If new files were created that future tasks need, add them to **Context references** immediately.

### During execution

- Do **not** start the next task until the plan is updated.
- Subagents do **not** edit the plan — the supervisor or implementing agent does.
- Prefer updating the plan over leaving progress in chat only.

### Delegation template (include when § Autonomy present)

Every `{{impl_agent_name}}` `prompt` in sequential-implementation should copy the plan’s **Authorization** block: project root, allowed operations, forbidden global scope, “do not update the plan”, autonomy/escalation pointer.

### Fresh chat handoff

**Single entry point:**

/sequential-implementation <project-root>/.local/<slug>-plan.md

1. **Project root:** …
2. Read this plan (Progress summary, Context references, scoreboard if any).
3. Load `.agents/skills/project-best-practices/SKILL.md` when under `.agents/`; open task-relevant `references/` from Context references.
4. Apply **code** user rule for source-editing tasks — run its checklist before marking each task done.
5. Load initiative refs from Context references.
6. **Next task:** `<id>` only — open `.local/<slug>/tasks/<id>.md`.
7. Load task-specific skills listed in task spec or phase (e.g. `~/.agents/skills/improve-parity/SKILL.md`, `sanity-best-practices`, `sanity-data-handling`).
8. Delegate `{{impl_agent_name}}`{{#cursor}} (`model="{{impl_agent_model}}"`){{/cursor}} with **Conventions** (project-best-practices + **code** rule) + plan **Authorization** when § Autonomy present; supervisor updates plan after each task.
9. **Continue autonomously** through **Implementation order**; pause only on plan § **User escalation required** (not fixed task IDs).
10. Prerequisites: …
```

Adjust steps for initiative; **never** omit single entry point or next task ID.

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
2. Check `<project-root>/.agents/skills/project-best-practices/SKILL.md`; map open tasks to **Conventions coverage** refs.
3. Write `.local/<slug>/` decisions/architecture as needed; durable conventions to agent `references/` or `docs/` when the initiative defines long-term rules.
4. Write task detail files for non-trivial tasks (paths, **Out of scope**, **Verification** when spawn-sized but not obvious).
5. Run **Task-fit checklist** on every open task; split and add task files until all pass.
6. Write `.local/<slug>-plan.md` last.
7. **Handoff readiness checklist** — fix all failures (or run **`check-plan`** to verify).
8. Tell user: `/check-plan <plan-path>` then `/sequential-implementation <plan-path>` in a fresh chat.

## Authoring rules

1. **Task IDs:** `<phase>.<sequence>` (e.g. `2.3`). Unique across the plan.
2. **One spawn per task:** Each ID is one `{{impl_agent_name}}` delegation — see **Task sizing**.
3. **Implementation order = open tasks only** — mandatory re-sync when tasks complete.
4. **Independence:** Each task should be delegatable alone; split mixed work into separate IDs.
5. **Phases are labels:** Tasks are delegatable units; never one umbrella task per whole phase unless truly one spawn.
6. **Progress:** Plan owns the summary table and per-task status columns — single source of truth.
7. **Lean plan:** Move specs to linked files; keep the plan as the **index** — never orphan detail outside **Context references** or task links.
8. **Self-contained:** **Context references** enumerates all files for a fresh chat; **Plan maintenance** defines how to keep progress current.
9. Fresh chat handoff **required** — not optional.
10. **Ready gate:** Set frontmatter `status: ready` only when **Handoff readiness checklist** passes.
11. **External environments:** Never add PR/deploy/import/hosting tasks by default; hand off to the user in decisions or runbook text instead.
12. **Re-sync before handoff:** If conventions or docs change after the plan was drafted, update the plan before telling the user to run `sequential-implementation`.
13. Re-run checklist after any structural edit.
14. **Conventions coverage:** Source-editing plans list project-best-practices (+ task-relevant references and Sanity siblings) and call out **code** user rule in **Fresh chat handoff**.
15. **Task-fit:** No open task fails **Task-fit checklist** — split before `status: ready`.

## Do not

- Put task files in a shared `.local/tasks/` directory — **always** `.local/<slug>/tasks/`.
- Put the main plan inside `.local/<slug>/` — **always** `.local/<slug>-plan.md` at `.local/` root.
- Leave `✅ Complete` IDs in **Implementation order**.
- Fresh chat handoff that says “start at 1.1” when only `8.1` is open.
- Mark ready without checklist.
- Plan tasks for PR/deploy/commit unless user requested or plan § Autonomy pre-approves.
- Embed full product briefs in the plan when `.local/<slug>/` is more appropriate.
- Leave implementation-relevant files unlisted in **Context references**.
- Omit project-best-practices references when the plan touches blocks, components, styling, tokens, or CMS — or omit **code** user rule from **Fresh chat handoff** when tasks edit source.
- Create tasks without IDs or without an **Implementation order** section.
- Mark `status: ready` while open questions block specific tasks (list them in Open questions with **Blocks** column).
- Context reference purposes that say “to update” when that work is already done.
- One mega-task spanning schema + UI + docs, or multiple independent areas in one ID.
- Merging investigation and implementation when exploration scope is still unclear.
- Phase-level umbrella tasks ("implement frontend") without spawn-sized task breakdown.
- Tasks whose acceptance criteria require another open task — reorder **Implementation order** or split.
- Tasks that open/close/merge PRs, push to remote, deploy, or mutate hosted services **unless the user explicitly requested that action**.
- “Ship” or “done” phases that auto-include GitHub/CI/deploy work without a direct user ask — use local verify + handoff instead.
- Structural plan edits without re-running this skill's checklist.
