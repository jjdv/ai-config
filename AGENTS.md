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

Exceptions (exact list, by category):

- the shared per-machine path `~/.config/ai`, only in `skills/update-harness/`, `skills/merge-ai-config/`, `skills/pull-ai-config/`, `skills/set-local/`, `BOOTSTRAP.md`, `AGENTS.md`, `README.md`;
- the project convention path `.agents/skills/project-best-practices` in `create-plan` and `check-plan`;
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

Structural (run from the repo root, expect no output):

```
grep -RnE '\{\{#|\{\{/' skills rules agents
grep -RnoE '\{\{[^}]*\}\}' skills rules agents | sed -E 's/.*(\{\{[^}]*\}\}).*/\1/' | sort -u
```

The last command lists every placeholder in use; each must be in the vocabulary of `placeholders.md`, and `{{model:` and `{{effort:` appear only under `agents/`. Run `grep -rnE '\{\{|Adapt for tool'` over the installed locations listed in each `profile.md` (Targets); expect no output. Canonical frontmatter keys are those of `formats.md` section 1.

Name lint (machine-local; never write the tokens into a repo file):

1. Build a token list in a scratch file from this machine: tool ids and display names from `~/.config/ai/*/profile.md`; keys and ids from the `tool:*` entries of `~/.config/ai/*/placeholders.json` (string, list and `null` values); model and vendor words you know.
2. Run `FILES=$(git ls-files -co --exclude-standard | grep -v '^\.gitignore$')`, then `echo "$FILES" | xargs grep -niwFf <tokens>` and `echo "$FILES" | xargs grep -nE '~/\.[a-z]' | grep -v '~/\.config/ai'`; expect no output.
3. Run `echo "$FILES" | grep -vE '^(skills/(update-harness|merge-ai-config|pull-ai-config|set-local)/|BOOTSTRAP\.md$|AGENTS\.md$|README\.md$)' | xargs grep -nF '~/.config/ai'`; expect no output.

`README.md` and `AGENTS.md` pass the name lint with no allowed hit other than `~/.config/ai`.

## 7. Comments

No comments, JSDoc or explanatory docs unless asked. Comment only what is non-obvious without context; prefer clearer names and structure.
