---
name: merge-ai-config
description: >-
  Bidirectional merge of ai-config: reconciles every skill, agent, and rule between the repo
  and this machine's Claude Code AND Cursor user config, then writes self-contained copies to
  the repo and to both tools. Use after git pull, after local edits, or on a new machine.
  Direct invocation only — /merge-ai-config.
disable-model-invocation: true
---

# merge-ai-config

One pass, all destinations. The **repo** holds one canonical definition per skill, agent, and rule. Each tool gets its own **full, self-contained copy** (no `@` includes, no "see shared file" pointers — agents do not follow references). This skill reconciles whatever differs, then writes the repo and both tools.

## Scope — only what is in the repo

ai-config manages **custom harness only**: items that exist in the repo's `skills/`, `agents/`, `rules/`. Everything else is **tool-specific** and **out of scope** — never read, adopted, merged, deleted, or reported as an orphan. That covers items that exist only in one tool's folders (e.g. a hand-made `~/.claude/skills/bar/`{{#cursor}} or `~/.cursor/agents/foo.md`{{/cursor}}), tool-managed content ({{#cursor}}`~/.cursor/skills-cursor/`, {{/cursor}}plugins), legacy backups (`*.pre-ai-config-*`{{#cursor}}, `~/.cursor/skills/`, `~/.agents/partials/`, `~/.cursor/rules/`{{/cursor}}), and `CLAUDE.md`/settings.

An item joins ai-config only by being added to the repo (authoring there, or naming it to `update-harness`) — never because the merge noticed it on a machine. An item that is in the repo **and** on a machine is managed on both sides, whichever tool it lives in.

Works from Claude Code or Cursor. Everything is plain files except **Cursor User Rules**, which can only be written from Cursor (see § Cursor User Rules).

## Canonical repo format

| Kind | Repo | Claude Code | Cursor |
| --- | --- | --- | --- |
| Skill | `skills/<name>/` (SKILL.md + bundled files) | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` |
| Agent | `agents/<name>.md` | `~/.claude/agents/<name>.md` | {{#cursor}}`~/.cursor/agents/<name>.md`{{/cursor}}{{#claude}}Cursor agents dir (path in `inventory` output){{/claude}} |
| Rule | `rules/<name>.md` | `~/.claude/rules/<name>.md` | User Rule titled `<name>` (MCP) |

- **Skills** are rendered per tool (text files through the template layer, binaries copied unchanged).
- **Agents** are canonical files in `agents/`; `lib/ai_sync.py` renders each tool's dialect. The canonical frontmatter keys are listed in `$REPO/README.md`; produce canonical agents with `ai_sync.py import`, never by hand-translating a tool's dialect.
- **Templates.** Repo bodies are shared by both tools and rendered through `\{{#cursor}}…\{{/cursor}}` / `\{{#claude}}…\{{/claude}}` blocks and `\{{placeholder}}`s defined in `$REPO/models.json` (syntax: `$REPO/README.md` § Templating). Machine copies are **rendered output**: never paste a machine copy over a repo file; edit the repo template instead.
- **Rules** are canonical in Cursor's frontmatter (`description`, `alwaysApply`, `globs`). Claude gets `paths:` from `globs` when not `alwaysApply`.
- **`targets.json`** (repo root, optional) restricts an item to one tool: `{"agents": {"gpt": ["cursor"]}, "skills": {"x": ["claude"]}}`. Unlisted = both. Use it for tool-specific items (Cursor model-lane agents, skills that call Cursor-only tools).
- Tool-managed directories of either tool are never read or written{{#cursor}} (e.g. `~/.cursor/skills-cursor/`){{/cursor}}.

## Machine-local state (never synced to the repo)

- `~/.ai-config/repo-path` — absolute path of this machine's clone.
- `~/.ai-config/local.md` — names (`## Skills`, `## Agents`, `## Rules`) to exclude on this machine. Add with `/set-local`.

Repo root resolution, first match wins: (1) current workspace has `skills/merge-ai-config/` and `lib/ai_sync.py`; (2) `~/.ai-config/repo-path`; (3) ask. If resolved from the workspace, rewrite `repo-path`. Set `REPO=<root>` and use `python3 $REPO/lib/ai_sync.py`.

## Step 0 — Git intent (which side's differences are intended)

```bash
git -C $REPO log --oneline -5
git -C $REPO diff HEAD~3..HEAD --name-status     # clamp to available history
```

Recent commits record deliberate changes. File names are not enough — read the **content** of what changed for each item that differs (`git -C $REPO log -p -3 -- <path>`).

- **Structure:** `D old` + `A new` of the same kind = rename/supersede (delete the old item from both tools). `D` alone = remove from the machine. Never resurrect repo-deleted items unless asked.
- **Content:** for each item where a machine copy differs from the repo, check whether the machine copy equals an **older repo version** (`git show HEAD~N:<path>`; render agents/rules through `lib/ai_sync.py` first; skills compare directly). Look back past 3 commits if recent ones do not match.
  - **Matches an older version** → the machine has no edits of its own; the later repo changes are intended. Take the repo version; do not revert them.
  - **Matches no version** → the machine copy has local edits: merge (Step 3), keeping reasonable, helpful changes from both sides.
- **Timestamps (tie-breaker only):** if still ambiguous, compare the path's last commit date (`git log -1 --format=%cI -- <path>`) with the machine file's mtime; the newer side is more likely intentional. Cursor User Rules have no mtime. Never let a timestamp override what the content comparison shows.
- No commits yet: nothing to infer; merge by content.

## Step 1 — Inventory

```bash
python3 $REPO/lib/ai_sync.py inventory --repo $REPO
```

Per skill/agent/rule it reports `repo` (bool), the machine path (`claude_path`, `cursor_path`) when present, and, for `claude` and `cursor`: `same`, `differs`, `missing` (repo has it, machine does not), `tool-specific` (on the machine only — **ignore**), `not-targeted`/`present-but-not-targeted`. Items in `local.md` are already omitted. "same" means the machine file equals exactly what install would write (the **rendered** output). The `excluded` key lists what `targets.json` keeps off each tool: **print it as "Excluded by targets.json" per tool** (e.g. Cursor-only agents are intentionally absent from Claude Code).

{{#cursor}}
Then list **Cursor User Rules** (MCP `cursor_dialog`, `scope: user`, `action: list`) if available, and consider only titles that match a repo rule; other titles are tool-specific. If MCP is unavailable, say so and skip: Cursor catches up on its next merge.
{{/cursor}}
{{#claude}}
Cursor User Rules cannot be listed or written from Claude Code: report them as pending; Cursor catches up on its next merge.
{{/claude}}

Ignore every `tool-specific` entry (do not even list them, except as a count in the report). Print a compact table of repo items that are not `same`, then classify:

| Status | Action |
| --- | --- |
| `same` on all targeted sides | nothing |
| `missing` on a machine side | write from repo |
| `differs` | merge (Step 3) |

## Step 2 — Normalize

For each repo item that `differs`, convert the machine copy to canonical before comparing:

```bash
python3 $REPO/lib/ai_sync.py import agent-claude ~/.claude/agents/<n>.md
python3 $REPO/lib/ai_sync.py import agent-cursor <cursor_path from inventory>
python3 $REPO/lib/ai_sync.py import rule-claude  ~/.claude/rules/<n>.md
python3 $REPO/lib/ai_sync.py import rule-cursor  <file-with-user-rule-content>   # strips the "# title" line
```

Then, on every candidate:

1. **Inline references.** Replace `@path` / "see shared file" pointers with the referenced content if it exists. Unresolvable pointers: keep the best inline text from another side; if none, ask.
2. Drop wrapper cruft (`# Foo (shared)` headings with no content).
3. Preserve information lost by conversion: Claude rules lack `alwaysApply`; Claude agents lack the Cursor model key. When the repo copy has that field, keep it — never downgrade a canonical field because a tool's dialect cannot express it.
4. Handle **tool-specific content** (one tool's spawn/ask tool names, model ids, MCP names, tool-only paths) **without asking**: translate it through `$REPO/models.json` placeholders (`\{{spawn_tool}}`, `\{{ask_tool}}`, `\{{impl_agent_model}}`, …) or wrap it in a `\{{#cursor}}` / `\{{#claude}}` block. **Never write a Cursor-only model id or name in a shared body outside a `\{{#cursor}}` block**; `verify --tool claude` rejects it. If the item is meaningless in one tool, restrict it with `targets.json`. Never drop content. List each decision in the report.

## Step 3 — Merge

For each differing repo item produce **one canonical document** from all sides (repo, Claude, Cursor):

- Keep **reasonable, helpful** changes from every side; never undo an intended repo change (Step 0).
- Keep the more complete procedure when one side is a stub; keep the better single-line `description`; valid frontmatter; `name` equals folder/file stem.
- Do not duplicate paragraphs. Prefer repo naming for duplicates.
- Skill dirs: merge `SKILL.md` and bundled files (`references/`, scripts); `assets/` of merge-ai-config is machine-local and never merged.
- Self-contained output.
- When a shared item needs different wording per tool, write it so both read correctly (e.g. "run the commit skill") rather than naming one tool's mechanism; if impossible, restrict via `targets.json`.

### Ask — required pauses

Stop and ask (batch related questions, 2–4 concrete options each, name the item and paths, tight diff summary) for: overlapping names with same intent; same name with substantially different bodies; incompatible guidance; destructive actions (deleting); invalid frontmatter; unresolvable pointers; unknown repo root; MCP failures.

Do not ask for: whitespace-only diffs, writing a repo item to a machine side that lacks it, one side strictly a subset (keep the superset), or anything covered by a global policy the user already stated in this chat (state the policy in the report).

## Step 4 — Write

Only after all asks are resolved.

1. **Repo.** Write merged canonical files under `skills/`, `agents/`, `rules/` (and `targets.json` if changed). `git rm`/delete superseded paths.
2. **Machine, files — script, not hand-copying:**

   ```bash
   python3 $REPO/lib/ai_sync.py install --repo $REPO --tool both
   ```

   Writes rendered skills, agents and Claude rules for both tools, honoring `targets.json` and `local.md`. It never deletes and never touches `merge-ai-config/assets/`.
3. **Cursor User Rules.**{{#cursor}} `python3 $REPO/lib/ai_sync.py export-rules --repo $REPO` prints `[{title, content}]`. In `cursor_dialog`: `list` first, match by **title**, then `update` (id + title + content) or `add`. Ids are machine-local. Never write `~/.cursor/rules/`.{{/cursor}}{{#claude}} Not writable from Claude Code: report as pending.{{/claude}}
4. **Removed/renamed repo items** (from Step 0 git intent, or `targets.json` narrowed): delete the old skill dir / agent file / rule from both tools{{#cursor}} (User Rule via MCP `remove`){{/cursor}} — only items that were in the repo. Just do it and list it. Broken symlinks at `~/.claude/{skills,agents,rules}` block writes: tell the user to run `./bootstrap.sh`.
5. **Verify — the merge fails on any error:**

   ```bash
   python3 $REPO/lib/ai_sync.py verify --repo $REPO --tool claude
   python3 $REPO/lib/ai_sync.py verify --repo $REPO --tool cursor
   ```

   It checks that no Claude output or source (outside Cursor-only blocks) matches the deny-list in `models.json`, that every targeted item is installed, and that installed files equal the rendered output. Fix the repo templates (never the installed files) and re-run until both pass.

Re-run `inventory` and confirm every non-excluded item is `same` (or `not-targeted`).

## Step 5 — Report

Repo items merged / written to a machine side (say which tool) · git intent (removed/renamed) · locally excluded · pointers inlined · conflicts asked vs auto-resolved · tool-specific *content* decisions (reworded / `targets.json`) · count of ignored tool-specific machine items · Cursor User Rules synced or **pending** · `verify` result for both tools (pass/fail, error lines) · agents/skills intentionally Cursor-only (`Excluded by targets.json`) · `git -C $REPO status --short`. Remind the user to commit and push.

## Self-merge

`merge-ai-config` and the other maintenance skills are ordinary repo items. Merge them like any other; never overwrite machine-local `~/.ai-config/`.

## Out of scope

Everything outside the repo's items (see § Scope), git merge/rebase (use `/pull-ai-config`), commit and push.
