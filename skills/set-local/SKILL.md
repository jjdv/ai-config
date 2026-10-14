---
name: set-local
description: >-
  Adds a skill, agent, or rule to the current tool's machine-local exclusion list
  (profile.md § Excluded items under ~/.config/ai) so merge and update-harness skip it
  in this tool, or removes it from that list with un-exclude. Direct invocation only: `{{tool:skill-prefix}}set-local skill|agent|rule <name>` or `{{tool:skill-prefix}}set-local un-exclude skill|agent|rule <name>`.
invocation: explicit
---

# set-local

Mark an item **machine-local** for the **current tool**: skipped by `merge-ai-config` and `update-harness` in this tool on this machine. File: `${XDG_CONFIG_HOME:-$HOME/.config}/ai/<tool-id>/profile.md`, section `## Excluded items` (never in the repo). Exclusions are per tool: run `set-local` in each tool that should skip the item.

## Input

| Kind | Aliases | Kind stored | Name stored |
| --- | --- | --- | --- |
| Skill | `skill`, `skills` | `skill` | folder name |
| Agent | `agent`, `agents`, `subagent` | `agent` | filename stem (no `.md`) |
| Rule | `rule`, `rules` | `rule` | rule stem (no `.md`) |

e.g. `{{tool:skill-prefix}}set-local skill create-pr-tiny`; `{{tool:skill-prefix}}set-local un-exclude skill create-pr-tiny` reverses it. Missing or ambiguous kind/name → ask once.

## Procedure

1. Locate the directory under `${XDG_CONFIG_HOME:-$HOME/.config}/ai/` whose `profile.md` describes this tool (as `update-harness` does). If its `profile.md` is missing, tell the user to bootstrap this tool by following `BOOTSTRAP.md` in the ai-config clone; stop.
2. Normalize the name: trim, drop a leading `- `, `.md`, use the last path segment if given a path.
3. Add (default): under `## Excluded items`, one `kind:name` per line (e.g. `skill:create-pr-tiny`). If the line is already listed, report "already excluded" and stop; otherwise append it. Edit only this section.
4. Un-exclude (first word `un-exclude`): remove the matching `kind:name` line from `## Excluded items`. If it is not listed, report "not excluded" and stop; if only a `<kind>:*` line covers it, say so and stop. Edit only this section.
5. Confirm in one line. Do not run merge, edit the repo, or touch installed copies: an excluded item already installed stays as is, and `update-harness` lists it as "excluded". After un-exclude, the next `merge-ai-config` or `update-harness` run syncs the item.
