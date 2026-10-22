---
name: commit
description: >-
  Proposes then creates git commits from uncommitted changes using conventional
  commits with short subject-only messages. Always present commit proposal(s) in
  chat and wait for explicit approval (go/yescommit) before staging or
  committing — never commit on continue/ok alone or in the same turn as analysis.
  Default: one commit per feature or initiative. Use when the user asks to
  commit, run commit, or create commits. Analysis and git commands are delegated per
  the base rule; the supervisor presents the proposal and gates approval.
invocation: explicit
---

# Commit

Create git commit(s) from uncommitted changes unless the user narrows scope (e.g. "only server", "except docs", "skip web", "split commits").

**Always propose before committing.** After delegated analysis, present the planned commit(s) in your **user-visible reply**, then **stop and wait for user approval** — do not `git add` or `git commit` until the user confirms with an **explicit approval phrase** (see below) or adjusts the proposal.

## Delegation (mandatory)

Per the **base** rule, the **supervisor** does not run git commands or read repo diffs in the main thread for commit work.

| Phase | Who | What |
| --- | --- | --- |
| Analysis (Turn A) | `junior` subagent | `git status`, diffs, recent log, capability clustering, secrets screening on paths to stage, mixed-file / `git add -p` notes; return structured input for the proposal block |
| Proposal (Turn A) | Supervisor | Format **Commit proposal** in chat from the subagent report; end turn without staging or committing |
| Execute (Turn B+) | `junior` subagent | After explicit user approval, stage and `git commit` per the approved plan (including patch staging when the proposal says so); report SHAs and remaining `git status` |

Spawn the analysis subagent in the **same turn** as `/commit` or a commit request. Include user scope exclusions and this skill's sections from **Scope analysis** through **Mixed-initiative files** in the subagent prompt.

The supervisor may tighten wording in the proposal but must not invent clusters, paths, or messages without subagent evidence. If analysis is incomplete, re-spawn `junior` before showing a proposal.

### Approval gate (hard)

1. **Proposal must land in chat** — running `git status` / `git diff` in tools is not enough. The user must see the full **Commit proposal** block (message, includes, excludes) in an assistant message **before** any `git add` or `git commit`.
2. **No commit in the analysis turn** — on `commit` or "commit changes", the first reply is **proposal only** (plus tool analysis if needed). Do not stage or commit in that same turn, even if analysis finished.
3. **No proposal yet → no commit** — if the prior turn only ran git commands or was cut off before the proposal block, the next user message does **not** auto-approve. Present (or re-present) the proposal and wait again.

### What counts as approval

**Counts** (commit only after these, in a turn **after** the proposal was shown):

- `go`, `yes`, `commit`, `commit it`, `do it`, `approved`
- `commit as proposed`, `use that message`, `as proposed`
- Same turn as proposal **only if** the user message already contains approval **and** a concrete message or clear reference to your proposal (e.g. `commit with message \`feat(x): …\``)

**Does not count** (treat as "still waiting" — show or repeat proposal):

- `continue`, `proceed`, `ok`, `sure`, `next`, `carry on`, `finish`, `done`
- Any reply that only continues the thread without referencing the proposed message or saying commit/go/yes
- Follow-ups after analysis-only turns (user said continue because the proposal never appeared)

Exception without prior proposal: user gives a **full commit subject** in the request itself (e.g. `commit with message \`feat(shell): …\``) — then analyze, show a one-line confirmation of that message and files, and still wait for explicit `go` unless they also said commit/go in the same message.

## Default: one commit per initiative

**After clustering** (below), merge only clusters that share **one user-visible capability** or **one reviewable story**:

- Server + API + client + e2e + product docs for the **same feature** → **one commit**
- Tests and docs are **part of the scope**, not separate commits (do not use `test(e2e): …` alone when the tests belong to the feature just shipped)
- Message names the **capability or theme**, not each layer

**Do not** treat “everything in this branch / session / repo” as one initiative. Distinct capabilities (e.g. nav vs inventory stock vs auth) → **separate commits** even when touched together.

Example (one commit for a cross-stack feature):

```
feat(shell): context-defined features gating nav and paths
```

That single commit naturally includes: feature resolver on server, session context API, client store, nav refactor, path guard, http-api / app-description updates, and e2e specs.

### When to split into multiple commits

Split **only** when:

| Situation | Action |
|-----------|--------|
| **Unrelated** changes in the same working tree (two independent features, drive-by fix + feature) | One commit per unrelated initiative |
| **Clustering** finds multiple independent capabilities (nav, domain module, auth, platform) | One commit per cluster |
| User explicitly asks ("split commits", "separate server commit", "only commit X") | Follow user |
| One change is huge and **independently reviewable** with no shared story (rare) | Split at clear boundaries |

**Split heuristic:** If the subject would read like `feat(x): A, B, and C` where A/B/C are unrelated user-facing capabilities → **default to split**, not one commit.

**Do not** split by default along server → client → e2e → docs just because layers differ. Layer order is for **planning**, not for commit granularity.

### When to keep one commit

| Situation | Action |
|-----------|--------|
| End-to-end feature (resolver, API, UI, guard, tests) | **One commit** |
| Bug fix + regression test | **One commit** |
| Refactor + updated callers + adjusted tests | **One commit** |
| Minor typo/formatting with the feature you just built | Bundle in same commit |

## Message format

- **Conventional commits**: `type(scope): summary`
- **Subject only** — no body, no footer, no description block
- **Short, outcome-oriented summary** — describe what the user/system gains, not a file list
- `scope` = feature area (`shell`, `billing`, `session`, …), not `server` / `web` / `e2e` unless the change is truly single-layer
- Minor bundled tweaks: omit from message or brief comma tail (e.g. `fix(units): owner invite flow, typo in label`)

### Types

| Type | Use for |
|------|---------|
| `feat` | New behavior or capability |
| `fix` | Bug fix |
| `refactor` | Behavior-preserving restructure |
| `docs` | Documentation **only** (no code/test changes) |
| `test` | Tests **only** (no production code — rare; prefer bundling with feat/fix) |
| `chore` | Tooling, deps, config, migrations scripts |
| `style` | Formatting-only (no logic change) |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |
| `build` | Build system changes |

Pick one primary `type` per commit.

## Scope analysis

The **analysis subagent** runs before any proposal (supervisor does not substitute its own diff read):

```bash
git status
git diff
git diff --staged
git log -5 --oneline
```

Run `status`, `diff`, and `log` in parallel when possible. Return cluster list, planned commit count, subject line(s), includes/excludes, warnings, and notes for the supervisor.

### Step 1 — Cluster changes (mandatory)

Group files/hunks by **capability**, not by repo layer or “field app” umbrella. Use path prefixes and diff themes:

| Signal | Example clusters |
|--------|------------------|
| Path / module | `nav/`, shell (`App.vue`, drawer), settings routes |
| Domain | `stock/`, inventory, warehouse, offline store |
| Cross-cutting infra | shared event listener, auth session |
| Platform | `mobile/`, capacitor, build docs |

List clusters in the **commit proposal** before deciding bundle vs split.

### Step 2 — Decide bundle vs split

1. **One cluster, one story** → **one commit** (stage everything for that cluster, except exclusions / secrets)
2. **Multiple unrelated clusters** → one commit each, in **dependency order** (shared lib → consumers; schema → domain → UI)
3. **Tie-breaker:** clusters that do not share files or a single user journey → **split**, even in the same session

**Anti-pattern:** one vague commit because changes “feel related” or landed in one chat — if clustering shows nav + stock + auth, propose multiple commits.

## Proposal (required before commit)

After analysis, present a **commit proposal** to the user. Do not stage or commit yet.

### Single commit — use this shape

```markdown
## Commit proposal

**Plan:** 1 commit (one initiative)

**Message:** `feat(shell): context-defined features gating nav and paths`

**Includes:**
- `server/...` — session context API
- `web/...` — nav + path guard
- `docs/...` — app description
- `e2e/...` — feature specs

**Excludes:** (none | list paths left unstaged per user request)

**Warnings:** (`none` | items that block or endanger the commit, e.g. `.env` detected — will not stage)

**Notes:** (`none` | key non-blocking context, max 3 one-line bullets)

Reply **go** to commit, or suggest changes (message, scope, split).
```

### Multiple commits — numbered list

For each planned commit: **message**, **paths / summary**, brief **why separate**, and **commit order** when later commits depend on earlier ones (e.g. shared widget before views that import it).

### Proposal rules

- Show the exact **subject line(s)** the user will see in `git log`
- When the workspace or project contains multiple repositories, group every proposed commit under a heading naming its repository, even when only one repository has proposed changes. Keep commits for the same repository together, and identify each commit within that group. When there is only one repository, keep the proposal format above.
- List **paths or areas** included — not a raw dump of every hunk unless the diff is tiny
- Call out **exclusions**, **secrets**, and **split rationale**
- **Warnings** lists only things that block or endanger the commit and need the reader's action or decision: secrets detected and excluded, secrets check not run, risky deletions, files that need isolation. When there are none, write exactly `none`
- **Notes** lists non-blocking context the reader may want (e.g. diff not reviewed line by line, no test suite covers the change, alternative split considered). Key notes only: at most 3 short bullets, one line each. Omit trivia, restated diff content and clean-check results (e.g. "no secrets found"). When there are none, write `none`
- **Secrets screening must be executed** before the proposal is presented: check the paths to be staged for secret-like names (`.env`, keys, credentials) and run a quick content scan for tokens. Never relay a subagent's or a skim's claim of "no secrets" as a verified result. If the check was not run, list that under Warnings
- Keep it scannable; one screenful when possible

## Workflow

```
Turn A (commit):
  1. Spawn junior — scope analysis, clustering, secrets screen (mandatory)
  2. Plan one commit per unrelated cluster; merge only clusters that share one story
  3. Supervisor presents commit proposal(s) in chat → END TURN (no git add / git commit)

Turn B (user approves):
  4. Verify proposal was shown in a prior assistant message
  5. Verify user used an explicit approval phrase (not "continue" alone)
  6. Spawn junior — stage files (or git add -p per split) and commit with HEREDOC subject
  7. Repeat 6 only if a second unrelated initiative remains in the approved plan
  8. Supervisor reports: commit SHAs, subjects, anything left uncommitted
```

## Staging

**Default**: stage **all** files for the current initiative — tracked modifications and **untracked** files included.

**Respect user exclusions**: skip paths the user named, or commit only what they named.

**Never stage** likely secrets (`.env`, credentials, keys). Warn if present.

## Mixed-initiative files

Rare — only when one file contains hunks for **unrelated** commits:

1. Prefer `git add -p` when hunks align cleanly
2. Otherwise use `git stash push -- <paths>` / `git stash pop` to isolate scopes when splitting unrelated changes
3. Do not split a file across layer-based commits when it belongs to one feature

## Git safety

- **Never** update git config
- **Never** `--no-verify` / skip hooks unless the user explicitly asks
- **Never** force-push, hard reset, or other destructive ops
- **Avoid** `commit --amend` unless the user asked **and** the last commit is yours and unpushed
- If a hook fails: fix the issue, then create a **new** commit (do not amend a failed commit)

## Commit command

Always pass the message via HEREDOC — subject line only:

```bash
git add <paths>
git commit -m "$(cat <<'EOF'
feat(shell): context-defined features gating nav and paths
EOF
)"
```

## Examples

**Default — one cross-stack feature**:

```
feat(shell): context-defined features gating nav and paths
```

(server resolver, session API, client store, nav, guard, docs, e2e — all in one commit)

**Unrelated work in same tree — split**:

```
1. feat(shell): context-defined features gating nav and paths
2. fix(auth): session cookie SameSite on staging
```

**User narrowed scope**:

User: "commit, but not docs" → commit all non-`docs/` changes; leave docs unstaged.

User: "split commits" → split at clear initiative boundaries (not per layer by default).

## Checklist

- [ ] Analysis delegated to `junior`; clusters listed in proposal
- [ ] Subagent ran full diff (`status`, `diff`, recent `log`)
- [ ] **Commit proposal block sent in chat** (not only in tool output), with Warnings (blocking only) and Notes (max 3 bullets) separated
- [ ] **No `git add` / `git commit` in the same turn as first `commit`**
- [ ] User used an **explicit approval phrase** (not `continue` / `ok` / `proceed` alone)
- [ ] **Proposal presented and user approved** before any `git commit`
- [ ] All intended changes committed (none left unstaged unless excluded)
- [ ] Default applied: one commit per initiative unless split was justified
- [ ] Tests/docs bundled with their feature when part of the same story
- [ ] Messages are conventional, subject-only, outcome-oriented
- [ ] No secrets committed
- [ ] `git status` clean (or only intentionally excluded paths remain)
