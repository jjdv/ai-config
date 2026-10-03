---
name: design-system
description: >-
  Pencil canonical design-system file (tokens, gallery, atoms). Use when
  authoring or refactoring the repo's design-system .pen or responsive themes.
---

# Design system (canonical `.pen` + tokens)

## Role of the canonical file

Convention: **`designs/design-system.pen`** at the repo root (adjust path if the project differs).

- **Canonical** source for **`themes`**, **`variables`**, a **pure token gallery** (stable id e.g. `ds_gallery`), and **atom/base components** (e.g. `ds_components`).
- **Product screens** in other `.pen` files should **reuse the same variables** (synced from here), not fork ad hoc hex values.
- **Separation:** tokens document design decisions; the atoms frame shows how tokens compose into reusable UI. Product copy and screen flows live in **band** files—not in the token gallery.

---

## Target structure and canvas layout

**Two editorial columns**

- **Token gallery** — left column (typical width ~1080px, `x = 0`).
- **Atoms column** — right column (width ~1080px, `x ≈ gallery width + gap`, e.g. gap **80px** → `x ≈ 1160`).
- Optional tooling/marker nodes: keep out of the visual story.

**Document-level overview (masthead)**

- **One** wide frame above both columns (width ≈ sum of columns + gap, often ~2240px).
- Title **Design system**; subtitle names **tokens** and **atoms**; no product name or marketing tagline.
- Remove duplicate heroes inside the columns once the overview exists.

**Inside the token gallery**

- **Direct children** = **section siblings** (each chapter in its own framed panel).
- Typical order: **Brand palette** → **Semantic palette** → **Typography** → **Dimensions** (spacing + layout table + radii).
- Panel chrome: presentation tokens (e.g. `--ds-doc-surface-panel`, `--ds-doc-border`); section titles use `--ds-doc-foreground*`, not product semantic text colors.

**Inside the atoms column**

- Section siblings (Buttons, Inputs, Alerts, etc.) with **h2 + optional lede + cards**, not a second file-wide hero.

**Stable ids**

- Keep stable frame **`id`s** (e.g. `ds_gallery`, `ds_components`) for scripts and automation; human-readable names can differ.

---

## Visual and copy rules

- **Product-agnostic** in gallery and overview: vocabulary like “tokens”, “semantic roles”, “atoms”.
- **Presentation layer ≠ product tokens:** `--color-semantic-*` / `--color-brand-*` are for **product UI**. Use **`--ds-doc-*`** only for documentation chrome (panels, masthead, section shells). Swatches and control demos use real product tokens.
- Do not use saturated brand fills for doc shells; reserve brand for swatches and examples.

---

## Vocabulary

| Term | Meaning |
| --- | --- |
| **Major regions** | Token gallery and atoms column as **siblings** in top-level `children`. |
| **Section siblings** | Peer frames **inside** one column. |
| **Overview / masthead** | Single wide frame introducing both columns. |
| **Hoist to root** | Frames beside gallery/atoms at file root—update scripts if ids change. |

**Tree pitfalls**

- Move **all** children off a parent before **Delete** on the parent.
- `Move(node, document)` may append to root; index `0` moves can fail—prefer append + reorder in UI.

---

## Gallery section checklist (token gallery children)

1. **Brand palette** — primary / secondary / tertiary ramps.
2. **Semantic palette** — surfaces, text, status (info/success/warning/error).
3. **Typography** — families + parameters + **one** responsive scale matrix (`base · md · lg · xl`).
4. **Dimensions** — spacing scale, layout constants table, radii.

Avoid empty spacer frames with no children.

---

## Tokens to include

### Themes

- Responsive axis (e.g. **`device`**: `base`, `md`, `lg`, `xl`); responsive numbers expose **four** values in that order.

### Colors

- **Brand** ramps; **semantic** roles (background, foreground, surfaces, border, status, on-dark).
- **One token per role**—no duplicate names for the same hue.

### Space, typography, layout, radii

- T-shirt spacing (`--space-xs` … `--space-2xl`); `--page-padding-x` for viewport inset.
- Font families, type scale, leading tokens; layout breakpoints and max content width.
- Radii and chrome heights as themed numbers where they vary by breakpoint.

### Atoms column

- Flow: canonical design system → `components.pen` (or equivalent) → band screens.
- Buttons, inputs, selects, badges: document states (default, hover, active, focus, disabled) with clear naming.

---

## Naming

- Variables: `--token-name`; bindings: `$--token-name`.
- **Product:** `--color-brand-*`, `--color-semantic-*`, `--space-*`, `--layout-*`, `--font-*`, `--leading-*`.
- **Pencil-only (often stripped on sync to bands):** `--ds-doc-background`, `--ds-doc-surface-panel`, `--ds-doc-border`, `--ds-doc-foreground*`.

---

## Gallery presentation

- Definitions-first: name + value + minimal visualization.
- No fake product UI inside the token gallery; atoms demos live in the atoms column.
- Layout constants as **tables**, not misleading viewport mockups.

---

## Maintenance

- Prefer **`scripts/`** at repo root to rebuild the gallery and **sync variables** to band/component files.
- Doc-only tokens (`--ds-doc-*`) typically stay in the canonical file only; sync scripts may strip them from copies.
- After manual layout experiments, align rebuild scripts or expect the next rebuild to overwrite structure.

---

## Agent tools and editor reality

- **Pencil MCP** for encrypted `.pen`; plain JSON repos may also use IDE/scripts—stay consistent with team workflow.
- Disk file and Pencil editor buffer can **diverge** until Save; `open_document` from disk may discard unsaved editor changes—warn before refresh.

---

## Quick reference

| Area | Rule |
| --- | --- |
| Overview | One masthead; tokens + atoms; no product name. |
| Columns | Gallery \| atoms; doc background on column chrome. |
| Token sections | Framed siblings (Brand, Semantic, Type, Dimensions). |
| Scripts | Preserve stable gallery id or update rebuild tooling. |
| Safety | Move children before deleting parents. |
