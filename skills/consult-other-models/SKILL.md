---
name: consult-other-models
description: >-
  Sequential two-model consultation: delegate review to gpt, then claude subagents,
  synthesize agreements and conflicts, update plans or docs when requested.
  Use when the user invokes /consult-other-models, asks to consult GPT/Claude,
  harden a spec/plan with other LLMs, or get a second opinion before implementation.
disable-model-invocation: true
---

# Consult other models

Run a **structured, sequential** review with fixed subagents before committing to a plan, spec, or major decision. The main thread supervises; reviewers run in background subagents.

## Fixed reviewers (do not substitute)

| Order | Subagent | Model | Role |
|-------|----------|-------|------|
| 1 | `gpt` | Highest GPT Sol model, high reasoning | First critique — assumptions, gaps, concrete recommendations |
| 2 | `claude` | Highest Opus model, high effort | Second pass — **simplicity check on round 1**, verdicts, PO items |

**Always sequential** (gpt → wait → claude). Never spawn these reviewers in parallel.

Round 2 must **challenge over-engineering** from round 1, not only add more hardening.

## When to use

- Hardening product requirements, architecture, or implementation plans
- Pre-implementation review of docs in `docs/`, `.context/`, or `.local/` plans
- User says: consult GPT/Claude, second opinion, multi-model review, `/consult-other-models`

**Not for:** choosing between two options the user already understands — ask directly or use a single reviewer.

## Scope gate (mandatory)

Before spawning subagents, scope must be clear. If missing, **ask once** covering:

| # | Field | Example |
|---|--------|---------|
| 1 | **Subject** | `docs/product/solution.md` |
| 2 | **Goal** | Ship v1 / find gaps / compare options |
| 3 | **Product stance** | “Friction layer, not security boundary” / “Internal tool, low threat” |
| 4 | **Pragmatism tier** | `v1-ship` · `production` · `high-security` (default **`v1-ship`** if unstated) |
| 5 | **Locked** | Decisions reviewers must not overturn |
| 6 | **Deliverable** | **Report + PO sign-off** (default) — not auto-merge all suggestions |
| 7 | **Open questions** | Specific items to resolve (optional) |

**Do not** start round 1 without product stance + pragmatism tier (infer from conversation or ask).

### Pragmatism tiers (tell reviewers explicitly)

| Tier | Reviewer bias |
|------|----------------|
| **v1-ship** | Prefer minimal APIs, defer crypto/ops hardening unless gap blocks shipping |
| **production** | Balance correctness and hardening; flag security without gold-plating |
| **high-security** | Full threat modeling; hardened options expected |

## Consultation process

### Phase 0 — Prepare (main thread)

Build a **consultation brief** for subagent prompts:

```markdown
## Product stance
{one paragraph — what the product is NOT}

## Pragmatism tier
v1-ship | production | high-security

## Locked (do not overturn)
- …

## In scope / out of scope for this review
- In: …
- Out: new features, full threat model rewrite, …

## Open questions for reviewers
- …
```

Include artifact paths. **Default deliverable:** structured report + PO sign-off list — **not** “merge everything into docs.”

### Phase 1 — GPT review

Request structured markdown with **tiered recommendations**:

1. Assumptions validation (sound vs risky **for stated product stance**)
2. Gaps that **block implementation** vs nice-to-have
3. Critique of current proposal
4. For each major recommendation, use:
   - **Tier:** `must-fix` | `should-fix` | `optional` | `overkill-for-tier`
   - **Minimal (v1)** vs **Hardened** option when security/architecture is involved
5. Top 5 **must-fix** only (ranked)

Explicit instruction in prompt:

> Do not recommend encryption, HMAC, key management, or new packages unless the gap cannot be closed at the stated pragmatism tier. Label speculative hardening `overkill-for-tier`.

### Phase 2 — Claude review

Include GPT summary. Request:

1. Per GPT item: **AGREE / DISAGREE / MODIFY** + rationale
2. **Over-engineering audit:** list GPT items to **reject** or **defer** for v1-ship
3. **Minimal viable spec** snippets (not maximal hardened spec)
4. **PO sign-off** items only — not a full rewrite

Explicit instruction:

> Your job includes pushing back on round 1 security/crypto complexity when product stance is friction/telemetry. Prefer the smallest change that closes real gaps.

### Phase 3 — Synthesize (main thread)

1. **Cross-review table:** topic | GPT | Claude | **resolution** | **accepted?**
2. **Accepted** — merge into docs only after user confirms (or deliverable said “update docs”)
3. **Rejected / deferred** table
4. **PO sign-off** — only items that need human choice; offer **2–3 options** with tradeoffs
5. Tell user: what was **kept**, **reverted**, **deferred to v2**

**Do not** bulk-merge reviewer output into `solution.md` before PO answers.

### Phase 4 — Optional follow-up

Only for: locked-constraint conflict, narrow topic, or user request (e.g. send `gpt` Claude's disputes on its items for a rebuttal). Skip if PO list is empty and rejected table is clear.

## Subagent prompt template

```markdown
You are reviewer {N} of 2 for: {title}

## Product stance
{…}

## Pragmatism tier
{v1-ship | production | high-security}

## Locked
{bullets}

## Artifacts
{paths}

## Prior review (round 2: GPT)
{summaries with tier labels}

## Output rules
- Tag each recommendation: must-fix | should-fix | optional | overkill-for-tier
- For security/crypto: always give Minimal (v1) AND Hardened options
- Do not expand scope beyond artifacts unless gap is blocking

## Your task
{phase-specific sections}
```

## Output artifacts

| Artifact | When |
|----------|------|
| `review-consensus.md` | Cross-review + **rejected/deferred** + PO items |
| Primary spec | **After PO sign-off** — accepted items only |
| Report in chat | Always |

## Lessons (from practice)

Consultation adds value on **gaps, a11y, honest threat models, and ambiguous aggregation** — but reviewers **over-index on security best practices** when the product is not a security boundary.

| Tendency | Mitigation in this skill |
|----------|---------------------------|
| HMAC, encryption, key rotation | Require minimal vs hardened options; default v1-ship |
| New packages, schema columns, purge jobs | Tag `optional`; PO defers |
| Replacing simple flows (threshold on submit → server config → token bind) | PO sign-off with options, not auto-merge |
| Round 2 agrees with round 1 hardening | Claude explicitly audits for over-engineering |
| Synthesis merges everything | **Rejected/deferred** table + no doc merge before PO |

**Cannot fully avoid** clarification rounds — reviewers lack your risk tolerance until the brief states it. **Can reduce** noise by: pragmatism tier, tiered recommendations, rejected table, default report-only deliverable.

## Anti-patterns

| Avoid | Do instead |
|-------|------------|
| Parallel gpt + claude | Sequential |
| Auto-merge all suggestions into docs | PO sign-off first |
| “Harden the spec” without product stance | Brief includes stance + tier |
| Round 2 only adds complexity | Claude audits round 1 for overkill |
| Single “recommended” crypto option | Minimal + hardened + overkill label |
| Re-litigating rejected items | **Rejected/deferred** table in consensus |

## Checklist

- [ ] Product stance + pragmatism tier in brief
- [ ] Locked decisions listed
- [ ] GPT round: tiered recommendations
- [ ] Claude round: over-engineering audit
- [ ] Cross-review + **rejected/deferred** + PO items
- [ ] Docs updated only for **accepted** items (unless user pre-approved merge)
- [ ] User told: kept / reverted / deferred / need another round?
