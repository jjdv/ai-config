---
name: set-local
description: >-
  Adds a skill, agent, or rule to the current tool's machine-local exclusion list
  (profile.md § Excluded items under ~/.config/ai) so merge and update-harness skip it
  in this tool. Direct invocation only — /set-local skill|agent|rule <name>.
disable-model-invocation: true
---

# set-local

Mark an item **machine-local** for the **current tool**: skipped by `/merge-ai-config` and `/update-harness` in this tool on this machine. File: `${XDG_CONFIG_HOME:-$HOME/.config}/ai/<tool-id>/profile.md`, section `## Excluded items` (never in the repo). Exclusions are per tool: run `/set-local` in each tool that should skip the item.

## Input

| Kind | Aliases | Kind stored | Name stored |
| --- | --- | --- | --- |
| Skill | `skill`, `skills` | `skill` | folder name |
| Agent | `agent`, `agents`, `subagent` | `agent` | filename stem (no `.md`) |
| Rule | `rule`, `rules` | `rule` | rule stem (no `.md`/`.mdc`) |

e.g. `/set-local skill create-pr-tiny`. Missing or ambiguous kind/name → ask once.

## Procedure

1. Locate the current tool's `<tool-id>` directory under `${XDG_CONFIG_HOME:-$HOME/.config}/ai/`. If its `profile.md` is missing, tell the user to bootstrap this tool by following `BOOTSTRAP.md` in the ai-config clone; stop.
2. Normalize the name: trim, drop a leading `- `, `.md`, `.mdc`, use the last path segment if given a path.
3. Under `## Excluded items`, one `kind:name` per line (e.g. `skill:create-pr-tiny`). If the line is already listed, report "already excluded" and stop; otherwise append it. Edit only this section.
4. Confirm in one line. Do not run merge, edit the repo, or touch installed copies: an excluded item already installed stays as is, and `update-harness` lists it as "excluded".
