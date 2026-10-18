---
name: sequential-implementation
description: >-
  Execute a plan task by task as a thin executor under the Delegation rules:
  audit the plan with check-plan (READY required), then for each task write a
  decision-complete run-time spec from the task, its Decisions and its notes,
  run the task's Agent, verify, update plan status. Plan issues trigger a
  replan via create-plan. Use when the user asks to implement, execute, or
  continue a plan step-by-step, or run /sequential-implementation on a plan path.
invocation: explicit
---

# Sequential implementation

{{block:tool-note}}

Act as a **thin executor** under **Delegation**: the supervisor writes each task's spec, the task's recorded **Agent** does the work, and the supervisor verifies and **updates progress as the last action** before starting the next task. Do not do task work yourself unless the user explicitly overrides.

## Run to completion (default)

Invoking this skill on a plan (including **continue** on an in-progress plan) means: execute **every** open task in **Implementation order** until a **Stop condition** applies. That is the default; the user does not need to repeat "keep going" each turn.

- After each successful task, go straight to **After a task** step 3 (**Next task**): delegate the next ID in the same session. Do **not** end the turn early just because one or several tasks finished.
- **One task succeeding is not a stop condition.** Finishing task 8.3 does not permit pausing before 8.4 unless a stop condition applies.
- User-visible progress while the run continues: update the plan file; the chat summary is optional and brief. Do **not** treat "report once" (below) as permission to stop after every batch of tasks.
- If the platform ends your turn while tasks remain and no stop condition applied, the **next** turn on the same plan should resume at the first open ID **without** asking whether to continue.

Only **Stop conditions** may end the run early (see below). Anything else — including polite offers to continue — is a violation.

## Plan contract

A plan task is small: one goal, bounded scope, acceptance check or verification command, references to **Decisions** by ID, `Notes in` and `Notes out`, and an Agent. It is not a decision-complete spec: you write that at run time. **`check-plan`** owns readiness rules; **`create-plan`** owns plan structure and replanning.

## Plan source

| Mode | When | Source |
| --- | --- | --- |
| **File** | User gives a plan path (e.g. `.local/feature-plan.md`) | Read from disk; pre-flight below |
| **Pasted** | User pastes the plan in the prompt | Use only what is pasted; if a task lacks goal, scope or verification, report it as a plan issue; add progress tracking per Plan templates if missing |

## Pre-flight (file plans)

1. Spawn a read-only `senior` subagent given the path of `check-plan`'s SKILL.md and the plan path; it returns the audit report.
2. Start only on verdict `READY`. On `NOT READY`, stop and report the failed checks by check name or plain description (not audit IDs alone); **`create-plan`** fixes them. On `COMPLETE`, report that nothing is left to run.
3. Flag ⏸ blocked tasks to the user before delegating (name each task by title; say what blocks it and what you need from the user, per **User actions** below when input is required).
4. Resolve the project root from the plan's `**Project root:**` line. Check whether `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists (it governs the Conventions block below).

## Per-task loop

Repeat until a stop condition applies:

1. **Pick** the first runnable task in **Implementation order**.
2. **Read** its plan row and task file, the **Decisions** it references and the notes in its `Notes in`.
3. **Write the spec** per **Delegation**: files, exact change, interfaces, out of scope, verification command, only the context needed. If you cannot write a spec the task's Agent can execute, it is a plan issue: go to **Replan flow**.
4. **Spawn** the task's Agent with the prompt below.
5. **Verify** deliverables: paths touched, verification command result, diff free of redundant comments (have them removed), drive-by churn and rule violations; when `project-best-practices` exists, compliance with it; when source files changed, the **code** user rule checklist.
6. **Update the plan** (Progress tracking), then decide the next action (After a task).

Sequential only: one task at a time unless the user explicitly requests parallel runs. Only the supervisor edits the plan; subagents never do.

**Reporting:** Per-task status lives in the plan file. In chat, give a **full** summary only when the **whole run** stops (all tasks done plus final review, or a stop condition). While the run continues, chat messages may be omitted or limited to blockers and escalations — never a "done for now" recap that invites the user to opt in to more work.

**User-facing reports:** Whenever you report to the user (blockers, escalations, final summary, replan notices, relayed questions, or why a stop condition applied), name tasks, decisions, sections, and findings by **title or short plain-language description**, not by plan IDs alone. Do not point the user at plan document IDs as the primary way to understand what you mean. An optional bracketed task or decision id only when two similar titles need disambiguation. The plan file may still use IDs for progress tracking; this rule applies to **chat only**.

### Task prompt

Self-contained and small; never pass the plan body or chat history. Include only what the Agent needs:

```markdown
Task ID: <id>
Level: 2
Goal: <one outcome>
Spec: <the run-time spec: files, exact change, interfaces, out of scope>
Verification: <command and expected result>
Notes in: <paths to note files the task reads, omit when none>
Notes out: <paths the task must write, omit when none>
Reference: <paths to Decisions or docs the task needs, omit when none>
Conventions: <only when project-best-practices exists: read `.agents/skills/project-best-practices/SKILL.md` first, then the task-relevant `references/` and `docs/` paths from the plan's Context references; write all code in compliance with it. For source edits also apply the **code** user rule checklist (intention-revealing names, small units, KISS/DRY, project conventions) before finishing>
Context: <`.context/` paths the plan lists, omit when none>
Comments: add no comments or doc comments unless the spec requires them; none that restate the code.
Naming: in Return to the supervisor, name sections, tasks, findings and decisions by title; include the plan id in brackets when it helps cross-reference — never id alone without a title. The supervisor relays to the user by title per **User-facing reports** above.
Return: summary, paths touched, verification result, blockers; or `needs upgrade: <tier> - <reason>`; or `needs split: <subtasks, each with suggested tier>`; or `question: <question>`; or `plan issue: <description>`
Do not update the plan; the supervisor does (including from user-reported results in chat).

## Authorization

**Project root:** `/absolute/path/to/repo`

The user already approved this task. You may read and write any file under the project root without asking for per-file permission. Do not edit outside this tree. Do not commit unless asked.
```

Run the Agent with the spawn call `{{tool:spawn-agent}}({{agent:standard}})` (the task's Agent in place of `standard`). When the plan has § **Autonomy & authorization**, use that plan's **Authorization** block instead of the generic one.

{{block:spawn-rule}}

Task Agents run as level 2 (this supervisor is level 1): per **Delegation** they may spawn subtasks, or return `needs split` / `needs upgrade`.

Never pick a heavier Agent than the plan records, except by escalation per **Delegation** step 4.

## Returns from an executing agent

- `needs upgrade: <tier> - <reason>`: handle per **Delegation** step 4 (a `principal` or `expert` Agent still needs user approval, recorded in the plan's **Agent approvals**, and only for a criterion in the Delegation scope table, never for size: an oversized task is split instead). Relay approval to the user with **User actions** (what to approve and why). On approval in chat, apply **User-reported results** (write **Agent approvals** in the plan); do not ask the user to edit the plan.
- `needs split: <subtasks>`: the task is oversized; **Replan flow**.
- `plan issue: <description>`: **Replan flow**.
- `question: <question>`: relay per **Delegation**, worded per the **ask-questions** skill; name the task by title (optional id in brackets only to disambiguate). Give the user **User actions** steps to answer. Mark the task `⏸ Blocked` with the question in **Open questions** until answered; on the user's chat reply, apply **User-reported results** and resume with the answer in the spec.

## Replan flow

Triggered by a `plan issue:` result, an oversized task, a task whose spec cannot be written, or a task needing a follow-up spawn for the same ID.

1. Stop the loop. Spawn a `staff` replan agent that follows `create-plan`'s replan mode, given the plan path and the issue.
2. Re-run the `check-plan` audit (Pre-flight step 1); resume only on `READY`.
3. Report the replan to the user in 1-2 lines (what changed and why, by task or decision **title**), even when no approval was needed. If the user must approve or act before you resume, follow **User actions** — do not send them to the plan alone.

Replan limits (defined in `create-plan`): edits only unfinished tasks, within the original goal and scope, no reversal of user-approved Decisions, no `principal` or `expert` assignment without recorded user approval. Anything beyond needs the user's approval before the plan changes; spell out what you need in chat per **User actions**.

## Progress tracking

Progress lives in the plan file (file mode) or in the plan text maintained in replies (pasted mode); the plan is the source of truth. Follow the plan's **Plan maintenance** section. Default checklist after each task:

1. Set the task row to `✅ Complete` (or `⏸ Blocked` with reason).
2. Sync the linked task file `**Status:**` line if present.
3. Remove the task ID from **Implementation order**; recompute **Progress summary**; update the `(next: **<id>**)` header.
4. Update `**Last updated:**` and frontmatter `last_updated`; set `status: in_progress` on first completion and `status: complete` when all tasks are done.
5. Update **Open questions**; add to **Context references** any file the task created that later work needs.

**Never** start the next delegation before the plan is updated.

**Note to supervisor:** IDs in **Implementation order**, task rows, and `(next: **<id>**)` are for the plan file only. In chat, follow **User-facing reports**.

## User actions

When user input or action is required (approval, answer, env secret, scope choice, or unblocking a `⏸ Blocked` task), give **ready-to-use step-by-step instructions** in chat: what to do, in order, with enough context to execute without opening the plan. Say explicitly that they may **reply in chat only** — they are not required to edit the plan or linked task files; you update those from their reply per **User-reported results**. Include a short **why** (one line) per step or for the request overall. Do not ask the user to mirror progress, **Agent approvals**, **Open questions**, or task **Status** in the plan. Do not substitute "see the plan", "update Implementation order", or "fill Agent approvals in the plan" for a chat answer. If the plan holds the only copy of a value the user must choose, summarize the options and your recommendation in chat; plan paths are optional reference only.

## User-reported results

When the user reports an outcome in chat (approval, answer, scope choice, env or access ready, blocker cleared, or "done" on a manual step you requested), treat the message as authoritative. Parse what applies to the current pause (task by **title**, decision, **Agent approvals**, **Open questions**, or blocked status). Update the plan per **Progress tracking** and the plan's **Plan maintenance** (including linked task files' `**Status:**` lines when present). Then resume the loop from **After a task** — do not ask the user to duplicate the same information in the plan.

## After a task

Apply in order, from the result alone:

1. **Pause** when user input is required per the plan's § **User escalation required** (or the agent returned `needs upgrade: <tier> - <reason>`), or a question is relayed. Name the task by title (**User-facing reports**). Tell the user exactly what to do per **User actions** (concrete approval wording or answer shape when you know it — not "update the plan" alone). On their next chat message that supplies it, **User-reported results** then continue at step 2 or 3 as appropriate.
2. **Escalate or follow up** per **Delegation** step 4 for a failed task (never retried at the same tier) or `needs upgrade`; run a follow-up for the same task only for lint or typecheck fixes; a follow-up beyond that is a plan issue (**Replan flow**).
3. **Next task**: otherwise delegate the next open task immediately; when none remains, go to step 4.
4. **Final review**: spawn one `staff` subagent (level 2, read-only, with an Authorization block) to review the combined diff of the run against the plan's Decisions and Conventions; it returns findings only. Fix accepted findings per step 2, then report.

### Stop conditions

Stop **only** when one of these is true:

- User input required (including approvals per **Delegation**): paused per **After a task** step 1; a chat reply ends the stop once **User-reported results** is applied
- Unresolvable blocker without user action
- All plan tasks complete and the final review done
- The user **explicitly** limited scope in the **same** message that invoked this skill (e.g. "only 8.3", "one task", "stop after phase 8 matrix"). Vague "continue the plan" or `/sequential-implementation` on a path is **not** a chunk limit.
- Platform or user abort of the run (then report where the plan stopped: name the last completed and next runnable tasks by **title**, optional id in brackets)

**Not** stop conditions: completing one task; completing several tasks; a long diff; approaching a context limit (delegate the next task first, then stop if you must).

### Anti-patterns (forbidden)

- Asking whether to continue, or phrasing that puts continuation on the user ("say if you want…", "I can keep going through 8.5…", "want me to continue?") — after one task or after many
- Ending the turn after a successful task when the next ID in **Implementation order** is runnable and no stop condition applies
- Starting the next task in the parent context instead of delegating
- Choosing an Agent not recorded in the plan, or a `principal` or `expert` Agent not recorded in **Agent approvals**
- Passing the full plan or chat history into a task prompt
- Omitting the Conventions block when `project-best-practices` exists, or accepting code that ignores it
- Delegating a task you cannot write a spec for, instead of replanning
- Omitting the plan's Authorization block when § Autonomy is present

## Plan templates

For pasted plans missing progress tracking; use the smallest that fits.

```markdown
# [Plan title]

**Last updated:** YYYY-MM-DD (next: **T02**)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| T01 | … | standard | [x] |
| T02 | … | standard | [ ] |
```

For a single task, a `## Current task` block with `**ID:** T01 · **Status:** [ ]`, `### Goal` and `### Acceptance`; migrate to the table before starting a second task.

## Example invocation (user)

> Run sequential implementation on `.local/feature-plan.md`

> Continue /sequential-implementation of `.local/feature-plan.md`

> Implement this plan step by step: [pasted plan]

Unless the message adds an explicit scope limit (see **Stop conditions**), all three mean: run every open task until complete or blocked — not "do the next task only."
