# ai-config

One git repo for **Claude Code** and **Cursor** user config: skills, agents, rules. Synced between the repo and both tools on each machine with **`/merge-ai-config`**.

**Scope:** only items in this repo. Anything that exists only in a tool's own folders (hand-made tool-specific items, `*.pre-ai-config-*` backups, tool-managed dirs) is ignored. New items join by being added to the repo (or named to `update-harness`), never by being found on a machine.

Every item is **duplicated in full** into each tool (no references), so agents actually read it.

## Layout

```
skills/<name>/       # → ~/.claude/skills/ and ~/.agents/skills/ (text files rendered per tool)
agents/<name>.md     # canonical frontmatter; rendered per tool
rules/<name>.md      # canonical = Cursor frontmatter (description, alwaysApply, globs)
targets.json         # optional: restrict an item to one tool
models.json          # model id maps, template placeholders, Claude deny-list
lib/ai_sync.py       # converters, templating, install, inventory, verify
bootstrap.sh         # first-time machine setup
```

| Kind | Claude Code | Cursor |
| --- | --- | --- |
| Skill | `~/.claude/skills/<n>/` | `~/.agents/skills/<n>/` |
| Agent | `~/.claude/agents/<n>.md` (`model`, `effort`, `tools`) | `~/.cursor/agents/<n>.md` (`model`, `readonly`, `is_background`) |
| Rule | `~/.claude/rules/<n>.md` (`paths:` from globs) | User Rules via `cursor_dialog` MCP |

Agent canonical keys: `name`, `description`, `cursor-model`, `claude-model`, `claude-effort`, `readonly`, `is_background`, `tools`.

Agents: the implementation tiers `standard`, `senior`, `principal`, `expert`, the reviewers `claude` and `gpt`, and `playwright`.

| Tier | Claude Code | Cursor |
| --- | --- | --- |
| `standard` | Sonnet, medium effort | `composer-2.5[fast=false]` |
| `senior` | Sonnet, high effort | `grok-4.6[effort=high,fast=false]` |
| `principal` | Opus, medium effort | Opus, `effort=medium,fast=false` |
| `expert` | Opus, high effort | Opus, `effort=high,fast=false` |

All Cursor models run non-fast.

Tool-specific items in `targets.json`: `{"agents": {"gpt": ["cursor"], "claude": ["cursor"]}, "skills": {"consult-other-models": ["cursor"]}}`. `claude` and `gpt` are the two Cursor-only reviewers used by `consult-other-models`. Excluded items are reported as "intentionally excluded" by `inventory` and `verify`.

## Templating

Rules, agent `description`/body and every text file of a skill are rendered per tool; binaries are copied unchanged.

- `{{#cursor}}…{{/cursor}}` / `{{#claude}}…{{/claude}}`: kept only in that tool's render. Tags alone on their lines drop those lines; otherwise the block is inline. Blocks do not nest.
- `{{name}}`: placeholder from `models.json` → `placeholders.<tool>` (`tool_name`, `impl_agent_name`, `impl_agent_model`, `impl_agent_label`, `impl_agent_desc`, `senior_agent_name`, `senior_agent_model`, `explore_agent_name` (built-in read-only search subagent: Claude `Explore`, Cursor `explore`), `spawn_tool`, `ask_tool`, `ide_browser`, `browser_tmp_dir`, `agents_dir`, `skills_dir`, `tool_mapping_note`). Unknown names are left as-is.
- `\{{` writes a literal `{{`.
- Never write Cursor-only names (`composer-2.5[fast=false]`, `cursor_dialog`, `~/.cursor/`, `@Browser`, `AskQuestion`, …) in a shared body outside a `{{#cursor}}` block. The Claude deny-list lives in `models.json` → `deny.claude`.
- Model ids: `models.json` → `cursor_to_claude` / `claude_to_cursor`. Claude uses unpinned aliases (`sonnet`, `opus`, `haiku`).

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

`inventory` (also lists `excluded` by `targets.json`), `install --tool claude|cursor|both [--only kind:name …]`, `verify --tool claude|cursor [--only …]` (deny-list on rendered output and sources, composer ids in shared source as errors, model ids in cursor blocks as review notes, missing targeted items, installed-vs-rendered drift; exits nonzero on error), `export-rules [--only …]`, `import {agent,rule}-{claude,cursor}`. All take `--repo`; `--home` and `--local-file` default to `~` and `~/.ai-config/local.md`. `install` never deletes.
