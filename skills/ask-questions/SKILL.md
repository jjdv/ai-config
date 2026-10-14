---
name: ask-questions
description: >-
  Ask the user structured clarifying questions before guessing on scope, product
  policy, or ambiguous requirements. Uses {{tool:ask-user}} with scoped prompts and
  concrete options. Use when a decision would change implementation, acceptance
  criteria, or which option to build; when requirements are incomplete; or when
  the user asks for questions before proceeding.
---

# Ask questions

{{block:tool-note}}

**Ask (do not guess)** when the answer would change what you build, validate, or recommend next.

## Tool first

When **`{{tool:ask-user}}`** is available, use it instead of a prose numbered list or open-ended “any questions?”.

| Prefer | Avoid |
| --- | --- |
| One **`{{tool:ask-user}}`** call with 1–4 related questions | Seven loose bullets the user must reply to in free text |
| Options that name **outcomes** | Vague yes/no without saying what each path means |
| **Wait** for answers before delegating or editing | Stating a default and continuing |

If **`{{tool:ask-user}}`** is unavailable, use the same structure in chat: short **Decision** line, **Options** (A/B/C), **Why it matters** — then wait.

## Question design

Each question must make **scope obvious** in the `prompt`:

1. **Decision** — what you need chosen (one sentence), naming any referenced item by title or short description (id in brackets only as extra help).
2. **Context** — why it matters / what blocks without it (one short clause).
3. **Options** — 2–4 concrete paths; labels readable without reading the rest of the chat.

**Option labels**

- Name the **behavior or artifact**, not jargon alone.
- Keep labels scannable (roughly one line).
- Put the recommended option **first** and suffix **`(Recommended)`** when you have a clear default **and** the user may still override. State the reason for the recommendation in the question's prompt, as propose-plan requires.
- Do not hide “do nothing / defer” — add an explicit option when valid.

**When to allow several answers**

- Independent concerns that can combine (e.g. “enforce on server **and** hide in UI”).
- Not for mutually exclusive product choices — use single-select.

**Batching**

| Situation | Batch |
| --- | --- |
| One decision, 2–4 alternatives | 1 question |
| Related decisions (same feature area) | 1 **`{{tool:ask-user}}`**, up to **4** questions |
| Unrelated decisions | **Separate** **`{{tool:ask-user}}`** rounds — finish round 1, act or summarize, then round 2 |
| More than 4 decisions | Split across rounds; never one mega-form |

**Forbidden**

- Questions answerable from repo docs or the current message — read first.
- Referring to anything only by id, section or task number; restate it by title.
- “Is this OK?” without stating what “this” is.
- Options that all mean the same thing with different wording.
- Proceeding after asking without waiting for answers.

## Procedure

1. **Identify blockers** — list only choices that change scope, policy, or acceptance criteria.
2. **Draft prompts** — decision + context + options per question.
3. **Call `{{tool:ask-user}}`** — give each question a stable kebab-case `id`; allow several answers only when options may combine. Ids stay internal; question text and option labels must not depend on them.
4. **Stop** — no implementation, delegation, or speculative defaults until the user answers.
5. **Reflect answers** — one short sentence confirming what was chosen, then continue.

## Example (product policy)

**Bad (chat prose):**

> 1. Daily expiry? 2. Without errors? 3. Reading value? …

**Good (`{{tool:ask-user}}`):**

| id | prompt (pattern) | options |
| --- | --- | --- |
| `trial-expiry` | **When should a trial account stop being eligible for upgrade?** Recommended: stop at trial end, because billing and access rules already assume it; a grace period needs its own support path. | Stop at trial end (Recommended) · Keep a 7-day grace period · Other |
| `trial-reminders` | **Which channels should warn trial users before expiry?** Recommended: email plus an in-app banner, because email alone is often missed; each channel adds consent and support load. | Email only · Email and in-app banner (Recommended) · Other |

## Subagents

When a subagent of any tier is blocked on user policy, return **draft `{{tool:ask-user}}` payloads** (ids, prompts, options) to the main thread — do not pick product defaults in the subagent. Every item a draft payload refers to gets a title (ids optional, in brackets); the supervisor rewrites id-only items before showing them.

## Relation to `base`

The **`base`** rule requires clarify-before-act. This skill is the **format** for that step: structured form, scoped prompts, wait for answers.
