# File formats

Canonical item formats, the per-machine files, hash recipes and sync states. Used by `update-harness`, `merge-ai-config` and the one-time bootstrap. Placeholder meanings: `placeholders.md`. Procedures: `adaptation.md`.

## 1. Canonical items (repo)

- **Skill**: `skills/<name>/SKILL.md` plus bundled files. Frontmatter: `name`, `description`, optional `disable-model-invocation`. Text files may use placeholders; binaries are copied unchanged. A machine-local top-level `assets/` directory is never synced.
- **Agent**: `agents/<name>.md`. Frontmatter: `name`, `description`, `model` (`{{model:<name>}}`), `effort` (`{{effort:<name>}}`), optional `readonly`, `background`. An agent without a `model` line inherits. The body has a generic `## Model` section: model and effort are set in the definition; do not override unless the parent asks.
- **Rule**: `rules/<name>.md`. Frontmatter: `description`, `always` (true/false), `globs`.
- Tool keys, tool ids, permission keys and tool-specific action names never appear in canonical items: capabilities are written semantically or as `{{tool:<capability>}}` (vocabulary in `placeholders.md`). `readonly: true` means the read-only capability set defined there; the exact keys come from `placeholders.json`, how a tool lays them out is a `profile.md` rule.
- There is no per-item tool restriction key: every canonical item applies to every tool. A tool leaves out items it cannot use through `profile.md` § Excluded items (decided at the bootstrap scope gate or later with `set-local`).

## 2. Per-machine files

```
${XDG_CONFIG_HOME:-$HOME/.config}/ai/
  repo-path                 one line: absolute path of the repo clone
  <tool-id>/                tool id: short kebab-case id chosen at bootstrap
    placeholders.json
    profile.md
    registry.json
```

### placeholders.json

```json
{
  "version": 1,
  "tool": "<tool-id>",
  "entries": {
    "agent:<name>": "<call-site selector text>",
    "model:<name>": "<tool-native model id>",
    "effort:<name>": "<tool-native effort or empty>",
    "tool:spawn-agent": "<exact tool key text for the capability>",
    "tool:search-files": ["<key one>", "<key two>"],
    "tool:delete-files": null,
    "path:skills": "<installed skills dir>",
    "block:spawn-rule": "<multi-line text, newlines as \\n>"
  }
}
```

Flat map. Rule of thumb for the two per-tool files: exact values the agent copies verbatim live in `placeholders.json`; prose rules and recorded decisions live in `profile.md`.

Value types:

- String: copied verbatim into rendered output.
- List of strings (only for `tool:<capability>`, where one capability maps to several tool keys): rendered inline as the keys joined with `, `; expanded one entry per key where `profile.md` § Frontmatter rules defines a list layout (the `readonly` expansion).
- `null` (only for `tool:<capability>`): the user confirmed that the tool has no equivalent. The capability contributes no key and no text; wherever a canonical item used `{{tool:<capability>}}` the adapting agent applies the decision recorded in `profile.md` § Confirmed decisions (skip the sentence or the item). A `null` value is written only after the user's explicit answer. A missing key means unmapped (protocol in `adaptation.md`), which is not the same as `null`.

The agent never invents a value: an unmapped placeholder or capability follows the protocol in `adaptation.md`. The `tool:*` entries are part of the map hash (section 3), so changing a capability re-adapts every item that uses it.

### profile.md (fixed headings)

```
# Profile: <tool-id>
## Tool                 display name, version notes, bootstrap date, migrated-from note
## Targets              table: kind | installed location | layout (file/dir/other mechanism) | notes
## Frontmatter rules    per kind: canonical key -> tool key / dropped / derived; value rules; keys to omit; how `readonly` and background are laid out (allowlist syntax, permission mode, native flag); the keys themselves come from `placeholders.json`
## Rendering rules      placeholder resolution, adaptation-note handling, rules mechanism, model/effort handling
## Skip list            tool built-ins, plugin and third-party dirs, tool-managed dirs, legacy backups: never read, merged or deleted
## Excluded items       machine-local exclusions: one kind:name per line
## Confirmed decisions  dated log: question, options shown, user's answer; includes the rationale for unusual capability mappings and the decision for each capability mapped to `null`
```

### registry.json

```json
{
  "version": 1,
  "tool": "<tool-id>",
  "items": [
    {
      "kind": "agent",
      "name": "<name>",
      "installed": "<installed path or <mechanism>:<title>>",
      "source_hash": "<sha256 of canonical source>",
      "installed_hash": "<sha256 of installed file or tree>",
      "map_hash": "<sha256 or null>"
    }
  ]
}
```

`kind` is `skill`, `agent` or `rule`. Registry membership means managed; anything not listed is foreign and never touched. Only the bootstrap, `merge-ai-config` and `update-harness` write the registry. Items stored through a non-file mechanism use `<mechanism>:<title>` as `installed`, a scheme defined in `profile.md` § Targets.

## 3. Hash recipes

The agent runs these at run time; no script is maintained.

- File: `sha256sum <file> | cut -d' ' -f1`.
- Skill directory (canonical or installed): `(cd <dir> && find . -type f -not -path './assets/*' | LC_ALL=C sort | xargs sha256sum) | sha256sum | cut -d' ' -f1`.
- Non-file item: sha256 of the exact content string sent through the tool mechanism (`printf %s '<content>' | sha256sum`).
- `map_hash`: compact JSON of only the `placeholders.json` entries the item uses, keys sorted (`jq -S -c`), then `sha256sum`; `null` when the item uses no placeholder. Entries used include the `tool:*` entries of the `readonly` capability set (`placeholders.md`) for an agent with `readonly: true`. List and `null` values are hashed as they stand.

## 4. Sync states (per registry item, per run, current tool only)

Inputs: `S` = hash of the canonical source now, `I` = hash of the installed item now, `M` = map hash now. The registry holds `S0`, `I0`, `M0`.

| Condition | Meaning | Action | Confirm? |
| --- | --- | --- | --- |
| `S=S0, I=I0, M=M0` | in sync | none | no |
| `S!=S0, I=I0` or `M!=M0, I=I0` | repo or map changed | re-adapt, write installed, refresh hashes | no (hash refresh) |
| `S=S0, M=M0, I!=I0` | installed edited | reverse-adapt to canonical, show diff, write repo | yes (changes repo) |
| `S=S0, M!=M0, I!=I0` | map changed, installed edited | reverse-adapt, three-way merge with the repo version and the re-rendered result (`adaptation.md` § 4); clean and unambiguous: apply and report; overlap or doubt: ask; never overwrite the installed edit silently | only on overlap or doubt |
| `S!=S0` and `I!=I0` | both changed | three-way merge from the `S0` version (`adaptation.md` § 4), ask on conflict | yes |
| installed missing | deleted locally | ask: restore or drop entry | yes |
| in repo, not in registry, name free in tool | new item | list; install after the user confirms scope | yes |
| in repo, not in registry, name exists in tool | collision | ask: skip / adopt after diff / replace after backup; never silent | yes |
| in registry, not in repo | removal candidate | list; delete installed item and drop entry after confirmation | yes |
| in tool, not in registry, not in repo | foreign (including items an old install list names) | never adopted, registered, edited or deleted; reported as a count, listed by name only at bootstrap | n/a |

Ownership changes (adopt, import, delete) always need user confirmation; hash refreshes do not.
