---
name: give-instructions
description: >-
  Give clear numbered steps for actions only the human should take (terminal
  commands, UI, approvals, pasting output back) when a gate blocks the agent.
  Use staged relay: operator set A first, then the agent runs set B, then
  operator set C adapted from B. Also when the user invokes /give-instructions
  or attaches this skill.
---

# Give instructions

At **gate situations**, split work into three **sets** (names are logical, not runbook labels):

| Set | Who runs | In chat |
| --- | --- | --- |
| **A** | Operator only | **Your steps** — numbered; wait for reply before B |
| **B** | Agent (supervisor or subagent) | **Never** in **Your steps** — run after A completes (or before A when the runbook has no operator prerequisite) |
| **C** | Operator only | **Your steps** in a **later** message, after B — tailored from B results |

## Classification test

For every runbook line before you write **Your steps**, ask: *can the agent do this without secrets, live prod access, or an irreversible external effect?*

- **Yes** → **B** (supervisor or delegate). Never a numbered **Your steps** item. If the gate implies repo-local prep must exist before the operator can apply safely, run that prep in **B-before-A** (below) — do not push it into **Your steps** as “check first” or “fix locally.”
- **No** → operator-only: **A** or **C** under **Your steps** (with fenced commands when the step is shell/UI).

Do **not** give one combined checklist for A+B+C when any part is agent-runnable.

### B-before-A

Before the **first** **Your steps** at a gate, the supervisor (or delegate) completes all repo-local prep the runbook implies must already exist before live apply (read-only verification, diffs, syntax checks, manifest reconciliation, local edits that need no unlock). Put outcomes in **Situation**, not in numbered operator steps. Then send **Your steps** = **A** only — or **C** only when no operator prerequisite remains.

**Staged flow (default):**

1. Classify runbook / gate steps with the **Classification test** (A, B, C).
2. Send **give-instructions** with **Situation** + **Your steps** = **A only** (plus paste-back for A). End with **Agent (after you paste …):** stating you will run **B**, then return with **C** if still needed (or record gate / resume the plan).
3. On user reply (**User-reported results**): run **B** (preflight, read-only scripts, diffs, local tests that need no unlock — or delegate extraction). Do not ask the user to re-run what B just proved.
4. If operator work remains, send a **new** **give-instructions** message: **Situation** includes B outcomes; **Your steps** = **C** only (adapted). Repeat A→B→C until the gate is satisfied or you hit a stop condition.

**Gated operator work** (secrets, prod SSH, `git rm vault.yml`, browser on prod, approvals) stays in **A** or **C** only — the agent must not run it unless the user explicitly asks after reading the steps.

## Agent preflight (part of **B**)

**Mandatory for supervisors** on plan gates (`sequential-implementation` **Operator gate relay**): run everything that passes the **Classification test** in **B** / **B-before-A** before numbering operator work. **Do not** ask the user to run a diagnostic, read-only script, repo edit, or preflight you can run without secrets.

When the user already pasted output that **B** would reproduce, still reconcile with a fresh **B** run when cheap before writing **C**.

Then write **give-instructions**:

- **Situation** — gate context plus **B** results (pass/fail, counts, missing ids, exit codes) when B has run.
- **Your steps** — **current operator set only** (**A** or **C**): actions that fail the **Classification test**. Name **specific** gaps from B, not generic “fix store.”

## Response shape

- **Situation** — one short line, or omit when the thread already makes it obvious.
- **Your steps** (purity) — numbered list where **every** item fails the **Classification test** (secrets, live prod, irreversible external effect, or UI/approval only the human can take). Forbidden in the numbered list: repo edits, local read-only checks, preflight or diagnostic scripts, “verify before apply,” or any **B** work dressed as operator steps — even when the runbook listed them under an operator heading.
- **Agent (between steps)** — when the agent should act after a user step, say so in a short labeled block **outside** the numbered list (for example **Agent (after you paste the output):** then you will run set **B**, update records, and send **Your steps** for set **C** if needed). **Wait** for the user to finish the preceding operator set (including pasting results) before **B**; do not continue in the same turn unless they already supplied it.
- Each user step: **1–3 sentences** of prose (what to do; **why** only when not obvious). **Do not** put shell commands in inline backticks inside the numbered line — commands belong in fenced blocks (below).
- **Commands** — every shell command and multi-line command sequence in its **own** markdown fenced code block with a language tag (`bash` by default). Place the block **immediately under** the numbered step it belongs to. When several steps run in one shell session, one combined `bash` block under the last of those steps is fine. Single-line `curl`, env edits, or paste-back snippets use `bash` or `text` fences as appropriate. UI-only steps stay prose with no command fence. Use placeholders only when values are unknown, and say what to substitute in the step prose above the block.
- **Do not** run gated commands or take gated UI actions yourself unless the user explicitly asks after reading the steps.
- **Do** run set **B** yourself (see **Agent preflight** and **Classification test**) — never list **B** in **Your steps**.
- No long preamble; no agent todo list disguised as user instructions.

## Gate evidence (sequential-implementation / create-plan)

**Executor obligation:** Any **Operator gate relay** or **User actions** pause in `sequential-implementation` must use this skill's **Response shape** and **Staged gate relay** (A → B → C). Gate title, place, and purpose belong in **Situation**; operator runbook commands belong under **Your steps** for **A** or **C** only, with fenced blocks.

When a runbook gate is **documentation-only** (record in `gate-results.md`, unlock agent work), the user does **not** format the gate record. They run **human-only** checks (browser, SSH, UI) and reply in chat with **evidence fragments** (command output, HTTP status, “confirmed in browser that …”). The **supervisor** composes the official section under the exact `gate-results.md` heading per **User-reported results** in `sequential-implementation`.

**Your steps** for such gates: numbered **checks and confirmations only** — never “paste this template into gate-results” or “copy this block into the plan.” End with: reply in chat with outputs or short confirmations.

**Agent (after evidence in chat):** Write `gate-results.md`, update the plan, continue **Implementation order** (or relay the next operator gate with a new **Your steps** list).

## Example pattern

**Situation:** The API key must be set locally before the agent can call the service.

**Your steps**

1. Open the project `.env` and set `SERVICE_API_KEY` to the key from the provider dashboard.

   ```bash
   # append or edit in .env
   SERVICE_API_KEY=your-key-here
   ```

2. Load the variable in the shell you use for the app, or restart the dev server so it picks up `.env`.

   ```bash
   set -a && source .env && set +a
   ```

3. Check health and paste the HTTP status code here.

   ```bash
   curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health
   ```

**Agent (after you paste the HTTP status):** If it is `200`, continue with the planned API checks; if not, narrow the failure from your output before asking for more steps.
