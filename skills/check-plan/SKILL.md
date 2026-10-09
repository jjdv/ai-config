---
name: check-plan
description: >-
  Single owner of plan readiness rules, used by create-plan (authoring audit) and
  sequential-implementation (pre-flight). Verifies an implementation plan is
  handoff-ready for /sequential-implementation in a fresh chat — structure,
  Decisions and Change log sections, open-only implementation order, linked task
  and note files, small tasks with acceptance checks and bounded scope, agents
  (non-standard user-agreed), autonomy/scope when claimed. Invoke with the plan
  file path. Read-only audit; use create-plan to fix gaps.
disable-model-invocation: false
---

# Check plan

{{block:tool-note}}

Answer: **Is this plan file a single entry point for `/sequential-implementation` in a fresh chat?**

**Read-only.** Never edit the plan, task files or notes. Fixes belong to **`create-plan`**.

This skill owns the readiness checklist. `create-plan` reads it before authoring and runs it as an audit at the end; `sequential-implementation` runs it as pre-flight and starts only on `READY`. Callers pass this skill's SKILL.md path and the plan path to a read-only `standard` subagent via `{{tool:spawn-agent}}({{agent:standard}})`; that subagent performs the audit and returns the report.

## Invocation

The user (or a calling skill) provides **one plan file path** (required):

```
/check-plan <plan-path>
```

Resolve the path relative to a workspace root when not absolute. If no path is given, ask once.

## Procedure

1. **Read** the plan file end-to-end.
2. **Resolve project root** from the `**Project root:**` line, or the parent of `.local/` if missing (flag fail).
3. **Run every check** in § Checklist. Verify on disk where applicable: open and read the linked files, do not assume.
4. **Emit report** (§ Output format).
5. **Verdict:** `READY` only if every applicable check passes (zero **fail**). Warnings do not block `READY` but must be listed.

If `status: complete` and **Implementation order** is empty with every task done in the phase tables, the verdict is `COMPLETE` (nothing to run).

## Severity

- **fail**: a requirement is missing or violated and a fresh chat would stall, run the wrong task, run an unapproved agent, or run a task that cannot be verified. Blocks `READY`.
- **warn**: advisory quality issue that does not change what runs or how it is verified. Listed, never blocks.
- **skip**: not applicable (a conditional check whose condition is absent).

Every check below is **fail** unless its row says **warn**.

## Checklist

### A — Structure

| ID | Check | Pass when |
| --- | --- | --- |
| A1 | **Frontmatter** | `plan: true`, `version`, `status`, `last_updated` present |
| A2 | **Project root** | `**Project root:**` absolute path; directory exists |
| A3 | **Header next task** | `**Last updated:**` includes `(next: **<id>**)` matching first open task in **Implementation order**, or `(next: —)` / omitted only when plan `status: complete` |
| A4 | **Progress summary** | Table or equivalent with phases and status |
| A5 | **Phases** | At least one `### Phase N` with task table; every task has a unique `<phase>.<sequence>` ID |
| A6 | **Implementation order** | Section exists; lists **only** open task IDs, no `✅ Complete` or superseded IDs |
| A7 | **Phase table vs order** | Every ID in **Implementation order** appears in **Phases** with non-complete status (or ⏸ with documented block); completed tasks stay in **Phases** with `✅` |
| A8 | **Decisions section** | `## Decisions` exists holding cross-task decisions (interfaces, data shapes, ordering, naming) with IDs; it may be empty only if no task references a decision |
| A9 | **Change log section** | `## Change log` exists, recording replans (what changed, why); may be empty on a never-replanned plan |
| A10 | **Agent approvals table** | `## Agent approvals` exists with columns Task ID, Agent, Justification, Agreed by user (rows only for non-`standard` tasks; empty otherwise) |
| A11 | **Plan maintenance** | Section present with per-task update rules |
| A12 | **Fresh chat handoff** | `### Fresh chat handoff` (or equivalent) with numbered steps naming the next task ID and skills to load |
| A13 | **Single entry point** | Handoff includes the exact `/sequential-implementation <plan-path>` invocation matching this file |
| A14 | **Open questions** | Table present; **Blocks** column empty or only IDs that are truly ⏸ blocked |

### B — Linked artifacts (verify on disk)

| ID | Check | Pass when |
| --- | --- | --- |
| B1 | **Context references** | Every linked path under project root **exists** (note installed-skill paths under the user home and sibling `../` repos as external, not failures) |
| B2 | **Context purposes** | No stale "to update in task X" for already-✅ work |
| B3 | **Initiative refs** | Files such as `brief.md` or `architecture.md` in the plan's directory exist when referenced |
| B4 | **Task files** | Every non-`—` Details link resolves to a readable `.md` under project root |
| B5 | **Task status sync** | Open tasks in order are not `✅ Complete` in the linked task file `**Status:**` |
| B6 | **Plan directory layout** | Entry point at `.local/<slug>-plan.md`; supporting files (task files, `notes/`, brief, architecture) in the plan's own `.local/<slug>/` directory, none in a shared flat `.local/tasks/` |
| B7 | **Target artifacts** | **warn** only: rows marked **Target (task)** whose file is missing while the task is next open |

### C — Task contract and fit (each open task)

Read each open task (plan row and linked task file). A task is **small**: one outcome, bounded scope, one verification. It is not required to be a full spec; the executing supervisor writes the spec at run time from the task, the Decisions section and the notes. Fail the task's row if any criterion fails.

| ID | Check | Pass when |
| --- | --- | --- |
| C1 | **One outcome** | Summary is one concrete deliverable a reviewer can sign off; not joined by "and" across unrelated outcomes (tokens and layout and CMS and parity) |
| C2 | **One session** | One spawn of its Agent, no planned follow-up spawn for the same ID |
| C3 | **Scope within 8 paths** | Scope lists expected files or areas, at most 8 primary paths, or one cohesive subsystem; not 3+ unrelated subsystems |
| C4 | **Acceptance check** | Task has an acceptance check or verification command with its expected result |
| C5 | **Acceptance cap** | At most 7 acceptance criteria, all serving the one outcome |
| C6 | **Single verify track** | One primary verification path, not independent parity, import and deploy tracks |
| C7 | **No investigate + build** | No task mixes spike, audit or gap analysis with implementation; analysis is a separate report-only ID that writes notes |
| C8 | **Sequenced deps only** | Depends only on earlier-sequenced tasks; acceptance does not require a later ID's work and does not overlap another open task |
| C9 | **Decision references** | Where a task depends on cross-task decisions (interfaces, data shapes, ordering, naming), it references them by ID and every referenced ID exists in **Decisions**; design choices are not left to the executor |
| C10 | **Notes in** | Every `Notes in` entry refers to a note that exists on disk or is listed in the `Notes out` of an **earlier** task in **Implementation order** |
| C11 | **Notes out** | Every `Notes out` path lies in the plan's `notes/` folder; no scout or analysis task omits `Notes out` |
| C12 | **Agent field** | Every task row in **Phases** has an **Agent** value (default `standard`) |
| C13 | **Agent approvals** | Every task with a non-`standard` Agent has a row in `## Agent approvals` with justification and a user-agreed date; none are unapproved |
| C14 | **Blocked tasks** | Any ⏸ task has its reason in **Open questions** or the phase row, and is not listed in **Implementation order** ahead of its unblock |
| C15 | **Runnable next task** | At least one delegable open task passes C1–C13, or the plan is legitimately `complete` |

A vertical slice (one GROQ → props → UI path, tokens plus styles for one surface, a deletion sweep) is one outcome even across several files; unrelated packages or layers bundled without a single slice are not.

### D — Conditional (when the plan claims them)

| ID | Check | Pass when |
| --- | --- | --- |
| D1 | **Autonomy** | If the plan says "autonomous" or has auto-decisions: § **Autonomy & authorization** with pre-approved operations, auto-decisions, user escalation, and a delegation **Authorization** template |
| D2 | **Scope boundary** | If parity/migration touches theme or shared architecture: § **Scope boundary** with domain vs global paths |
| D3 | **Plan lineage** | If a banner says "continues in child plan": parent `status: complete`, child path exists and is linked |
| D4 | **Operator handoff** | Commit, deploy, import and other external steps are in **Operator handoff** or pre-approved in § Autonomy; no task mutates a remote environment otherwise |
| D5 | **Scoreboard / parity** | If parity plan: baseline scoreboard or link to audit file; `improve-parity` in handoff or context when verify tasks exist |
| D6 | **Target vs code** | If target docs differ from current code: banner under the title marks **target** vs **current**, and canonical specs are in **Context references** |

### E — Project conventions (conditional)

| ID | Check | Pass when |
| --- | --- | --- |
| E1 | **project-best-practices** | If `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists: listed in **Context references**, and **Fresh chat handoff** mentions it for implementation tasks |
| E2 | **Task-relevant references** | Plan touches blocks/components: `placement.md` and `website-structure.md` in context or handoff; styling tasks: `styling.md`; CMS blocks: `cms-blocks.md` |
| E3 | **Sanity siblings** | Plan has Sanity schema/GROQ/Studio/content tasks: `sanity-best-practices` and/or `sanity-data-handling` in **Context references** or handoff per task type |
| E4 | **code user rule** | Open tasks edit source: **Fresh chat handoff** requires the **code** user rule checklist before marking tasks done |

## Output format

```markdown
# Plan check: <filename>

**Path:** `<absolute plan path>`
**Project root:** `<absolute root>`
**Verdict:** READY | NOT READY | COMPLETE

## Summary

<1–2 sentences>

## Checks

| ID | Status | Notes |
|----|--------|-------|
| A1 | pass / fail / warn / skip | … |
| … | | |

## Failed checks (fix before /sequential-implementation)

1. **A6** — …
2. …

## Warnings (non-blocking)

- …

## Fresh chat entry

\`\`\`
/sequential-implementation <plan-path>
\`\`\`

**Next task:** `<id>` · **Task spec:** `<path>`
```

Per-task checks (section C) are reported per task ID in Notes.

## After NOT READY

1. Tell the user to fix the gaps (or offer to fix with **`create-plan`** if they ask).
2. Re-run **`check-plan`** on the same path after edits.
3. **`sequential-implementation`** does not start until the verdict is `READY`.

## Related skills

| Skill | When |
| --- | --- |
| **`create-plan`** | Reads this checklist before authoring; runs it as the final audit; fixes gaps |
| **`sequential-implementation`** | Runs this as pre-flight; requires `READY` before starting |
| **`update-harness`** | After editing this skill file |

## Do not

- Mark `READY` with any **fail** row
- Assume task or note files exist without reading disk
- Edit the plan, task files or notes during a check
- Substitute chat history for missing plan sections
