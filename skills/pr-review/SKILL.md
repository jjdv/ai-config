---
name: pr-review
description: Review GitHub pull requests in the repo's review style and process, including temporary stash handling and restore.
invocation: explicit
---

# PR Review (Manual)

Tool-heavy steps (repo lookup, git, `gh`, diff reading) run as delegated execution per the base rule (Harness skill workflows); the main thread only gates, asks the user and relays.

## Purpose

Review a GitHub PR, draft comments in the repo's review style, and show proposed comments first.
Do not submit anything to GitHub unless the user explicitly asks.

## Required Input

- PR URL (for example `https://github.com/<owner>/<repo>/pull/<number>`)

## Workflow

1. **Validate repo is available in current codebase**
2. **Prepare local PR review context (stash + checkout)**
3. **Review with checklist + comment style rules** (includes **§3.G clean code / micro-refactor** pass when the diff touches implementation)
4. **Draft proposed comments and show to user**
5. **Iterate with user corrections**
6. **Submit review comments only on explicit user instruction**
7. **Restore previous branch and clean temporary stash (if created)**

---

## 1) Validate Repo In Current Codebase

Parse PR metadata first (use fields your `gh` version exposes; `repository` may be unavailable — prefer `headRepository`):

```bash
PR_URL="<paste-pr-url>"
REPO_NAME=$(gh pr view "$PR_URL" --json headRepository --jq '.headRepository.name')
```

Then verify the repository exists in current workspace/codebase context.

- If no local repository matches `REPO_NAME`, report:
  - that the PR repo is not in the current codebase,
  - that review cannot proceed safely,
  - and exit.

When found, switch to that repository root before continuing.

---

## 2) Prepare Local PR Review Context (Stash + Checkout)

Goal: avoid mixing local WIP with PR review context and review against the PR branch code.

1. Capture current git context to restore later:

```bash
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
ORIGINAL_HEAD=$(git rev-parse HEAD)
```

2. Read PR changed files:

```bash
gh pr view "$PR_URL" --json files --jq '.files[].path'
```

3. Read local modified/untracked files:

```bash
git status --porcelain
```

4. Ask the user before any stash or checkout: state which local files will be stashed (or that nothing will be), and which PR branch will be checked out. Proceed only on an explicit yes; on no, stop.

5. If any local changed file overlaps PR-changed files, stash them:

```bash
git stash push -u -m "tmp: temporary stash for PR review (<owner>/<repo>#<number>)"
```

6. If there is no overlap, do not stash.

7. Check out the PR branch:

```bash
gh pr checkout "$PR_URL"
```

8. Verify local HEAD matches PR head SHA:

```bash
PR_HEAD_SHA=$(gh pr view "$PR_URL" --json headRefOid --jq '.headRefOid')
test "$(git rev-parse HEAD)" = "$PR_HEAD_SHA"
```

9. Track whether stash was created and store original branch/HEAD for the restore in §7.

---

## 3) Review Rules (Checklist + Style)

If `.agents/skills/project-best-practices/references/pr-review.md` exists in the reviewed repo, read it and apply its checklist and comment style; it overrides the defaults below.

Default checklist (when no project reference exists):

- [ ] Single source of truth, encapsulation, logic and style placed in the correct owner (architecture and ownership).
- [ ] Clear short names, minimal interfaces, no redundant fields, no unnecessary casts (API and type design).
- [ ] KISS: no unnecessary abstractions or unused flexibility; reuse existing primitives (simplicity).
- [ ] Styling defined in the component that owns it (component boundaries).
- [ ] Questionable UX choices raised as targeted questions; defaults applied at the correct boundary (behavior and integration).
- [ ] Earlier mistaken feedback corrected in-thread; comments actionable and tied to concrete code locations (consistency and accuracy).

### G. Clean Code and Micro-Refactors

Run this **after** architecture/API/behaviour; use for **readability, DRY, and local consistency** without expanding scope. Match the usual **1–2 sentence** comment style unless the suggestion needs a one-line code sample.

**Selectors and DOM**

- [ ] Prefer **one** `:not(...)` with a **selector list** (Selectors Level 4) instead of chaining many `:not()` when semantics match and the project’s browser support allows it.
- [ ] Flag **fragile** selectors (overly long chains, duplicated fragments); suggest extracting a **named constant** or helper that builds the selector.
- [ ] Prefer **`data-*` or `data-role`** hooks that already exist over deep positional selectors when suggesting changes.

**TypeScript / logic**

- [ ] Question **`!` non-null assertions** after `querySelector` — suggest early return, guard, or `throw` with context if failure is possible.
- [ ] Flag **`catch {}` without binding** when logging or user-visible error state might help; at least consider rethrow or a narrow typed error.
- [ ] Spot **duplicated** success/error UI branches (same lines in `if` and `catch`) — suggest a tiny local helper.
- [ ] Replace **magic literals** (thresholds, timeouts, weights) with **named constants** or values **derived from existing config** when it clarifies intent.

**Structure and coupling**

- [ ] Note **circular imports** and **god-function** blocks that could be split (still file under architecture if large; here flag only if the fix is small).
- [ ] Large **`innerHTML`** templates: optional note — DOM builders or fragments **if** maintainability is suffering (don’t mandate refactors for small templates).

**Docs parity**

- [ ] If clean-up touches public behaviour, **one line** reminding to sync README/types (avoid duplicating a full docs review).

When producing the draft artifact, you may add a **`### Clean code / micro-refactors`** (or **`### Nits`**) subsection so the author can batch-triage low-risk edits.

---

## 4) Comment Style Rules

Follow the project reference style when present. Defaults:

- Concise, direct, constructive, non-hostile; default one to two sentences per comment, a short question when it fits better.
- Reference the exact symbol or file intent and offer a concrete alternative; one issue per comment.
- When the user clarifies design intent in-thread, fold it into the next draft as a single factual suggestion.
- Do not add praise sections unless the user explicitly asks.

---

## 5) Draft Proposed Comments (Do Not Submit)

Produce a draft review artifact and show it to the user in chat.

**Preferred format** (adapt priority headings to the PR; omit empty sections):

```markdown
## Proposed PR Review for <owner>/<repo>#<number>

### High priority
- [path:line] Comment text...

### Medium priority
- [path:line] Comment text...

### Questions
- [path:line] Question text...

### Clean code / micro-refactors (optional)
- [path:line] Comment text...
```

For **final review handoff** after iteration, a **flat list** grouped by file (with short comments only) is acceptable — match whatever structure the user asked for in-session. When §3.G applies, include **nits** in the draft (subsection or inline with file headers).

Rules:
- Do not call `gh pr review` or submit via API in this phase unless the user explicitly moves to the submission gate (§7).
- Keep comment count focused; prefer highest-impact findings.
- Iterate on wording with the user until they confirm submission.
- For each proposed comment, include code context from the referenced change when helpful:
  - Prefer a short snippet (about 3-15 lines) showing the exact code/hunk the comment refers to.
  - Label each proposal with file and line reference.
  - If snippet retrieval is not possible, still provide precise references (file path + line number/range + symbol/function name when available).
- **Cross-cutting behaviour:** when a change touches multiple layers (e.g. modal + timing check), call out **integration checks** explicitly if the same file isn’t the whole story (name every file the reviewer should consider).

---

## 6) User Iteration Loop

After showing drafts:

1. Ask for changes ("keep", "drop", "reword", "add").
2. Update the proposed set.
3. Repeat until user explicitly confirms submission.

---

## 7) Submission Gate (Only After Explicit Ask)

Only when user clearly says to submit/push review comments:

1. Reconfirm target PR.
2. Submit agreed comments using one of the approaches below.
3. Report what was submitted (count + links).
4. Ask the user before restoring: state the branch to return to and, if a stash was created, that it will be popped. Proceed only on an explicit yes.
5. Return to the original branch captured in §2:
   - `git checkout "$ORIGINAL_BRANCH"` (or restore by `ORIGINAL_HEAD` if branch no longer resolves).
6. If this run created a temporary stash in §2, restore it and clean it up:
   - Prefer `git stash pop` for the tracked stash entry.
   - If conflicts occur, stop and report conflict details to the user.
   - Ensure the temporary stash entry created for this review is not left behind.

Never submit automatically.
Never approve or request changes from this skill.

### GitHub “draft” / pending reviews vs `gh pr review`

- **`gh pr review --comment -b "..."`** submits a **finished** review (review event `COMMENT`). It is **not** a GitHub **pending** review draft and does **not** support a `--draft` flag.
- **Line-level (inline) comments** are separate: use **`gh api`** to create pull request review comments on a commit (or paste into the web UI). See `gh help api` and [REST: create a review comment](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request).
- **Pending batch reviews** (start a review, add many inline comments, then submit once) are a **web UI** workflow; the REST API also supports creating a review without submitting immediately — `gh` does not wrap that ergonomically. If the user needs true draft/pending behaviour, prefer the **GitHub web UI** or document the exact `gh api` sequence.
- Do not confuse with **Draft PR**: that marks the whole pull request as draft, not the review state.

---

## Operational Notes

- Restore context in this order: submit comments -> return to original branch -> pop temporary stash.
- If gh access fails, report the exact blocking command and stop.
- Keep review reproducible: cite PR URL, commit SHA, and changed files scope in analysis notes.
