---
name: update-harness
description: >-
  MANDATORY after creating, updating, renaming, or deleting any rule, skill, or agent in
  Claude Code or Cursor user config (~/.claude/*, ~/.agents/skills, ~/.cursor/agents, Cursor
  User Rules, or ai-config repo files). Dual-writes the named items to the ai-config repo and
  BOTH tools in the same turn. Also on /update-harness. Narrower than /merge-ai-config.
---

# update-harness

Targeted sync of **named** harness items (rules, skills, agents) to the repo and **both** tools. Run it **in the same turn** you create, update, rename, or delete one — do not ask "should I sync?". Skip items listed in `~/.ai-config/local.md`. **Only custom harness belongs here:** an item is part of ai-config when it is in the repo or the user explicitly names it. Tool-specific items (hand-made only in one tool's folder and not named, tool-managed content, `*.pre-ai-config-*` backups) are out of scope — do not sync them, and if you edited one of those this turn, don't run this skill. Unknown drift or first setup → `/merge-ai-config` instead.

## Paths

| Kind | Repo | Claude Code | Cursor |
| --- | --- | --- | --- |
| Skill | `skills/<name>/` | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` |
| Agent | `agents/<name>.md` | `~/.claude/agents/<name>.md` | `~/.cursor/agents/<name>.md` |
| Rule | `rules/<name>.md` | `~/.claude/rules/<name>.md` | User Rule `<name>` (`cursor_dialog` MCP) |

Repo root: workspace (has `skills/merge-ai-config/` + `lib/ai_sync.py`) → `~/.ai-config/repo-path` → ask. Format details (canonical agent/rule frontmatter, `targets.json`) are in `merge-ai-config/SKILL.md` § Canonical repo format.

## Procedure

1. **Scope** — items edited this chat, or the names given. Ambiguous → ask once.
2. **Source of truth** — the edit made in this chat wins. If an edit was made in one tool's dialect, convert to canonical first (`python3 $REPO/lib/ai_sync.py import agent-claude|agent-cursor|rule-claude|rule-cursor <file>`). Both sides differ with no edit from this chat → apply `merge-ai-config` § Step 0 (older-version match, then timestamps as tie-breaker); still unclear → ask with a one-line diff.
3. **Normalize** — self-contained (no `@` pointers or "see shared file"), valid frontmatter, single-line `description`, skill `name` = folder.
4. **Write repo** — canonical file(s) under `skills/`, `agents/`, `rules/`.
5. **Write machine** — `python3 $REPO/lib/ai_sync.py install --repo $REPO --tool both --only <kind>:<name> …` (one `--only` per named item, e.g. `--only skills:commit --only rules:base`; **never run it without `--only`** — that rewrites every item and can overwrite unmerged machine edits to others; never deletes; honors `targets.json` and `local.md`). Rules: also `python3 $REPO/lib/ai_sync.py export-rules --repo $REPO --only rules:<name> …`, then `cursor_dialog` `list` → match by title → `update`/`add`. If MCP is unavailable, report the Cursor rule as **pending**; the next `/merge-ai-config` in Cursor applies it.
6. **Delete / rename** — remove old paths on the repo and both tools in the same pass (`git rm`; rm file/dir; User Rule via MCP `remove` using the id from `list`).
7. **Report** — per item: kind, name, operation, repo / Claude / Cursor written or removed. Remind to commit and push; other machines run `/pull-ai-config`.

Tool-specific content in a shared item: reword neutrally, or restrict with `targets.json`; don't ask, report the decision.

Errors: MCP failure → retry once, then report; do not claim the rule synced. Broken symlink at `~/.claude/{skills,agents,rules}` → run `./bootstrap.sh`.
