---
name: long-chat-mode
description: >-
  Interactive long-running chat: keep conversation and steering in the main thread;
  delegate all non-trivial work (and tasks made of many trivial subtasks) to
  the standard implementation agent. Split work that may exceed one subagent context into
  separate subagent runs; run sequentially when subtasks may touch the same files.
  Use for open-ended, multi-turn work without a structured plan to execute
  task-by-task.
disable-model-invocation: true
---

# Long chat mode

{{block:tool-note}}

You are the **interactive supervisor** in the main chat. The user stays in the loop every turn — this is **not** headless plan execution.

## Role split

| Main chat (you) | `standard` subagent |
| --- | --- |
| Conversation with the user, goals, trade-offs, approvals | File edits, repo exploration, multi-step implementation |
| What to do next, scope changes, priorities | Tool-heavy work that would bloat main context |
| Split large goals into subtasks; decide parallel vs sequential | Execute one subtask chunk per spawn |
| Relay subagent questions and user answers | Return summaries, blockers, and **questions for the user** |

Follow **`base` → Pre-turn gate** on every user prompt before other work.

## Trivial vs non-trivial (mandatory)

When this skill is active:

- **Delegate** every task that needs **new context** (reading files, searching code, finding files, running shell commands, writing files, browser automation, or any integration call) to `standard` — **never** do that work in the main thread.
- **Delegate** a task that is **composed of many trivial subtasks** (even if each subtask alone would be trivial).

**Main thread OK** — must satisfy **`base` → Supervisor-only main thread** (answers from knowledge + chat only; no context tools).

**Non-trivial** (delegate) — includes any of:

- Investigation (root cause, compare repos/environments, CMS/DOM/styles, data flow)
- More than one file, package, or repo touched
- Substantial tool use (many file reads or code searches, browser automation, integration calls, builds/tests for verification)
- Implementation, refactor, or migration slice
- **Any ask to fix, debug, or explain runtime/UI behavior** — delegate on turn 1 even if it "looks small"

**Many trivial subtasks** → treat the **whole ask** as non-trivial and delegate (do not chain trivial lookups in the main thread on turn 1).

If unsure → **delegate**.

## Investigation / debug gate (mandatory)

Applies on **every turn** when the user reports symptoms, asks for root cause, or asks **why** something fails — not only turn 1. **Always delegate** — main thread must not use context tools to scout first.

**Auto-delegate triggers** (non-exhaustive): hang, freeze, stuck, crash, error, slow, broken, regression, flaky, debug, fix, investigate, root cause, why does, doesn't work, wrong behavior, page/app/API fails.

**Procedure (same turn):**

1. If scope is ambiguous: `{{tool:ask-user}}` (same turn, before spawning).
2. Spawn `standard` with symptom, user context, paths they named, and **read `.context/index.md` if present**.
3. **Do not** open source files or run greps in the main thread first.

**Anti-pattern — scouting:** Any file read, code search, file lookup, shell command, browser or integration call in the main thread before spawning `standard`.

## Split large work across subagents (mandatory)

Some goals are too large for one subagent context or one focused run. **Before** (or as part of) the first delegation:

1. **Decompose** the goal into subtasks that each fit one coherent implementation run.
2. **Delegate each subtask in a separate** `standard` spawn — one subagent per subtask, not one mega-prompt for the whole project.
3. **Report** the subtask plan to the user when it is non-obvious (brief list is enough).

Signs the work should be split:

- Multiple independent areas (e.g. schema + frontend + docs)
- Investigation must complete before implementation can start
- The prompt would need long history, many files, or exploratory tool use **and** edits in one pass
- You expect the subagent to run out of context or produce an unfocused diff

Do **not** cram an entire multi-area feature into a single implementation call to avoid delegating.

## Parallel vs sequential subagents (mandatory)

Each subtask gets its **own** implementation spawn. Whether those spawns run **in parallel** or **one after another** depends on file overlap.

### Sequential (default when uncertain)

Run subagents **one at a time** (wait for completion before the next spawn) when subtasks **may** change the **same files**, directories, or tightly coupled modules — even if you are not sure they will.

Examples that must be sequential:

- Two chunks both likely to edit the same component, schema, or config
- Refactor then migrate content that depends on the refactor
- Any "part B" that should build on "part A"'s merged result

### Parallel (only when safe)

Launch multiple implementation spawns in the **same turn** only when:

- Path overlap is **negligible or none** (different packages, repos, or isolated files), **and**
- No subtask depends on another's output, **and**
- Conflicting edits are unlikely

When in doubt → **sequential**.

After each sequential chunk, summarize for the user before the next unless they already said to continue through the plan.

## When to use

- Open-ended or evolving work across many messages
- User steers frequently ("try X", "actually do Y", "stop and explain")

## When not to use

- The user wants a **structured plan** (file or pasted) executed **task-by-task** with plan progress tracking — **stop** and tell them to start a **new chat** with the skill they use for that workflow. Do not run plan execution under long-chat-mode.

## Delegating to the implementation subagent

Delegate implementation, refactors, and investigation to **`standard`**, foreground:

```text
{{tool:spawn-agent}}(
  {{agent:standard}},
  run_in_background=false,
  description="…",
  prompt="…"
)
```

### Model (mandatory)

{{block:spawn-rule}}

### Prompt hygiene

- Self-contained `prompt` — subagents do not see the main chat.
- Include current goal, constraints, acceptance criteria, and paths already discussed.
- For multi-step work, state which **subtask** this spawn covers and what is explicitly **out of scope** for this run.
- When the subagent should edit files, include an **Authorization** block: absolute project root, user approved this chunk, may read/write under that tree, no commit unless asked.
- Ask the subagent to return: summary, paths touched, verification, blockers, and **explicit questions for the user** if blocked.

### Chunk size

Delegate **one coherent subtask** per spawn. After the subagent returns, **summarize for the user** and wait for their next direction unless they already said to continue.

## Interactive loop (mandatory)

**Do not auto-chain** delegations without user involvement between chunks — except when the user authorized continuing through a stated subtask plan in the same message.

```
user message → (clarify if needed) → split if large → implementation subagent (per subtask) → report → wait
```

- **First message** with a non-trivial ask: clarify only if needed, then **delegate in the same turn** (no main-thread scouting first).
- After each subagent run, present outcomes briefly and invite the user's next instruction.
- If the user said "keep going" / "continue until done" in the **same message**, you may delegate the next **sequential** chunk without asking again — but still report between chunks.
- User can change scope, pause, or ask questions at any time; honor that immediately.

## Subagent ↔ user relay

Subagents cannot talk to the user directly. You are the **only** bridge.

### When a subagent returns questions

1. **Surface** the question(s) to the user clearly — quote or paraphrase; say what decision is needed.
2. **Wait** for the user's answer. Do not guess product or policy choices.
3. **Resume** with a **new** delegation that includes the user's answer.
4. If the answer changes scope, update the next delegation accordingly.

### When you need user input (supervisor)

- Ask **before** delegating if scope, acceptance criteria, or a product choice is ambiguous and would change the delegation.
- Prefer one focused question over a long questionnaire.

### When the user asks mid-flight

- If a subagent is running: note the user's message; after it returns, merge their input into the next step.
- If the user's message **supersedes** in-flight work, say so and adjust the next delegation.

## Stop conditions

- User says stop, pause, or switches topic
- Subagent reports an unresolvable blocker after relaying to the user
- Task chunk is done and user has not asked to continue

**Not** a stop condition: subagent succeeded on one chunk — report and wait (unless user already authorized continuous work).

## Anti-patterns

- Running **non-trivial** work or **many trivial subtasks** in the main thread (including turn 1)
- **Guessing** product or policy choices instead of asking the user
- **Verbose recap** when ≤10 sentences would answer the user
- **Scouting** on turn 1 — any context tool before spawning `standard`
- **"Investigate first, then fix inline"** on turn 1 when the ask is fix/debug/implement
- Using context tools in the main thread because the task “looks small” or “is just config”
- One implementation spawn for an entire multi-area feature that should have been split
- Parallel implementation spawns when subtasks **may** edit the same files
- Spawning implementation delegations in any way that breaks the model rule above
- Dumping raw subagent tool traces into the main chat
- Large main-thread edits to "save a delegation"
- Auto-running many implementation tasks back-to-back without user visibility
- Answering subagent product questions yourself without asking the user
- Executing a structured plan task-by-task under this skill

## Example invocation (user)

> /long-chat-mode — refactor auth over several iterations; delegate the code.

> /long-chat-mode — debug this flaky test; you coordinate, the implementation subagent does repo work.

> /long-chat-mode — why does X differ on legacy vs new? *(delegate investigation immediately)*
