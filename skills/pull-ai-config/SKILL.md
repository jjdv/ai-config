---
name: pull-ai-config
description: >-
  Pulls latest origin/main into the local ai-config clone (stash WIP, rebase, restore stash
  with conflict care, drop stash), then runs /merge-ai-config. Direct invocation only —
  /pull-ai-config.
disable-model-invocation: true
---

# pull-ai-config

Update the **ai-config** clone from `origin/main`, then sync both Claude Code and Cursor via **`/merge-ai-config`**. Works from either tool, from any workspace. Never pushes; never touches other repos.

## Repo root

First match wins: (1) workspace contains `skills/merge-ai-config/` and `lib/ai_sync.py`; (2) `~/.ai-config/repo-path`; (3) ask. Rewrite `repo-path` when resolved from the workspace. Never write `~/.ai-config/` into the repo.

## Procedure

Run git in the repo root.

1. **Fetch** — `git fetch origin`. If the current branch is not `main`, report it and **ask**; do not switch or rebase another branch.
2. **Stash** — if the tree is dirty: `git stash push -u -m "pull-ai-config: <iso-timestamp>"`; record it. If clean, skip stash steps.
3. **Rebase** — `git rebase origin/main`. Preserve both remote and local intent on overlapping hunks; combine complementary edits; **ask** if they contradict. No `rebase -i`, `--force`, hard reset, or skipping hooks unless asked. On conflicts: resolve, report per file (path / remote / local / resolution), **ask for approval and wait**.
4. **Stash apply** — `git stash apply` (not `pop`). Same conflict handling and approval gate.
5. **Commit (conditional)** — only if conflicts needed resolving and those resolutions are uncommitted: use the commit skill on the conflicted files only; wait for explicit approval ("go", "yes", "commit" — not "ok"). No conflicts → no commit.
6. **Drop stash** — only if apply succeeded and any resolutions are approved; match by the `pull-ai-config:` message.
7. **Merge** — follow `/merge-ai-config` (`merge-ai-config/SKILL.md`), honoring its ask-before-write pauses.

## Safety

If fetch, rebase, or stash fails: stop, report, **do not** drop the stash. Vague assent ("continue") does not pass an approval gate. No push unless asked.
