---
name: check-plan
description: >-
  Verify an implementation plan is handoff-ready for /sequential-implementation
  in a fresh chat — structure, open-only implementation order, linked task files,
  context refs on disk, fresh chat handoff, autonomy/scope when claimed. Invoke
  with the plan file path. Read-only audit; use create-plan to fix gaps.
disable-model-invocation: false
---

# Check plan

Answer: **Is this plan file a single entry point for `/sequential-implementation` in a fresh chat?**

**Read-only.** Do not edit the plan unless the user explicitly asks to fix gaps (then use **`create-plan`**).

## Invocation

The user provides **one plan file path** (required):

```
/check-plan uploadcare.com/.local/customers-parity-plan.md
```

```
/check-plan /Users/jacek/Projects/uploadcare.com/.local/my-feature-plan.md
```

Resolve path relative to a workspace root when not absolute. If no path given, ask once.

## Procedure

1. **Read** the plan file end-to-end.
2. **Resolve project root** from `**Project root:**` line, or parent of `.local/` if missing (flag fail).
3. **Run every check** in § Checklist — verify on disk where applicable (`Glob`/`Read`, not assumptions).
4. **Emit report** (§ Output format).
5. **Verdict:** `READY` only if zero **fail** checks. Warnings do not block `READY` but must be listed.

Optional: if `status: complete` and implementation order empty, verdict can be `COMPLETE` (nothing to run) when phase tables show all tasks done.

## Checklist

### A — Structure (required)

| ID | Check | Pass when |
| --- | --- | --- |
| A1 | **Frontmatter** | `plan: true`, `version`, `status`, `last_updated` present |
| A2 | **Project root** | `**Project root:**` absolute path; directory exists |
| A3 | **Header next task** | `**Last updated:**` includes `(next: **<id>**)` matching first open task in **Implementation order**, or `(next: —)` / omitted only when plan `status: complete` |
| A4 | **Progress summary** | Table or equivalent with phases and status |
| A5 | **Phases** | At least one `### Phase N` with task table; every task has `<phase>.<sequence>` ID |
| A6 | **Implementation order** | Section exists; lists **only** open task IDs — no `✅ Complete` / superseded IDs |
| A7 | **Phase table vs order** | Every ID in **Implementation order** appears in **Phases** with non-complete status (or ⏸ with documented block) |
| A8 | **Plan maintenance** | Section present with per-task update rules |
| A9 | **Fresh chat handoff** | `### Fresh chat handoff` (or equivalent) with numbered steps |
| A10 | **Single entry point** | Handoff includes exact `/sequential-implementation <plan-path>` invocation matching this file |
| A11 | **Open questions** | Table present; **Blocks** column empty or only IDs that are truly ⏸ blocked |

### B — Linked artifacts (verify on disk)

| ID | Check | Pass when |
| --- | --- | --- |
| B1 | **Context references** | Every linked path under project root **exists** (skip `~/.agents/…` and sibling `../` repos — note as external) |
| B2 | **Context purposes** | No stale “to update in task X” for already-✅ work |
| B3 | **Initiative refs** | `.local/<slug>/decisions.md` etc. exist when referenced |
| B4 | **Task files** | Every non-`—` Details link resolves to a readable `.md` under project root |
| B5 | **Task status sync** | Open tasks in order are not `✅ Complete` in linked task file `**Status:**` |
| B6 | **Target artifacts** | Rows marked **Target (task)** — optional fail if task is next open and file missing |

### C — Composer / execution fit

Apply **Composer-fit checklist** (`create-plan`) to **each open task** (read linked task spec). **Fail** the task's row if any criterion fails.

| ID | Check | Pass when |
| --- | --- | --- |
| C1 | **One outcome** | No open task summary bundles unrelated deliverables (tokens + layout + CMS + parity in one ID) |
| C2 | **One session** | Each open task is reasonable for one `composer` spawn without a planned second spawn for the same ID |
| C3 | **Bounded scope** | Each open task ≤8 primary in-scope paths or one cohesive subsystem; not 3+ unrelated subsystems |
| C4 | **Acceptance cap** | Each open task has ≤7 acceptance criteria serving one outcome |
| C5 | **Single verify track** | Each open task has one primary verification path (not independent parity + import + deploy tracks) |
| C6 | **No investigate + build** | No open task mixes spike/audit with implementation in the same ID |
| C7 | **Runnable next task** | At least one delegable open task passes C1–C6, **or** plan legitimately `complete` |
| C8 | **Blocked tasks** | Any ⏸ task has reason in **Open questions** or phase row; not listed in **Implementation order** ahead of unblock |

### D — Conditional (when plan claims them)

| ID | Check | Pass when |
| --- | --- | --- |
| D1 | **Autonomy** | If plan says “autonomous” or has auto-decisions: § **Autonomy & authorization** with pre-approved ops, auto-decisions, user escalation, composer **Authorization** template |
| D2 | **Scope boundary** | If parity/migration touches theme or shared architecture: § **Scope boundary** with domain vs global paths |
| D3 | **Plan lineage** | If banner says “continues in child plan”: parent `status: complete`, child path exists and linked |
| D4 | **Operator handoff** | Commit/deploy/import either in **Operator handoff** or pre-approved in § Autonomy |
| D5 | **Scoreboard / parity** | If parity plan: baseline scoreboard or link to audit file; `improve-parity` in handoff or context when verify tasks exist |

### E — Project conventions (conditional)

| ID | Check | Pass when |
| --- | --- | --- |
| E1 | **project-best-practices** | If `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists: listed in **Context references** and **Fresh chat handoff** mentions it for implementation tasks |
| E2 | **Task-relevant references** | When plan touches blocks/components: `placement.md` + `website-structure.md` in context or handoff; styling tasks → `styling.md`; CMS blocks → `cms-blocks.md` |
| E3 | **Sanity siblings** | When plan has Sanity schema/GROQ/Studio/content tasks: `sanity-best-practices` and/or `sanity-data-handling` in **Context references** or handoff per task type |
| E4 | **code user rule** | When open tasks edit source: **Fresh chat handoff** requires **code** user rule checklist before marking tasks done |

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

- **fail** → must fix for `READY`
- **warn** → recommend fix; does not block `READY`
- **skip** → not applicable (e.g. D2 when plan has no shared-architecture edits)

## After NOT READY

1. Tell user to fix gaps (or offer to fix with **`create-plan`** if they ask).
2. Re-run **`check-plan`** on the same path after edits.
3. Do not start **`sequential-implementation`** until `READY`.

## Related skills

| Skill | When |
| --- | --- |
| **`create-plan`** | Author or fix plan structure |
| **`sequential-implementation`** | Execute after `READY` |
| **`update-harness`** | After editing this skill file |

## Do not

- Mark `READY` with any **fail** row
- Assume task files exist without reading disk
- Edit the plan during a check-only invocation
- Substitute chat history for missing plan sections
