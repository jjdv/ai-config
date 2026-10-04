# Migration analysis brief (Phase 1–2)

Structure for Phase 2 chat output; expand sections only on request.

```markdown
## Migration scope

- **Domain / slug:** …
- **Routes:** … (count)
- **Source:** … (repo path + production base URL)
- **Target:** `<project-root>` / `website/`
- **Out of scope:** …

## Proposed architecture

| Layer | Action | Items |
| --- | --- | --- |
| Page types | new / reuse | … |
| Blocks | new / extend | `blocks/…` — … |
| Components | new / extend | `components/…` — … |
| Utilities | new | migrator, GROQ, redirects, … |
| Theme / tokens | override / none | page-type SCSS, `rich_text` variant, palettes |
| Sanity | schemas / import | … |

## Route → page-type map (summary)

| Route pattern | Page type | Notes |
| --- | --- | --- |
| … | … | … |

## Block / component candidates

| Production pattern | Proposed unit | Placement | Rationale (one line) |
| --- | --- | --- | --- |
| … | `*Block` / component | ui / common / domain / PageName | … |

## Phases (sketch)

1. **Foundation** — …
2. **Blocks** — …
3. **Routes & CMS** — …
4. **Parity** — fixtures: …; viewports: …; iterations/phase: …
5. **Closure** — …

## Parity

- **Fixture URLs:** …
- **Viewports / iterations:** defaults from migration-workflow § Parity defaults (or …)
- **In scope regions:** main content, …
- **Excluded:** global header/footer, …
- **Structural risks:** …

## Scope boundary

| Domain (autonomous) | Global (propose only) |
| --- | --- |
| `blocks/<domain>/`, … | `components/ui/`, theme JSON, … |

## Open points

1. …
2. …

## Deferred

- …
```

After user agreement, copy locked rows into `.local/<slug>/decisions.md` and expand inventory into `.local/<slug>/architecture.md`.
