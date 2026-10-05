---
description: Code style — DRY, KISS, Clean Code, SOLID, Don't Make Me Think; project-best-practices when present
globs: "**/*.{ts,tsx,js,jsx,mjs,cjs,vue,svelte,astro,css,scss,sass,less,html,py,go,rs}"
always: false
---

# Code

## When to read and apply

- **Read this file whenever** you edit, add, or review **source files** under the user's intent (implement, refactor, fix, types, components).
- **After reading**, run through the **Checklist** before considering the edit done.
- **Workspace scope:** When a change spans **multiple packages or repos**, run the checklist on **every file path you touched for that feature**.
- **Comments:** see **`base`** (always on) — this rule does not repeat that policy.
- **Project best practices (single definition):** when **adding, changing or deleting project code** and `.agents/skills/project-best-practices/SKILL.md` exists in the project root, **read that skill first**, then the task-relevant files it references (its `references/` and the sibling skills it names), and follow them. This is the only location for every tool: there is no per-tool variant. If the file is absent, skip — do not invent a stand-in. Other items refer to this paragraph instead of restating it.

## Naming

- Prefer **intention-revealing** identifiers over terse or cryptic abbreviations.
- **Scope heuristic:** tighter scope → shorter locals are OK (`i`, `id`) if conventional; broader scope or persisted API → fuller names.
- **Avoid** single-letter names except idiomatic indices (`i`) and conventional scalars on axes.
- **Functions** read as verbs; **predicates/booleans** read as yes/no (`isExpired`, `hasItems`).

## Structure

- Prefer **small, named functions** (and components/modules where applicable) with a single clear responsibility.
- Prefer **fewer branching levels** via early returns or small extracted helpers rather than sprawling nested `if`s when it clarifies intent.

## Principles

- **Clean Code** and **SOLID:** meaningful names, short units, low coupling, clear boundaries; one reason to change per unit; depend on interfaces/types, not hidden globals.
- **KISS:** simplest structure that fits the real use cases; no speculative generalization.
- **DRY:** do not repeat the same knowledge; extract only when copies would change for the same reason — not lookalike code with different reasons.
- **Don't Make Me Think:** names, layout, and control flow should be obvious at the call site; if a reader has to decode, rename or restructure first.
- Prefer **immutable-by-default** for values you don't mutate; mutation should be visibly localized.

## Checklist before finishing

- [ ] **Don't Make Me Think:** call sites and branches are obvious without a tour of helpers.
- [ ] **Names** spell intent at call sites without reading the whole body.
- [ ] **Units** are small enough to hold in memory; oversized functions warrant extraction.
- [ ] **KISS / DRY:** no extra abstraction; duplicated knowledge is extracted, coincidental similarity is not.
- [ ] **SOLID-lite:** one reason to change per unit; callers depend on interfaces/types, not hidden globals.
- [ ] **Project best practices:** if `.agents/skills/project-best-practices/SKILL.md` exists in the project root, it was read before the edit and the diff complies with it.
- [ ] Diff matches the **task** — no drive-by churn on unrelated identifiers or structure.
