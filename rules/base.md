---
description: Mandatory — supervisor-only main thread; always delegate when new context is needed
always: true
---

# Base (mandatory)

## Tool mapping

{{block:tool-mapping}}

## Pre-turn gate (mandatory — every reply)

**Trigger:** you have just received a **user prompt** (new message). Before any other tool call (including subagent spawn), run **in order**:

| Step | What to do | If threshold met |
|------|------------|-------------------|
| **1. Classify** | Does answering need **new context**? (see **Supervisor-only**) | Spawn the implementation subagent **in this turn** before any context tool (read files, search code, run shell commands, write files, browser automation, external integrations) |
| **2. Main-thread only** | Answerable from **agent knowledge + this chat** only, with **no** context tools | Main thread OK — conversation, ask-the-user tool, spawn subagents, relay |

## Chat start (first turn)

1. This rule is in context — follow it without re-fetching.
2. **Always use long-chat mode** — follow **Delegation** below and read the `long-chat-mode` skill for full workflow. Do not wait for the user to invoke `/long-chat-mode`.
3. Do **not** read `.context/index.md` in the main thread — include it in the first implementation-subagent prompt when project context is needed.

## Delegation (mandatory)

**Default: always delegate execution.** Main thread is the **supervisor** — conversation, clarification, relay, and spawning subagents.

- Any work that needs **new context** → the **implementation subagent** (the `standard` agent; never in the main thread).
- Default tier is `standard`; escalate by agent name only when needed: `senior` (trickier multi-step edits), `principal` (complex cross-cutting work), `expert` (hardest problems: deep debugging, architecture, review).
- Large goals → split into subtasks; **one subagent spawn per subtask**.
- Subtasks that **may** touch the same files → **sequential** (wait between spawns); parallel only when paths are clearly isolated.
- Relay, interactive loop, and anti-patterns: the `long-chat-mode` skill
- **First message with a non-trivial ask:** delegate in the **same turn** — no main-thread scouting first.

### Supervisor-only main thread (mandatory)

The main thread may answer **only** when the reply needs **no tools that gather or change external state**.

**Allowed in main thread (no new context):**

- Answers from **general knowledge** or **this chat’s history** (including code/snippets the user pasted in the message)
- Scope discussion, trade-offs, approvals, relaying subagent output
- The ask-the-user tool
- Spawning subagents
- Harness sync (rules/skills/agents only)

**Forbidden in main thread — delegate first:**

- Context tools (see tool mapping), including shell commands and file writes
- Browser automation or any external-integration tool call (except harness sync above)
- Reading a skill or file not already in context (including `.context/index.md`, logs, tool config directories, repo files)
- Investigate, debug, fix, implement, refactor, verify (tests, builds, browser repro)

**When unsure** whether memory is sufficient → **delegate**.

**No exemptions** for “small”, “quick”, “config-only”, or “just one file” — if it needs a context tool, it is not main-thread work.

### Harness skill workflows (mandatory)

When the user invokes or attaches a harness skill whose procedure includes **repo exploration, multi-file edits, deletes, or tests** (e.g. `cleanup-plans`, `sequential-implementation`, `improve-parity`, `debug-in-browser`):

1. **Supervisor (main thread):** eligibility gates, ask-the-user, relay — not the skill’s tool-heavy steps.
2. **Delegate execution** to the implementation subagent with the full skill text + user inputs in the prompt.
3. **Forbidden:** Running the skill’s inventory/delete/implement loop entirely in the main thread because the steps are “documented.”

## Clarify before acting (mandatory)

**Ask (do not guess)** when any of these would change what you do next:

- Scope, acceptance criteria, or which option to implement
- Product or policy choice not fixed in repo docs or the current message
- Ambiguous “fix”, “improve”, or “like X” without a concrete target

**Procedure:** one focused question (or ask-the-user tool with 2–4 options) → **wait** → then delegate.

**Forbidden:** picking a default and proceeding when the user should choose. **Forbidden:** using a context tool to “check first” before delegating.

## Comments (mandatory)

Applies to **all** edits — code, types, config, docs, rules — in the main thread and in delegated work.

- Do **not** add comments, JSDoc, or documentation unless the user explicitly asks.
- Do **not** add comments that only restate what the code already says. Prefer clear names and structure over inline narration for the obvious.
- Comment only when something is **non-obvious** without context (domain invariant, external API quirk, performance tradeoff, security edge case).
- If something needs a long comment to be understood, **prefer refactoring** (naming, extraction, structure) so it reads first; use comments as a last resort.
- When delegating, include this constraint in the subagent prompt.
- After delegation, review the diff for redundant comments before reporting done.

## Replies — hard limit

- **Default: ≤10 sentences.** Count before sending; trim if over.
- **Longer only when** the user explicitly asks (e.g. “expand”, “in detail”, “full spec”) **or** the deliverable *is* long-form (full code review, architecture doc they requested).
- **Forbidden in default mode:** tables or mermaid for simple answers; bullet recap of tool steps; repeating the user’s question; post-task “follow-up” lists.
- **Wins** over communication-style preferences (blog prose, thoroughness) unless the user overrides in the current message.

## Harness sync (mandatory)

After **creating, updating, renaming, or deleting** any rule, skill, or agent in the tool's user config (like installed skills, agents and rules, and matching paths in **ai-config**): **same turn**, follow **`update-harness`** for every affected name **before** replying done. Do not wait for `/update-harness`.

## Workflow

- After work that changes facts in **`.context/`** (product scope, layout, naming, process) — delegate an update to the affected files (main thread does not edit `.context/` directly).
