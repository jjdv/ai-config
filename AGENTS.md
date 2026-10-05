# Maintainer guide

> **Layering rule.** This repo holds canonical, tool-agnostic harness definitions only (items and process specs). Anything specific to a tool or model lives on the machine under `~/.config/ai/<tool-id>/`, never here. Any tool or model name anywhere in the repo is a violation.

This repo is the custom harness config: the single source of truth for the custom harness, namely its items (today rules, skills, agents) and the processes that sync and maintain them across tools and machines (bootstrap, pull, merge, update, set-local, verification and lint). The set of items and processes is expected to grow; this guide applies to whatever is added.

## 1. Layers

| Layer | Holds | Must not hold |
| --- | --- | --- |
| Canonical rules and skills (`rules/`, `skills/`) | Generic text, agent names, `{{kind:name}}` placeholders, adaptation notes | Model ids, effort levels, tool or vendor names, tool paths |
| Canonical agents (`agents/`) | The above, plus `model: {{model:<name>}}` and `effort: {{effort:<name>}}` | Concrete model ids or effort values |
| Per-machine data (`~/.config/ai/<tool-id>/`) | Everything tool-specific: placeholder values, profile, registry | Nothing is committed from here |
| Installed output (each tool's own folders) | Rendered items only, no placeholders or adaptation notes | Edits that are not synced back |

Banned anywhere in the repo, described by category: tool names, vendor names, model names and ids, tool-native tool names, tool keys and ids, permission keys, allowlists, tool-specific paths, a `tools:` key.

Allowed anywhere in the repo (exact list):

- `~/.config/ai`, the shared per-machine path;
- `.agents/skills/project-best-practices`, the tool-agnostic project convention path;
- third-party products that are not harness tools may be named as products, never by tool key or id.

Capabilities are written semantically (read files, run shell commands, browser automation) or as `{{tool:<capability>}}`. Never write tool keys, MCP tool ids, permission keys or allowlists in a canonical item.

## 2. Repo map

- `rules/<name>.md`, `skills/<name>/`, `agents/<name>.md`: canonical items. The maintenance skills (`pull-ai-config`, `merge-ai-config`, `update-harness`, `set-local`) are the sync and maintenance processes.
- `skills/update-harness/references/`: `formats.md` (item and per-machine formats, hashes, sync states), `placeholders.md` (placeholder and capability vocabulary), `adaptation.md` (render, reverse-adapt, checks). These are the single source; do not restate them elsewhere.
- `BOOTSTRAP.md`: one-time per-tool setup, driven by an agent.
- `README.md`: overview and daily flow.

## 3. Add or change an item

1. Edit the canonical item under the layering rule.
2. Run the lints in section 6.
3. Run `update-harness` for the named items.
4. Commit.

## 4. Capabilities and placeholders

The vocabulary is closed and lives in `skills/update-harness/references/placeholders.md`. Adding a capability or placeholder needs a maintainer decision and an update of that file in the same change.

## 5. Models and effort

Model and effort are tool-local. A model change is a local edit of the installed agent or of `placeholders.json`, handled by `update-harness`; never edit the repo for it.

## 6. Lint

Run every block from the repo root, in `zsh` or `bash`. "Expect no output" is the pass criterion; the exit status of `xargs` (123 when `grep` matches nothing) is irrelevant.

`skills/update-harness/references/*` is installed verbatim (`formats.md` section 1): it is exempt from every placeholder lint below and subject to the name lint.

Structural:

```
CANON=$(git ls-files -co --exclude-standard skills rules agents | grep -v '^skills/update-harness/references/')
echo "$CANON" | xargs grep -nE '\{\{#|\{\{/'
echo "$CANON" | xargs grep -ohE '\{\{[^}]*\}\}' | sort -u | grep -vE '^\{\{(agent|model|effort):[a-z-]+\}\}$' | grep -vxFf <(grep -ohE '\{\{(tool|path|block):[a-z-]+\}\}' skills/update-harness/references/placeholders.md | sort -u)
echo "$CANON" | grep -v '^agents/' | xargs grep -nE '\{\{(model|effort):'
```

The second command passes only when every placeholder in use is in the vocabulary of `placeholders.md` (the allowed `tool`, `path` and `block` tokens are read from that file); the third when `{{model:` and `{{effort:` appear only under `agents/`. Canonical frontmatter keys are those of `formats.md` section 1.

Installed locations (the directories listed in each `profile.md` under Targets; expect no output):

```
grep -rnE '\{\{|Adapt for tool' <installed dirs> | grep -v '/update-harness/references/'
```

Name lint (machine-local; never write the tokens into a repo file):

```
S=$(mktemp -d)
FILES=$(git ls-files -co --exclude-standard | grep -v '^\.gitignore$')
for d in ~/.config/ai/*/; do t=$(basename "$d"); [ "$t" = backups ] || echo "$t"; done > $S/ids
jq -r '.entries|to_entries[]|select(.key|startswith("tool:"))|.value|if type=="array" then .[] else . end|select(. != null and . != "")' ~/.config/ai/*/placeholders.json | sort -u > $S/keys
grep -E '^[A-Z][a-z]+$' $S/keys | sed 's/.*/`&`/' > $S/plain
grep -vE '^[A-Z][a-z]+$' $S/keys > $S/exact
```

then add to `$S/ids`, one per line, the display names from the Tool section of each `~/.config/ai/*/profile.md` and the model and vendor words you know, and run:

```
echo "$FILES" | xargs grep -niwFf $S/ids
echo "$FILES" | xargs grep -nwFf $S/exact
echo "$FILES" | xargs grep -nFf $S/plain
echo "$FILES" | xargs grep -nE '~/\.[a-z]' | grep -v '~/\.config/ai'
```

Single capitalized plain words (for example a tool key that is also an English word) are matched only inside backticks, so ordinary prose does not produce hits; every other key is matched as a case-sensitive whole word. Any path under the home directory other than `~/.config/ai` is flagged as tool-specific; `.agents/skills/project-best-practices` is allowed everywhere.

## 7. Comments

No comments, JSDoc or explanatory docs unless asked. Comment only what is non-obvious without context; prefer clearer names and structure.
