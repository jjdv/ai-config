---
name: ask-questions
description: >-
  Ask the user structured clarifying questions before guessing on scope, product
  policy, or ambiguous requirements. Uses AskQuestion with scoped prompts and
  concrete options. Use when a decision would change implementation, acceptance
  criteria, or which option to build; when requirements are incomplete; or when
  the user asks for questions before proceeding.
---

# Ask questions

**Ask (do not guess)** when the answer would change what you build, validate, or recommend next.

## Tool first

When **`AskQuestion`** is available, use it instead of a prose numbered list or open-ended “any questions?”.

| Prefer | Avoid |
| --- | --- |
| One **`AskQuestion`** call with 1–4 related questions | Seven loose bullets the user must reply to in free text |
| Options that name **outcomes** | Vague yes/no without saying what each path means |
| **Wait** for answers before delegating or editing | Stating a default and continuing |

If **`AskQuestion`** is unavailable, use the same structure in chat: short **Decision** line, **Options** (A/B/C), **Why it matters** — then wait.

## Question design

Each question must make **scope obvious** in the `prompt`:

1. **Decision** — what you need chosen (one sentence).
2. **Context** — why it matters / what blocks without it (one short clause).
3. **Options** — 2–4 concrete paths; labels readable without reading the rest of the chat.

**Option labels**

- Name the **behavior or artifact**, not jargon alone.
- Keep labels scannable (roughly one line).
- Put the recommended option **first** and suffix **`(Recommended)`** when you have a clear default **and** the user may still override.
- Do not hide “do nothing / defer” — add an explicit option when valid.

**When to use `allow_multiple: true`**

- Independent concerns that can combine (e.g. “enforce on server **and** hide in UI”).
- Not for mutually exclusive product choices — use single-select.

**Batching**

| Situation | Batch |
| --- | --- |
| One decision, 2–4 alternatives | 1 question |
| Related decisions (same feature area) | 1 **`AskQuestion`**, up to **4** questions |
| Unrelated decisions | **Separate** **`AskQuestion`** rounds — finish round 1, act or summarize, then round 2 |
| More than 4 decisions | Split across rounds; never one mega-form |

**Forbidden**

- Questions answerable from repo docs or the current message — read first.
- “Is this OK?” without stating what “this” is.
- Options that all mean the same thing with different wording.
- Proceeding after asking without waiting for answers.

## Procedure

1. **Identify blockers** — list only choices that change scope, policy, or acceptance criteria.
2. **Draft prompts** — decision + context + options per question.
3. **Call `AskQuestion`** — use stable `id`s (kebab-case); set `allow_multiple` only when options may combine.
4. **Stop** — no implementation, delegation, or speculative defaults until the user answers.
5. **Reflect answers** — one short sentence confirming what was chosen, then continue.

## Example (product policy)

**Bad (chat prose):**

> 1. Daily expiry? 2. Without errors? 3. Reading value? …

**Good (`AskQuestion`):**

| id | prompt (pattern) | options |
| --- | --- | --- |
| `ready-expiry` | **When should a meter stop being pickable for install?** After midnight (Europe/Warsaw), should it stay `READY` in DB but be hidden until re-read, or demote to `ACCEPTED`? | Stay READY, hide until re-read (Recommended) · Demote to ACCEPTED · Other |
| `ready-errors` | **What counts as “wM-Bus read without errors” for ready-for-install?** This defines magazyn eligibility. | Decode/decrypt success only · Also exclude health anomalies · Also require full parameter backfill · Other |

## Subagents

When **`composer`** or another subagent is blocked on user policy, return **draft `AskQuestion` payloads** (ids, prompts, options) to the main thread — do not pick product defaults in the subagent.

## Relation to `base`

The **`base`** rule requires clarify-before-act. This skill is the **format** for that step: structured form, scoped prompts, wait for answers.
