---
name: improve-parity
description: >-
  CSS parity then visual parity — compare localhost vs production on mapped
  key elements (block → component → text), classify gaps (CSS vs structural
  vs original-inconsistency), fix CSS-fixable issues, and report structural /
  reference problems before pixel-chasing. Use when pages drifted after refactors,
  migration parity regressed, or the user asks for visual/CSS parity, improve-parity,
  production match, or 1:1 styling vs uploadcare.com.
---

# Improve parity

{{block:tool-note}}

Repeatable **CSS-first, then visual** compare → fix loop between an **implemented page** (local dev) and a **reference page** (production URL and/or reference repo source).

**One invocation** = a **single pass**: **Phase A (CSS)** → **Phase B (visual)**. There is no outer “improvement rounds” loop — do not run Phase A→B multiple times in one invocation.

**Rounds** (user term) = **compare→fix iterations within each phase**. Same as **iterations per phase**. Default **2** in Phase A and **2** in Phase B unless the user or plan specifies another number (e.g. `5 rounds` → 5 iterations in Phase A and 5 in Phase B).

Skip Phase A entirely only when the user explicitly asks for **visual only** (e.g. “visual compare only”). Skip Phase B when the user asks for **css only**.

Migration plans (e.g. `uploadcare.com/.local/customers-migration-plan.md`) should **delegate parity work to this skill** — do not duplicate compare/fix steps in the plan body. Plans may cap **iterations per phase** and maintain a **parity scoreboard**; this skill defines execution and scoring.

## Defaults

| Setting | Default | Override via user request |
| --- | --- | --- |
| Invocation shape | **One pass:** Phase A → Phase B | `css only`, `visual only` |
| **Rounds / iterations per phase** | **2** compare→fix cycles in Phase A and **2** in Phase B | e.g. `5 rounds`, `3 iterations` |
| Viewport(s) | **1250 / 900 / 320** for migration parity; **1250px** for single-route spot checks | e.g. `mobile`, `744px` |
| **CSS target** | **100%** — zero open key-element diffs + visual spacing supplements @ each viewport | — |
| **Visual target** | **≥99%** — worst viewport in the set | — |
| Scope | Page(s) named in the request | If omitted, ask which route(s) |

Parse overrides from the **same message** that invokes this skill. **`N rounds`** and **`N iterations`** both mean **N compare→fix cycles per phase** (applied to Phase A and Phase B separately unless user says otherwise).

**After iterations are exhausted:** always produce the **parity scoreboard**, **Structural issues**, **Original inconsistencies** (when applicable), **Component / block gap hints** (when structural signals fire — see below), **Recommended next steps**, and **Below threshold**. **Never** imply visual success if visual &lt; 99% on any scoped URL unless the gap is **approved divergence** (documented, user-accepted).

**Reference hierarchy** (when sources conflict — **active plan overrides** when present):

| Priority | Source | When |
| --- | --- | --- |
| 0 | **Live production (Tier A truth)** | Mapped key elements: local computed styles vs same element on production @ each scoped viewport |
| 1 | **Active plan locked targets** | Advisory for disputes, original-inconsistency resolution, and fix direction — **not** a substitute for live prod diff |
| 2 | **Domain foundation doc** | e.g. `customers-foundation.md` — default when prod is ambiguous |
| 3 | **Consistent production / source repo** | Same component/region behaves the same across fixture URLs in reference repo |
| 4 | **Inconsistent production** | Differs across stories for the **same role** → survey corpus prevalence if plan requires; else document and propose **one** rule — **Tier D / approved divergence last resort** after gap analysis + fix slices |

**Plan autonomy:** Respect plan § **Scope boundary** — `domain` fixes in-scope; `global` (shared theme, `components/ui/`, site-wide tokens) → propose only, return `ESCALATE: global-scope`. See `create-plan` § Scope boundary.

## Reference sources

| Role | Typical source |
| --- | --- |
| Production UI (truth) | `https://uploadcare.com/<route>` |
| Local implementation | `http://localhost:4321/<route>` (confirm dev server) |
| Source patterns / values | Sibling repo `uploadcare-website` at `/Users/jacek/Projects/uploadcare-website` |
| Project conventions | `uploadcare.com` → `.agents/skills/project-best-practices/`, `docs/website/tokens.md` |
| Domain foundation docs | e.g. `docs/website/customers-foundation.md`, `docs/website/blog-foundation.md` |

For **uploadcare.com core-marketing**, also read `.local/core-marketing-visual-parity-process.md` (route order, in/out of scope).

## In / out of scope (per invocation)

| In scope | Out of scope (unless user expands) |
| --- | --- |
| Main page content: blocks, typography, spacing, palettes, DOM/CSS structure | Global site header nav and footer (separate invocation) |
| Story chrome on scoped routes (in-page nav, company band, embedded quotes) when migration scope includes them | Form submit / API smoke |
| CMS palette/content when needed for parity | Chasing live widget interactivity |
| Layout/styling for known intentional gaps (e.g. static uploader) | — |

**Decision rule:** For **CSS-fixable** gaps, fix until **live local vs prod** key-element diff passes; use locked plan targets and foundation when prod is inconsistent or ambiguous. For **structural** gaps: **do not** equate fewer DOM nodes with unfixable — produce **gap matrix hints** (missing block variant, spacing model, layout rule) before recommending stop pixel-chasing or Tier D. For **original-inconsistency**, use plan survey / corpus prevalence when defined.

---

## Issue taxonomy (mandatory classification)

Every gap found in Phase A or B must be tagged **one** primary type:

| Type | Meaning | Action in this invocation |
| --- | --- | --- |
| **CSS-fixable** | Same DOM role; computed styles differ from target (plan locked → foundation → consistent prod) | Phase A2 / B2 fix within **plan domain scope** |
| **Structural — fixable** | Visual/height gap from missing or wrong block variant, spacing model, layout module, CMS flag — **not** mere node-count difference | Report + **gap matrix row** (prod pattern → current → missing piece); fix in B2 **if plan authorizes** and scope is domain |
| **Structural — divergent** | Irreconcilable after gap analysis + authorized fix slices; or requires **global/shared** scope change | Report; **Tier D / user last resort** — do not default to “accept fewer blocks” |
| **Original-inconsistency** | Same **role**, different prod rules across fixture URLs | Report; propose **one** rule from plan survey / prevalence when defined; else foundation-aligned rule |
| **Excluded** | Tier C / out of scope (global header, video frames, etc.) | List only; no fix |

**Tier C gate:** Do **not** classify a gap as **Excluded / Tier C** until **key-element CSS parity passes** for that region (all mapped block → component → text elements @ each scoped viewport). Under-probed CSS drift (e.g. wrapper-only typography checks, missing `font-family`) is **CSS-fixable**, not Tier C. **Mis-bucketing CSS probe failures as Tier C is an anti-pattern.**

**CSS vs structural rhythm:** A failed key-element diff → **CSS-fixable** when roles map; **Structural — fixable** only when the wrong DOM layer or variant blocks a fair comparison *after* Text-tier typography passes. Do not label merge-rhythm or block-count gaps **Structural** while open key-element CSS diffs remain for the same region. **Tier B clip % alone does not prove rhythm** — run § Vertical rhythm probes; in-block CSS can be correct while holistic body score stays flat on merged blocks.

**Node-count rule:** Local `content[]` block count ≪ production MDX wrappers is a **signal**, not a verdict. Classify **Structural — fixable** when a consolidated block could replicate prod rhythm via variants/SCSS; **Structural — divergent** only when gap matrix shows no domain-scoped fix path.

**Structural signals** (any → classify Structural before more B2):

- Block-boundary / wrapper-vs-inner probe fails while typography probes pass
- Region height Δ &gt; ~100px with similar text content (block count or wrapper padding)
- Local `content[]` block count ≪ production MDX component sequence
- Wrong ecru band / quote surface despite correct token (wrapper layer issue)
- CMS variant flags missing where reference source is explicit (band context, spacing tier, media controls)

**Original-inconsistency signals** (any → classify Original-inconsistency):

- Same shortcode/component (e.g. `Paragraph`, `StoryBreak`, `Link`) yields **different** spacing, underline, or typography on two+ fixture URLs in `uploadcare-website`
- Production spot-check contradicts foundation **and** another story’s production behavior
- Chasing one story’s prod values would **break** foundation or another fixture URL

---

## Key-element CSS parity (Phase A core)

Tier A CSS pass requires a **live local vs production** computed-style diff on **mapped key elements** — not a closed selector/property checklist, not hardcoded constants without prod fetch, and not every DOM node on the page.

### Three tiers

| Tier | Meaning | Examples |
| --- | --- | --- |
| **Block** | Page or column-level section | main content column, footer band, listing hero, in-page chrome band |
| **Component** | Reusable structure inside a block | footer CTA, quote figure, company band, rich-text container, card grid |
| **Text** | Innermost visible text-bearing node | button label, `h2`, paragraph, link text, list item text |

Migrated pages are built to replicate the original — expect a **role map** prod block → local block, prod component → local component, prod text → local text. Matching uses **role + order within block** (and stable text content where helpful), not identical selectors or node counts.

### Discovery and mapping

**Default — infer when plan/command is silent:**

| Tier | How to discover |
| --- | --- |
| **Block** | Semantic landmarks (`main`, `article`, `[role="main"]`, page-type section roots) + ordered CMS/content blocks (`_type`, `data-block`, section wrappers) |
| **Component** | Reusable structures inside each block (nav band, CTA cluster, figure, quote, list container, band/surface wrapper) |
| **Text** | **All visible text nodes** inside each component — always probe the **innermost text-bearing element** per text run |

**Plan/command overlay (optional):** fixture URLs, viewports, scope boundaries, block-type → prod-role hints, region exclusions, reference repo paths. Plans supply **mapping hints when inference is ambiguous** — they do **not** define which CSS properties to check or replace live prod comparison.

**Do not** tie discovery to implementation-specific CSS class names in this skill. Domain-specific class patterns belong in plan-local mapping docs only.

### Property bundles (open per element kind)

Compare the full bundle for each mapped element @ **each declared viewport**. Numeric tolerance **±1px** unless the plan specifies otherwise. Normalize `font-family` (first family in stack must match).

| Element kind | Properties (computed) |
| --- | --- |
| **Text** | `font-family`, `font-size`, `font-weight`, `line-height`, `letter-spacing`, `color`, `text-transform`, `-webkit-font-smoothing`, `text-rendering` |
| **Component** (layout/surface) | `padding`, `margin`, `gap`, `max-width`, `width`, `min-height`, `display`, flex/grid alignment, `text-align`, `background-color`, `border`, `border-radius`, `box-shadow` |
| **Media** | `width`, `height`, `max-width`, `min-height`, `object-fit`, `aspect-ratio` |
| **Media (inline icon)** | Same as Media, plus **rendered identity** vs prod: SVG `fill`/`stroke`, path data or stable outerHTML hash — icons beside mapped Text are **not** optional decoration |

**Text measurement rule (mandatory):** assert on the **Text tier** — innermost text-bearing node. If a wrapper (e.g. `<a>`, button root) and inner text node differ, the **inner node** is the probe target. Wrapper-only passes **do not** count as CSS parity.

**Comparison mode (mandatory):** fetch **both** local and production at the same viewport; diff computed styles on paired key elements. Plan locked targets and foundation docs are **advisory** for ambiguous or inconsistent prod — they never replace live prod diff for Tier A pass.

### Pass / fail

| Outcome | When |
| --- | --- |
| **CSS-fixable** | Mapped elements exist; computed styles differ local vs prod |
| **Structural — fixable** | Role mappable in principle but wrong variant, wrapper layer, spacing model, or CMS flag |
| **Structural — divergent** | No stable role map after inference + plan matching rules |
| **CSS parity 100%** | Zero open **CSS-fixable** diffs on all mapped key elements @ all scoped viewports **and** zero open **visual spacing** supplement failures (see below) |

**CSS parity %:** **100%** only when zero open key-element diffs **and** visual spacing supplements pass for that page **at every scoped viewport and region**. One failed Text/Component/Media bundle property, one failed adjacent text/surface gap, or one failed margin-chain probe @ any viewport → CSS &lt; 100%. **Do not** collapse multi-viewport results into a single URL-level pass without a per-viewport breakdown.

### Mapping completeness (mandatory)

Phase A passes only when **discovery + diff** satisfy all of the following — in addition to property bundles and supplements. These are **general** rules (not page-specific probe IDs):

| Rule | Requirement |
| --- | --- |
| **Per-region spacing** | Discover horizontal/vertical spacing **separately for each page region** (chrome, main content, footer bands, listing bands, etc.). Do **not** apply one padding ladder or locked target from region A to region B. |
| **Effective spacing element** | Diff padding/margin on the **DOM node that actually sets computed inset in production** (often a centering wrapper with explicit zero horizontal padding), not a parent template default or a differently named local wrapper. |
| **Icons in mapped components** | Any visible icon or inline SVG inside a mapped interactive component (links, CTAs, nav controls, card actions) must appear in the map at **Media** tier and be compared to prod @ **each** viewport. Text-only pass on the label does **not** certify the component. |
| **Layout @ every viewport** | Component-tier properties that change geometry (`grid-template-*`, `gap`, band `padding-block`, flex alignment) must be evaluated at **every** declared viewport. A pass at one width **does not** exempt others. |
| **Ordered repeats** | Grids/lists of repeated components require **inventory parity** before CSS gate closes: same **count** and same **stable identity order** (href, slug, or equivalent) as production — order affects layout, not only typography. **Heterogeneous rows** (e.g. label row vs link row vs CTA row in one list) map as **separate component variants** — do not treat every `<li>` as one generic role. |
| **Visual spacing (cross-DOM)** | After property bundles, measure **rendered geometry** between paired key visual anchors @ **each** viewport — see § Visual spacing parity. Wrapper `margin`/`gap` equality alone does **not** close spacing when local and prod DOM trees differ. |
| **Breakpoint thresholds** | When production layout changes at media breakpoints (column count, band height), verify **computed layout at each scoped viewport** against live prod — not inferred from mixin names or from a pass at another width. |
| **Gate reporting** | Report Tier A failures as **region × viewport** (and element role). When scope includes multiple viewports, include a **CSS pass matrix** (URL or region × viewport) in the scoreboard — not only one aggregate “CSS 100%” cell. |

**Anti-patterns (fail Tier A audit):** wrapper-only typography pass while icons differ; spacing probed on parent while prod zeros padding on inner wrapper; **container `gap`/`margin` pass while adjacent text or surface gaps differ**; single-viewport sign-off; assuming identical styles with different repeat order; homogeneous list-item mapping when rows use different classes or DOM; using plan locked targets or foundation constants **instead of** live prod fetch on the paired element; **defaulting to DOM/template changes** before exhausting CSS-only fixes on the existing tree; **adding margin where production only stacked padding** on adjacent wrappers; **selectors that never match** the emitted class/DOM (e.g. static global class names against hashed modules).

**Plan overlays:** Domain plans may add mapping hints (selectors, fixture URLs) — they **extend** this checklist; they do not replace live prod diff or shorten the completeness rules above.

### Visual spacing parity (cross-DOM, mandatory)

Property bundles on **paired same-role nodes** are insufficient when local and production **DOM trees differ** (extra wrapper, different `<li>` class, consolidated block, inline vs block link). Spacing parity is measured on **what the user sees** — text ink, visible borders, and surface edges — not on box boundaries that exist on only one side.

**Pairing rule:** Match anchors by **role + stable text content + order within region**, not identical selectors or node depth. When trees differ, compare **corresponding visual anchors** on both origins (e.g. HQ value text → website link text, not `li` bottom → `p` top unless those boxes bound the same visual gap on both sides).

**Mandatory measurements @ each scoped viewport** (tolerance **±1px** unless plan overrides):

| Anchor pair | What to measure | Typical miss |
| --- | --- | --- |
| **Text → text** (vertical) | Distance from bottom edge of innermost text in row N to top edge of innermost text in row N+1 | List `gap` matches but in-row `line-height` / link margin inflates gap |
| **Text → text** (horizontal) | Gap between adjacent inline labels, values, and links in one row | Flex `gap` on parent only; label/value link spacing wrong |
| **Text → surface edge** | Distance from innermost text to visible background/border of its component (ecru band, card, quote figure) | Padding on wrong wrapper layer |
| **Surface → surface** | Gap between adjacent component backgrounds or border boxes in the same region | Block-boundary margin on wrong sibling |
| **Media ink → text** | Distance from bottom of rendered image/video to top of following text ink | Block `padding-bottom` matches reference wrapper but **inner media layout** omits slack below the asset |
| **Text → border** | Distance from text to decorative rule, avatar ring, or figure border when it defines rhythm | Border on wrapper; text inset not probed |

**Tools:** `getBoundingClientRect()` on local and production at the same viewport width; reference source repo when prod uses quirky margin stacking.

**List / metadata repeats — two probes (both required):**

1. **Row boundary** — box bottom of repeat N → box top of repeat N+1 (grid/flex `gap`, sibling margins).
2. **Row interior** — within each repeat variant, text-to-text gaps between label, value, and action (link, button).

A pass on row boundary does **not** exempt row interior or adjacent-text probes.

**Margin-chain rule:** When production reference or live prod shows `margin` on a wrapper, diff **every descendant** in that subtree that also carries margin in the source (e.g. `<p>` + `<a>` both margined). **Pass requires** matching **effective text-to-text gap**, not wrapper property equality alone.

**Inherited typography:** For Text-tier nodes, record whether `line-height` is explicit or inherited. Probe at **narrowest** scoped viewport first — responsive inheritance often matches at wide desktop only.

**Post-fix regression:** After any spacing fix in a mapped component, re-run adjacent text and surface-gap probes for that component’s repeats — wrapper fixes can leave text-level residuals.

### Vertical rhythm (consolidated prose blocks)

Common on CMS migrations: production wrapped **each** source node in its own padded section; local consolidates many nodes into one prose or rich-text block. Typography tokens may match while **vertical rhythm** still fails — and **Tier B holistic clips** may barely move even after good CSS fixes (merged-block height Δ dominates pixel diff).

**Always separate three layers** — probe each @ every scoped viewport; do not collapse into one “body rhythm” score:

| Layer | What it is | Example probes |
| --- | --- | --- |
| **Block edge** | CMS block wrapper ↔ first/last ink inside rich-text | Block top → first text; last text → block bottom |
| **In-block** | Adjacent elements **inside** one rich-text root | `p→p`, `p→h2`, `h2→p`, `h2→h3`, `p→ul` |
| **Block boundary** | Sibling CMS blocks (prose ↔ media, quote, embed) | Margin/padding on block roots + text-to-text across boundary |

A pass on **in-block** `p + h2` margin does **not** close **block edge** or **block boundary** gaps.

**Derive prod rules from reference source**, not from one computed margin on local:

1. Read reference-repo wrappers and shortcodes — rhythm is often **per-wrapper padding** plus **adjacent-sibling rules** between wrapper types, not one container ladder.
2. Measure **text-to-text** gaps on live prod; back-calculate local spacing so the **ink gap** matches — matching a single wrapper property often fails when prod stacks padding and margin across layers.
3. **Typical miss:** an in-block adjacent rule matches a reference **container** rule but text-to-text still differs because prod stacked bottom padding on the preceding wrapper, top padding on the next, and optional margin between wrapper types.
4. **Media blocks:** reference section padding on figure/embed wrappers is often **symmetric**, but **effective space below the image** can exceed `padding-bottom` when inner wrappers (picture, line-box, grid cell) extend below the bitmap — probe **image bottom → next text ink**, not block-root padding alone.

**Rhythm anti-patterns (fail audit):** classify by **pattern**, not page — domain plans document concrete selectors and values.

| Pattern | Symptom | Prefer |
| --- | --- | --- |
| **Symmetric block padding** | Extra space before first ink or after last ink | Asymmetric or **bottom-only** block padding that mirrors prod’s last wrapper in the sequence |
| **Megablock container padding** | Phantom trailing/leading space after merge | In-block margin ladder + block-edge padding; avoid container rules that simulate per-node wrappers |
| **Double ownership** | First heading or block edge over-spaced | **One owner** per inset (block edge vs page vs in-block adjacent rule) |
| **Global prose defaults on variants** | List markers, row gaps, link styles wrong inside bands/surfaces | Domain variant overrides scoped to surface context |
| **Margin + padding stack on siblings** | Gap larger than prod across block boundary | Identify prod’s **spacing owner** (padding-only vs margin-only vs mixed); zero the layer prod did not use |
| **Generic adjacency beats variant** | Spacing flags / band context ignored | **Pair + variant** rules with higher specificity and later source order than generic adjacent-block rules |
| **Selectors that don’t match DOM** | Rule never applies (hashed modules, wrong attribute) | Match how classes and `data-*` are actually emitted — verify in computed styles, not source alone |
| **In-block rules across block splits** | Short gap when one prod section became two CMS blocks | Boundary-layer rules for first/last ink in the **following** block when content was split |
| **Padding-only match on media blocks** | Image-to-heading/paragraph gap smaller than prod | Measure **media ink → next text** on live prod; trailing space = inner layout slack + block padding |

**Block boundary audit (CMS sibling blocks):**

Do not assume in-block prose rhythm closes **block boundary** gaps. Process:

1. **Enumerate** ordered sibling blocks in CMS content (or DOM `data-block` / section sequence) on fixture pages — every adjacent pair, not only prose-internal adjacency.
2. **Read reference model** for each pair type (and variant flags): which wrapper carried padding, margin, or neither between siblings.
3. **Measure** text-to-text (or surface-to-surface) across each boundary on live prod @ **each** scoped viewport. For **media → prose** pairs, anchor from **rendered media bottom** to following text ink — sibling block margins may be zero while spacing still differs inside the media block.
4. **Implement** in **block-level** stylesheets using pair selectors (block type A + block type B) and variant attributes when spacing depends on CMS flags; do not rely on last-child margin inside prose unless prod used the same layer.
5. **Fixture coverage:** use the plan’s mapping doc / fixture URLs so diverse block types and spacing variants appear in the audit — not a single story.

**Margin model discipline (A2):**

- Prefer **margin-top-only** adjacent pairs inside a single prose root with **zero** default margins on flow elements — mirrors reference “margin only after preceding block type” patterns.
- Set explicit **padding on headings** when reference headings used padding — do not rely on margin alone for heading internal rhythm.
- Reset **first/last child** margins inside prose roots so block-edge padding is not doubled.
- **Block-boundary** spacing lives at the **block adjacency** layer — not inside prose unless reference did the same.

**Prose inside non-prose surfaces** (bands, inset quotes, cards): lists and paragraphs often need **scoped variant overrides** — global rich-text defaults are a frequent CSS-fixable miss unrelated to merge rhythm.

**Tier A vs Tier B for rhythm:**

| Signal | Classification |
| --- | --- |
| Text-to-text / block-edge probes fail; roles map | **CSS-fixable** — fix variant SCSS before Tier C |
| In-block probes pass; **block-boundary** text-to-text fails only across megablock vs many prod wrappers | **Structural — fixable** — migrator split / `mergeProfile`; document gap matrix row |
| Holistic body clip &lt;99% but edge + in-block probes pass | **Structural** height from merge — **do not** keep tuning margins for pixel %; report probe pass separately |
| User accepts visible layout improvement vs prod | **Approved divergence** — record in closure; Tier B may still fail |

**Report rhythm work explicitly:** In scoreboard or migration notes, include a **spacing probe matrix** (edge / in-block / boundary × viewport) — not only Tier B %. A visible rhythm fix that leaves Tier B flat is **success at Tier A supplements**, not a failed fix.

### Supplemental rhythm probes

After key-element diff, run **supplemental** checks where DOM consolidation hides rhythm (local vs prod @ each viewport — still **live**, not constants-only):

| Probe | Typical miss | What to compare |
| --- | --- | --- |
| **Block edge insets** | Only in-block `p + h2` checked | Block top → first text ink; last text ink → block bottom — § Vertical rhythm |
| **Consecutive prose `p + p`** | One Portable Text block vs per-MDX `Paragraph` wrappers | Effective gap between second and first body `<p>` |
| **`p + heading` / `heading + p`** | Only `p + h2` audited | **Text-to-text** gap + computed `margin`/`padding` on heading after paragraph and first `p` after heading |
| **`h2 + h2` / `h2 + h3` stacks** | Only single heading breaks | Text-to-text between stacked section headings inside one megablock |
| **`li + li` row boundary** | List font size only | Box bottom → next box top; list `margin`/`padding`, `gap`, `li + li` margin |
| **Repeat row interior** | Homogeneous `<li>` assumption | Per-variant row: label/value/link **text-to-text** gaps inside each `<li>` or grid cell |
| **Adjacent text gap (cross-DOM)** | Wrapper `gap`/`margin` only | Innermost text bottom → next innermost text top @ each viewport — § Visual spacing parity |
| **Text → surface inset** | Component padding on parent | Text ink → visible background/border edge of mapped component |
| **Margin chain** | Wrapper margin matched | All margined descendants in subtree; effective text-to-text gap |
| **Block boundary gaps** | Only inside rich-text | Margin/padding between **sibling CMS blocks** — § Block boundary audit; include **media ink → text** |
| **Wrapper vs inner** | Spacing on `<p>` while prod uses wrapper padding | Computed gap at the layer production uses **plus** text-to-text gap when trees differ |
| **Per-region padding** | One ladder applied site-wide | Independent horizontal/vertical models per chrome / content / footer band |
| **Icons beside text** | Link label typography only | Media tier on inline SVG/icon in mapped interactive components |
| **Repeat order** | Styles match on sample card | Full grid/list: count + stable identity sequence vs prod |
| **Layout breakpoints** | Pass at primary width only | `grid-template-*`, band padding, column count @ **each** scoped viewport |
| **Quote surface context** | All large quotes get ecru band | Background per quote vs source intent (band vs inline) |
| **Chrome nav inventory** | Assumed prev/next symmetry | Link **text**, **href**, and **count** vs production |
| **DOM / landmark inventory** | CSS on existing nodes only | Interactive elements present, absent, or extra vs production |
| **All declared viewports** | Primary width only | Re-run key-element diff + supplements @ **each** viewport in scope |
| **CMS content present** | Empty route / fixture | Confirm full content renders before scoring |

Cross-check ambiguous prod values against the reference source repo when the plan names one.

**Domain mapping docs (project-local):** When a migration plan lists a mapping spec in **Context references**, use it for block-type → role hints and fixture URLs. This skill defines **methodology and bundles**; plans define **mapping overlays**, not closed property tables. Do not hardcode project paths in this skill.

**Footer Tier B clips:** When visual compare covers a page footer band, capture **both** an **element-scoped clip** (CTA band root) **and** a **regional clip** (footer + adjacent related content). Report both; do not infer footer pass from page-level screenshot alone.

---

## Phase A — CSS parity (do first)

Audit **computed styles** on matching elements local vs production before screenshot-driven visual compare. Fixes most drift at the source (tokens, modules, variant SCSS).

Run **N** compare→fix iterations (default **2**): A1 → A2 → A1 → A2 … then proceed to Phase B (even if CSS &lt; 100% — report in scoreboard).

### A1 — CSS compare (read-only)

- Load **local** and **production** at **each** viewport in scope (default primary **1250px**).
- **Discover and map** key elements (block → component → text + media icons) — infer by default; apply plan/command mapping overlay when provided.
- Satisfy **Mapping completeness (mandatory)** — per-region spacing, effective spacing element, icons, layout @ every viewport, ordered repeats, breakpoint thresholds.
- For **every mapped element**, diff the **property bundle** for its kind (Text / Component / Media) — **live local vs prod** on paired elements @ **each** viewport independently.
- Apply **Text measurement rule:** innermost visible text-bearing node; never accept wrapper-only typography pass.
- Run **visual spacing parity** (cross-DOM) and **supplemental rhythm probes** (above) — mandatory for every mapped region with repeats, metadata lists, CTAs in bands, and quote/testimonial figures.
- Inspect scope per invocation — exclude global site chrome unless scope or plan includes it.
- Tools: Playwright `evaluate` on both origins, browser devtools, reference repo when prod is ambiguous.
- Output: ranked CSS issues (cap ~10 in chat summary; full list in report file when plan requests); each row: block/component/text role, property, local vs prod, **type**, likely fix path.
- Run **original-inconsistency cross-check** when a migration plan names a source repo: compare the same **role** across **≥2 fixture URLs**.
- End with **CSS parity %** per page @ **each scoped viewport** (100% = zero open key-element diffs + supplements pass for that viewport). When multiple viewports: also publish a **CSS pass matrix** (region × viewport).

**Do not** take parity screenshots as the primary A1 deliverable — computed-style diff first. **Do not** use local-only hardcoded expected values as Tier A pass without live prod fetch on the paired element.

### A2 — CSS fix

- Fix **CSS-fixable** issues only (tokens → `pnpm generate:tokens` when JSON changes).
- Do **not** implement workarounds for **Structural** or **Original-inconsistency** issues in A2 unless the plan explicitly authorizes a structural task in this invocation.
- **DOM-preserving fix ladder (mandatory):** Before changing component/block **architecture** (TSX/template structure, wrapper nesting, CMS block splits, migrator merge profiles), exhaust CSS-only options on the **existing** tree:
  1. **Margin / padding / gap** on nodes already present (`margin`, `padding`, `gap`, `line-height`, `min-height`).
  2. **Scoped variant SCSS** on existing module classes (e.g. row-specific modifier) without template edits.
  3. **Compensating margin** (including negative) when extra local box height comes from a class on an existing node — only when it does not break adjacent regions.
  4. **Template / DOM change** in domain component — document why steps 1–3 cannot reach ±1px on visual spacing probes.
  5. **Block / schema / migrator architecture** — plan task; not default A2.
  When prod and local trees differ, prefer step 1–3 to **match visual anchors** (text-to-text, text-to-surface) rather than **match DOM shape**.
  For **vertical rhythm** fixes: apply § Vertical rhythm (margin model discipline, block boundary audit) before megablock splits or migrator changes.
- Re-run key-element diff, **visual spacing supplements**, and applicable rhythm probes on changed areas before the next A1 iteration or Phase B.
- Report updated CSS parity % per page after each iteration.
- After final A2 iteration: publish draft **Structural issues** and **Original inconsistencies** lists (complete after Phase B if visual run happens).

---

## Phase B — Visual parity (after Phase A)

Screenshot-driven compare → fix for holistic layout and anything CSS audit missed.

Run **N** compare→fix iterations (default **2**, same N as Phase A unless user specifies per-phase counts): B1 → B2 → B1 → B2 … then produce scoreboard.

### B1 — Visual compare (read-only)

- Resize to target viewport(s) — default **1250px**; when user names breakpoints (e.g. **1250 / 900 / 320**), run B1 at **each** width before B2.
- Load local and production side by side (or capture both).
- Visual diff + DOM structure; confirm CMS content present (no empty fixture fallbacks unless user scoped that).
- Screenshots → `.tmp/playwright-mcp/` or `.tmp/{{path:browser-tmp}}/` only.
- Output: **≤10 visual issues**, ranked by impact; **type** per issue; likely fix paths.
- For each failing region, note whether residual gap is **CSS-fixable**, **Structural**, or **Original-inconsistency** (use height Δ + A1 classification).
- When body/chrome Tier B is sub-99% but § Vertical rhythm spacing probes pass, report **probe pass** separately — do not imply margins are still wrong.
- End with **visual parity %** per page — **worst viewport** in the set counts for pass/fail vs **≥99%** target.

### B2 — Visual fix

- Implement fixes for **CSS-fixable** (and plan-authorized **Structural**) issues only.
- Apply the **DOM-preserving fix ladder** from A2 before structural DOM or block-architecture changes.
- **Stop B2** on a region when further iterations only move **Original-inconsistency** or **Structural — divergent** items — add to reports instead of tweaking margins.
- **Continue B2** for **Structural — fixable** when plan authorizes domain-scoped component/block work.
- Re-check affected page(s) at target viewport(s).
- Report visual parity % after each iteration (per page, worst viewport).

---

## Parity scoreboard (mandatory end of every invocation)

Always produce after Phase A and Phase B complete (or after `css only` / `visual only`). Update the **plan scoreboard** when a migration plan owns the work.

**Targets:** CSS **100%** @ **every scoped viewport** (zero open key-element diffs + supplements + mapping completeness) · Visual **≥99%** (worst viewport in scope)

```markdown
## Parity scoreboard

**Iterations per phase:** N (default 2) · **Viewports:** e.g. 1250 / 900 / 320

| URL | CSS % (all VPs) | Visual % (worst viewport) | CSS pass | Visual pass | Remaining gaps |
|-----|-----------------|---------------------------|----------|-------------|----------------|
| /example/ | 100 | 99 | ✅ | ✅ | — |

### CSS pass matrix (required when scope has >1 viewport)

| URL / region | @1250 | @900 | @320 |
|--------------|-------|------|------|
| /example/ chrome | ✅ | ✅ | ❌ padding |
| /example/ body | ✅ | ✅ | ✅ |

### Below threshold (required — list every failing URL × viewport × region)

| URL | CSS % | Visual % | Viewport | Region | Gap summary |
|-----|-------|----------|----------|--------|-------------|
| … | 92 | 93 | 320 | chrome | … |

**Targets not met:** CSS 100% on [count] URL(s); visual ≥99% on [count] URL(s) — see table above.

### Invocation log (plans with multiple parity passes)

| Pass | Iterations/phase | CSS fixes (summary) | Visual fixes (summary) | Still below threshold |
|------|------------------|---------------------|------------------------|------------------------|
| 1 | 2 | … | … | URLs … |
```

**Pass columns:** CSS pass = 100% @ **all** scoped viewports (and mapping completeness); Visual pass = ≥99% on worst viewport **or** gap covered by **approved divergence**.

**Never** mark a plan parity task complete while any in-scope URL fails visual **and** the gap is neither fixed nor **approved divergence** / Tier C.

Domain foundation docs may mirror notes; the **plan scoreboard** is the migration SSOT for pass/fail status.

### Structural issues (mandatory when any Structural gaps remain)

```markdown
## Structural issues

| ID | URL / region | Evidence | Subtype | Proposed fix | Scope | Effort | Blocks Tier B? |
|----|--------------|----------|---------|--------------|-------|--------|----------------|
| S1 | /example/ body @1250 | Region height Δ; fewer local blocks than reference wrappers | fixable | Block-root spacing variants / in-block rhythm | domain | M | yes |
```

- **Subtype:** `fixable` (domain component/block/layout) · `divergent` (needs global scope or Tier D)
- **Scope:** `domain` · `global` — **global → escalate; do not implement in parity invocation**
- **Effort:** S (&lt;1 implementation spawn) · M (1 spawn) · L (plan task / schema+migrator)
- **Blocks Tier B:** yes = do not spend more B2 on margin-chasing until fixable path implemented or user accepts divergence

When **Subtype = fixable** for most of a region’s gap, **Recommended next steps** must **not** say stop pixel-chasing for that region — say **plan task / fix slice** with gap matrix reference instead.

### Original inconsistencies (mandatory when detected)

```markdown
## Original inconsistencies

| ID | Pattern | Prod varies how | Target rule | Recommended new-site rule |
|----|---------|-----------------|-------------|---------------------------|
| O1 | Prose link underline | Underline differs across fixture URLs | plan locked / foundation | one consistent rule |

### Approved divergence (requires user / plan — not agent alone)

| ID | Scope | New site behavior | Prod behavior we intentionally differ from |
|----|-------|-------------------|---------------------------------------------|
| O1 | story prose links | no underline | inconsistent prod underlines |
```

Agents **propose** approved divergence rows; **only the user or plan** marks them accepted (Tier C / parity-policy allowlist).

### Recommended next steps (mandatory end of invocation)

```markdown
## Recommended next steps

1. **Fix now** — CSS-fixable + **Structural — fixable** (domain scope) items still open — **including failed key-element diffs** and **failed visual spacing supplements** (adjacent text, text-to-surface, margin-chain) — prefer **DOM-preserving ladder** before template/block changes
2. **Plan task** — gap matrix rows needing analysis or implementation beyond one small task (S1, …), split by `create-plan` — **not** open key-element CSS diffs (those belong in (1))
3. **Approve divergence** — **Structural — divergent** or original-inconsistency only after (1)–(2) exhausted **and** key-element CSS parity passes for that region — user confirms. **Do not** Tier C open CSS diffs
4. **Re-run parity** — after (2) or (3), which URLs/regions only; include **spacing probe matrix** when rhythm was the focus
5. **Escalate global scope** — any fix touching shared theme / `components/ui/` / site-wide tokens — user before implement
```

Say **stop pixel-chasing** only when gaps are **Structural — divergent** or **Original-inconsistency** with no fixable path — not when **Structural — fixable** gap matrix rows remain or **key-element CSS diffs** still fail (**mis-bucketing as Tier C is an anti-pattern**).

---

## Full loop (one invocation)

```
Phase A: (A1 → A2) × N iterations   // default N = 2; classify every gap
Phase B: (B1 → B2) × N iterations   // default N = 2; CSS-fixable + authorized structural only
→ Parity scoreboard
→ Structural issues + Original inconsistencies
→ Recommended next steps
→ Below threshold (exclude approved divergence)
```

**Migration plan handoff:** supervisor uses **Recommended next steps** to extend the plan (gap analysis / fix slices) or close with **approved divergence** — user only when plan § escalation triggers (Tier D, global scope, ties).

Respect plan § **Autonomy & authorization** — do not pause for routine verify/fix loops.

When multiple pages: finish **Phase A→B on one page** (or one coherent scope) before the next unless user requests batch CSS-only across routes.

## Subagent routing

One coherent chunk per spawn (~15min). **Do not bundle multiple full invocations in one subagent.**

| Step | Subagent |
| --- | --- |
| A1 CSS compare + inconsistency cross-check | `playwright` or `standard` |
| A2 CSS fix | `standard` |
| B1 Visual compare | `playwright` (prefer headless script) |
| B2 Visual fix | `standard` |
| Structural report synthesis | supervisor or `standard` read-only |

Supervisor relays **product choices** (approved divergence, plan extension) to the user — agents propose, user accepts.

## Core-marketing page order

When scope is “core-marketing” without a single route, process in order (full **A→B** per route before next):

1. `/` 2. `/pricing/` 3. `/schedule-demo/` 4. `/file-infrastructure-platform/` 5. `/api/` 6. `/partners/` 7. `/migrate-from-filestack/` 8. `/discover/file-uploader/` 9. `/uploader1/` 10. `/404`

Then **nav + footer** as a separate invocation if requested.

## Deliverables

- **Chat (mandatory):** parity scoreboard · structural issues · original inconsistencies (or “none detected”) · recommended next steps · below threshold · explicit **targets not met** line when any in-scope URL fails and is not approved divergence.
- **Per page:** CSS % @ each scoped viewport + aggregate; visual % (worst viewport); pass/fail vs 100% / 99% or approved divergence.
- **Optional file:** migration plans may ask for `.tmp/<tool>/<slug>/parity-report.md` mirroring the chat sections.
- **Temp artifacts:** screenshots under `.tmp/<tool>/` only.

## Invocation examples

```
/improve-parity /customers/gempages/ — 1250/900/320, 5 rounds
```

```
/improve-parity homepage after styling refactor
```

```
/improve-parity core-marketing — 3 rounds per phase
```

```
/improve-parity /pricing/ — visual only, 2 rounds
```

```
/improve-parity /customers/ css only
```

```
/improve-parity /api/ and /partners/
```

(`N rounds` = N compare→fix iterations in each phase; default **2** if omitted.)

## Related

- Plan shape (autonomy, scope, retros): `{{path:skills}}/create-plan/SKILL.md`
- Browser tooling: `debug-in-browser` skill
- **Project-local:** migration plans may supply fixture URLs, viewports, block-type → role mapping hints, and parity reports — follow plan **Context references** when present (not paths hardcoded in this skill)
