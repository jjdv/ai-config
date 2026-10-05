---
name: pen-library
description: Multi-file Pencil .pen library layout and token sync. Use when splitting components or bands or syncing variables across .pen files.
---

# Pencil design library (multi-file `.pen`)

## Typical file roles

Paths are relative to the **repository root** unless noted.

| File (convention) | Purpose |
| --- | --- |
| `designs/design-system.pen` | **Canonical** `themes` + `variables`; token gallery frame (e.g. `ds_gallery`); atom/base control specs (e.g. `ds_components`). Single source of truth for tokens and base control look. |
| `designs/components.pen` | **Reusable component definitions** aligned with the design system; same `variables` as the canonical file (synced). Flow: design system atoms → component roots → screen bands. |
| `designs/common.pen` | **Shared** screens or flows reused across areas (optional). |
| `designs/<band>.pen` | **Area or product bands** (screens and local frames). Variables must match the canonical design system (synced). |

Adjust directory names (`designs/`, `scripts/`) to match the repo; keep **one canonical** token source.

## Variable sync

- Band and component files should **embed the same** `variables` (and `themes`) as the canonical design-system file—usually via a **sync script** under `scripts/` at the repo root, run after token changes.
- **Do not** hand-edit large `variables` blocks in band files; change the canonical file, then **sync** so all files resolve `$--` tokens consistently.
- Responsive number tokens often use a **`device`** (or similar) theme axis with ordered breakpoints (e.g. `base`, `md`, `lg`, `xl`).

## Structure and reuse

### Design system (documentation + tokens)

- Keep the **token gallery** for tokens only; keep **atoms** in a separate frame/column for controls (buttons, fields, select, etc.).
- Split the gallery by concern: **colors**, **space**, **typography**, **layout constants**, **radii** (pure shapes, not fake product chrome).
- Prefer a **regeneration script** so the gallery stays consistent and reviewable in git.

### Components

- Mark reusable UIs as **`reusable: true`** (or schema equivalent) on **root** component frames; stable names for discovery.
- **Instance** elsewhere as **`ref`** nodes with **`ref: "<componentId>"`**; override with **`descendants`** for nested paths—copied nodes get **new ids**; do not assume ids stay stable after copy.
- **Slots:** insert children into `instanceId/slotId` where the component defines slot frames.

### Screens (bands)

- Compose from **component instances** and **layout frames** using token bindings (`$--color-semantic-*`, `$--space-*`, etc.).
- Avoid hardcoded colors or arbitrary spacing in new work.

## Workflow checklist

1. Change tokens or gallery in the **canonical** design-system file (or via its rebuild script).
2. **Run** the repo’s variable sync script so components and bands match.
3. Instance components; override only what the screen needs.
4. Validate with screenshots or export if the toolchain supports it.

## Pencil MCP vs files on disk

- If `.pen` files are **encrypted / MCP-only**, use Pencil tools (read design nodes, apply design operations, read design variables)—do not read them as plain text.
- If the repo stores `.pen` as **JSON**, agents may edit on disk and run scripts—still prefer Pencil MCP when the user works in the Pencil app (disk vs unsaved buffer can diverge until **Save**).

## Anti-patterns

- Forking token values in a band file instead of updating the canonical source + sync.
- Duplicate color roles under multiple names without a single semantic token.
- Large one-off gallery edits without a script when the project **generates** the gallery (drift and merge pain).
