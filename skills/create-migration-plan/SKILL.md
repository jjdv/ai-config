---
name: create-migration-plan
description: >-
  Analyze a website/page-group migration scope, agree an architecture with the
  user, then author a handoff-ready sequential-implementation plan. Use when
  migrating routes or domains from a reference repo to the monorepo, planning
  blocks/components/page types, or when the user says create migration plan,
  migration scope, or /create-migration-plan.
---

# Create migration plan

> **Tool mapping (Cursor / Claude Code):** subagent spawn `Task(subagent_type=…, model=…)` → `Agent(subagent_type=…)`; `AskQuestion` → `AskUserQuestion`; `@Browser` / `cursor-ide-browser` → Claude browser tools; `Write`/`StrReplace`/`Shell` → `Write`/`Edit`/`Bash`. The `composer` agent exists in both tools (Cursor runs `composer-2.5` — always pass `model="composer-2.5"`; in Claude Code it is pinned to `sonnet` — do not pass `model`). User skills live in `~/.agents/skills/` (Cursor) or `~/.claude/skills/` (Claude Code).

**Upstream:** analysis + user agreement → **downstream:** [`create-plan`](../create-plan/SKILL.md) plan file + `.local/<slug>/` artifacts.

**Do not** write the plan until the user explicitly agrees the proposed solution (Phase 3 gate).

## When to use

- New page-group or route-batch migration (e.g. `/legal/*`, `products`, single landing page)
- Follow-on child plan after a parent migration shell ships (parity, gaps, CMS seed)
- User provides **migration scope** in the prompt (routes, domain name, source repo, constraints)

Not for: one-line bug fixes, parity-only passes on already-agreed architecture (use `improve-parity` + existing plan), or harness/rule edits.

## Required skills (load before Phase 1)

| Skill | When |
| --- | --- |
| `project-best-practices` | When `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists — **mandatory** for that repo's migrations |
| [`create-plan`](../create-plan/SKILL.md) | Phase 4 only — plan shape, checklist, composer-fit |
| [`improve-parity`](../improve-parity/SKILL.md) | Phase 1 analysis + Phase 4 parity task design |
| [`documentation`](../documentation/SKILL.md) | Durable docs vs `.local/` split |
| [`ask-questions`](../ask-questions/SKILL.md) | Phase 2 — structured choices for open points |

**Code quality:** Plans that edit source must require the **code** user rule in **Fresh chat handoff** (per `create-plan` § Conventions coverage).

## Workflow overview

```
Phase 1 — Analyze scope (read-only)
Phase 2 — Propose solution (concise) + open questions
Phase 3 — Discuss → user agrees final solution  ← GATE
Phase 4 — Author plan (create-plan + parity caps)
```

Track phase in chat; do not skip Phase 3.

---

## Phase 1 — Analyze migration scope

**Goal:** Inventory source → target mapping and candidate architecture **before** proposing tasks.

### 1.1 Parse scope from prompt

Extract and confirm:

| Field | Examples |
| --- | --- |
| **Routes / URLs** | `/products/*`, 27 legal pages, single `/pricing/` |
| **Domain slug** | `legal`, `products`, `core-marketing` |
| **Source** | Sibling repo path, production URLs, MDX/CMS export |
| **Target** | Monorepo package (`website/`), dataset |
| **Constraints** | Tier, redirects, out-of-scope (header, forms), deadline |
| **Parent plan** | Link if child of `existing-website-migration-plan.md` or similar |

If scope is ambiguous, **one** `AskQuestion` round — do not guess route lists or source repo.

### 1.2 Load conventions and references

When `project-best-practices` exists, read **at minimum**:

- `SKILL.md`
- `references/placement.md`, `references/website-structure.md`
- Task-relevant: `references/cms-blocks.md`, `references/styling.md`
- `docs/website/migration-sources.md` when migrating from production siblings

Also check: `docs/website/block-inventory.md`, domain foundation docs (`docs/website/*-foundation.md`), existing `.local/` plans for the same domain.

### 1.3 Source investigation (read-only)

Survey reference material for the scoped routes:

- Route manifest, page templates, MDX/component sequences
- Reusable patterns vs one-off sections
- CMS shapes (if any), images/assets, redirects
- Production vs source-repo inconsistencies (flag for parity policy)

Use `composer` or `explore` subagent when scope spans **>3 routes** or multiple source files — **one** investigation spawn per domain slug.

### 1.4 Architecture analysis dimensions

For each scoped route group, decide **candidates** (not final — Phase 2 proposes):

| Dimension | Questions |
| --- | --- |
| **Blocks** | Which CMS `*Block` units? New dedicated `blocks/<PageName>/` vs `blocks/<domain>/` vs extend `blocks/ui|common/`? |
| **Components** | New `components/ui|common|<domain>|<PageName>/`? Extend existing primitives with `variant`? |
| **Page types** | New `pageTypes/<PageName>/` shell? Reuse `mainPage` / domain page type? |
| **Theme / tokens** | New palette entries, page-type SCSS, `rich_text` variant, band surfaces? **Global token change → escalate** |
| **Utilities** | Migrator script, `mapBlocks`, GROQ in `SanityCmsService`, redirects, manifest/404 routes |
| **Sanity** | New schemas, singletons, seed/import strategy (OAuth MCP/CLI only per `sanity-data-handling`) |
| **Parity** | Fixture URLs, viewports (default **1250 / 900 / 320**), regions in/out of scope |
| **Scope boundary** | Domain paths agents may edit vs global/shared (`components/ui/`, theme JSON) — propose only |

Apply **placement.md** decision guides: judge by **potential** reuse; prefer extend over fork; thin domain blocks over fat page-type blocks when CMS-driven.

### 1.5 Parity pre-analysis

Per `improve-parity`:

- List fixture URLs (representative, not every route unless small batch)
- Note structural risks (merged prose, block-count mismatch, chrome bands)
- Default parity invocation: **Phase A (CSS) → Phase B (visual)**; **5 iterations per phase** per parity scope (max 5; user may lower in agreement)
- Plan will **delegate** parity steps to `improve-parity` — do not duplicate methodology in task bodies

### 1.6 Output (internal)

Draft content for `.local/<slug>/architecture.md` and open questions — **do not write files yet** unless user asked to persist early.

Use [analysis brief template](references/analysis-brief.md) for structure.

---

## Phase 2 — Propose solution (concise)

**Goal:** User can scan in ~2 minutes; details on request.

Present **only**:

1. **Scope recap** — routes, source, out-of-scope (1–3 lines)
2. **Architecture summary** — table: layer → new / extend / reuse (blocks, components, page types, utilities)
3. **Page-type & styling** — new shells, token/variant overrides (call out **global** items)
4. **CMS & data** — schemas, migrator/import approach (high level)
5. **Phases sketch** — 3–6 phase names with one-line outcomes (not task IDs yet)
6. **Parity approach** — fixture URLs, viewports, **5 iterations per phase** (max 5 per scope)
7. **Open points** — numbered; use `AskQuestion` for decisions that change implementation

**Do not** dump full file trees or every route unless asked.

### Open points — must clarify before Phase 3

Escalate to user when any apply:

- Global theme / `components/ui/` changes
- Duplicate vs consolidate blocks (merge profile / megablock)
- Production inconsistency with no foundation rule
- CMS import to production dataset
- Redirect policy, retired routes, Tier D divergence
- Parity scope (include nav/footer or not)

---

## Phase 3 — Agree final solution

Iterate Phase 2 until the user confirms explicitly (e.g. “agreed”, “looks good”, “create the plan”).

On agreement, **lock** in chat summary:

- Final block/component/page-type placement
- Scope boundary (domain vs global)
- Parity fixtures, viewports, **iterations per phase** (default **5**, max 5)
- Deferred / out-of-scope items
- Child vs parent plan relationship

**Gate:** No `.local/*-plan.md` until Phase 3 complete.

---

## Phase 4 — Author plan

Follow [`create-plan`](../create-plan/SKILL.md) end-to-end.

### 4.1 Slug and artifacts

| Artifact | Path |
| --- | --- |
| Main plan | `.local/<slug>-plan.md` |
| Decisions | `.local/<slug>/decisions.md` — locked choices from Phase 3 |
| Architecture | `.local/<slug>/architecture.md` — route map, block inventory, retirement notes |
| Task specs | `.local/<slug>/tasks/<id>.md` — non-trivial tasks only |
| Mapping (optional) | `.local/<slug>/parity-mapping.md` — block-type → prod role hints for `improve-parity` |

Ensure `.local/` is gitignored when creating new plans.

### 4.2 Migration-specific plan sections

Include when applicable (patterns from `create-plan` optional sections):

| Section | Migration use |
| --- | --- |
| **Target vs current** banner | Docs vs code lag |
| **Autonomy & authorization** | Dev server, parity, domain-scoped edits, CMS import if pre-approved |
| **Scope boundary** | Domain paths vs global/shared |
| **Parity scoreboard** | Empty table; update during `improve-parity` tasks |
| **Operator handoff** | Import, deploy, asset copy — not plan tasks unless user requested |

### 4.3 Typical phase pattern

Adapt to scope size; split until **composer-fit** passes:

| Phase | Typical tasks |
| --- | --- |
| **1 — Foundation** | Schemas, page type shell, tokens/SCSS entry, redirects |
| **2 — Blocks & components** | Vertical slices: schema → block → component → registry |
| **3 — Routes & CMS** | Pages, GROQ, migrator, seed/import |
| **4 — Parity** | One task per coherent URL batch; task body points to `improve-parity` with agreed iterations/viewports |
| **5 — Closure** | Scoreboard sign-off, docs update, parent index link |

**Parity tasks** — task spec must include:

```markdown
## Parity invocation

- Skill: `improve-parity`
- URLs: …
- Viewports: 1250 / 900 / 320 (or agreed set)
- Iterations per phase: 5 (max 5; lower only if agreed in Phase 3)
- Out of scope: global header/footer unless listed
- Mapping overlay: `.local/<slug>/parity-mapping.md` (if present)
```

Do **not** embed full CSS probe checklists — reference the skill.

### 4.4 Composer-fit and parity

- One parity task = one route batch finishable in one spawn (e.g. listing + one story, not entire domain unless ≤3 URLs)
- Investigation-only work → separate report task ID before implementation tasks
- **5** compare→fix iterations per phase per parity scope in task spec (max 5; lower only if Phase 3 agreed)

### 4.5 Checklist before `status: ready`

Run **create-plan** Handoff readiness checklist. Additionally:

| Check | Pass when |
| --- | --- |
| User agreement | Phase 3 confirmed in chat |
| Decisions file | `decisions.md` reflects locked choices |
| Parity delegation | Every parity task references `improve-parity`; no duplicated methodology |
| Iteration cap | Each parity task ≤5 iterations/phase |
| Scope boundary | Global paths listed under escalation |
| Parent link | Child plans link from parent index when applicable |

Run [`check-plan`](../check-plan/SKILL.md) when available.

### 4.6 Hand off to user

```
/check-plan <project-root>/.local/<slug>-plan.md
/sequential-implementation <project-root>/.local/<slug>-plan.md
```

---

## Anti-patterns

- Writing the plan before user agreement
- Mega-tasks: “migrate legal” without block/route slices
- Duplicating `improve-parity` CSS probe rules in task files
- Defaulting global token changes without escalation
- Skipping `project-best-practices` placement analysis
- Parity tasks with >5 iterations per phase
- Implementation order listing completed task IDs

---

## Examples

```
/create-migration-plan legal — Tier A, 27 routes from uploadcare-website, rich_text legal variant
```

```
/create-migration-plan /products/file-uploader/ and /products/uploading/ — single page type, parity 3 rounds
```

```
/create-migration-plan customers parity child plan — fixtures in customers-foundation.md, max 5 iterations
```

---

## Related

- Plan execution: `sequential-implementation`
- Parity execution: `improve-parity`
- Uploadcare index: `.local/existing-website-migration-plan.md`
- After editing this skill: `update-harness`
