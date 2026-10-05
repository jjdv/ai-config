# ai-config (custom harness config)

The custom harness config: the single source of truth for the whole custom harness. It holds the harness items (today agents, rules and skills) and the processes that sync and maintain them across tools and machines: bootstrap, pull, merge, update, set-local, and the verification and lint procedures. The definition is canonical and tool-agnostic; an agent adapts it to each tool on each machine, and nothing tool-specific is committed. The set of items and processes is expected to grow. Maintainers: read `AGENTS.md` first (layering rule).

## New machine

Clone the repo, open the tool, and ask its agent to read `BOOTSTRAP.md` and bootstrap the tool. This runs once per tool and writes per-machine state to `~/.config/ai/<tool-id>/`. Then run `merge-ai-config` for the remaining items.

## Daily flow

| Skill | Purpose |
| --- | --- |
| `pull-ai-config` | Stash, rebase on the remote, then merge |
| `merge-ai-config` | Reconcile repo and installed items; asks on conflicts |
| `update-harness` | After creating, editing or deleting named items: sync only those |
| `set-local` | Exclude an item on this machine |

Edit, then `merge-ai-config` or `update-harness`, then commit and push. On another machine: `pull-ai-config`.

## Per-machine state

`~/.config/ai/repo-path` plus `~/.config/ai/<tool-id>/{placeholders.json,profile.md,registry.json}`: placeholder values, model choices, local exclusions and sync registry. Never committed. Model changes are local edits handled by `update-harness`.

## Layout (current items)

```
rules/<name>.md      skills/<name>/      agents/<name>.md
BOOTSTRAP.md         AGENTS.md           skills/update-harness/references/
```
