---
name: give-instructions
description: >-
  Give clear numbered steps for actions only the human should take (terminal
  commands, UI, approvals, pasting output back) when a gate blocks the agent,
  the work must not be run by the agent, the thread does not say what the user
  should do, or it is unclear which commands or UI steps the user should run.
  Also use when the user invokes /give-instructions or attaches this skill.
---

# Give instructions

At **gate situations**: work must be done by the human; the agent must not run it unless the user explicitly asks after reading the steps.

## Response shape

- **Situation** — one short line, or omit when the thread already makes it obvious.
- **Your steps** — numbered list of **human-only** actions (terminal, UI, approvals, paste output back, etc.). Every numbered item is something **only the user** runs or does. Do not put agent-runnable work (read files, run checks, edit code, delegate) in the numbered list as if the user should do it.
- **Agent (between steps)** — when the agent should act after a user step, say so in a short labeled block **outside** the numbered list (for example **Agent (after you paste the output):** then what you will do). **Wait** for the user to finish the preceding step (including pasting results) before that agent work; do not continue in the same turn unless they already supplied it.
- Each user step: **1–3 sentences** of prose (what to do; **why** only when not obvious). **Do not** put shell commands in inline backticks inside the numbered line — commands belong in fenced blocks (below).
- **Commands** — every shell command and multi-line command sequence in its **own** markdown fenced code block with a language tag (`bash` by default). Place the block **immediately under** the numbered step it belongs to. When several steps run in one shell session, one combined `bash` block under the last of those steps is fine. Single-line `curl`, env edits, or paste-back snippets use `bash` or `text` fences as appropriate. UI-only steps stay prose with no command fence. Use placeholders only when values are unknown, and say what to substitute in the step prose above the block.
- **Do not** run gated commands or take gated UI actions yourself unless the user explicitly asks after reading the steps.
- No long preamble; no agent todo list disguised as user instructions.

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
