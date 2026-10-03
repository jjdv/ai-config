---
name: debug-in-browser
description: >-
  ALWAYS use when browser debugging is needed. Route lightweight checks to
  Cursor @Browser; delegate deep automation (evaluate, caret, console/network,
  flaky repro) to the playwright subagent. Evidence-first workflow with
  mandatory cleanup of DEBUG_TMP instrumentation.
---

# Debug in browser

> **Tool mapping (Cursor / Claude Code):** subagent spawn `Task(subagent_type=…, model=…)` → `Agent(subagent_type=…)`; `AskQuestion` → `AskUserQuestion`; `@Browser` / `cursor-ide-browser` → Claude browser tools; `Write`/`StrReplace`/`Shell` → `Write`/`Edit`/`Bash`. The `composer` agent exists in both tools (Cursor runs `composer-2.5` — always pass `model="composer-2.5"`; in Claude Code it is pinned to `sonnet` — do not pass `model`). User skills live in `~/.agents/skills/` (Cursor) or `~/.claude/skills/` (Claude Code).

## Goal

Fast root-cause discovery with minimal iteration. Pick **one** primary path per atomic check by **evidence goal**, not by wording.

Phrases like **debug in browser**, **browser debugging**, **test in the browser**, or **repro in the browser** all trigger this skill.

## Routing

Compare the check to the table. Do **not** run two browser stacks in parallel for the same check.

| Prefer **@Browser** (IDE-integrated) | Prefer **playwright subagent** (deep automation) |
| --- | --- |
| Reproduce with **clicks, typing, keys** | Need **`page.evaluate` / in-page JS** (selection, ranges, offsets) |
| **Accessibility snapshot** or screenshots are enough | Need **precise DOM or selection state** around the caret |
| Quick **smoke check** after a change | **Flaky** or timing-sensitive repro; structured capture and retries |
| Console / network forensics **not** required | Need **console, network, or evaluate** tied to one hypothesis |

**Default:** try **@Browser** first when the check fits the left column.

**Escalation:** If @Browser cannot falsify the hypothesis, start a **new** loop with the playwright subagent (new hypothesis, explicit stop condition). Stop after **two** iterations without improving confidence; ask the user.

## Tooling rules (main agent)

| Path | Main agent may |
| --- | --- |
| **@Browser** | Use Cursor IDE Browser (`@Browser`, MCP `cursor-ide-browser`) directly |
| **Playwright MCP** | **Must not** call Playwright MCP directly — delegate via **`/playwright`** or `Task(subagent_type="playwright")` with a scenario packet |

## Workflow

1. Analyze relevant code paths; define **one** hypothesis, evidence target, expected outcome, and stop condition.
2. Route per table above.
3. Execute the shortest reproduction path for that route.
4. Update or falsify the hypothesis from evidence.
5. Add `DEBUG_TMP:` instrumentation only if evidence is still insufficient.
6. Implement fix, re-validate with the **same class of tooling**, remove all debug instrumentation.
7. Report root cause, fix, validation, cleanup, and whether escalation occurred.

## Bounded interactivity

- One focused pass, one clear outcome by default.
- Next loop: re-classify tooling, new hypothesis, new evidence target, explicit stop condition.
- If confidence does not improve after **two** iterations, stop and ask the user.

## @Browser path

1. Confirm the check fits the lightweight column; if not, switch to playwright delegation.
2. Drive reproduction with integrated browser tools; snapshots/screenshots as needed.
3. Report: tooling used, steps (short), evidence summary, hypothesis + confidence, whether to escalate.

Store screenshots under `.tmp/cursor-browser/` per the **temp-files** rule.

## Playwright subagent path

Write a **scenario packet** before delegating. Task prompt **must** require session teardown.

```markdown
Scenario: <short name>
Theory under test: <single falsifiable statement>
Objective: <what this run proves or disproves>
Target URL(s): <exact environment/page>
Preconditions: <auth/data/state/setup>
Steps to reproduce:
1) …
(For caret/selection: **expected Before state** per step; assert before each caret-moving key.)
Expected result: <correct behavior>
Observed result (known): <current behavior; omit if unknown>
Data to gather (must collect):
- <e.g. evaluate: anchorNode, anchorOffset, isCollapsed>
Success criteria:
- <criterion 1—binary or measurable>
Required feedback (answer each):
1) Does the theory hold? (yes/no/unclear) with justification.
Allowed measures:
- console / network / screenshots / evaluate / retries: yes/no each
Instrumentation policy:
- Temporary debug logs allowed: yes/no
- Cleanup requirement: remove all temporary logs before completion
Deliverables:
- Findings: ≤5 bullets tied to theory or success criteria
- Evidence for each **Data to gather** item
- Verdict: confirmed / rejected / inconclusive + confidence
- **Session teardown:** confirmed or explicit deferral
```

Fill the brief from `references/playwright-brief-template.md` (in this skill), then spawn with `subagent_type="playwright"`. Subagent spec: `~/.cursor/agents/playwright.md`.

## Debug logging

- Add temporary logs only after one evidence pass fails to isolate cause.
- Prefix: `DEBUG_TMP:`.
- Keep instrumentation minimal and scoped to the suspected branch.
- Remove all `DEBUG_TMP:` markers and branches before finishing.

## Cleanup (mandatory)

1. Remove all `DEBUG_TMP:` logs and temporary branches.
2. Re-run the target scenario without instrumentation.
3. Confirm no leftover debug markers.
4. Report cleanup status explicitly.

## Approval

Assume task-level debugging is approved. If MCP prompts block progress, ask the user to enable persistent trust for the relevant MCP server, then resume with the same scenario and no scope drift.

## Output contract

1. Route used (@Browser or playwright subagent)
2. Scenario executed
3. Evidence summary (high-signal only)
4. Root cause hypothesis + confidence
5. Fix applied (if any) and validation result
6. Debug instrumentation cleanup confirmation
