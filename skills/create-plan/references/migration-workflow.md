# Migration plan workflow

Loaded by `create-plan` for a website/page-group migration (routes or domains from a reference repo to the target monorepo, blocks/components/page types, or a follow-on child plan such as parity, gaps, CMS seed). Not for one-line fixes, parity-only passes on an agreed architecture (`improve-parity` + existing plan), or harness edits.

**Upstream:** analysis + user agreement → **downstream:** a `create-plan` plan file + `.local/<slug>/` artifacts.

**Gate:** do **not** write any `.local/*-plan.md` until the user explicitly agrees the proposed solution (Phase 3).

## Execution

Phases 1, 2 and 4 run on `{{senior_agent_name}}`{{#cursor}} (`model="{{senior_agent_model}}"`){{/cursor}} per `create-plan` § Execution. Phase 3 is the supervisor's: it presents the Phase 2 proposal, iterates with `{{ask_tool}}`, and spawns `{{senior_agent_name}}` for Phase 4 only after explicit agreement, passing the locked summary. Track the phase in chat.

## Required skills (load before Phase 1)

| Skill | When |
| --- | --- |
| `project-best-practices` | Mandatory when `<project-root>/.agents/skills/project-best-practices/SKILL.md` exists |
| `improve-parity` | Phase 1 analysis + Phase 4 parity task design |
| `documentation` | Durable docs vs `.local/` split |
| `ask-questions` | Phase 2 — structured choices for open points |

Source-editing plans require the **code** user rule in **Fresh chat handoff** (`create-plan` § Conventions coverage).

## Parity defaults (single source)

Fixtures: representative URLs, not every route unless the batch is small. Viewports **1250 / 900 / 320**. Order **Phase A (CSS) → Phase B (visual)**. **5 iterations per phase** per parity scope (max 5; lower only if agreed in Phase 3). Plans **delegate** parity to `improve-parity` — never duplicate its methodology or CSS probe checklists in task bodies.

## Phase 1 — Analyze (read-only)

Inventory source → target mapping and candidate architecture **before** proposing tasks.

**1.1 Parse scope.** Extract and confirm: routes/URLs (`/products/*`, 27 legal pages); domain slug (`legal`, `core-marketing`); source (sibling repo, production URLs, MDX/CMS export); target (monorepo package, dataset); constraints (tier, redirects, out-of-scope header/forms, deadline); parent plan (child of `existing-website-migration-plan.md` or similar). Ambiguous scope → **one** `{{ask_tool}}` round; never guess route lists or source repo.

**1.2 Conventions.** With `project-best-practices`, read at minimum `SKILL.md`, `references/placement.md`, `references/website-structure.md`; task-relevant `references/cms-blocks.md`, `references/styling.md`; `docs/website/migration-sources.md` when migrating from production siblings. Also check `docs/website/block-inventory.md`, domain foundation docs (`docs/website/*-foundation.md`), existing `.local/` plans for the domain.

**1.3 Source investigation.** Survey for the scoped routes: route manifest, page templates, MDX/component sequences; reusable patterns vs one-off sections; CMS shapes, images/assets, redirects; production vs source-repo inconsistencies (flag for parity policy). When scope spans **>3 routes** or multiple source files, use the `{{explore_agent_name}}` subagent (read-only search) — **one** investigation spawn per domain slug.

**1.4 Architecture dimensions.** Per route group, decide **candidates** (Phase 2 proposes):

| Dimension | Questions |
| --- | --- |
| **Blocks** | Which CMS `*Block` units? New `blocks/<PageName>/` vs `blocks/<domain>/` vs extend `blocks/ui|common/`? |
| **Components** | New `components/ui|common|<domain>|<PageName>/`? Extend primitives with `variant`? |
| **Page types** | New `pageTypes/<PageName>/` shell? Reuse `mainPage` / domain page type? |
| **Theme / tokens** | New palette entries, page-type SCSS, `rich_text` variant, band surfaces? **Global token change → escalate** |
| **Utilities** | Migrator script, `mapBlocks`, GROQ in `SanityCmsService`, redirects, manifest/404 routes |
| **Sanity** | New schemas, singletons, seed/import strategy (OAuth MCP/CLI only per `sanity-data-handling`) |
| **Parity** | Fixture URLs, regions in/out of scope (defaults above) |
| **Scope boundary** | Domain paths agents may edit vs global/shared (`components/ui/`, theme JSON) — propose only |

Apply **placement.md** decision guides: judge by **potential** reuse; prefer extend over fork; thin domain blocks over fat page-type blocks when CMS-driven.

**1.5 Parity pre-analysis** (per `improve-parity`): list fixture URLs; note structural risks (merged prose, block-count mismatch, chrome bands).

**1.6 Output (internal).** Draft `.local/<slug>/architecture.md` content and open questions using [analysis-brief.md](analysis-brief.md); **do not write files** unless the user asked to persist early.

## Phase 2 — Propose (concise, ~2-minute scan)

Present **only**: (1) scope recap — routes, source, out-of-scope; (2) architecture summary — layer → new/extend/reuse; (3) page-type & styling — new shells, token/variant overrides, **global** items called out; (4) CMS & data — schemas, migrator/import approach; (5) phases sketch — 3–6 phase names with one-line outcomes (no task IDs); (6) parity approach (fixtures, viewports, iterations); (7) numbered open points, using `{{ask_tool}}` for decisions that change implementation. No full file trees or route dumps unless asked.

**Escalate to the user before Phase 3 when:** global theme / `components/ui/` changes; duplicate vs consolidate blocks (merge profile / megablock); production inconsistency with no foundation rule; CMS import to the production dataset; redirect policy, retired routes, Tier D divergence; parity scope (include nav/footer or not).

## Phase 3 — Agree (gate)

Iterate Phase 2 until the user confirms explicitly ("agreed", "looks good", "create the plan"). On agreement, **lock** in a chat summary: final block/component/page-type placement; scope boundary (domain vs global); parity fixtures, viewports, iterations; deferred/out-of-scope items; child vs parent plan relationship.

## Phase 4 — Author

Follow `create-plan` end-to-end. Migration extras:

| Artifact | Path |
| --- | --- |
| Decisions | `.local/<slug>/decisions.md` — locked choices from Phase 3 |
| Architecture | `.local/<slug>/architecture.md` — route map, block inventory, retirement notes |
| Parity mapping (optional) | `.local/<slug>/parity-mapping.md` — block-type → prod role hints for `improve-parity` |

Plan sections (patterns in `create-plan` § Optional sections; **Target vs code** banner per its checklist): **Autonomy & authorization** (dev server, parity, domain-scoped edits, CMS import if pre-approved), **Scope boundary**, **Parity scoreboard** (empty table, updated during `improve-parity` tasks), **Operator handoff** (import, deploy, asset copy — not tasks unless requested).

**Typical phases** (adapt to scope; split until task-fit passes):

| Phase | Typical tasks |
| --- | --- |
| **1 — Foundation** | Schemas, page type shell, tokens/SCSS entry, redirects |
| **2 — Blocks & components** | Vertical slices: schema → block → component → registry |
| **3 — Routes & CMS** | Pages, GROQ, migrator, seed/import |
| **4 — Parity** | One task per coherent URL batch (e.g. listing + one story; whole domain only if ≤3 URLs) |
| **5 — Closure** | Scoreboard sign-off, docs update, parent index link |

Investigation-only work is a separate report-only task ID before implementation tasks. Every parity task spec includes:

```markdown
## Parity invocation

- Skill: `improve-parity`
- URLs: …
- Viewports: 1250 / 900 / 320 (or agreed set)
- Iterations per phase: 5 (max 5; lower only if agreed in Phase 3)
- Out of scope: global header/footer unless listed
- Mapping overlay: `.local/<slug>/parity-mapping.md` (if present)
```

**Before `status: ready`:** run the `create-plan` Handoff readiness checklist, plus:

| Check | Pass when |
| --- | --- |
| User agreement | Phase 3 confirmed in chat |
| Decisions file | `decisions.md` reflects locked choices |
| Parity delegation | Every parity task references `improve-parity`; iterations ≤ cap |
| Scope boundary | Global paths listed under escalation |
| Parent link | Child plans linked from the parent index when applicable |

Then run `check-plan` and hand off to the user:

```
/check-plan <project-root>/.local/<slug>-plan.md
/sequential-implementation <project-root>/.local/<slug>-plan.md
```

## Anti-patterns

- Writing the plan before user agreement.
- Mega-tasks ("migrate legal") without block/route slices.
- Defaulting global token changes without escalation.
- Skipping `project-best-practices` placement analysis.
