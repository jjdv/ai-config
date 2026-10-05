---
name: pull-ai-config
description: >-
  Pulls latest origin/main into the local ai-config clone (stash WIP, rebase, restore stash
  with conflict care, drop stash), then runs /merge-ai-config for the current tool. Direct invocation only —
  /pull-ai-config.
disable-model-invocation: true
---

# pull-ai-config

Update the **ai-config** clone from `origin/main`, then sync the current tool via **`/merge-ai-config`**. Works from any tool and any workspace. Never pushes; never touches other repos.

## Repo root

First match wins: (1) the workspace contains the `skills/merge-ai-config` and `skills/update-harness` directories; (2) the single line of `${XDG_CONFIG_HOME:-$HOME/.config}/ai/repo-path`; (3) ask for the path. When resolved from the workspace or by asking, write the absolute path to `repo-path` (create the directory if needed). Never write `~/.config/ai` paths into the repo.

## Procedure

Run git in the repo root.

1. **Fetch** — `git fetch origin`. If the current branch is not `main`, report it and **ask**; do not switch or rebase another branch.
2. **Stash** — if the tree is dirty: `git stash push -u -m "pull-ai-config: <iso-timestamp>"`; record it. If clean, skip stash steps.
3. **Rebase** — `git rebase origin/main`. Preserve both remote and local intent on overlapping hunks; combine complementary edits; **ask** if they contradict. No `rebase -i`, `--force`, hard reset, or skipping hooks unless asked. On conflicts: resolve, report per file (path / remote / local / resolution), **ask for approval and wait**.
4. **Stash apply** — `git stash apply` (not `pop`). Same conflict handling and approval gate.
5. **Commit (conditional)** — only if conflicts needed resolving and those resolutions are uncommitted: use the commit skill on the conflicted files only; wait for explicit approval ("go", "yes", "commit" — not "ok"). No conflicts → no commit.
6. **Drop stash** — only if apply succeeded and any resolutions are approved; match by the `pull-ai-config:` message.
7. **Merge** — follow the `merge-ai-config` skill (`/merge-ai-config`), honoring its ask-before-write pauses.

## Safety

If fetch, rebase, or stash fails: stop, report, **do not** drop the stash. Vague assent ("continue") does not pass an approval gate. No push unless asked.
