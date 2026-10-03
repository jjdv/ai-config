---
name: cleanup-plans
description: >-
  Retire finished implementation plans (sequential YAML or alternate trackers):
  promote durable content to docs/, agent references, and committed code; relocate
  operational scripts out of .local/; then delete the entire plan footprint so
  .local/ holds only active work. Requires the user to name the plans directory;
  discover candidates by probing markdown in that folder's root — not by filename.
  Use when the user asks to cleanup plans, clean up .local/, or retire completed
  trackers after sequential-implementation — without leaving orphaned subfolders.
disable-model-invocation: true
---

# Cleanup plans

Retire **finished** plans — sequential YAML (`plan: true`) **or** alternate-format trackers. **`.local/` (or any `PLANS_DIR`) is temporary:** it holds plans only while they are being created or executed. When a plan completes, this skill **promotes** what must persist, **relocates** operational tooling into committed project paths, then **deletes the entire plan footprint** — no orphaned initiative folders, scripts, or output caches.

Pair with **`create-plan`** / **`sequential-implementation`** and the **`documentation`** skill.

**Do not** require a `*-plan.md` (or any other) filename. Discover candidates by **content** in the **root** of the named plans directory.

## Mandatory input — plans directory

**Do not start** until the user gives an explicit **plans directory** (`PLANS_DIR`) — absolute path or path relative to the project git root.

| User provides | Meaning |
|---------------|---------|
| `/path/to/repo/.local` | Scope discovery and deletions to this tree only |
| `.local` | Resolve under project root |

If the directory is missing, ambiguous, or equals the repo root → **stop and ask**.

**Never** assume `.local/` without the user naming it in the current message.

Optional **narrowing** (user may add):

- Specific plan file(s) by name — still subject to **eligibility gate** below
- “All eligible plans in `PLANS_DIR`” — means all that pass discovery **and** the gate, not every markdown file in the root

## Candidate discovery (mandatory)

Scan **only markdown files (`*.md`) directly in `PLANS_DIR` root** — not recursive. Do not walk `tasks/`, initiative subfolders, `GUS-*`, or other nested trees looking for plans.

For each root `*.md`, read the **first 40 lines** (identification window). If the file starts with `---` and the closing `---` is not in those 40 lines, extend the read to the closing `---` or **line 80**, whichever comes first.

Classify from that window:

| Class | When |
|-------|------|
| **Sequential plan** | YAML frontmatter contains `plan: true` |
| **Alternate plan/tracker** | No `plan: true`, but the window looks like a plan/tracker (see **Identification heuristics**) |
| **Not a plan** | Spike, import readme, fixture notes, `.local/README.md` if present, or no plan/tracker signals |

User-named files are candidates even if they sit outside the root or fail the 40-line probe — still run the **completion** gate; do not skip the gate.

Skip non-markdown and Always-keep extensions at this step (they are never candidates).

## Eligibility gate (mandatory — every candidate)

A plan is **eligible for retirement** only when **all** are true:

| # | Requirement | If false |
|---|-------------|----------|
| 1 | File is a discovered candidate (or the user named this exact file) | Skip — not in scope |
| 2 | **Completion** (format-specific — see below) | **Stop for this plan** — report reason; ask if ambiguous |
| 3 | User did not contradict eligibility (e.g. “also remove the draft plan”) | Ask |

**Named plans are not exempt.** If the user names a file that fails completion, skip it and say why.

**No blanket deletes.** Never delete paths outside an eligible plan's **footprint** (see below).

### Completion — sequential (`plan: true` in frontmatter)

All must hold:

- Frontmatter `status: complete`
- Every task row in **Phases** is `✅ Complete` (no open `⬜` / `🔄` / `⏸`)

If `plan: true` but status is not complete or tasks are open → **stop for this plan**; report as in-progress.

### Completion — alternate format (no `plan: true`)

The file must be a plan/tracker (not a spike, import readme, or fixture). Treat as complete only when **its own tracked work is done**, using the document’s native progress mechanism:

- Status/header says complete / shipped / all steps done / last scope complete, **and**
- Progress tables show 0 open / all done, **and**
- No in-scope open task markers (`[ ]`, ⬜, 🔄, ⏸, “Next open” pointing at real work)

**Superseded rows do not block** when the plan itself says they were merged into a successor **and** that successor’s tracked work is complete (or the successor file is also eligible / already retired).

**Optional follow-ups, deferred items, and out-of-band notes** (e.g. “optional typecheck debt”, “NFC deferred”) **do not block** if they are not rows in the plan’s tracked task/progress table.

If alternate-format completion is **ambiguous** → **ask**; do not delete.

## Plan footprint (mandatory — what gets removed)

For each eligible plan, build its **footprint**: every path under `PLANS_DIR` that exists **because of that plan**. After promote + relocate + reference fixes, **delete the whole footprint** — not just markdown.

**Deny by default outside footprints.** If a path is not in at least one eligible plan's footprint, **do not delete it**.

### Paths in a plan's footprint

Include **all** of the following when they exist and belong to the plan:

1. The plan file itself
2. Every path in **Context references**, initiative links, or equivalent
3. Every `tasks/<id>.md` linked from **Details** (or equivalent) in phase tables
4. Every **initiative folder** explicitly referenced (e.g. `<slug>/` under `PLANS_DIR`) — **entire tree**, including:
   - `scripts/`, `lib/`, `package.json`, `node_modules/`
   - `output/`, scratch NDJSON, convert caches
   - decisions, architecture, parity notes, reports, probes
5. Scope / tracker files the plan links as its task list (e.g. `scopes/I01-….md`)
6. Any other path named in the plan body as a deliverable location for that initiative (e.g. `.local/customers-migration/`)

**Footprint = full subtree** for referenced initiative folders. Do not leave `scripts/` or `output/` behind “because the runbook still points here” — **relocate first**, then delete.

### Never in a footprint (unless user explicitly overrides)

- Another plan/tracker file that **failed** the eligibility gate (and that plan's own footprint)
- Reference fixtures with **no plan parent**: `*.csv`, `*.xlsx`, `*.xml`, `*.pdf`, `*.wsdl`, third-party doc trees (e.g. `GUS-*`)
- Spike notes, import readmes, scratch with no eligible-plan parent
- `.gitignore` and other config at `PLANS_DIR` root
- `tasks/<id>.md` not linked from the plan(s) being retired

**Forbidden:**

- `.local/archive/` or copying plans “for history”
- `.local/README.md` at the plans root
- Deleting paths outside the union of eligible plan footprints
- Leaving committed `docs/` or agent references pointing at deleted `.local/` paths

## Workflow

### 1. Discover layout

Read **`documentation`** skill Step 0:

- `.context/index.md`, `.context/project-description.md`
- `docs/README.md`
- Repo conventions skill (`project-best-practices` or declared override) when present

### 2. Inventory and gate

In `PLANS_DIR` only:

1. List root `*.md` files; probe the first 40 lines (extend to 80 if unclosed frontmatter). Add any user-named files.
2. Run **eligibility gate** on each candidate.
3. For each **eligible** plan, read context refs, initiative folders, scope/tracker links, linked `tasks/*.md`, and any named deliverable paths.
4. Build the **footprint** per eligible plan (union for batch cleanup).
5. Produce **pre-delete manifest** (footprint list) — **no deletes before this**.

If **zero** eligible plans → stop; report ineligible files and exit.

### 3. Promote (before relocate or delete)

For each eligible plan, merge **only** what is not already canonical:

| Source (typical) | Destination |
|------------------|-------------|
| Locked decisions, architecture sketch | `docs/<area>/<topic>.md` or conventions skill `references/` — extend, don’t duplicate |
| Shipped status, dates | Product spec header + `docs/README.md` index row |
| IA / routes | `.context/app-pages.md` + product spec (legacy) or conventions `references/` |
| API outline | `docs/server/http-api.md` (if shipped) |
| Runbook steps, import checks | `docs/operations/<topic>-runbook.md` |

Remove plan-backlog wording; mark **shipped** + date. **No `.local/` links** in promoted targets.

### 4. Relocate operational artifacts (before delete)

Anything in the footprint that must **keep working** after cleanup moves to **committed** project paths. Typical mapping:

| Was in footprint | Relocate to |
|------------------|-------------|
| Migrator / convert scripts | `scripts/<topic>/` (match repo precedent, e.g. `scripts/blog-migration/`) |
| Redirect merge scripts | `scripts/<topic>/` or `scripts/redirects/` |
| `package.json` scripts | Root or package `package.json` — wire to new paths |
| Runbook commands pointing at `.local/…` | Update to `scripts/…` in the runbook **in the same pass** |

**Do not relocate:**

- Regenerable output (`output/*.ndjson`, convert caches) — delete with footprint
- `node_modules/` under `.local/` — delete; document `npm install` in runbook for the new `scripts/` path
- One-off scratch with no ongoing use

If relocation is non-trivial and the user did not authorize scope expansion → **stop**, report what must move, and ask.

### 5. Fix references repo-wide

Search committed docs, runbooks, `package.json`, and agent references for paths on the footprint. Replace with canonical `docs/`, `scripts/`, or conventions targets. Re-run until **nothing** points at paths you will delete.

### 6. Delete (footprint only)

Delete **exactly** the paths on the pre-delete manifest:

1. Files in footprint (deepest first within each subtree)
2. Initiative folders when the entire subtree is in the footprint
3. Empty directories that contained only deleted footprint entries
4. Plan file(s) last among their siblings if helpful for verification

After delete: list **remaining** files in `PLANS_DIR`. For a fully retired plan, its initiative folder should be **gone**.

### 7. Report

```markdown
## Plan cleanup — <project>

**Plans directory:** `<absolute path>`

### Eligible plans
- `<plan>` — format: sequential | alternate; completion: <evidence one line>

### Skipped (ineligible)
- `<plan>` — reason

### Plan footprint (pre-delete manifest)
- `<path>` — reason (plan file | initiative tree | task 2.1 | output cache | …)

### Promoted
- `<path>` — one line

### Relocated
- `<old .local path>` → `<committed path>` — one line (or “none”)

### Deleted
- `<path>` (must match footprint manifest)

### Left in PLANS_DIR (untouched)
- Active / ineligible plans and non-plan fixtures only

### Follow-ups
- optional ops notes — do not auto-run
```

## Identification heuristics

**Window:** first **40 lines** of each root `*.md` (or to frontmatter close / line 80). Filename is irrelevant.

**Sequential** — `plan: true` in YAML frontmatter:

```yaml
---
plan: true
version: <n>
status: complete   # required for retirement
---
```

**Alternate format** (no `plan: true`) — the window looks like a plan/tracker, for example:

- Heading or status line with “plan”, “tracker”, “master plan”, or equivalent
- A progress / scope table (columns such as Scope, Open, Status, Phase)

**Not a plan** (even in the root): import readmes, spike notes, fixture commentary, a root `README.md`.

Typical layout during **active** work (names vary):

```
PLANS_DIR/
├── <any-name>.md      # candidate if 40-line probe says plan/tracker
├── <slug>/            # initiative — entire tree deleted on retirement
├── scopes/
└── tasks/<id>.md
```

After retirement of a completed plan: **no** `<slug>/` folder and **no** plan file remain.

## Anti-patterns

- Cleaning without a user-named `PLANS_DIR`
- Using `*-plan.md` (or any filename) as the discovery signal
- Recursing into `PLANS_DIR` to **find** plans (only to enumerate an eligible plan's footprint)
- Deleting any root markdown without passing the eligibility gate
- **Leaving `scripts/`, `output/`, or initiative folders** after plan completion
- Promoting markdown but leaving operational paths in `.local/` because docs still link there
- Deleting paths outside the footprint union
- Leaving `docs/` / `.context/` / `package.json` links to deleted `.local/` paths
- Promoting full plan prose when a product spec already exists
- Treating gitignored NDJSON output as something to preserve in `.local/`

## Related skills

| Skill | When |
|-------|------|
| **`documentation`** | Where promoted content and `.local/` lifespan rules live |
| **`create-plan`** | Sequential plan shape being retired |
| **`sequential-implementation`** | Typical precursor for YAML plans |

## Example invocation

```
/cleanup-plans /home/me/proj/.local

Clean advance-settlement.md and meter-lifecycle.md.
```

```
/cleanup-plans .local

Clean all eligible plans; keep GUS and CSV fixtures.
```

```
/cleanup-plans .local

Retire customers-migration-plan — relocate migrator to scripts/, then remove .local/customers-migration/.
```
