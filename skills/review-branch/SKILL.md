---
name: review-branch
description: >-
  Manual-only read-only git branch review scoped to branch delta. When no branch
  is named, reviews the current branch vs main. Default --pr mode reports only
  PR blockers (proven runtime/editor breakage); --full adds regression risk and
  unnecessary-global table. Infers ticket/page-group scope; applies
  intentional-scoping, necessary-for-ticket, pre-existing-pattern, and
  finding-legitimacy gates. Discovers per-repo `references/code-review.md` from
  project-best-practices when present. Invoke only when attached or asked (e.g.
  /review-branch). Review only — no edits, commits, or branch checkout without
  permission.
disable-model-invocation: true
---

# review-branch

{{tool_mapping_note}}

Structured, **read-only** review of a git branch before merge. Produce a report the user can act on; do not implement fixes unless they ask separately.

## Invocation

**Manual only.** Run this workflow only when the user attaches this skill or explicitly requests a branch review (e.g. `/review-branch`, "review branch X"). Do not infer or auto-start from unrelated messages.

### Review target

Resolve the branch under review in **Phase 0** from the user message.

| Target | Trigger |
|--------|---------|
| **Current branch (default)** | `/review-branch`, "review current branch", or any invocation **without** a named branch — use `HEAD` (`git branch --show-current`) |
| **Named branch** | "review branch `feature/foo`", `/review-branch feature/foo` — use that branch name |

**Comparison base:** always `main` (or the repo’s default branch if not `main`). Diff scope is `<merge-base-with-main>...<review-target>` — never the working tree alone.

When the review target is the current branch, **stay on it**; do not checkout or stash for the review.

### Report modes

Resolve mode in **Phase 0** from the user message. **Default: `pr`.**

| Mode | Trigger | Published sections |
|------|---------|-------------------|
| **`pr`** | Default; `/review-branch`, "before PR", "key issues" | Summary, What works, Must fix before merge, **Should fix before PR approval** |
| **`full`** | `/review-branch --full`, "full review", "include regressions" | Above + Regression risk, Unnecessary global changes, Open questions |

**PR blocker** (eligible for numbered items in `pr` mode): runtime failure, wrong/missing render on **named** routes, unwired CMS field editors can set and runtime should consume, proven cross-boundary leak, unsafe cutover.

**Not PR blockers** (omit in `pr` mode): placement preference, intra-ticket DRY, Presentation/catalog-only edge cases, schema/query shape drift with **no** user/editor-visible delta, hypothetical paths blocked by wrapper defaults or schema validation.

**Domain activation by mode:**

| Domain | `pr` | `full` |
|--------|------|--------|
| 1 Project practices | Yes | Yes |
| 2 Code principles | Yes (cross-boundary / `pr_blocker` only) | Yes |
| 3 Regression | Investigate when shared surfaces change; **publish** only proven regressions | Investigate + publish |
| 4 Unnecessary global | **Skip lane** unless user asks | Run when shared/global surfaces change |

During synthesis, load core `references/false-positives.md`, repo manifest § False-positive patterns when adapter loaded, and apply § Necessary for ticket gate.

## Hard constraints

- **Review only.** Do not edit files, commit, push, stash (except to preserve unrelated work the user already asked for), patch Sanity/CMS content, or run formatters that modify the tree.
- **Default review target is the current branch** — when no branch is named (§ Review target), review `HEAD` vs `main`; **do not switch branches or stash**. Use `git diff <merge-base-with-main>...HEAD` and `git log` for the branch delta; uncommitted working-tree changes do not require stash for the review.
- **Named branch off HEAD** — when the user names a different branch and HEAD is not on it, **do not checkout** if you can inspect via `git fetch` + `git diff <merge-base-with-main>...origin/<branch>`.
- **If checkout is required** (e.g. HEAD is not on the review branch and remote diff is insufficient, local branch missing, tests only runnable on that branch), **ask the user for permission first** and state why.
- Prefer **`git fetch`** + **`git diff <merge-base>...origin/<branch>`** (when not on the branch), **`git diff <merge-base>...HEAD`** (when already on it), **`git log`**, and path-scoped reads over checking out the branch.
- Ignore unrelated dirty files on the current branch unless they are part of the branch under review.

## Scope: branch delta only

**Report only issues introduced, worsened, or directly extended by this branch's diff.** Do not flag pre-existing repo problems unless the branch touches that code in a meaningful way.

| In scope | Out of scope |
|----------|--------------|
| New or changed lines in added/modified files on the branch | Pre-existing patterns in unchanged files (e.g. an old file the branch never edits) |
| Refactors that move logic but change behavior or boundaries | Incidental context you read for comparison but the branch did not alter |
| Global files the branch edits (`theme.scss`, shared `Heading`, nav) — judge the **delta** | "The whole file is 600 lines" when the branch only added 10 lines and did not worsen structure |
| Extending a pre-existing pattern when the extension adds new risk (e.g. more entries in the same transform pipeline) | Criticizing the pre-existing pattern alone with no branch change |
| **Shared code the branch changes** that can break pages the branch did not add (tokens, primitives, transforms, mappers, footer/nav defaults) | Hypothetical regressions with no changed line to cite |

When unsure, ask: **"Would this issue exist if we reverted only this branch's commits?"** If no → omit.

## Layering: core skill vs repo adapter

| Layer | Scope | When |
|-------|--------|------|
| **Core (this skill)** | Branch delta, four domains, scoping gates, synthesis, report template — **no product- or repo-specific names** | Every review |
| **Repo adapter** | Project conventions, CMS stack paths, editor schema layout, fixture locations — loaded per § Repo adapter discovery | When diff touches that repo’s app/CMS surfaces |

Core rules use generic terms: **page group**, **global registry**, **scoped registry**, **route preprocessor**, **editor palette**, **shared primitive**, **page shell**. Repo adapters map those to concrete files (e.g. `pageBuilderBlocks`, `enrich*Page.ts`) — adapters **extend** core checks; they do not replace scoping gates.

## Ticket and page-group scope (mandatory, Phase 0)

Before activating domain lanes, infer the branch’s **target page group(s)** and **intentional boundaries** from branch name, commits, and diff paths (new route modules, page-type folders, domain block trees, new content types, scoped editor block lists, catch-all filters, context keys such as `pageClass`).

Record internally (not in the user report):

| Triage field | Meaning |
|--------------|---------|
| **Target routes / page family** | URL prefix or route family the ticket owns (e.g. `/docs/*`, `/account/*`) |
| **New boundaries** | Dedicated route; catch-all exclusion; scoped editor block list; context-keyed dispatch |
| **Dual-registry types** | Content/block types registered in **both** the **global** editor palette/registry **and** a **scoped** registry for the page group |
| **Preprocessor-protected routes** | Routes where a **route preprocessor** replaces, filters, or rewrites content before render |

**Pass this scope briefing to every lane subagent.** Domain 3 and 4 must use it — a change is not “unnecessary global” or a “regression” merely because it touches a shared file if the ticket **deliberately** introduces a page-group boundary.

### Editor placement scope matrix (mandatory when CMS/editor schemas change)

Before any **placement** or **shared-primitive default** finding on a component tied to a block type, classify each affected type:

| Editor placement | Rule for shared-primitive defaults / placement Should fix |
|------------------|----------------------------------------------------------|
| **Scoped palette only** (not in global editor list) | **Forbidden** — omit; wrapper + primitive redundancy is intentional |
| **Global palette only** | Global rules apply; regressions need named routes outside the ticket group |
| **Dual-registry** (global **and** scoped) | Apply § Dual-registry dispatch; report only **proven** leaks on global routes minus preprocessor-protected paths |

**Hard stop:** If a lane candidate cites “shared `ui/` default should move to wrapper” but the block type is **scoped-palette-only**, drop it — ledger: `intentional page-group scoping` (no exception without dual-registry evidence).

**Synthesis veto (mandatory):** Any finding on `components/ui/` (or repo equivalent) **defaults** for scoped-palette-only block types is **auto-dropped** unless dual-registry leak is proven with a **named** global route minus preprocessors.

## Necessary for ticket gate (mandatory before global/placement findings)

Before a **Domain 4** row, placement Should fix on shared code, or “could be narrower” finding:

1. Would **reverting only the global hunk** break the ticket’s new routes?
2. Is there a **narrower** implementation that preserves the same data path and behavior?

If (1) yes and (2) no → **intentional supporting change** — omit from numbered items and global table; may note in **What works**. Examples: shared media projection widenings for ticket image sizing; opt-in primitive variants passed from ticket wrappers.

## Pre-existing pattern check (mandatory before numbered items)

Compare `git show <base>:<path>` at the same callsite. If the branch **moved** code without changing behavior, or the pattern **already existed on base**, drop unless the branch **worsened** it (new default, new leak, new crash path).

## Intentional scoping gate (mandatory before reporting)

Complete this gate **before** emitting placement, styling, token-pipeline, “unnecessary global”, or convention findings. If all applicable rows classify the change as intentional **and** no cross-boundary leak is proven → **omit** from Must fix / Should fix / Regression (ledger: `dropped — intentional page-group scoping`).

### Likely intentional — do not flag alone

| Signal | Why |
|--------|-----|
| Layout/typography in page-type shell SCSS or layout wrapper | Allowed page-shell lever; domain-specific width/heading vars are not automatic design-token violations |
| Domain default only in domain wrapper / adapter component | Wrapper pattern — defaults belong on wrapper, not always on shared primitives |
| Block type **scoped-palette-only** (§ Editor placement scope matrix) | **Never** report shared-primitive defaults as Should fix or global-table rows |
| Same default on wrapper **and** shared primitive when editor is scoped-palette-only | Redundant but harmless — omit |
| Context-keyed dispatch on ticket routes only | Deliberate separation — not a bug by itself |
| **Exclusive-registry dispatch** — scoped-palette-only types always route to page-group registry without `pageClass` check | Intentional when global editor **cannot** place those types; omit unless fixtures/CMS prove raw usage on global routes |
| Dedicated route + catch-all exclusion + new content `type` | Standard migration split when repo already uses that pattern |
| New opt-in variant on shared primitive, passed only from wrappers | Opt-in additive |
| Restricted editor block list on new content type | Product scope — not “missing blocks” unless ticket requires parity |

### Cross-boundary leak — still report (with evidence)

| Signal | Require |
|--------|---------|
| Dual-registry type: global editor palette + scoped dispatch returns empty/null off-group | **Named routes** with raw content (fixtures, seed data, CMS grep) **minus** preprocessor-protected paths |
| Shared primitive default changed | **Named pre-existing consumers** outside ticket group that still render through changed code |
| Schema/query field not mapped on **new** ticket surfaces when CMS sends data editors can set | Branch-introduced wiring gap — Should fix when projection exists but mapper/transform drops fields |
| Silent empty from dispatch/registry on routes the **global** editor can still build | Must fix when proven on live route shapes |

### Convention and docs

- **Never** cite a single naming/placement bullet from docs alone — repo may be mixed (`Homepage/` vs `BlogPostPage/`).
- **Verify** with at least two existing repo examples **or** branch-updated project docs that describe the same pattern.
- Convention / placement → **Should fix** only when branch pattern **contradicts** repo reality, not when it contradicts one stale doc line.

### Below Should fix (omit from report)

Drop lane candidates that are **correct** but deferrable — ledger: `below should-fix`. Do **not** list as Should fix, Regression, or global table.

| Category | Rule |
|----------|------|
| **Comment / doc drift** | Stale comment contradicts code but behavior is correct (e.g. registry comment vs dual-list wiring) — fix in passing only if at all; not a numbered item |
| **File / module location preference** | Moving transforms, mappers, or helpers to a “cleaner” path with no proven cross-boundary leak or import-cycle failure — architectural preference, not branch review |
| **Intra-ticket DRY** | Duplication **introduced entirely by this branch** within the same page family (parallel block SCSS, repeated Studio field option arrays in new schema files) — extract in follow-up unless values diverge and cause inconsistent runtime |
| **Cosmetic on new ticket surface only** | Missing modifier class, redundant `clsx` key, DS path mismatch — omit when defect is visible only on the branch’s new routes/blocks and does not break pre-existing pages |
| **Redundant wrapper + primitive default** | When editor placement is scoped-palette-only — omit |
| **Opt-in global API extension** | New enum key / optional prop on shared type used only from ticket wrappers or page shell — omit until callers outside the group pass it |
| **Identical mapper override** | Later mapper in merge registry replaces earlier but bodies are the same — omit |
| **Catalog / preview-only** | Preview context, fixture paths, design-catalog metadata — omit unless production dispatch is wrong |
| **Speculative test-coverage ask** | “Add regression tests for refactor” with no proven behavior change — omit |
| **Idempotent style refactor** | Mixin/extract equivalent to prior output (typography move, literal alias of helper) — omit from Regression and global table |

**Operational cutover vs code:** Documenting content migration from legacy content type to new type belongs in **Summary** (one sentence) when the route split is intentional — **not** a numbered Should fix unless code **cannot** work post-migration (data loss, no import path). Runbook steps are not code defects.

**New-surface-only defects:** Edge cases visible only on the ticket’s new routes (empty slug → hidden heading, dead CSS class on new component) → **below should-fix** unless they break **pre-existing** pages or block launch of the new route family.

**Branch-introduced wiring on new surfaces:** Dropped projections, unwired schema controls on the **new** content type, or inconsistent field validation vs sibling types on that type → **Should fix** when editors can set values that runtime ignores (not merely radio vs free-text when both work).

**Domain 2** (DRY, KISS, SOLID) must apply this table **and** § Intentional scoping gate — code-principle nits do not bypass page-group scope rules.

## Repo adapter discovery (mandatory, Phase 0)

Before activating domain lanes, check the **repository under review** (workspace being reviewed — not the harness config repo) for project conventions:

| Priority | Location |
|----------|----------|
| 1 | `.agents/skills/project-best-practices/SKILL.md` |
| 2 | `.agents/skills/<name>-best-practices/SKILL.md` |
| 3 | Repo `AGENTS.md` or README conventions section — when no skill exists |

When a project skill exists, load **`references/code-review.md`** from that skill when present. The manifest is the repo adapter: term mapping, path→reference matrix, content-stack parity extensions, optional Domain 1 sub-lane triggers, and repo false-positive patterns. **Do not** deep-read every reference file on every review — use the manifest’s path matrix against the branch diff.

| When adapter exists | Action |
|---------------------|--------|
| Load | Project skill + `code-review.md`; references selected by path matrix only |
| Brief Domain 1 | Term mapping, parity extensions, selected reference paths, preprocessor/dual-registry notes from manifest |
| Sub-lane | When manifest § Domain 1 sub-lane conditions match → spawn **project-adapter** Domain 1 sub-lane (candidate findings only) |
| Synthesis | Merge core `references/false-positives.md` with manifest § False-positive patterns |

**When no adapter:** run Domain 1 from diff shape and generic checklists; record assumptions in internal scope briefing only (not the user report).

For CMS-backed repos: treat schema/content inspection as **read-only** (query/get only; no patches or publishes).

**Synthesis:** always load core `references/false-positives.md`; also apply manifest § False-positive patterns when an adapter was loaded in Phase 0.

## Four review domains (canonical)

Every branch review uses **four domains**. Report sections map to them; investigation lanes are **one per domain** — not per ticket type (migration, CMS, refactor, etc.).

| Domain | Report home | What it covers |
|--------|-------------|----------------|
| **1. Project best practices** | Must fix / Should fix (`[Placement]`, `[CMS blocks]`, `[Styling]`, `[Routing / page model]`) | Where code lives, CMS stack wiring, styling/token pipeline, routing and page shell — **including** CMS parity and route/deploy checks when the diff touches those surfaces (see § Conditional sub-checklists) |
| **2. Code principles** | Must fix / Should fix (`[DRY]`, `[KISS]`, `[Clean Code]`, `[SOLID]`, `[Don't Make Me Think]`) | DRY, KISS, Clean Code, SOLID, surprising APIs on **changed** lines |
| **3. Regression on existing pages** | Regression risk (`[Regression]`) | Default-changing edits to shared code that can break **pre-existing** routes/page types |
| **4. Unnecessary global changes** | Unnecessary global changes table (+ numbered regression when default-changing) | Cross-cutting deltas that could have been page-/domain-scoped; blast radius vs ticket scope |

**No separate “migration” or “CMS parity” lanes.** Those are **conditional sub-checklists** inside domain 1 (and findings land in Must/Should fix or Regression per § Severity and report placement). Branches that only touch isolated tokens or libs skip route/deploy sub-checklists; branches that split routes, document types, or catch-all behavior must run them under domain 1.

## Investigation architecture (mandatory)

**Goal:** every **PR-relevant** issue in the branch delta is found once with evidence — lanes may investigate broadly; the **published report** stays key-only for the chosen mode.

**When in doubt (orchestrator, not lanes):**

| Finding class | Default |
|---------------|---------|
| Regression, global blast, placement on shared code | **Omit** unless proven (named consumer + behavior delta) |
| Branch-introduced wiring on ticket surface | **Verify once** (schema → query → transform → component); keep only if broken |
| Lane candidate with `pr_blocker: no` in `pr` mode | **Drop** without debate |

Do not drop verified wiring gaps or proven cross-boundary leaks to shorten the report.

**Do not split subagents by report section** (must-fix vs regression vs global). The same diff hunk can be must-fix *and* regression. Split by **domain lane** (the four rows above), then **synthesize** into the report template (how severe / where to list).

### Phase 0 — Triage (orchestrator, main thread)

1. **Identify the review target** — § Review target: if no branch named, target is current branch (`HEAD`); otherwise use the named branch. Record exact branch name; stay on `HEAD` when it is the target.
2. **Resolve report mode** — § Report modes (`pr` default).
3. **Set comparison base** — merge-base with `main` (or repo default branch); `git fetch` when needed. Diff: `<merge-base>...HEAD` when reviewing current branch, else `<merge-base>...origin/<branch>` (or local ref if present).
4. **Discover repo adapter** — § Repo adapter discovery: load project skill + `code-review.md` when present; select references from path matrix.
5. **Build a diff inventory** — group changed paths by architectural layer (shared primitives, domain modules, page types, routes, editor schemas, data/query layer, tokens/theme, catalog/preview).
   - **infer ticket / page-group scope** — § Ticket and page-group scope; build § Editor placement scope matrix when editor schemas change; list dual-registry types and preprocessor-protected routes (from manifest when loaded)
   - **activate domain lanes** — per § Report modes: domain **3** investigate when shared surfaces change (publish per mode); domain **4** only in `full` mode; domain **1** when structure/CMS/routes change; domain **2** when any source file changes (see § Phase 1)
6. **Decide parallelism** — see § Lane splitting; evaluate sub-split thresholds **per activated domain** before spawning; spawn sub-lanes in one turn when paths are isolated.
7. **Scope domain activation** — docs-only or test-only diffs with no runtime behavior change: domains **2** (if source touched) may suffice; skip domains **3**–**4** unless shared surfaces change. Backend/API-only diffs: activate domains **2** and **3** on shared contracts, migrations, and flags; domain **1** route/CMS sub-checklists only when routing or content-model paths change.
8. **Brief lane subagents** — target page group, intentional boundaries, editor placement matrix, dual-registry list, preprocessor-protected routes, and **repo adapter manifest** (when loaded) from steps 4–5.

### Phase 1 — Domain lanes (subagents when scope warrants)

Each lane returns **candidate findings** in the standard record format (§ Finding record). Lanes are **read-only**; cite branch-diff paths/lines only. Apply the § Scope revert test before emitting a candidate — checklist coverage is not a finding list. **Cap: max 2 candidates per lane** unless `pr_blocker: yes`; prefer dropping `evidence_strength: hypothetical`.

**Four lanes** — one per review domain. Activate every lane whose trigger matches; run **conditional sub-checklists** inside domain 1 when paths match (§ Conditional sub-checklists).

| Domain lane | Activate when diff touches… | Must complete |
|-------------|----------------------------|---------------|
| **1. Project best practices** | App routes, page types, editor schemas, block/component registries, query/data layer | Placement; CMS/content stack end-to-end when applicable; styling on **cross-group** surfaces; routing and page shell. Run § Conditional sub-checklists when triggered. Apply § Repo adapter discovery manifest when loaded. |
| **2. Code principles** | Any source file in the branch delta | Repo `code` rule **after** § Intentional scoping gate and § Below Should fix — leaks and cross-group impact only. |
| **3. Regression on existing pages** | Shared primitives, global theme/tokens, transform/mapper pipeline, shared query fragments | Diff → behavior delta → consumers → subtract preprocessor-protected routes → § Shared-surface classification → § Editor placement scope matrix → § Dual-registry dispatch when scoped registry added. **Named** pre-existing routes only. |
| **4. Unnecessary global changes** | Shared primitives, global tokens, cross-cutting modules beyond ticket page family | Per delta: § Intentional scoping gate → blast radius beyond ticket intent? Default-changing + unprotected consumers → domain 3 regression. **Omit** page-shell and scoped-wrapper rows. |

### Conditional sub-checklists (domain 1 only — not separate lanes)

Run inside **domain 1** when the diff touches the paths below. Findings use domain-1 scope tags and land in Must/Should fix (or Regression via domain 3 when a shared surface breaks pre-existing pages).

| Sub-checklist | Run when diff touches… | Key checks |
|---------------|------------------------|------------|
| **Content stack parity** (when repo has CMS/editor) | Editor schemas, query layer, registries, transforms | Field → query → mapper/transform → registry → render path; **every projection field on every mapper return path**; **media resolver branches** when transforms map images/logos/awards; dead schema fields; consistent layout props within page family. Run manifest § Content stack parity when adapter loaded; else generic parity trace. |
| **Routing / deploy** | Route tables, catch-all filters, new content `type`, redirects/sitemap | Dedicated vs catch-all; content on correct type; shell context in primary builder. **Cutover:** § Deploy and cutover. **Dual-registry:** § Dual-registry dispatch. |

**Lane splitting (mandatory when scope is large):**

Split **before** spawning when a single domain lane would touch too many paths — oversized lanes time out, abort, or return shallow results. The orchestrator merges sub-lane outputs into one domain result before Phase 2 synthesis.

| Condition | Split into |
|-----------|------------|
| ≥ 3 changed files under shared primitives / `components/ui/` (or repo equivalent) | One subagent **per changed primitive directory** (domains **3** + **2** on those paths) |
| New domain block tree with ≥ 2 new block modules | Domain **1** subagent scoped to that domain block tree |
| `transform` / mapper pipeline refactor | Domain **2** + **3** on transform diff; domain **1** if registry/query also changed |
| Both editor schemas and query layer changed | Domain **1** with **content stack parity** sub-checklist |
| Repo adapter manifest loaded; Domain 1 activated; manifest § Domain 1 sub-lane conditions met | Domain **1** **project-adapter** sub-lane (manifest parity + path-matrix references only) |
| > ~40 changed files on branch | Run **all four activated domain lanes** in parallel; split domains 2–4 by path bucket (below) |
| **Any activated domain lane** with **≥ 8** changed files in its bucket **or** **≥ 3** top-level path prefixes (e.g. `components/ui/`, `lib/cms/`, `theme/`) | **Mandatory sub-split** that domain — never one monolithic subagent for the whole bucket |
| **Domain 4** (unnecessary global changes) activated and diff touches **both** shared primitives **and** transform/mapper/theme layers | **Two sub-lanes minimum:** (a) shared primitives + SCSS defaults, (b) transform/mapper/query pipeline — spawn in parallel |
| **Domain 3** (regression) with **≥ 4** changed shared primitives | One subagent **per primitive directory** or per path prefix — not one agent for all `components/ui/` |
| **Domain 1** with new content type **and** **≥ 5** new block modules | (a) editor schemas + document type, (b) domain block tree + registries — parallel sub-lanes |
| **Domain 2** with **≥ 15** changed source files | Split by path prefix (`blocks/`, `lib/`, `components/`) — cap **~10 files per sub-lane** |

**Sub-lane brief (mandatory):** Each subagent receives the Phase 0 scope briefing **plus** an explicit path allowlist (directories/files only — no whole-repo grep). Sub-lanes return candidate findings only; they do not write report sections.

**Sub-lane time budget:** If a sub-lane cannot finish its allowlist, return partial candidates with `paths_not_reviewed: [...]` — orchestrator spawns a follow-up sub-lane for the remainder or completes on main thread before synthesis (§ Lane failure / abortion).

Use `{{senior_agent_name}}`{{#cursor}} (`model="{{senior_agent_model}}"`){{/cursor}} for lane subagents. Orchestrator merges outputs — lanes do not write the final report.

**Lane failure / abortion (mandatory):** If a domain lane subagent **times out, aborts, or returns incomplete output**, the orchestrator must either (a) finish that lane’s scope on the main thread before synthesis, or (b) record the gap in **Open questions** (e.g. “Domain 4 incomplete — global-blast table not fully verified”). Do **not** publish a complete-looking report when an activated lane did not finish.

### Orchestrator delivery gate (mandatory)

**Do not publish until every spawned lane has finished successfully.** When Phase 1 spawns lane subagents, the orchestrator stays in **wait mode** until the lane-completion checklist passes. **Phase 2 and the § Report template are forbidden before that.**

The goal is **prevention**, not recovery: synthesize and publish only once, with **all** lane outputs in hand — never a partial report followed by patches or addenda.

#### Lane-completion checklist (mandatory before Phase 2)

At spawn time, record `lanes_spawned` (count + IDs/descriptions). **Do not start Phase 2** until **every** row passes:

| Check | Pass when |
|-------|-----------|
| **All lanes finished** | `lanes_finished === lanes_spawned` — each subagent returned **successfully** (candidate findings delivered), or that lane’s scope was completed on the main thread per § Lane failure / abortion |
| **None still running** | No in-flight Task/Await; no subagent status “still running” |
| **No aborted lane unhandled** | Timed-out or incomplete lanes were either re-run, finished on main thread, or their gap is recorded for **Open questions** — not folded into a partial report |

If **any** check fails → **remain in wait mode**. Forbidden: synthesizing, spot-checking findings for the report, or publishing because “most lanes are done,” an `Await` timer elapsed, or a system follow-up prompt arrived.

#### Delivery rules

| Rule | Requirement |
|------|-------------|
| **Wait for lanes** | After spawning, end the turn with lane work in flight only — **no** § Report template, no numbered findings, no interim summary. |
| **Single delivery** | After the checklist passes: Phase 2 → publish **exactly one** user-facing report in **one** message (full § Report template). |
| **No partial or follow-up reports** | Forbidden: publishing before the checklist passes; addendum messages; “report already stands”; “one gap to add mentally”; lane status updates to the user. |
| **Lanes complete in a later turn** | Normal when subagents outlive the spawn turn: **still wait** until the checklist passes, then Phase 2 → **one** report in that turn. Late lane output is input to synthesis, not a reason to append to an earlier message. |
| **System / follow-up prompts** | e.g. “perform follow-up actions in response to subagent completion” — means **continue waiting** until the checklist passes, then deliver the **first and only** report. Not permission to publish early or add to a prior message. |
| **Await / timeout** | Expired `Await` is **not** lane completion. On timeout: wait again, poll until all lanes finish, complete remaining scope on main thread, or end with **Open questions** only (no report) if a lane cannot be completed. |
| **No subagents spawned** | Branches reviewed entirely on the main thread may publish in the same turn after Phase 0–2 complete. |

The disposition ledger and lane merge happen **before** the single publish.

### Phase 2 — Synthesis (orchestrator)

**Entry condition:** every activated domain lane from Phase 0 has finished (subagent output received or main-thread completion per § Lane failure / abortion). Do **not** start Phase 2 while any lane is still running.

Lanes return **candidate** findings; the published report includes **only verified legitimate issues** (§ Finding legitimacy gate) and must not omit branch-introduced wiring gaps (§ Pre-publish gates). Investigation breadth ≠ report length, but **under-reporting real wiring gaps is worse than one extra should-fix line**; **over-reporting unverified regressions is also a failure**.

1. **Load** `references/false-positives.md` and manifest § False-positive patterns (when adapter loaded) — apply during steps 2–6.
2. **Merge findings** — dedupe by root cause (same behavioral change cited in multiple files or domains = one numbered item). **Operational launch sequencing** — apply § Deploy and cutover; at most **one** Must fix item when code ships an **unsafe** cutover with no documented stagger path.
3. **PR-mode filter (`pr` only)** — drop every candidate with `pr_blocker: no` unless upgraded after orchestrator spot-check proves user/editor-visible breakage.
4. **Intentional design reconciliation (mandatory)** — tag each candidate: `intentional-scoping` | `cross-boundary-leak` | `neutral`. Apply § Intentional scoping gate and § Necessary for ticket gate. Drop `intentional-scoping` unless cross-boundary leak evidence names specific routes or consumers.
5. **Pre-existing pattern check** — apply § Pre-existing pattern check; drop move-only / already-on-base patterns.
6. **Finding legitimacy gate (mandatory)** — for **every** surviving candidate: run § Finding legitimacy gate **and** § Behavior delta bar. Never publish from diff shape alone.
7. **Reconcile conflicting domains** — group candidates that cite the **same file/hunk** with opposite verdicts. Apply § Shared-surface classification; pick **one** verdict. Never list the same hunk in **What works** and a numbered finding.
8. **Candidate disposition ledger (internal, mandatory)** — list every lane candidate; record kept / merged / downgraded / dropped with gate citation.
9. **Retention filter** — drop candidates that fail **all** retention tests (§ Scope revert test, opt-in additive, below should-fix, intentional scoping, core and repo false-positive pattern match).
10. **Assign report section** — § Severity and report placement; in `pr` mode map Should fix → **Should fix before PR approval** only when `pr_blocker: yes`.
11. **Summary alignment** — merge blockers in Summary must match Must fix items exactly.
12. **Pre-publish gates** — legitimacy, placement matrix, regression naming, global table eligibility (`full` only), user-facing report only.
13. **Write the report** — § Report template for resolved mode.

### Finding legitimacy gate (mandatory — orchestrator, before retention filter)

**Goal:** report only issues that survive evidence-based verification — neither inflate with unproven regressions nor omit real branch-introduced wiring gaps. Lane subagents propose; the orchestrator **must verify** before a candidate becomes a numbered item.

For each `must-fix`, `should-fix`, or `regression` candidate, confirm **at least one** verification source (read the cited paths — do not rely on lane prose alone):

| Verification | Required when candidate claims… | Pass when |
|--------------|----------------------------------|-----------|
| **Schema read** | CMS/editor field unwired, wrong type, silent default, dead schema type | Schema field list, `validation`, `initialValue`, and editor placement (§ Editor placement scope matrix) match the claim; drop “silent editor surprise” if schema already requires the field or sets the same `initialValue` |
| **GROQ / query read** | Projection missing, wrong nesting, coalesce needed | Actual projection in query layer matches schema; cite which field path is fetched vs which mapper reads |
| **Transform / main data path** | Unwired runtime, dropped dimensions, palette/stega bug | Trace mapper → `transformCmsBlock` (or repo equivalent) → component; drop “missing `stegaClean` at component” if pipeline already normalizes the same prop on **all** CMS paths |
| **Wrapper / page-group context** | Shared primitive default wrong; dead CSS class | Ticket wrapper always passes overriding prop/variant (scoped-palette-only); dead class is no-op on ticket routes |
| **Consumer grep** | Regression on pre-existing pages | **Named** routes/components outside ticket group still hit changed code; subtract preprocessor-protected paths |
| **Sibling parity** | Inconsistent empty-body check, validation, or mapper vs co-introduced block on same page family | Read sibling block/component on same branch; keep when inconsistency is real and affects editors or render |

**Drop or downgrade (ledger required) when:**

| Pattern | Action |
|---------|--------|
| Removal of render-time cleanup **already done** on main CMS data path | Drop regression — § Shared-surface classification idempotent |
| SCSS refactor to mixin/equivalent with same computed output | Drop regression unless spot-check shows different computed style |
| Transform `fallbackTitle` / default **duplicates** schema `initialValue` on a **required** heading field | Drop “silent English default” — below should-fix or omit |
| Schema field projected but UI intentionally omits it (e.g. logo-only card; `actionText` used only in Studio `preview`) | Drop unwired-field finding unless frontend is supposed to render it per sibling block |
| Hypothetical type coercion (e.g. numeric CMS value) when schema field is `string` and Sanity path delivers strings | Drop unless evidence of non-string values on live path |
| Architecture preference (transform registered via domain definitions but logic in neutral `ui/` module; identical mapper override) | Drop global-table / Should fix unless proven behavior change |
| Global-table row with “prefer instead: keep / intentional” | Delete row per § Global table eligibility |

**Never drop without verification when:**

- Branch **added** schema field + query fragment but projection nests wrong path (e.g. block-level vs `image.maxWidth`)
- Branch-introduced block inconsistent with sibling empty-body / portable-text handling on same page builder
- Dead registered schema type with zero field references
- Cross-boundary leak with named route + fixture/CMS evidence

**Regression bar (mandatory):** a `[Regression]` item requires **all three**: (1) branch changed line cited, (2) **behavior delta** for users/editors on named pre-existing routes, (3) change is **not** idempotent/refactor-equivalent per § Shared-surface classification. Missing any → drop or downgrade to Summary spot-check only.

### Behavior delta bar (mandatory — all numbered items)

Every **Must fix**, **Should fix**, and **Regression** item requires a **user- or editor-visible** behavior delta — not schema/query shape alone.

| Claim | Required proof | Drop when |
|-------|----------------|-----------|
| Must / Should fix | Wrong/missing render, crash on valid CMS input, or editor sets value runtime ignores | Parity drift with no runtime effect; Presentation-only; schema `required` prevents bad input |
| Regression | Named pre-existing route + non-idempotent visual/functional change | Opt-in additive; idempotent refactor; no legacy CMS data for new fields |
| CMS projection wider than schema | — | Fields stay `undefined` at runtime (see `references/false-positives.md`) |

### Finding record (lanes return this; orchestrator maps to template)

```text
lane: project-practices | code | regression | global-blast
problem: <one sentence>
evidence: <paths changed on branch; optional short hunk description>
behavior_delta: <user/editor-visible change, or "none">
affected: <routes, page types, or block types — pre-existing only for regression>
scoping: intentional-scoping | cross-boundary-leak | neutral
severity_hint: must-fix | should-fix | regression | global-table
pr_blocker: yes | no
revert_test: exists_on_base | branch_introduced | branch_worsened
evidence_strength: proven | hypothetical
fix_hint: <what to do instead>
scope_tag: [Placement] | [CMS blocks] | [Styling] | [Routing / page model] | [DRY] | [KISS] | [Clean Code] | [SOLID] | [Don't Make Me Think] | [Regression]
```

Lanes must set `scoping` using § Intentional scoping gate. Orchestrator drops `intentional-scoping` unless `cross-boundary-leak` evidence is cited.

### Shared-surface classification (mandatory before severity)

Classify every changed shared primitive, token, transform, or CMS field **before** assigning `severity_hint` or report section:

| Class | How to recognize | Report as |
|-------|------------------|-----------|
| **Page-group-scoped intentional** | Change lives in page shell, domain wrapper, context registry, or Studio list scoped to ticket routes; no proven consumer outside group | **Omit** — ledger: intentional page-group scoping. May note in **What works** if it is a clear strength |
| **Default-changing** | SCSS/component default changed when prop omitted; transform injects new fallback; layout/sizing change with no CMS gate — **and** unprotected pre-existing routes still hit changed code | Numbered **Regression risk** or **Should fix** — **name** affected routes (fixtures/CMS), minus preprocessor-protected paths |
| **Idempotent / defense-in-depth** | Render-time helper duplicates logic already applied on the main data path (e.g. transform `normalizePaletteProps` then `cleanLayoutStega` then component); equivalent string refactor (`getPaletteClass` → literal class); **removing** redundant `stegaClean` when pipeline already cleans | **Not** a regression; omit or Summary spot-check only |
| **Refactor-equivalent** | SCSS/typography moved to mixin or level class with same variables/output; inner element still sets the same effective rule | **Not** a regression; omit unless computed style differs on a named consumer |
| **Schema-duplicated default** | Transform injects `fallbackTitle` / default that matches schema `initialValue` on a **required** field | Omit “editor surprise” finding; below should-fix at most |
| **Studio-preview-only field** | Schema field used in `preview.select` / Studio label but not in frontend component by design (e.g. logo-only card vs customer-story card with CTA) | Omit unwired-field finding unless sibling block type renders the same field |
| **Correctness fix on pre-existing gap** | Maps **invalid** CMS/config value to a **valid** theme/token that never existed (e.g. `palette-white` → `palette-light` when `.palette-white` is absent from theme); prior behavior was a no-op or broken class | **Omit** from regressions; optional one-line **Summary** spot-check — not numbered |
| **Deliberate alias remap (valid → valid)** | Changes one working token to another with different visuals | **Regression risk** or **Should fix** — confirm intent |
| **Opt-in additive** | New schema field, optional prop, or CMS knob; transform passes through only when set; no new default when omitted; new key on shared union only used by ticket wrappers | Omit from numbered regressions. Global-table row only when API surface is wide **and** values are already used outside the ticket group |

**Common mistakes (drop before publish):**

- Reporting regression because a **shared file** changed without tracing the **main data path** and naming unprotected consumers.
- Treating **removed duplicate normalization** as regression when transforms/mappers already clean the value.
- Flagging **transform fallbacks** as “silent English” when schema already sets the same `initialValue` on a required field.
- Flagging **projected but unrendered** fields without checking Studio preview-only use or intentional logo-only vs CTA card patterns.
- **Omitting** GROQ projection bugs the branch introduced (wrong field path, missing `image.*` coalesce) because they “only affect new surfaces” or a non-ticket block type.
- **Omitting** sibling parity gaps among blocks on the same scoped page builder (e.g. `body?.length` vs `portableTextToHtml`).

**Shared component regressions:** cite the **default-changing SCSS or layout rule** first. Mention DOM/markup moves only when they add risk beyond the style/layout change.

### Severity and report placement (mandatory)

Use this table when assigning numbered sections. Global table rows **supplement** numbered items; they do not replace default-changing regressions.

| Finding type | Report section |
|--------------|----------------|
| **Unsafe cutover in code** — branch ships routing/`_type` split that **requires** published content with **no** documented stagger path and proven 404/wrong-doc risk on launch | **Must fix before merge** `[Routing / page model]` — rare; see § Deploy and cutover |
| **Fragile wiring / cross-boundary leak** — silent mis-map; context dispatch returns `null` for dual-registry types on **proven** routes (named paths, not “all pages”) | **Must fix before merge** `[Don't Make Me Think]` / `[CMS blocks]` |
| **Unwired optional field** — declared in schema/config/API but not fetched, mapped, or applied at runtime; defaults still work | **Should fix** in `full` only — in `pr` only if editors can set values that break or silently drop on ticket routes |
| **New surface parity** — branch-introduced unit inconsistent with siblings | **Should fix** only when verified wiring gap (editor can set → runtime ignores) — not empty-guard cosmetics |
| **Shell/context fragility** — dispatch or rendering depends on a side-effect enrichment step instead of the primary builder | **Should fix** `[Routing / page model]` |
| **Convention / placement** — wrong layer vs **verified** repo examples | **Should fix** only with cross-group impact or two contradicting repo examples — not ticket-scoped `ui/` + wrapper pattern |
| **Default-changing shared primitive** — style/component default when prop omitted; affects **pre-existing** consumers | **Regression risk** `[Regression]` |
| **Invalid-token alias remap** — maps CMS value with no theme/CSS counterpart to a valid token; prior render was broken or unstyled | **Summary** spot-check only — **not** numbered (see § Shared-surface classification) |
| **Deliberate alias remap (valid → valid)** on shared code | **Regression risk** or **Should fix** (confirm intent) |
| **Idempotent normalization** on the main data path | **Summary** one sentence spot-check only — **not** numbered, **not** What works |
| **Opt-in additive** — new optional field/prop, unchanged when omitted | Omit numbered; global table if API surface is wide |
| **Could be scoped narrower** | **Unnecessary global changes** table (`full` mode only) + numbered regression when default-changing **and** unprotected consumers named |

**Branch-introduced surface:** issues on code **added by this branch** for the ticket’s scope are in scope even when they do not affect pre-existing consumers. Tag appropriately; do not defer as “follow-up” unless below should-fix per retention filter.

### Deploy and cutover (route / content-type splits)

When the branch adds dedicated routes, a new content `type`, and catch-all exclusion for the same URL family:

| Situation | Report as |
|-----------|-------------|
| Intentional split matching an established repo migration pattern | **Omit** numbered items — optional one line in **Summary**: document schema → content migration → deploy order |
| Code lacks fallback **and** launch requires staggered ship with no runbook | **Must fix** — one deduped operational item |
| Runbook or team process already defines cutover | **Omit** — not a code defect |

Do **not** treat “app ships before new-type content exists → 404” as automatic Must fix when the split **is** the ticket goal.

### Dual-registry dispatch (domains 1 and 3)

When the branch adds context-keyed dispatch (scoped registry checked before global registry):

1. List types in **both** global editor palette/registry **and** scoped registry.
2. For each dual-registry type: which routes use **route preprocessors** that replace or remove the type before render?
3. Search fixtures / seed content / CMS samples for **raw** usage on global routes not covered by preprocessors.
4. Report only **proven** affected routes.
5. Scoped dispatch returning empty off-group is **intentional** for scoped-palette-only types; it is a **leak** only for dual-registry types with proven raw usage on global routes.

### Exclusive-registry dispatch (domains 1 and 3)

When dispatch routes **exclusive** (scoped-palette-only) types to the page-group registry **without** a `pageClass` guard:

1. Confirm the type is **not** in the global editor palette — only in the scoped registry for the ticket page group.
2. If scoped-palette-only → **omit** “missing `pageClass` guard” findings — ledger: intentional page-group scoping. Defense-in-depth is below should-fix without proven global-route content.
3. Report only when fixtures, seed data, or CMS samples show the exclusive type on a **global** route the editor can still build — same evidence bar as § Dual-registry dispatch.

### Global table eligibility

Include a row in **Unnecessary global changes** only when **all** are true:

- Change is on a shared module/token **and** could have been scoped narrower **beyond** ticket intent.
- Not classified as page-group-scoped intentional, opt-in additive, or idempotent refactor.
- Not already a numbered Must fix / Regression (unless row adds a distinct “prefer instead” beyond the fix hint).
- Blast radius is **named** (routes or callers), not “all consumers of shared file.”

**Always omit rows for:** opt-in props with no consumers yet; idempotent typography refactors; page-shell CSS variables; scoped-only enum keys; refactor “add tests” without proven gap; duplicate of numbered items; rows whose “Prefer instead” is **keep** / **appropriate** / **none until passed** (no narrower scope proposed).

If every surviving row would be omitted by the above → **omit entire section**.

### Pipeline vs render normalization (general)

When the diff touches normalization helpers on both data pipeline and render path:

1. **Trace the main path** — does the transform/mapper already normalize the value before the component?
2. **If yes** — render-time duplicate is usually **idempotent**; omit regression unless branch changes transform logic or adds deliberate alias remap.
3. **If no / bypass paths exist** — non-pipeline callers may **gain** behavior; classify as **default-changing** for those paths only.
4. **Encoding / overlay cleanup** (e.g. stripping editor overlay metadata from class strings) at pipeline layer — omit render-layer removal as regression if pipeline already cleans.
5. **Invalid legacy CMS values** — when the old value had no theme/CSS counterpart (broken class, silent no-op), mapping to a valid token is a **correctness fix**, not a regression — verify the old value was ineffective before classifying as default-changing.

### Synthesis rules (mandatory)

Apply during Phase 2 after reconciliation; these govern severity and section choice across all branch types:

| Rule | Requirement |
|------|-------------|
| **Severity integrity** | In `pr` mode: numbered items need `pr_blocker: yes` and § Behavior delta bar. Schema/query parity without runtime effect → omit. |
| **Summary ↔ Must fix** | Summary may name **only** items in **Must fix before merge** as merge blockers. Should fix and Regression items are risks or follow-ups — not “blocked merge” unless also listed under Must fix. |
| **Launch sequencing dedup** | Related deploy/migration/schema steps for one cutover → **one** Must fix entry. |
| **Open questions scope** | Unresolved **product or architecture intent** not already covered by a numbered item. Do not restate Should fix or Regression findings; do not use for launch sequencing (→ Must fix). |
| **Evidence bar for edge cases** | Path normalization, trailing forms, locale/timezone, auth edge cases → Should fix or Regression only when the diff introduces a mismatch **and** evidence shows the bad form is accepted (fixtures, validation, production URLs, API examples). Otherwise omit or one-line Summary. |
| **Peer asymmetry** | Missing field/option vs a sibling document/route/API type introduced on the **same branch** → **Should fix** when editors can set values runtime ignores, or when sibling uses constrained controls (radio/list) and new type uses free-text for the same field. Omit only when both forms work and ticket scope does not require parity. |
| **Same-theme dedup** | Multiple findings on one convention (e.g. token pipeline on several new files) → one numbered item with representative paths, unless severities differ. |
| **Intentional scoping first** | Page-shell SCSS, domain wrappers, restricted Studio lists, context dispatch → apply § Intentional scoping gate before convention or “unnecessary global” findings. |
| **Consumer naming** | Regression and leak findings must name **specific routes or preprocessor gaps** — never “all pages” / “site-wide” from shared file path alone. |
| **Legitimacy before severity** | Apply § Finding legitimacy gate before assigning Must fix / Should fix / Regression; unverified lane candidates stay in ledger as dropped — not in the user report. |
| **Branch-introduced wiring** | GROQ projection path errors, dead schema types, and sibling parity on the ticket’s page builder are **Should fix** when verified — not deferred as “new surface only” without proof they work. |
| **Contingent regression** | When Must fix unblocks a code path on pre-existing routes, check default-changing shared primitives on **those same routes** — one Regression item or Summary spot-check. |
| **SOLID/DRY on wrappers** | Registry passthrough, transform wiring via domain definitions, thin wrappers, intra-ticket duplication, module path preferences → not findings unless proven leak or inconsistent runtime. |

### Transform vs render normalization

See § Pipeline vs render normalization (general) in Phase 2 synthesis area above.

## Review workflow (summary)

Phase 0 triage (load repo adapter when applicable) → Phase 1 parallel **four domain lanes** (conditional sub-checklists inside domain 1 when paths match) → **wait until every spawned lane finishes successfully** (§ Lane-completion checklist) → Phase 2 synthesis (§ Finding legitimacy gate on every candidate) → **one** report (§ Report template) in **one** message.

## What to evaluate

The **four domain lanes** are the evaluation lenses. This section is a reference index — lanes must cover changed code only (see § Scope).

### Domain 1 — Project best practices

| Sub-lens | Look for |
|----------|----------|
| **Placement** | Blocks/components in correct layer (`ui` → `common` → domain → page-type); domain imports from `ui`, not the reverse |
| **CMS blocks** | Checklist followed (schema, query, registry, transform, group entry); block metadata colocated with render; extend vs new block — use manifest § Content stack parity when adapter loaded |
| **Styling** | Token pipeline respected on **cross-group** shared surfaces; page-shell SCSS and domain wrapper scoping per § Intentional scoping gate — not automatic violations |
| **Routing / page model** | Correct route/page-type assembly; catch-all vs dedicated routes; deploy order; page shell — use § Routing / deploy sub-checklist when `pages/` or `_type` split changes |

### Domain 2 — Code principles

| Principle | Look for (in branch delta) |
|-----------|----------------------------|
| **DRY** | Duplicated PT/HTML/SCSS, parallel mappers, near-duplicate blocks/components the branch added |
| **KISS** | Unnecessary abstraction, oversized new files, indirect control flow the branch introduced |
| **Clean Code** | Naming, small units, clear boundaries; inverted dependencies the branch created |
| **SOLID** | SRP at block/component level; dependency direction (`ui` must not depend on domain); narrow props |
| **Don't Make Me Think** | Ambiguous block choice, hidden domain behavior in generic-looking APIs, surprising defaults |

### Domain 3 — Regression on existing pages

**Mandatory when the branch touches shared code.** Any branch type — not only migrations — can break homepage, legal, blog, API, partners, or catch-all CMS pages via shared surfaces.

| Surface (branch delta) | Check on pre-existing pages |
|------------------------|----------------------------|
| **Generated tokens / `theme.scss` / `palettes.json`** | Body text, link, border, and palette-class colors site-wide |
| **Shared primitives** (`Heading`, `Image`, `Grid`, `SectionContainer`, `RichText`, `TwoColumn`, `Card`, …) | Every block/component that imports the changed module — grep call sites |
| **Transform / mapper pipeline** | Existing content/block types still map and render with same props/layout |
| **Query projections** (shared fragments, existing block types) | Pages already fetching those fields — missing or renamed projections |
| **Theme / palette resolution** | Run § Pipeline vs render normalization first. Deliberate alias remaps are **default-changing**. Duplicate normalization on an already-normalized main path is usually **idempotent** |
| **Common / singleton blocks** (nav, footer, chrome) | Site chrome and blocks embedded on many routes |
| **Global editor palette blocks** | New defaults or variants on blocks editors can place on global routes |

For each regression finding: name the **changed file**, the **behavior delta**, and **which specific routes** are at risk — subtract preprocessor-protected paths. Apply § Intentional scoping gate and § Dual-registry dispatch. Omit **opt-in additive** and **page-group-scoped intentional** items. Prefer the **default-changing** surface over adjacent new optional fields.

### Domain 4 — Unnecessary global changes

| Lens | Look for |
|------|----------|
| **Scope vs ticket** | Changes to `palettes.json`, `typography.json`, `theme.scss`, shared primitives, nav/footer — could they be page-/domain-scoped? **Skip rows** that are already intentional per § Intentional scoping gate (page shell, wrappers, opt-in variants). |
| **Overlap with domain 3** | Default-changing globals with **unprotected** consumers get a **numbered** regression in domain 3; domain 4 table adds “prefer instead” |

## Report template

Use the template for the resolved **report mode** (§ Report modes). **Key findings only** — omit empty sections.

### `pr` mode (default)

```markdown
## Summary
[2–3 sentences. Name merge blockers only if listed under Must fix. Note intentional supporting global changes in one phrase when relevant — not as findings.]

## What works
[2–4 bullets max]

## Must fix before merge
[Numbered list. Omit section if none.]

## Should fix before PR approval
[Numbered list. **PR blockers only** — proven user/editor-visible breakage. Omit section if none.]
```

### `full` mode

Add after Should fix (continuous numbering):

```markdown
## Should fix
[Deferrable items not required before PR — omit if none.]

## Regression risk on existing pages
[Proven default-changing shared surfaces + named pre-existing routes. Omit if none.]

## Unnecessary global changes
[Table — omit if no rows survive § Global table eligibility.]

## Open questions
[Unresolved product intent only. Omit if none.]
```

**Numbering:** Continuous across Must fix, Should fix, Regression. Each item: `N. [Scope tag] Problem → evidence → fix.`

### Writing rules for the report

- **Branch delta only** — every issue must trace to something this branch added or changed; omit pre-existing debt the branch did not touch.
- **Regression items cite the diff** — name the shared module or token the branch changed and which existing consumers are at risk; do not list generic "test everything" advice.
- **Key data only** — every section must earn its place; omit empty sections entirely.
- **No branch metadata** — do not include commit counts, file counts, line deltas, or merge-base hashes in the report.
- **No nice-to-have** — do not list deferrable polish, optional refactors, or low-priority suggestions. Schema field option parity (e.g. radio vs free-text) when behavior works is below should-fix unless it blocks editors.
- **Do not shrink the report** — dropping verified `should-fix` / `regression` candidates to stay short is an anti-pattern; use the disposition ledger, § Finding legitimacy gate, § Severity and report placement, and § Synthesis rules instead.
- **Do not inflate the report** — unverified regressions, global-table noise, placement on scoped-palette-only types, and `pr_blocker: no` candidates must not appear as numbered items in `pr` mode.
- **Necessary supporting globals are not findings** — shared projection/transform widenings required for the ticket belong in Summary or What works, not Should fix or global table.
- **Summary accuracy** — merge blockers in Summary must match Must fix items exactly; unwired optional fields are not merge blockers by default.
- **Concise but complete** — full sentences; no telegraphic shorthand or vague "consider refactoring."
- **Specific where it helps** — name files, block types, variants, and route/page families; one-line evidence beats generic advice.
- **Do not** paste large diffs, repeat the user's question, or list every changed file.
- **Do not** inflate "What works" — keep it short so fixes stay the focus.
- **Do not** add a **By principle** section — scope tags in brackets on each numbered item are sufficient.
- **Global table** — omit rows that duplicate a numbered Must fix / Regression item unless the row adds a distinct “prefer instead” beyond the fix hint; never list Studio-only ui defaults in the table; delete rows whose “Prefer instead” endorses keeping the change.
- **User-facing report only** — publish § Report template sections only; never append disposition ledger, domain reconciliation tables, subagent status, or “withdraw/keep” verdict matrices.
- **Single consolidated delivery** — one report message, published only after every spawned lane has finished successfully; never split across turns

## Anti-patterns (for the reviewing agent)

- Auto-invoking this skill without explicit user request
- Implementing fixes because the review "found issues"
- Checking out, stashing, or asking to switch when already on the review branch
- Checking out the review branch without permission when HEAD is on a different branch
- Flagging pre-existing patterns the branch did not modify (e.g. criticizing a file's overall size when only a small additive hunk landed)
- Treating a bundled global token rewrite as in-scope when the ticket is a single page migration
- Reviewing only file names without comparing to existing repo primitives and legacy production
- **Reviewing only new page files** and skipping regression when shared primitives, tokens, or transforms changed
- **Single monolithic pass** on large branches (>40 files or ≥3 shared primitives) without spawning lane subagents
- **Category-first subagents** (one agent for “must fix”, one for “regression”) instead of **domain** lanes
- **Separate CMS parity or migration lanes** — those are domain-1 sub-checklists, not parallel lanes
- **Regression without behavior delta** — numbered `[Regression]` from shared-file path or diff hunk alone, without named pre-existing consumer and verified non-idempotent change
- **Unverified lane echo** — publishing lane candidate verbatim without orchestrator schema/GROQ/transform spot-check per § Finding legitimacy gate
- **False unwired-field alarm** — `actionText` / optional card fields projected but intentionally not rendered, or Studio-preview-only, without sibling-block comparison
- **Missed branch wiring** — omitting verified GROQ projection mismatch, dead schema type, or sibling parity gap on scoped page builder because “below should-fix” or “new surface only”
- **Schema-default blind spot** — “silent English fallback” when transform duplicates schema `initialValue` on required heading
- **Idempotent cleanup as regression** — `stegaClean` / normalization removed at component when pipeline already normalizes the same prop
- **Refactor-equivalent SCSS as regression** — typography moved to mixin/level class without computed-style change on named route
- **Publishing before all lanes finish** — running Phase 2 or publishing § Report template before the § Lane-completion checklist passes
- **Partial or follow-up reports** — addendum messages, “report already stands,” “one gap to add mentally,” or any second user-facing report chunk for the same review
- **Await timeout treated as done** — proceeding after `Await` expires while lanes are still in flight
- **Premature synthesis** — spot-checking or verifying findings for the report while spawned lanes have not all finished successfully
- **Follow-up prompt misread** — treating subagent-completion system messages as permission to publish before the checklist passes
- **Subagent status to user** — “Domain 3 is running…”, lane IDs, or “I’ll synthesize when they complete” instead of waiting silently and delivering one report
- **Contradictory praise** — listing a changed shared surface in What works while a lane flagged it as regression (reconcile first per § Phase 2)
- **Verdict flip without reconcile** — promoting idempotent normalization to What works while dropping the regression lane’s candidate with no classification
- **SCSS vs CMS field confusion** — flagging new optional CMS fields as regression while missing default-changing shared SCSS on the same component
- **Silent drop** — omitting a lane’s regression candidate during dedup without merge, downgrade rationale, or § Shared-surface classification
- **Disposition ledger skipped** — publishing without reconciling every lane `must-fix` / `should-fix` / `regression` candidate
- **Deploy cutover auto-elevated** — treating standard migration splits as Must fix **or numbered Should fix** code defects; one-line cutover note in Summary is enough when intentional
- **Page-group scoping as defect** — flagging page-shell SCSS, domain wrappers, restricted Studio block lists, or context dispatch as token-pipeline / placement / “unnecessary global” violations when they match ticket boundaries
- **Stale doc convention** — citing one naming/placement bullet (e.g. “no Page suffix”) without verifying mixed `pageTypes/` reality or branch-updated docs
- **Site-wide regression from path** — reporting regression because a shared file changed without naming unprotected consumers and subtracting preprocessor-protected routes
- **Preprocessor-blind regression** — claiming routes break on a dual-registry type when preprocessors replace or remove that type before render
- **SOLID/DRY wrapper noise** — registry passthrough, transform wiring via domain definitions, thin domain wrappers, intra-ticket SCSS/Studio duplication, or module path preferences as Should fix without a proven leak
- **Deploy order demoted** — putting **unsafe** cutover (no stagger path, proven launch 404) only in Open questions — use Must fix per § Deploy and cutover
- **Regression demoted to global table only** — default-changing shared primitives listed only in Unnecessary global changes with no numbered regression item
- **Branch-introduced parity dropped** — omitting wiring or layout parity on **new** ticket code as “not key” because it only affects the new surface
- **Media resolver branch drop missed** — transform mapper reads `maxWidth`/`maxHeight`/etc. but shared media resolver omits them on CMS ref (or other) branch
- **Exclusive dispatch as leak** — “missing `pageClass` guard” for scoped-palette-only exclusive types without proven global-route content
- **Invalid-token remap as regression** — treating legacy CMS value → valid theme token as visual regression when the old value had no CSS counterpart
- **Global table as dumping ground** — rows that say keep/appropriate/none-until-passed, or duplicate numbered items without a distinct narrower-scope alternative
- **Lane abortion ignored** — publishing after a domain lane timed out/aborted without finishing that scope or noting incomplete coverage
- **Oversized domain lane** — one subagent for an entire domain bucket (especially domain 4 global-blast) when § Lane splitting thresholds are met — split into path-scoped sub-lanes instead
- **Ledger leaked to user** — disposition ledger, “Reconciled Domain N”, subagent status, or verdict tables appended after the report template
- **Open questions filler** — “None” / “None beyond numbered items” / restating cutover runbook already covered in Summary
- **Should fix elevated to Must fix** — unwired optional config/schema fields or editor parity gaps treated as merge blockers without runtime failure or explicit launch requirement
- **Duplicate launch Must fix** — multiple numbered items for the same cutover story (schema + migration + deploy) instead of one deduped entry
- **Open questions as duplicate verdicts** — restating a numbered Should fix or Regression item as an open question
- **Hypothetical edge case without evidence** — reporting path/normalization/locale risks with no fixture, validation, or production signal
- **When in doubt, keep the finding** — superseded by § Investigation architecture “When in doubt” table; default is **omit** for regression/global/placement
- **Publishing Domain 4 rows in `pr` mode** — Domain 4 is `full`-only unless user explicitly requests global-blast analysis
- **Schema/query parity without behavior delta** — numbered Should fix from projection wider than schema slice
- **Placement on scoped-palette-only `ui/` defaults** — when wrapper exists and no dual-registry leak
- **Necessary-for-ticket global change as global-table row** — when revert breaks ticket routes
- **Pre-existing pattern reported as branch defect** — without `revert_test: branch_introduced` or `branch_worsened`
- Adding branch stats, nice-to-have items, or passing checklist noise to the report
- Adding a **By principle** section or repeating the same finding twice under different headings
- **Appending the disposition ledger** to the user-facing report (internal only)

## Example invocation

User attaches this skill: `/review-branch` (on branch `feature/account-settings`).

Agent: Phase 0 — review target = current branch `feature/account-settings` vs `main`; mode = `pr`; discover repo adapter (`code-review.md` when present); triage (diff inventory + activate matching **four domain lanes**) → Phase 1 parallel subagents (domains 1–4 as triggered; content-stack/routing sub-checklists and **project-adapter** sub-lane when manifest triggers) → **wait until every spawned lane finishes successfully** → Phase 2 synthesis (**§ Finding legitimacy gate** on every candidate) → **one** report (§ Report template) → **no file edits**.

Named branch variant: "Review branch `feature/account-settings`" — same workflow; target is the named branch, not inferred from a different `HEAD`.
