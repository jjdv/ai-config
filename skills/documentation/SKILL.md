---
name: documentation
description: >-
  Places and formats project documentation in the correct folder (agent skills,
  docs, package README, .local). When the repo has project-best-practices,
  treat it as part of the documentation set — update references/ alongside docs/.
  Use when creating, moving, or restructuring docs, READMEs, specs, runbooks,
  agent context, implementation plans, API documentation, glossaries, or when
  the user asks where documentation belongs.
---

# Project documentation

General rules for repos that separate **agent context** (skills or `.context/`), **developer docs**, **package runbooks**, and **temporary work**. Always **discover** the repo's layout before writing.

## Step 0 — Discover layout

1. Read **`.agents/skills/project-best-practices/SKILL.md`** if present — default conventions skill for repo layout and agent context; open listed `references/` files as needed.
2. If step 1 is missing, check **`references/project-description.md`** (under any `.agents/skills/<name>/`) or **`.context/project-description.md`** for an **`Agent skill:`** line that names a non-default skill folder under `.agents/skills/`; read that skill's `SKILL.md` instead.
3. Else read **`.context/index.md`** if present — lists **only** other files in `.context/`; open every file it lists.
4. Read **`references/project-description.md`** (from the conventions skill) or **`.context/project-description.md`** — repo doc layout, folder roles, **project name**, language rules, links to `docs/` and package READMEs.
5. Read **`docs/README.md`** if present.
6. If those are missing, infer from existing trees (`.agents/skills/`, `.context/`, `docs/`, `.local/`) and ask the user only when ambiguous.

**Default conventions skill name:** `project-best-practices`. Repos that use another folder name document it in `project-description.md` (see below). The **project/product name** always belongs in `project-description.md`, not in the skill folder name.

Do **not** assume project-specific file names until you have read the conventions skill router or `.context/index.md` and followed its links.

## Project documentation set

Repos that ship **`.agents/skills/project-best-practices/`** use a fixed documentation set. Treat these as one system — update the matching layers together when conventions change (styling, routing, blocks, tokens).

| Layer | Path | Audience | Role |
|-------|------|----------|------|
| **Conventions router** | `.agents/skills/project-best-practices/SKILL.md` | Agents | When to load; table of `references/` |
| **Agent references** | `.agents/skills/project-best-practices/references/*.md` | Agents | Canonical project rules — **file names vary** (read the skill router table) |
| **Developer docs** | `docs/README.md` → `docs/**` | Humans | Durable technical reference (summaries + depth; link to skill refs) |
| **Package runbooks** | `README.md`, `<package>/README.md` | Humans | Install, env, scripts — link into `docs/` |
| **Active work** | `.local/` | Implementers | Sequential plans and spikes — not agent context |

**Step 0 default:** if `project-best-practices` exists, read its `SKILL.md` before `docs/` or `.context/`. Legacy `.context/` is optional; prefer skill `references/` for agent context.

**Cross-layer rule:** agent detail lives in `references/`; `docs/` holds human-oriented summaries that link back. Do not duplicate long prose in both. Exact pairing (which `docs/` path maps to which reference) is **project-defined** — read the repo conventions skill.

### Updating `project-best-practices` (mandatory when present)

When the repo ships **`.agents/skills/project-best-practices/`**, it is **part of the documentation set** — not a separate concern from `docs/`.

| Change type | Update |
|-------------|--------|
| Project conventions (styling, routing, blocks, CMS, naming, layout, …) | Matching file in that repo's `references/` — use the conventions skill **router table**, not guessed paths |
| New reference topic agents need | New or extended `references/<topic>.md` + row in that skill's `SKILL.md` router table |
| Commands, env, monorepo layout | `references/project-description.md` (or equivalent listed in the router) |
| Human-facing depth (catalogs, inventories, runbooks) | `docs/` summary + link to skill `references/` — not duplicate agent rules |

**Promotion from completed work:** when a sequential plan or `.local/` initiative changes durable conventions, merge agent rules into the repo conventions skill `references/` (and `SKILL.md` if routing changes) in the **same documentation pass** as any `docs/` update. Do not leave conventions only in `.local/` or only in `docs/`.

**Location:** project conventions skills live under **that repo's** `.agents/skills/` (not user-scope `~/.agents/skills/` unless the repo mirrors them there).

### Project-specific topics (styling, blocks, pages, …)

This skill is **user-scope and repo-agnostic**. It does **not** name project files, sections, or stacks.

1. **Step 0** — if `.agents/skills/project-best-practices/` (or the skill named in `project-description`) exists, read its `SKILL.md` and open the `references/` files its router lists.
2. **Document there** — all project-specific rules (e.g. styling architecture, page variants, CMS patterns) belong in that repo's references, not in this skill.
3. **General patterns** (use only when the repo skill is silent and the pattern clearly fits):
   - Prefer component/block APIs and shared design tokens over page CSS that pierces child modules.
   - Route- or page-group layout may live in page-level styles; component appearance belongs in components/blocks.
   - Editor-selectable behavior → CMS fields; fixed per-route behavior → code (enrichers, config, dedicated block types) — document the split in the **repo** skill.

## Audience and lifespan (quick)

| Location | Audience | Lifespan |
|----------|----------|----------|
| `.local/` | Agents + implementers (current work) | Temporary — implementation in progress |
| `.agents/skills/<name>/` or `.context/` | Agents | Long-term — stable project knowledge |
| `docs/` | Humans | Long-term — durable reference |

```
Is it only needed for the current implementation?
  yes → .local/
  no → Who is the primary reader?
         agent → skill references/ or .context/ (+ update skill router or index.md)
         human → docs/ (+ update README.md)
```

## Folder roles

| Location | Audience | Put here | Never put here |
|----------|----------|----------|----------------|
| **`.agents/skills/<name>/`** | Agents | Stable conventions with discoverable `SKILL.md` frontmatter; detail in `references/` | Long HTTP specs, ops runbooks, links to **`.local/`** |
| **`.context/`** (legacy) | Agents | Same as skills when a repo has not migrated yet | Prefer skills for new agent context |
| **`docs/`** | Developers | **Focused** technical and product reference — one topic per file, sized for quick reading (see § Document size) | Monolithic specs; "run these three commands" only (→ package README); disposable plans (→ `.local/`) |
| **`<package>/README.md`** | Developers | **Concise** bootstrap: install, env vars, scripts, smoke tests, **links** into `docs/` | Full API catalogs, multi-page product spec |
| **`.local/`** | Current work (often gitignored) | Active plans, deliverable folders, spikes, session notes | Canonical product or API truth; **`.local/archive/`**; **`.local/README.md`** (or any index at `.local/` root) |

**Index files:** skill `SKILL.md` routes to `references/`; legacy `.context/index.md` indexes **only** sibling files under `.context/`; `docs/README.md` indexes the `docs/` tree. Update the matching index when adding discoverable docs in that tree.

## Document size and focus

Keep every committed doc **short and scannable**. Long specs belong in a **topic directory**, not one file.

### Length budget

| Guideline | Target |
|-----------|--------|
| Default max | **~2 screens** (~80–120 lines of markdown, or ~3–4 KiB prose) |
| Hard max | **3 screens** only when a single cohesive artifact cannot split without harm (note why in the directory `README.md`) |
| Index / router pages | Table + ≤1 short paragraph — **no** duplicated body content |

**When a draft exceeds 2 screens:** split into focused files under a group directory (e.g. `docs/product/requirements/`, `docs/product/solution/`) and add or extend a `README.md` index in that directory.

### Focus rules

1. **One primary topic per file** — e.g. client API, scoring model, server persistence; not “entire product spec”.
2. **Requirements vs solution** — *what* in `requirements/`; *how* (types, algorithms, schema) in `solution/`; link across; do not paste the same tables in both.
3. **Omit inferable content** — skip prose that restates obvious code behavior, repeated routing essays, and “see also” lists that duplicate the index.
4. **Tables over paragraphs** for options, fields, and enums; prose only for non-obvious rules and tradeoffs.
5. **No bloat anti-patterns** — motivational copy, historical review narrative in canonical specs (→ `review-consensus.md` or `.local/`), duplicate defaults summaries.

### Splitting pattern

```
docs/<area>/<topic-group>/
├── README.md          # index + 1-paragraph scope
├── client.md
├── server.md
└── scoring.md
```

Replace monolithic files with **stub redirects** only when external links must keep working; prefer updating indexes and deleting the old file.

## Quick routing

```
Product behaviour, users, screens, domain rules, UI language vs code identifiers
  → agent skill references/ or .context/ (extend existing product / IA / glossary files)

HTTP/API contract, auth, authorization model, server architecture
  → docs/<area>/ (e.g. docs/server/…) + short summary in the package README

Open questions, spec gaps, backlog vs implemented
  → docs/product/ (or equivalent)

Security, access, registration, audit codes (reference, not sprint plan)
  → docs/product/ or docs/<domain>/ — one canonical file per topic

Backup, DR, performance, compliance, retention, accessibility audits
  → docs/operations/<topic>.md

How to run a package, env vars, test seeding
  → that package's README.md

Styling, UI architecture, page/route conventions, component or block patterns
  → repo .agents/skills/project-best-practices/ (or declared conventions skill) references/ — read router table first

Work in progress
  → .local/ active tracker or sequential plan (open steps only)

Completed implementation work
  → run **`cleanup-plans`** on `PLANS_DIR`: promote to `docs/` / agent `references/`, relocate scripts to `scripts/`, delete entire plan footprint
  → `.local/` must not retain initiative folders, migrators, or output caches after retirement
  → do **not** create `.local/archive/` or duplicate completed plans
```

Adjust subpaths (`server/`, `product/`, `operations/`) to match the repo's `docs/` tree.

## Agent skills vs `.context/`

Prefer **`.agents/skills/<name>/`** when the repo uses Cursor/Codex skills (Claude Code reads project skills from **`.claude/skills/<name>/`** — mirror or symlink when the repo is used with Claude Code).

**Default conventions skill:** `.agents/skills/project-best-practices/` — use this folder name in new repos unless `project-description.md` declares otherwise.

| Piece | Role |
|-------|------|
| `SKILL.md` | Frontmatter `description` for auto-discovery; router table; when to apply |
| `references/*.md` | Stable agent context (same substance as legacy `.context/` files) |
| `references/project-description.md` | Project/product name, doc layout, commands; optional **`Agent skill:`** override |
| Cross-skill links | Domain skills in `.agents/skills/` (e.g. vendor or stack-specific guides) |

### `project-description.md` — agent skill pin (optional)

Include only when the repo does **not** use the default folder name:

```markdown
## Agent conventions skill

**Agent skill:** `<folder-name>`   <!-- under .agents/skills/; omit section when using project-best-practices -->
```

The **project name** and product scope live in the `project-description` title and body — not in the skill slug.

**`docs/`** may link to skill `references/` for human discoverability but should not duplicate agent convention prose.

### Legacy `.context/` rules (when skills are not used)

1. **Self-contained for agents** — a fresh chat can understand product scope without the codebase (via `index.md` plus the files it lists).
2. **No links to `.local/`** — temporary plans must not be agent context.
3. **Link out** for technical depth (`docs/…`, package READMEs) from reference files — not from `index.md`.
4. **Follow the repo's language policy** for UI copy vs code/docs (read `project-description` or vocabulary; do not invent locale rules).
5. **One canonical home per topic** — extend or link; do not duplicate long specs.

Typical filenames (vary by project): `index.md`, `project-description.md`, product/domain description, pages/routes IA, vocabulary/glossary, test-environment contract.

### `.context/index.md` (strict, legacy)

**Only** an index of files in `.context/` — nothing else.

| Allowed | Forbidden |
|---------|-----------|
| One-line title (e.g. "Project context") | Product snapshots, domain tables, architecture summaries |
| Optional ≤2 sentences: what `.context/` is for | Folder-role essays, routing guides, language policy |
| Table: each **other** `.context/` file → one-line description | Links to `docs/`, package READMEs, `.local/`, or paths outside `.context/` |
| Relative links to sibling `.context/` files only | Section pointers into other docs ("see §5.1 in …") — put those in the target file |

Put repo layout, links to developer docs, and onboarding prose in **`project-description.md`** (or another listed file), not in `index.md`.

When adding a new agent context doc: register in the skill `SKILL.md` table or `.context/index.md`; put substance in `references/` or a sibling `.context/` file.

## `docs/` rules

1. **Developer-facing**; match the repo's doc language convention (often English for technical prose).
2. **Stable** — update when contracts or policy change; park uncertainty in a gaps/analysis doc.
3. **Suggested structure** (adapt to repo):
   - `docs/README.md` — index
   - `docs/<component>/` — e.g. server/API, client, infra
   - `docs/product/` — gaps, feature references
   - `docs/operations/` — runbooks
4. **Narrative API/architecture specs** belong in `docs/`, not agent skills/`.context/` or `.local/`.
5. Cross-link with **relative paths within `docs/`** — never point from committed docs to `.local/`.

## Package `README.md` rules

1. **Short** — run the package in minutes from the README alone.
2. **Tables** for env vars and scripts.
3. **Link** to the full spec in `docs/` for anything longer than a summary table.
4. **No** pasting full API or product specifications.

## `.local/` rules (when the repo uses them)

| Pattern | Role |
|---------|------|
| **Architecture index** (e.g. `existing-website-migration-plan.md`) | Phases, principles, open questions; one-line index of completed work |
| **Active sequential plan** (e.g. `*-plan.md` with `plan: true`) | Runnable open tasks only — **retire via `cleanup-plans` when complete** |
| **Initiative folder** (e.g. `<slug>/` under a plan) | Temporary — scripts, tasks, output; **entire tree removed** when the parent plan is retired |
| **Deliverable folder** (e.g. `page-domains/`) | Phase outputs while parent tracker is active; promote then delete per **`cleanup-plans`** |

**Do not use `.local/archive/`** — no archive subfolder or shadow copies of completed sequential plans.

**Do not add `.local/README.md`** — no index or routing doc at the `.local/` root. Pointers to canonical docs live in `docs/`, agent `references/`, or package READMEs. Nested deliverable folders may include a README only when that folder is the active work surface (delete or promote when done).

**When a sequential plan completes:** run **`cleanup-plans`** — promote durable content, relocate operational scripts to committed paths (`scripts/`, `package.json`), fix all references, then delete the **entire plan footprint** (plan file, initiative folder, tasks, output caches). `.local/` should contain only **other active or ineligible** work afterward.

Treat `.local/` as **execution scratch only** — never the canonical home for scripts, runbooks, or product truth.

Repos may document repo-specific names in `references/project-description.md` or `.context/project-description.md` (e.g. which file is the architecture index).

## Code comments

- Reference **stable** paths: `.agents/skills/…/references/…`, `.context/…`, `docs/…`.
- Avoid `.local/…` except transient pointers during active work.

## Checklist (new or moved doc)

- [ ] Confirmed layout via skill router / index / `project-description`
- [ ] Chose folder from routing table
- [ ] **Repo conventions skill present?** Updated the matching `references/` files and router table listed in **that** skill (not guessed paths)
- [ ] File ≤2 screens (or split + group `README.md` with justification if 3)
- [ ] One topic; no duplicate tables across requirements/solution
- [ ] Updated `docs/README.md` (human layer) when `docs/` changed; linked to skill `references/` where appropriate
- [ ] Updated legacy skill `SKILL.md` / `.context/index.md` if repo does not use `project-best-practices`
- [ ] Legacy `index.md` still lists only `.context/` files — no product or external links added
- [ ] Package README gets a link only, not a duplicate spec
- [ ] No `.local/` links from agent context or committed `docs/`
- [ ] Not duplicating the same convention prose in both `references/` and `docs/`

## Anti-patterns

- Single doc growing past **2 screens** without splitting into a topic directory
- Duplicating the same API table in requirements and solution
- Index pages that paste full sections from child docs
- Product snapshots, routing tables, or `docs/` links in `.context/index.md` (→ dedicated reference file or `project-description.md`)
- Implementation plans or step briefs in agent skills/`.context/`
- Product domain only in a package README
- Committed docs linking into `.local/`
- Large API specs under `.local/` instead of `docs/`
- `.local/archive/` or keeping completed sequential plans “for history” after merging into index + deliverable folder
- `.local/README.md` or any permanent index at `.local/` root (use `docs/` or agent `references/` instead)
- Mixing unrelated products/repos in one skill or `.context/` without explicit scope
- Duplicating the same convention prose in both `references/` and `docs/`
- **Project-specific paths or rules in this user-scope skill** (→ repo `.agents/skills/<conventions>/references/`)

## Monorepos and siblings

- Each **package or repo** may have its own skills, `.context/`, and READMEs.
- Repos with **`.agents/skills/project-best-practices/`** include that skill in the project documentation set (see § Project documentation set).
- Document **only** the tree the user scoped; cross-repo pointers belong in `project-description.md` (or another reference doc), not in `index.md` and not as merged product specs.

## More detail — reference

### Discovering canonical paths

| If you find… | It usually defines… |
|--------------|---------------------|
| `.agents/skills/project-best-practices/SKILL.md` | Default conventions skill — when to apply, links to `references/` |
| `references/project-description.md` → **`Agent skill:`** | Non-default conventions skill folder under `.agents/skills/` |
| `.context/index.md` (legacy) | **Table only** — one row per other file in `.context/` |
| `references/project-description.md` or `.context/project-description.md` | **Project name**, repo layout, doc folder roles, language rules, links to `docs/` and package READMEs |
| `docs/README.md` | Developer doc index |
| `<pkg>/README.md` | Runbook for that package |

Search before creating: `rg -l 'Documentation layout' .agents/skills .context docs 2>/dev/null` or list those directories.

### Generic `docs/` layout

```
docs/
├── README.md           # index
├── <component>/        # e.g. server, web, infra — API & architecture
├── product/            # gaps, feature references, domain technical notes
└── operations/         # runbooks: backup, performance, compliance, …
```

Names are conventions — follow the repo's existing subdivisions.

### Migrating misplaced documentation

| Was in (wrong place) | Move to |
|----------------------|---------|
| `.context/` files | `.agents/skills/project-best-practices/references/` (or declared `Agent skill:` folder) + `SKILL.md` router |
| `.context/index.md` — product snapshot, routing, `docs/` links | Dedicated reference file and/or `project-description.md`; leave one router row |
| `.local/` — API/architecture spec | `docs/<component>/` + README summary |
| `.local/` — spec gap analysis | `docs/product/` |
| `.local/` — glossary / vocabulary | agent `references/` or `.context/` |
| `.local/` — long completed implementation brief | Deliverable folder + one-line index in architecture tracker; **delete** runner plan |
| Product essay only in README | agent `references/` + README link |

After move: delete the old copy; fix links (`rg` for old paths).

### When not to write files

- Answer-only question; user did not ask to persist
- Change with no contract, env, ops, or product impact
- Generated artifact already canonical (e.g. OpenAPI → types) — narrative spec in `docs/` only when humans need it

**Do** persist: contract changes, new env vars, new procedures, product rule changes, new agent context — including the **repo's** conventions skill `references/` when that skill exists.
