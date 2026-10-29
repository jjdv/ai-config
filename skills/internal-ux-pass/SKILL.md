---
name: internal-ux-pass
description: >-
  Internal UX/UI design pass before the first product edit when implementing
  simple user-facing surfaces (visual UI and CLI/terminal output humans read).
  Apply when output, prompts, progress, exit status, quiet/verbose, or
  structured vs human-readable presentation changes. Agent decides flows and
  layout internally — no user-facing UX proposals in chat. Use when adding,
  fixing, or changing user-facing surfaces in a bounded implementation task.
  Not for greenfield multi-aspect shaping (propose-plan), read-only assessment
  of existing scope (assess-scope), localhost vs production visual parity
  (improve-parity), or canonical design tokens and library files (design-system
  / project design-system skill).
---

# Internal UX pass

{{block:tool-note}}

**Design before build** for simple user-facing work: decide UX and UI **internally**, then implement. Do not present flow or screen options in chat. Do not ask the user except the **Escalation** case below.

## When to apply

- A bounded task adds, fixes, or changes **user-visible surfaces**: visual UI (forms, dialogs, lists, settings, controls, wizards, empty states, toasts) or **CLI/terminal** output and interaction (commands, operators, developers at the terminal).
- The supervisor or implementing agent loads this skill before the **first** edit to product code or config that affects what users see in UI or terminal.
- **`sequential-implementation`** user-facing tasks: run this pass before the first product edit; the supervisor names this skill in the delegated task spec.

## When not

- Backend-only, infra, or API-only changes with **no user-visible** effect (no change to UI or to terminal output, prompts, or interactivity).
- Copy-only typo fixes with no layout, interaction, or output-format change.
- Pure refactor that preserves existing UX verbatim.
- Full product shaping before a plan exists → **`propose-plan`**.
- Audit or improve an existing feature without a fixed implementation spec → **`assess-scope`**.
- Visual parity against a reference deployment → **`improve-parity`**.
- Design tokens, component gallery, or stack design library files → **`design-system`** (or the project's design-system skill when present).

## Internal pass (mandatory before first edit)

1. **Conventions (step 0).** When `<project-root>/.agents/skills/project-best-practices/` exists, read its UI, copy, interaction, and CLI/output references before inventing patterns.
2. **Frame.** One sentence each: goal, primary user, hard constraints (accessibility, platform, data already on screen or in context).
3. **Primary path.** Happy path in order. For visual UI: **empty**, **loading**, **error**, **success**, and **disabled** on the same surface. For CLI in parallel: primary command path; **progress** and **quiet/verbose** behaviour; **error/success** signaling (exit code, stderr tone); **disabled** or unavailable commands when relevant.
4. **Options (internal only).** Generate two or three plausible layouts, flows, or output shapes; do not paste them into chat.
5. **Pick one** using heuristics: clarity at a glance, feedback on action, recoverable errors, keyboard and focus order for UI, consistency with nearby UI and **existing CLI patterns** in the repo (flags, error tone, exit semantics).
6. **Record (optional, internal).** A few lines in the task handoff or the plan task file under `.local/` — not chat, not durable docs unless **`documentation`** says to persist.

Then implement the chosen pattern in one coherent pass unless the spec requires splitting.

## Escalation (only exception)

When UX is **clearly ambiguous** — any reasonable choice would **materially** change product behaviour — ask **once** with **`ask-questions`**: one focused question, two to four options, recommended option first with a short reason. After the answer, finish the internal pass and implement. No second UX round.

## Default when not ambiguous

Prefer the **safest boring** pattern: match existing screens and commands in the same area, reuse established components, flags, and copy tone, minimal new interaction idioms, explicit loading and error states rather than silent failure. Document the chosen pattern in the internal note or handoff, not in chat.

## Relationship

- **`propose-plan`**: settles product and multi-aspect decisions with the user before **`create-plan`**; this skill does not replace it.
- **`assess-scope`**: read-only findings on existing scope; implementation UX choices happen here at edit time.
- **`documentation`**: after the change, sync user-facing docs when that skill's persist rules apply — this skill does not author docs.

## Anti-patterns

- Dumping UX options or wireframes in chat for approval.
- Skipping the pass because the UI or CLI change is "small."
- Treating CLI output, prompts, or exit behaviour as "not UX."
- Multiple user questions across the task.
- Guessing when escalation criteria are met.
