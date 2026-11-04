---
name: sequential-implementation
description: >-
  Execute a plan task by task as a thin executor under the Delegation rules:
  audit the plan with check-plan (READY required), then for each task write a
  decision-complete run-time spec from the task, its Decisions and its notes,
  run the task's Agent, verify, update plan status. Plan issues trigger a
  replan via create-plan. Use when the user asks to implement, execute, or
  continue a plan step-by-step, or run sequential-implementation on a plan path.
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
2. Start only on verdict `READY`. On `NOT READY`, automatically enter **Replan flow** with the complete findings, then re-audit; repair within the original goal, scope and approved Decisions needs no extra proceed approval. On `COMPLETE`, report that nothing is left to run.
3. Flag ⏸ blocked tasks to the user before delegating (name each task by title; say what blocks it and what you need from the user, per **User actions** below when input is required).
4. **Plan anchoring (mandatory):** Record the absolute **Plan path** (this plan file) and **Project root** from the plan's `**Project root:**` line. Keep both for the whole run; every task spawn repeats them in the task prompt. On **continue** or a new turn, re-read the anchored plan path from the user's message or the last run — never infer a plan from a bare task id.
5. Check whether `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists (it governs the Conventions block below).

## Per-task loop

Repeat until a stop condition applies:

1. **Pick** the first runnable task in **Implementation order**.
2. **Read** its plan row and task file, the **Decisions** it references and the notes in its `Notes in`.
3. **Write the spec** per **Delegation**: files, exact change, interfaces, out of scope, verification command, only the context needed. For **user-facing surfaces** (UI or CLI), require the task's Agent to run **`internal-ux-pass`** (internal pass before the first product edit) and name that skill in the spawn spec. If you cannot write a spec the task's Agent can execute, it is a plan issue: go to **Replan flow**.
4. **Spawn** the task's Agent with the prompt below (complete the **Supervisor spawn checklist** first).
5. **Verify** deliverables: paths touched, verification command result, diff free of redundant comments (have them removed), drive-by churn and rule violations; when `project-best-practices` exists, compliance with it; when source files changed, the **code** user rule checklist; when the task scope or diff matches **`documentation`** **Do persist**, updated doc paths or explicit **N/A** with reason per **Post-change sync (mandatory)**.
6. **Update the plan** (Progress tracking), then decide the next action (After a task).

Sequential only: one task at a time unless the user explicitly requests parallel runs. Only the supervisor edits the plan; subagents never do.

**Reporting:** Per-task status lives in the plan file. In chat, give a **full** summary only when the **whole run** stops (all tasks done plus final review, or a stop condition). While the run continues, chat messages may be omitted or limited to blockers and escalations — never a "done for now" recap that invites the user to opt in to more work. **Exception:** when the next work is an **operator gate** (see **Operator gate relay** below), the chat message must include the full gate packet even if that exceeds the supervisor's usual brevity limit — do not wait for the user to ask for "step-by-step" instructions.

**User-facing reports (mandatory in chat):** Whenever you report to the user (blockers, escalations, final summary, replan notices, relayed questions, operator gate instructions, or why a stop condition applied), name tasks, decisions, **gates**, sections, and findings by **title or short plain-language description** — whichever reads clearest. **Never** use a bare plan id, gate code, or decision id as the main label (for example do not write "do UG8" or "next is 22.1" without the title).

| Bad (chat) | Good (chat) |
| --- | --- |
| "UG3 blocks 12.3" | "**OVH-G1 lock test** is recorded; **Lease core** can run" |
| "Run OP-S3c for 13.18" | "Run **Observability stack install** — unblocks obs wheel tasks" |
| "After 14.4" | "After **Retire tofu.auto.tfvars and hosts jq merge**" |

Optional bracketed id **only** when two similar titles need disambiguation (e.g. `Lease core [12.3]`). The plan file may still use ids for progress tracking; this rule applies to **chat only** (and to relaying subagent output to the user).

### Supervisor spawn checklist

Applies to **every** spawn in this run — implementation agents, read-only scouts, plan-progress bookkeeping, and operator runbook extractors — not only the task's recorded **Agent**.

Before every spawn, confirm the prompt includes: absolute **Plan path** (when this run is plan-anchored); absolute **Task file** when executing a plan task (`tasks/<id>.md` under the plan's directory); **Allowed read/write roots** from the task or plan **Project root** (plus any secondary repo the task names); the **Forbidden** scope line; and a **qualified task id** when relevant (plan title or slug plus id, e.g. `infra-iaasw-split task 12.1` — never bare `12.1`).

**Never** spawn plan-progress bookkeeping in parallel with the next implementation task. Finish or abort the bookkeeping spawn, update the plan, then spawn the next task.

### Task prompt

Self-contained and small; never pass the plan body or chat history. Include only what the Agent needs:

```markdown
Plan path: /absolute/path/to/plan.md
Task file: /absolute/path/to/tasks/<id>.md
Task ID: <qualified id — plan slug or title plus numeric id, not id alone>
Level: 2
Allowed read/write roots:
- /absolute/path/to/project-root
- <other roots the task allows, omit line when none>
Forbidden: do not read, write, search, or glob outside allowed roots; do not discover plans by task id alone; do not search parent directories (e.g. ~/Projects/Development) for plans or task ids
Goal: <one outcome>
Spec: <the run-time spec: files, exact change, interfaces, out of scope>
UX: <when user-facing surfaces (UI or CLI): load internal-ux-pass; complete internal pass before first product edit; omit line when not user-facing>
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

**Allowed read/write roots:** (same list as above)

The user already approved this task. You may read and write only under these roots without asking for per-file permission. Do not edit outside them. Do not commit unless asked.
```

Run the task with the spawn call `{{tool:spawn-agent}}({{agent:senior}})`, using the recorded Agent in place of `senior` when it is `junior` or `senior`. A recorded `staff` or `principal` Agent is advisory-only and the supervisor never spawns it: spawn `senior` instead, with the recorded tier and any recorded **Agent approvals** in its prompt, and it spawns that tier per the base rule. When the plan has § **Autonomy & authorization**, use that plan's **Authorization** block instead of the generic one. Follow **Spawn policy** in the mandatory **base** rule.

Task Agents run as level 2 (this supervisor is level 1): per **Delegation** they may spawn subtasks, or return `needs split` / `needs upgrade`.

Use the recorded Agent; escalation per **Delegation** step 4 may select the lowest fitting higher tier, routed the same way. Update the recorded **Agent** before execution and re-audit structural plan changes; `junior` through `senior` upgrades do not require user approval.

## Returns from an executing agent

- `needs upgrade: <tier> - <reason>`: handle per **Delegation** step 4 (a `principal` Agent needs user approval only when not already covered by the plan's recorded **Agent approvals**, and only for a criterion in the task-to-tier mapping, never for size: an oversized task is split instead). When approval is missing, request it with **User actions** (what to approve and why). On approval in chat, apply **User-reported results** (write **Agent approvals** in the plan); do not ask the user to edit the plan.
- `needs split: <subtasks>`: the task is oversized; **Replan flow**.
- `plan issue: <description>`: **Replan flow**.
- `question: <question>`: relay per **Delegation**, worded per the **ask-questions** skill; name the task by title (optional id in brackets only to disambiguate). Give the user **User actions** steps to answer. Mark the task `⏸ Blocked` with the question in **Open questions** until answered; on the user's chat reply, apply **User-reported results** and resume with the answer in the spec.

### Resume / replace (mis-scoped subagent)

After a mis-scoped subagent (wrong repo, workspace-wide search, or task id without an anchored task file), spawn a **new** agent with a full anchored task prompt. Do **not** resume the old transcript.

## Replan flow

Triggered by a `plan issue:` result, an oversized task, a task whose spec cannot be written, or a task needing a follow-up spawn for the same ID.

1. Suspend affected delegations. Spawn a `senior` replan agent that follows `create-plan`'s replan mode, given the plan path and the issue.
2. Re-run the `check-plan` audit (Pre-flight step 1); repair remaining findings automatically within the replan limits and resume only on `READY`. If an unchanged failure repeats with no progress, stop and explain the concrete blocker instead of looping.
3. Report the replan to the user in 1-2 lines (what changed and why, by task or decision **title**), even when no approval was needed — **unless** the next work is an operator gate; then append the full **Operator gate relay** packet in the same message. If the user must approve or act before you resume, follow **User actions** — do not send them to the plan alone.

Replan limits (defined in `create-plan`): edits only unfinished tasks, within the original goal and scope, no reversal of user-approved Decisions, no `principal` assignment without recorded user approval. Anything beyond needs the user's approval before the plan changes; spell out what you need in chat per **User actions**.

## Progress tracking

Progress lives in the plan file (file mode) or in the plan text maintained in replies (pasted mode); the plan is the source of truth. Follow the plan's **Plan maintenance** section. Default checklist after each task:

1. Set the task row to `✅ Complete` (or `⏸ Blocked` with reason).
2. Sync the linked task file `**Status:**` line if present.
3. Remove the task ID from **Implementation order**; recompute **Progress summary**; update the `(next: **<id>**)` header.
4. Update `**Last updated:**` and frontmatter `last_updated`; set `status: in_progress` on first completion and `status: complete` when all tasks are done.
5. Update **Open questions**; add to **Context references** any file the task created that later work needs.

**Never** start the next delegation before the plan is updated.

**Plan progress (supervisor).** Prefer updating the plan in the supervisor thread when the harness allows. If you delegate bookkeeping to `junior`, use the **Plan progress prompt** below — not a one-line "mark \<id\> complete" or ".local only".

```markdown
Plan path: /absolute/path/to/plan.md
Completed task file: /absolute/path/to/tasks/<id>.md
Completed task ID: <qualified id — plan slug or title plus numeric id>
Level: 2
Allowed read/write roots:
- /absolute/path/to/plan-directory (plan file, tasks/, notes/ under the plan's .local slug only)
Forbidden: do not read, write, search, or glob outside allowed roots; do not discover plans by task id alone; do not search parent directories (e.g. ~/Projects/Development) for plans or task ids
Goal: Apply Progress tracking checklist for the completed task only; set header (next: **<next-id>**); update Fresh chat handoff next task title + task file path.
Do not start the next implementation task; do not edit product code outside the plan directory.
Return: paths touched, new (next: …), blockers.
```

**Note to supervisor:** IDs in **Implementation order**, task rows, and `(next: **<id>**)` are for the plan file only. In chat, follow **User-facing reports**.

## Operator gates (from the plan)

When the plan marks **operator gates** (in `gates.md`, **Operator handoff**, or **Operator gates** table), the executor pauses per **After a task** step 1 and follows **User actions** / **User-reported results**.

### Operator gate relay (mandatory)

**Chat format:** Read and follow `{{path:skills}}/give-instructions/SKILL.md` (**Staged gate relay** A → B → C + **Response shape**). Do not dump the full runbook in one message when **B** is agent-runnable.

| Set | Executor |
| --- | --- |
| **A** | Operator — **Your steps** only; wait for chat reply |
| **B** | Supervisor (shell/delegate) — read-only verification, diffs, local scripts without secrets; **never** in **Your steps** |
| **C** | Operator — **Your steps** in a **follow-up** message after **B**, adapted from B results |

Emit a gate pause proactively when a stop condition applies, the next milestone is operator-only, or a replan leaves the queue blocked on a gate.

**First message at a gate:** **Situation** (title, place, purpose per **User-facing reports**) + **Your steps** = **A** only (or **C** only when **B** already ran and there is no **A**). **Agent (after you paste …):** run **B**, then send **C** or record `gate-results.md` / resume the plan.

**After user-reported results for A:** run **B** in the same turn before replying; then either (1) send **give-instructions** with **C** only, (2) record the gate and continue **Implementation order**, or (3) stop if still blocked.

Delegate a read-only subagent to extract runbook commands when needed — classify them into A/B/C; operator commands go under **Your steps**, agent commands execute in **B**.

For metadata the user needs in **Situation** (not a substitute for **Your steps**): gate title, place in plan, purpose, what unblocks (by **title**).

Group compatible gates into one session when the plan groups them. Do not ask the user to edit plan files or `gate-results.md`.

## User actions

When user input or action is required (approval, answer, env secret, scope choice, operator gate, or unblocking a `⏸ Blocked` task), give **give-instructions** using **Staged gate relay** — **Your steps** for the **current operator set only** (A or C), not agent set **B**: what to do, in order, with enough context to execute without opening the plan. Say explicitly that they may **reply in chat only** — they are not required to edit the plan or linked task files; you update those from their reply per **User-reported results**. Include a short **why** (one line) per step or for the request overall. Do not ask the user to mirror progress, **Agent approvals**, **Open questions**, or task **Status** in the plan. Do not substitute "see the plan", "update Implementation order", or "fill Agent approvals in the plan" for a chat answer. If the plan holds the only copy of a value the user must choose, summarize the options and your recommendation in chat; plan paths are optional reference only.

Batch independent questions already known into one input round and group compatible manual milestones. Do safe independent work while awaiting required input only when the plan's sequential order and dependencies permit it; do not start parallel tasks without authorization. Never guess an answer or bypass required approval. Confirmed scope and approvals persist, including specific shared paths/actions; ask again only for scope expansion, unapproved shared changes or a genuinely unresolved decision. Run locally available checks yourself and own all bookkeeping.

## User-reported results

When the user reports an outcome in chat (approval, answer, scope choice, env or access ready, blocker cleared, operator gate evidence, or "done" on a manual step you requested), treat the message as authoritative. For operator gates: that reply completes set **A** (or **C** when mid-cycle) — run set **B** before your next chat message when the runbook says verification follows operator action. Parse what applies to the current pause (task by **title**, decision, **Agent approvals**, **Open questions**, or blocked status). Update the plan per **Progress tracking** and the plan's **Plan maintenance** (including linked task files' `**Status:**` lines when present). Compose `gate-results.md` from chat when the gate is documentation-only. Then resume the loop from **After a task** — do not ask the user to duplicate the same information in the plan.

## After a task

Apply in order, from the result alone:

1. **Pause affected work** when user input is required per the plan's § **User escalation required** (including an upgrade needing approval not already recorded), operator gate per **Operator gate relay**, or a question is relayed. Name the task by title (**User-facing reports**). Tell the user exactly what to do per **User actions** (concrete approval wording, operator **Steps**, or answer shape when you know it — not "update the plan" alone). On their next chat message that supplies it, **User-reported results** then continue at step 2 or 3 as appropriate.
2. **Escalate or follow up** per **Delegation** step 4 for a failed task (never retried at the same tier) or `needs upgrade`; run a follow-up for the same task only for lint or typecheck fixes; a follow-up beyond that is a plan issue (**Replan flow**).
3. **Next task**: otherwise delegate the next open task immediately; when none remains, go to step 4.
4. **Final review**: spawn one `senior` subagent (level 2, read-only, with an Authorization block) to review the combined diff of the run against the plan's Decisions, Conventions, and **project documentation set** consistency (agent `references/`, `docs/`, package READMEs — not code-vs-conventions alone); it returns findings only. Fix accepted findings per step 2, then report.

### Stop conditions

Stop **only** when one of these is true:

- User input required (including missing approvals per **Delegation**) and no safe independent work can proceed within sequential/dependency limits: paused per **After a task** step 1; a chat reply ends the stop once **User-reported results** is applied
- Unresolvable blocker without user action
- All plan tasks complete and the final review done
- The user **explicitly** limited scope in the **same** message that invoked this skill (e.g. "only 8.3", "one task", "stop after phase 8 matrix"). Vague "continue the plan" or `/sequential-implementation` on a path is **not** a chunk limit.
- Platform or user abort of the run (then report where the plan stopped: name the last completed and next runnable tasks by **title**, optional id in brackets)

**Not** stop conditions: completing one task; completing several tasks; a long diff; approaching a context limit (delegate the next task first, then stop if you must).

### Anti-patterns (forbidden)

- Asking whether to continue, or phrasing that puts continuation on the user ("say if you want…", "I can keep going through 8.5…", "want me to continue?") — after one task or after many
- Ending the turn after a successful task when the next ID in **Implementation order** is runnable and no stop condition applies
- Starting the next task in the parent context instead of delegating
- Executing with an Agent before recording an approved escalation in the plan, or with a `principal` Agent lacking applicable recorded **Agent approvals**
- Passing the full plan or chat history into a task prompt
- Omitting the Conventions block when `project-best-practices` exists, or accepting code that ignores it
- Delegating a task you cannot write a spec for, instead of replanning
- Omitting the plan's Authorization block when § Autonomy is present
- Vague continuation prompts without **Plan path** and **Task file** (e.g. "do 12.1" with no anchored plan)
- User-facing text that leads with bare task ids, gate codes, or decision ids without titles (**User-facing reports**)
- Letting a subagent discover plans or tasks via workspace-wide glob/grep instead of paths in the prompt
- Delegating plan progress without **Plan path** and allowed plan-directory roots (e.g. ".local only", "mark 3.1 complete")
- Spawning plan-progress bookkeeping in parallel with the next implementation task
- Interpreting numeric task ids without opening the anchored **Task file**
- Pausing on an operator gate with only a gate title, runbook path, or "attempt N" summary — without **give-instructions** **Your steps**, fenced commands, and paste-back plus **Agent (after …)** (**Operator gate relay**)
- Sending **A+B+C** in one **Your steps** list when **B** is agent-runnable (**Staged gate relay**)
- Asking the user to run read-only gate verification that belongs in set **B** — without running **B** yourself first (**give-instructions**)
- Waiting for the user to ask for step-by-step instructions when **Operator gate relay** already applies

## Plan templates

For pasted plans missing progress tracking; use the smallest that fits.

```markdown
# [Plan title]

**Last updated:** YYYY-MM-DD (next: **T02**)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| T01 | … | junior | [x] |
| T02 | … | senior | [ ] |
```

For a single task, a `## Current task` block with `**ID:** T01 · **Status:** [ ]`, `### Goal` and `### Acceptance`; migrate to the table before starting a second task.

## Example invocation (user)

> Run sequential implementation on `.local/feature-plan.md`

> Continue /sequential-implementation of `.local/feature-plan.md`

> Implement this plan step by step: [pasted plan]

Unless the message adds an explicit scope limit (see **Stop conditions**), all three mean: run every open task until complete or blocked — not "do the next task only."
