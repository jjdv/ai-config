# ai-config

One git repo for **Claude Code** and **Cursor** user config: skills, agents, rules. Synced between the repo and both tools on each machine with **`/merge-ai-config`**.

**Scope:** only items in this repo. Anything that exists only in a tool's own folders (hand-made tool-specific items, `*.pre-ai-config-*` backups, tool-managed dirs) is ignored. New items join by being added to the repo (or named to `update-harness`), never by being found on a machine.

Every item is **duplicated in full** into each tool (no references), so agents actually read it.

## Layout

```
skills/<name>/       # → ~/.claude/skills/ and ~/.agents/skills/ (verbatim)
agents/<name>.md     # canonical frontmatter; rendered per tool
rules/<name>.md      # canonical = Cursor frontmatter (description, alwaysApply, globs)
targets.json         # optional: restrict an item to one tool
lib/ai_sync.py       # converters, install, inventory
bootstrap.sh         # first-time machine setup
```

| Kind | Claude Code | Cursor |
| --- | --- | --- |
| Skill | `~/.claude/skills/<n>/` | `~/.agents/skills/<n>/` |
| Agent | `~/.claude/agents/<n>.md` (`model`, `tools`) | `~/.cursor/agents/<n>.md` (`model`, `readonly`, `is_background`) |
| Rule | `~/.claude/rules/<n>.md` (`paths:` from globs) | User Rules via `cursor_dialog` MCP |

Agent canonical keys: `name`, `description`, `cursor-model`, `claude-model`, `readonly`, `is_background`, `tools`.
Tool-specific item: `{"agents": {"gpt": ["cursor"]}}` in `targets.json`.

## New machine

```bash
git clone <url> ai-config && cd ai-config && ./bootstrap.sh
```

Then run **`/merge-ai-config`** in Claude Code or Cursor. Bootstrap installs the four maintenance skills into both tools, removes broken `~/.claude/{skills,agents,rules}` symlinks from older setups, and writes `~/.ai-config/` (`repo-path`, `local.md`: machine-local, never synced).

## Skills

| Skill | Purpose |
| --- | --- |
| `/merge-ai-config` | Reconcile repo ↔ Claude ↔ Cursor for repo items; asks on conflicts |
| `/pull-ai-config` | Stash, rebase `origin/main`, then merge |
| `update-harness` | After creating/editing/deleting named items: write repo + both tools immediately (only those items) |
| `/set-local` | Exclude a skill/agent/rule on this machine |

Workflow: edit → `/merge-ai-config` (or `update-harness`) → `git commit && git push`. Elsewhere: `/pull-ai-config`.

## Cursor User Rules need Cursor

They live only in Cursor's MCP. From Claude Code the merge writes the repo and Claude rules and reports Cursor rules as pending; the next merge in Cursor applies them.

## lib/ai_sync.py

`inventory`, `install --tool claude|cursor|both [--only kind:name …]`, `export-rules [--only …]`, `import {agent,rule}-{claude,cursor}`. All take `--repo`; `--home` and `--local-file` default to `~` and `~/.ai-config/local.md`. `install` never deletes.
