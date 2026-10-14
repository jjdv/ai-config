---
name: sequential-implementation
description: >-
  Execute a plan task by task as a thin executor under the Delegation rules:
  audit the plan with check-plan (READY required), then for each task write a
  decision-complete run-time spec from the task, its Decisions and its notes,
  run the task's Agent, verify, update plan status. Plan issues trigger a
  replan via create-plan. Use when the user asks to implement, execute, or
  continue a plan step-by-step.
invocation: explicit
---

# Sequential implementation

{{block:tool-note}}

Act as a **thin executor** under **Delegation**: the supervisor writes each task's spec, the task's recorded **Agent** does the work, and the supervisor verifies and **updates progress as the last action** before starting the next task. Do not do task work yourself unless the user explicitly overrides.

**Keep going through open tasks** until a stop condition applies; do not ask after each task whether to continue.

## Plan contract

A plan task is small: one goal, bounded scope, acceptance check or verification command, references to **Decisions** by ID, `Notes in` and `Notes out`, and an Agent. It is not a decision-complete spec: you write that at run time. **`check-plan`** owns readiness rules; **`create-plan`** owns plan structure and replanning.

## Plan source

| Mode | When | Source |
| --- | --- | --- |
| **File** | User gives a plan path (e.g. `.local/feature-plan.md`) | Read from disk; pre-flight below |
| **Pasted** | User pastes the plan in the prompt | Use only what is pasted; if a task lacks goal, scope or verification, report it as a plan issue; add progress tracking per Plan templates if missing |

## Pre-flight (file plans)

1. Spawn a read-only `senior` subagent given the path of `check-plan`'s SKILL.md and the plan path; it returns the audit report.
2. Start only on verdict `READY`. On `NOT READY`, stop and report the failed checks; **`create-plan`** fixes them. On `COMPLETE`, report that nothing is left to run.
3. Flag ⏸ blocked tasks to the user before delegating.
4. Resolve the project root from the plan's `**Project root:**` line. Check whether `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists (it governs the Conventions block below).

## Per-task loop

Repeat until a stop condition applies:

1. **Pick** the first runnable task in **Implementation order**.
2. **Read** its plan row and task file, the **Decisions** it references and the notes in its `Notes in`.
3. **Write the spec** per **Delegation**: files, exact change, interfaces, out of scope, verification command, only the context needed. If you cannot write a spec the task's Agent can execute, it is a plan issue: go to **Replan flow**.
4. **Spawn** the task's Agent with the prompt below.
5. **Verify** deliverables: paths touched, verification command result, diff free of redundant comments (have them removed), drive-by churn and rule violations; when `project-best-practices` exists, compliance with it; when source files changed, the **code** user rule checklist.
6. **Update the plan** (Progress tracking), then decide the next action (After a task).

Sequential only: one task at a time unless the user explicitly requests parallel runs. Only the supervisor edits the plan; subagents never do. Report to the user once, at the end or at a stop condition, naming tasks by title with the ID in brackets (`Title [T02]`); per-task progress lives in the plan file.

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
Naming: refer to any section, task, finding or decision by its title, with an id in brackets only as extra, never alone.
Return: summary, paths touched, verification result, blockers; or `needs upgrade: <tier> - <reason>`; or `needs split: <subtasks, each with suggested tier>`; or `question: <question>`; or `plan issue: <description>`
Do not update the plan; the supervisor does.

## Authorization

**Project root:** `/absolute/path/to/repo`

The user already approved this task. You may read and write any file under the project root without asking for per-file permission. Do not edit outside this tree. Do not commit unless asked.
```

Run the Agent with the spawn call `{{tool:spawn-agent}}({{agent:standard}})` (the task's Agent in place of `standard`). When the plan has § **Autonomy & authorization**, use that plan's **Authorization** block instead of the generic one.

{{block:spawn-rule}}

Task Agents run as level 2 (this supervisor is level 1): per **Delegation** they may spawn subtasks, or return `needs split` / `needs upgrade`.

Never pick a heavier Agent than the plan records, except by escalation per **Delegation** step 4.

## Returns from an executing agent

- `needs upgrade: <tier> - <reason>`: handle per **Delegation** step 4 (a `principal` or `expert` Agent still needs user approval, recorded in the plan's **Agent approvals**, and only for a criterion in the Delegation scope table, never for size: an oversized task is split instead).
- `needs split: <subtasks>`: the task is oversized; **Replan flow**.
- `plan issue: <description>`: **Replan flow**.
- `question: <question>`: relay per **Delegation**, worded per the **ask-questions** skill and naming the task by title with its ID in brackets; mark the task `⏸ Blocked` with the question in **Open questions** until answered, then resume with the answer.

## Replan flow

Triggered by a `plan issue:` result, an oversized task, a task whose spec cannot be written, or a task needing a follow-up spawn for the same ID.

1. Stop the loop. Spawn a `staff` replan agent that follows `create-plan`'s replan mode, given the plan path and the issue.
2. Re-run the `check-plan` audit (Pre-flight step 1); resume only on `READY`.
3. Report the replan to the user in 1-2 lines, even when no approval was needed.

Replan limits (defined in `create-plan`): edits only unfinished tasks, within the original goal and scope, no reversal of user-approved Decisions, no `principal` or `expert` assignment without recorded user approval. Anything beyond needs the user's approval before the plan changes.

## Progress tracking

Progress lives in the plan file (file mode) or in the plan text maintained in replies (pasted mode); the plan is the source of truth. Follow the plan's **Plan maintenance** section. Default checklist after each task:

1. Set the task row to `✅ Complete` (or `⏸ Blocked` with reason).
2. Sync the linked task file `**Status:**` line if present.
3. Remove the task ID from **Implementation order**; recompute **Progress summary**; update the `(next: **<id>**)` header.
4. Update `**Last updated:**` and frontmatter `last_updated`; set `status: in_progress` on first completion and `status: complete` when all tasks are done.
5. Update **Open questions**; add to **Context references** any file the task created that later work needs.

**Never** start the next delegation before the plan is updated.

## After a task

Apply in order, from the result alone:

1. **Pause** when user input is required per the plan's § **User escalation required** (or the agent returned `needs upgrade: <tier> - <reason>`), or a question is relayed; the escalation names the task by title with its ID in brackets.
2. **Escalate or follow up** per **Delegation** step 4 for a failed task (never retried at the same tier) or `needs upgrade`; run a follow-up for the same task only for lint or typecheck fixes; a follow-up beyond that is a plan issue (**Replan flow**).
3. **Next task**: otherwise delegate the next open task immediately; when none remains, go to step 4.
4. **Final review**: spawn one `staff` subagent (level 2, read-only, with an Authorization block) to review the combined diff of the run against the plan's Decisions and Conventions; it returns findings only. Fix accepted findings per step 2, then report.

### Stop conditions

- User input required (including approvals per **Delegation**)
- Unresolvable blocker without user action
- All plan tasks complete and the final review done
- The end of the chunk the user asked for, unless the user asked to continue through all tasks
- The user explicitly limited scope (e.g. "only 1.1")

One task succeeding is not a stop condition.

### Anti-patterns (forbidden)

- Asking "Want me to continue?" after a successful task
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

> Implement this plan step by step: [pasted plan]
