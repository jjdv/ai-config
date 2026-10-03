---
name: set-local
description: >-
  Adds a skill, agent, or rule to this machine's ai-config exclusion list (~/.ai-config/local.md)
  so merge/update-harness skip it in both Claude Code and Cursor. Direct invocation only —
  /set-local skill|agent|rule <name>.
disable-model-invocation: true
---

# set-local

Mark an item **machine-local**: skipped by `/merge-ai-config`, `/update-harness` and `lib/ai_sync.py` on this machine, for both tools. File: `~/.ai-config/local.md` (never in the repo).

## Input

| Kind | Aliases | Name stored |
| --- | --- | --- |
| Skill | `skill`, `skills` | folder name |
| Agent | `agent`, `agents`, `subagent` | filename stem (no `.md`) |
| Rule | `rule`, `rules` | rule stem (no `.md`/`.mdc`) |

e.g. `/set-local skill create-pr-tiny`. Missing or ambiguous kind/name → ask once.

## Procedure

1. If `~/.ai-config/local.md` is missing, tell the user to run `./bootstrap.sh` from the ai-config clone.
2. Normalize the name: trim, drop `- `, `.md`, `.mdc`, use the last path segment if given a path.
3. Under `## Skills`, `## Agents`, or `## Rules`: if already listed, report "already excluded" and stop; otherwise append `- <name>`.
4. Confirm in one line. Do not run merge, edit the repo, or touch Cursor User Rules / installed copies — an excluded item already on the machine stays as is.
