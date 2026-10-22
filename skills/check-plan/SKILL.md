---
name: check-plan
description: >-
  Single owner of plan readiness rules, used by create-plan (authoring audit) and
  sequential-implementation (pre-flight). Verifies an implementation plan is
  handoff-ready for sequential-implementation in a fresh chat — structure,
  Decisions and Change log sections, open-only implementation order, linked task
  and note files, small tasks with acceptance checks and bounded scope, agents
  (principal/expert user-agreed), autonomy/scope when claimed. Invoke with the plan
  file path. Read-only audit; use create-plan to fix gaps.
---

# Check plan

{{block:tool-note}}

Answer: **Is this plan file a single entry point for `sequential-implementation` in a fresh chat?**

**Read-only.** Never edit the plan, task files or notes. Fixes belong to **`create-plan`**.

This skill owns the readiness checklist. `create-plan` reads it before authoring and runs it as an audit at the end; `sequential-implementation` runs it as pre-flight and starts only on `READY`. Callers pass this skill's SKILL.md path and the plan path to a read-only `senior` subagent via `{{tool:spawn-agent}}({{agent:senior}})`; that subagent performs the audit and returns the report.

## Invocation

The user (or a calling skill) provides **one plan file path** (required):

```
{{tool:skill-prefix}}check-plan <plan-path>
```

Resolve the path relative to a workspace root when not absolute. If no path is given, ask once.

## Procedure

1. **Read** the plan file end-to-end.
2. **Resolve project root** from the `**Project root:**` line, or the parent of `.local/` if missing (flag fail).
3. **Run the mechanical script** `scripts/check_plan_mechanical.py <plan-path>` (in this skill's directory; python3, standard library only; when python3 or the script is unavailable, run the checks it covers by hand). It prints `CHECK | LOCATION | MESSAGE` per finding and exits 1 when it prints any line, including `PARSE`. It covers A5, A6, A7, A8, B1, B4, C9, C10 and C11; every line it prints is a finding to carry into the report, enriched with the check name and task or decision title before user-facing output, and a `PARSE` line (a format it could not parse reliably) must be checked by hand.
4. **Run every other check** in § Checklist and **record every finding**. Verify on disk where applicable: open and read the linked files, do not assume. The audit never stops at the first failing check: all checks run, over every task, before the report is emitted.
5. **Emit report** (§ Output format) once, after all checks have run, with every finding in one table.
6. **Verdict:** `READY` only if every applicable check passes (zero **fail**). Warnings do not block `READY` but must be listed.

If `status: complete` and **Implementation order** is empty with every task done in the phase tables, the verdict is `COMPLETE` (nothing to run).

## Severity

- **fail**: a requirement is missing or violated and a fresh chat would stall, run the wrong task, run an unapproved agent, or run a task that cannot be verified. Blocks `READY`.
- **warn**: advisory quality issue that does not change what runs or how it is verified. Listed, never blocks.
- **skip**: not applicable (a conditional check whose condition is absent).

Every check below is **fail** unless its row says **warn**.

## Single-pass rule

One audit run reports **every** finding. The report lists each finding as one row with the check title (optional ID in brackets), the location (plan line, or task title plus file path), what is wrong and the concrete fix. Findings are never split across runs: a run that reports only the first failing check, or only one task's problems while others have the same kind, is incomplete. A check that fails for several tasks produces one row per task and location. A re-run after fixes should find nothing that the earlier run could already have found.

## User-facing wording

Name checks, findings, tasks, decisions and sections by title or short plain-language description in every user-facing report, including audit tables, locations and next-task handoffs. IDs may follow in brackets; they are never the sole subject. Keep machine IDs in plan tracking and raw script output internally; resolve them to meaningful names before presenting the report.

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
| A10 | **Agent approvals table** | `## Agent approvals` exists with columns Task ID, Agent, Justification, Agreed by user (rows only for `principal`/`expert` tasks; empty otherwise) |
| A11 | **Plan maintenance** | Section present with per-task update rules |
| A12 | **Fresh chat handoff** | `### Fresh chat handoff` (or equivalent) with numbered steps naming the next task by title (optional ID in brackets) and skills to load |
| A13 | **Single entry point** | Handoff includes the exact `{{tool:skill-prefix}}sequential-implementation <plan-path>` invocation matching this file |
| A14 | **Open questions** | Table present; **Blocks** column empty or only IDs that are truly ⏸ blocked |
| A15 | **Decision Affects** (**warn**) | Each Decision's **Affects** list names every task whose task file or plan row cites that Decision; `all ...` wording covers every task |
| A16 | **Superseded log rows** (**warn**) | A **Change log** row whose change a later row reverses or replaces is marked superseded (for example `Superseded by <date>` in its Change cell) |

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
| C12 | **Agent field** | Every task row in **Phases** has an **Agent** value that follows the Delegation scope table (lowest tier that fits) |
| C13 | **Agent approvals** | Every task with a `principal` or `expert` Agent has a row in `## Agent approvals` with a user-agreed date and a justification citing a Delegation scope table criterion (highest-complexity recommendation, or critical high-impact recommendation among options); a justification citing size or breadth alone fails; none are unapproved |
| C14 | **Blocked tasks** | Any ⏸ task has its reason in **Open questions** or the phase row, and is not listed in **Implementation order** ahead of its unblock |
| C15 | **Runnable next task** | At least one delegable open task passes C1–C13, or the plan is legitimately `complete` |
| C16 | **No contradictions** | No two statements contradict each other across **Decisions**, the plan's **Change log** and the task files (for example a Decision value that a task contradicts, a task acceptance that a later Change log row reversed, two tasks owning the same outcome with different values); each contradiction is one finding naming both locations |
| C17 | **Acceptance commands verified** (**warn**) | Every command named in a task's **Acceptance** is run by that task's **Verification**, or is covered by the plan's verification gate that the task cites |

A vertical slice (one data query → props → UI path, tokens plus styles for one surface, a deletion sweep) is one outcome even across several files; unrelated packages or layers bundled without a single slice are not.

### D — Conditional (when the plan claims them)

| ID | Check | Pass when |
| --- | --- | --- |
| D1 | **Autonomy** | If the plan says "autonomous" or has auto-decisions: § **Autonomy & authorization** with pre-approved operations, auto-decisions, user escalation, and a delegation **Authorization** template |
| D2 | **Scope boundary** | If the plan changes shared or root configuration (root config files, theme, shared architecture) or a parity/migration plan touches theme or shared architecture: § **Scope boundary** with domain vs global paths. **fail** when such a plan has no § **Scope boundary** (never downgraded to a warning) |
| D3 | **Plan lineage** | If a banner says "continues in child plan": parent `status: complete`, child path exists and is linked |
| D4 | **Operator handoff** | Commit, deploy, import and other external steps are in **Operator handoff** or pre-approved in § Autonomy; no task mutates a remote environment otherwise |
| D5 | **Scoreboard / parity** | If parity plan: baseline scoreboard or link to audit file; `improve-parity` in handoff or context when verify tasks exist |
| D6 | **Target vs code** | If target docs differ from current code: banner under the title marks **target** vs **current**, and canonical specs are in **Context references** |

### F — User work and execution gates (mandatory)

Inspect existing task files, handoffs, maintenance, approvals, open questions and authorization sections; no additional plan section is required.

| ID | Check | Pass when |
| --- | --- | --- |
| F1 | **Executor-owned bookkeeping** | The executor owns plan and task-file updates, approvals, questions and status; the user may report answers and manual outcomes in chat only, with no duplicated file edits |
| F2 | **Justified manual gates** | Each required manual action or pause has a concrete authority, access or unresolved product/policy reason; checks runnable by the executor locally are executor work; no redundant phase confirmations or approvals for `junior` through `senior` |
| F3 | **Grouped user inputs** | Independent questions knowable together are collected in one round and compatible manual milestones are grouped; dependent questions or authorization boundaries are not collapsed; safe independent work may continue within sequencing and dependency limits while required input is pending |
| F4 | **Persistent authorization** | Handoffs honor recorded approvals and confirmed scope, including specific shared paths and actions; only scope expansion, unapproved shared changes or genuinely unresolved decisions require renewed input |
| F5 | **Title-first handoff** | User-facing instructions, reports and next-task handoffs name tasks, decisions and checks by title or short description, with IDs only optional bracketed references |

### E — Project conventions (conditional)

| ID | Check | Pass when |
| --- | --- | --- |
| E1 | **project-best-practices** | If `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists: listed in **Context references**, and **Fresh chat handoff** mentions it for implementation tasks |
| E2 | **Task-relevant references** | When `project-best-practices` exists and its router names references per task type: for each task type in the plan, the matching `.agents/skills/project-best-practices/references/<topic>.md` is in **Context references** or handoff; skip when it names none |
| E3 | **Sibling skills** | When the project-best-practices router names sibling skills for a task type present in the plan: those skills are in **Context references** or handoff |
| E4 | **code user rule** | Open tasks edit source: **Fresh chat handoff** requires the **code** user rule checklist before marking tasks done |

## Output format

```markdown
# Plan check: <filename>

**Path:** `<absolute plan path>`
**Project root:** `<absolute root>`
**Verdict:** READY | NOT READY | COMPLETE

## Summary

<1–2 sentences: counts of fails and warns>

## Checks

| Check | Status | Notes |
|-------|--------|-------|
| Frontmatter [A1] | pass / fail / warn / skip | … |
| … | | |

## Findings

| # | Check | Location | Finding | Fix |
|---|-------|----------|---------|-----|
| 1 | Implementation order [A6] (fail) | plan line 482, Add cache layer [2.3] | … | … |
| 2 | Decision Affects [A15] (warn) | plan line 94, Cache invalidation [D4] | … | … |

## Fresh chat entry

\`\`\`
{{tool:skill-prefix}}sequential-implementation <plan-path>
\`\`\`

**Next task:** <task title> [<id>] · **Task spec:** `<path>`
```

The **Findings** table holds every fail and every warn, fails first, in check order within each group. `Fix` is concrete (the exact edit), never "review" or "consider". With no findings the table is replaced by `None.`. Per-task checks (section C) are reported by task title, with optional bracketed IDs, in Notes and in Findings.

## After NOT READY

1. Return the complete report and **Findings** table to the caller; a standalone audit remains read-only and does not instruct the user to edit files.
2. When called by `sequential-implementation`, pass the full findings to `create-plan` for repair within the original goal, scope and approved Decisions, then re-audit automatically; no additional proceed approval is needed. Only genuinely user-dependent decisions or authorization halt for input.
3. Do not repeat an unchanged repair/audit failure without progress: stop and explain the concrete blocker. Execution starts or resumes only on `READY`.

## Related skills

| Skill | When |
| --- | --- |
| **`create-plan`** | Reads this checklist before authoring; runs it as the final audit; fixes gaps |
| **`sequential-implementation`** | Runs this as pre-flight; requires `READY` before starting |
| **`update-harness`** | After editing this skill file |

## Do not

- Mark `READY` with any **fail** row
- Stop at the first failing check or report findings across several runs
- Assume task or note files exist without reading disk
- Edit the plan, task files or notes during a check
- Substitute chat history for missing plan sections
