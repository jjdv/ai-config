# File formats

Canonical item formats, the per-machine files, hash recipes and sync states. Used by `update-harness`, `merge-ai-config` and the one-time bootstrap. Placeholder meanings: `placeholders.md`. Procedures: `adaptation.md`.

## 1. Canonical items (repo)

- **Skill**: `skills/<name>/SKILL.md` plus bundled files. Frontmatter: `name`, `description`, optional `invocation`: `auto` (default) or `explicit` (only when the user or another item names it); each tool maps it per `profile.md` § Frontmatter rules. Text files may use placeholders; binaries are copied unchanged. A skill may bundle scripts: `SKILL.md` declares the runtime a script needs; when that runtime is missing on the machine, the step that needs it reports and falls back to the manual procedure in `SKILL.md`. A machine-local top-level `assets/` directory is never synced.
- **Agent**: `agents/<name>.md`. Frontmatter, in this key order: `name`, `description`, `model` (`{{model:<name>}}`), `effort` (`{{effort:<name>}}`), optional `background`, `readonly`. Tier agents (`junior`, `standard`, `senior`, `staff`, `principal`, `expert`) require `model`, `effort` and a body section `## Model`; special agents (any other agent) may omit them. An agent without a `model` or `effort` entry in the map renders the tool's own inherit form for it (or omits the line where the tool has none), as `profile.md` § Frontmatter rules states; no question is asked. The `## Model` section says: model and effort are set in the definition; do not override unless the parent asks.
- **Rule**: `rules/<name>.md`. Frontmatter: `description`, `always` (true/false; a rule without `always` is `always: false`), optional `globs` (omitted for always-on or on-demand rules).
- Tool keys, tool ids, permission keys and tool-specific action names never appear in canonical items: capabilities are written semantically or as `{{tool:<capability>}}` (vocabulary in `placeholders.md`). `readonly: true` means the read-only capability set defined there; the exact keys come from `placeholders.json`, how a tool lays them out is a `profile.md` rule. Top-tier advisory agents (`staff`, `principal`, `expert`) normally keep `readonly: false` when they may write recommendation artifacts named in spawn **Authorization** — `readonly: true` excludes write capabilities at the tool layer (`placeholders.md` § Capability sets).
- `skills/update-harness/references/*` is installed verbatim: copied byte for byte, no placeholder resolution, no note handling. These files document the placeholder grammar and the note syntax, so literal `{{...}}` text and the phrase "Adapt for tool" are part of their content. They are exempt from every placeholder lint (structural lint, installed-output lint, canonical-write placeholder check, verify item 2); the name lint still applies. This is a repo-wide rule: no per-machine decision and no question to the user.
- There is no per-item tool restriction key: every canonical item applies to every tool. A tool leaves out items it cannot use through `profile.md` § Excluded items (decided at the bootstrap scope gate or later with `set-local`).
- Hooks are not part of the harness; no hook is required.

## 2. Per-machine files

```
${XDG_CONFIG_HOME:-$HOME/.config}/ai/
  repo-path                 one line: absolute path of the repo clone
  backups/<tool-id>-<timestamp>/   bootstrap backup and the backup before every replace (section 4); timestamp is YYYYMMDD-HHMMSS
  <tool-id>/                tool id: short kebab-case id chosen by the user at bootstrap
    placeholders.json
    profile.md
    registry.json
    migration-report.md     written once by the bootstrap
```

The backup directory mirrors the layout of the tool's own locations (the same relative paths as the installed items, plus the instruction file, the settings), keeps file modification times, and gets a file list with sha256 sums. It is the only backup: nothing is saved elsewhere or in volatile locations.

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
- Empty string: allowed only for `tool:skill-prefix` (renders as nothing, so the bare skill name is used); no other entry may be empty, and this entry is never `null`.
- List of strings (only for `tool:<capability>`, where one capability maps to several tool keys): rendered inline as the keys joined with `, `; expanded one entry per key where `profile.md` § Frontmatter rules defines a list layout (the `readonly` expansion).
- `null` (for `tool:<capability>`; also for `agent:<name>` only when `tool:spawn-agent` is null, for `path:agents` or `path:skills` only when that kind has no `dir` mechanism, for `path:browser-tmp`, and for `block:*`): the tool has no equivalent. A capability contributes no key and no text; wherever a canonical item uses `{{tool:<capability>}}` the adapting agent skips that sentence, and the report names every item that uses it so the user can exclude one that cannot work without it. The other `null` entries are handled the same way: the sentence that uses them is skipped and reported. `null` is the default when discovery finds no equivalent: it is recorded in `profile.md` § Confirmed decisions with the reason and reported, not asked. Ask only when two or more plausible tools exist (the user picks one or `null`). A missing key means unmapped (protocol in `adaptation.md`), which is not the same as `null`. A capability that no item uses stays unmapped.

The agent never invents a value: an unmapped placeholder or capability follows the protocol in `adaptation.md`. The `tool:*` entries are part of the map hash (section 3), so changing a capability re-adapts every item that uses it.

### profile.md (fixed headings)

```
# Profile: <tool-id>
## Tool                 a `Tool id: <tool-id>` line (the folder name), display name, version notes, bootstrap date, migrated-from note
## Targets              table, one row per kind (rule, skill, agent): kind | Targets entry | notes. Entry `<mechanism>:<title>`: `dir:<absolute directory>` (one file or folder per item), `file:<absolute path of the shared file>` (managed blocks, see Single-file mechanism below) or `none:<reason>` (kind unsupported; a skill then degrades as `placeholders.md` § Degradation says; a rule or agent is excluded through `<kind>:*` in Excluded items)
## Frontmatter rules    per kind: canonical key -> tool key / dropped / derived; value rules; keys to omit; the `invocation` mapping; how `readonly` and background are laid out (allowlist syntax, permission mode, native flag); the keys themselves come from `placeholders.json`; a rule with `always: false` and no `globs` becomes the tool's description-triggered form or, when the tool cannot scope, a managed block of the shared file
## Rendering rules      placeholder resolution, adaptation-note handling, rules mechanism, whether bundled skill files are installed, model/effort handling
## Skip list            tool built-ins, plugin and third-party dirs, tool-managed dirs, legacy backups: never read, merged or deleted
## Excluded items       machine-local exclusions: one `kind:name` per line, or `<kind>:*` for every item of that kind
## Confirmed decisions  dated log: question, options shown, user's answer; includes the rationale for unusual capability mappings, the decision for each capability mapped to `null`, and each kind mapped to `none`
```

### Single-file mechanism (`file`)

For a tool that reads one shared instructions file. Each item is a managed block in that file, between a begin marker line and an end marker line that carry the kind and name:

```
<!-- harness:begin <kind>:<name> -->
<rendered body>
<!-- harness:end <kind>:<name> -->
```

- `installed_hash` is the hash of the block text: the begin marker line through the end marker line, exact bytes (section 3).
- Text outside the markers is foreign and never touched; a marker block whose name is not in the registry is foreign too.
- An unmatched or duplicated marker is never repaired silently: stop and ask.
- Frontmatter is not written inside a block; how the item's name, description and `globs` open the block is a layout choice recorded in `profile.md` § Rendering rules.
- The cap, when the tool has one, is in bytes. If the tool documents none, it is asked; if the user does not know, no cap is assumed and the migration report's Decisions records that.
- The default selection is the two maintenance skills (`update-harness`, `merge-ai-config`) plus every always-on rule. The bootstrap preview (and any later run that adds or grows a block) offers the other items that still fit under the cap and asks which to include; items left out are added to `profile.md` § Excluded items. If the default selection alone exceeds the cap, the preview says so and asks which always-on rules to drop.

### registry.json

```json
{
  "version": 1,
  "tool": "<tool-id>",
  "items": [
    {
      "kind": "agent",
      "name": "<name>",
      "installed": "<absolute installed path, or file:<kind>:<name>>",
      "source_hash": "<sha256 of canonical source>",
      "installed_hash": "<sha256 of installed file or tree>",
      "map_hash": "<sha256 or null>"
    }
  ]
}
```

`kind` is `skill`, `agent` or `rule`. Registry membership means managed; anything not listed is foreign and never touched. Only the bootstrap, `merge-ai-config` and `update-harness` write the registry. Items of a `file` mechanism (Single-file mechanism) use `file:<kind>:<name>` as `installed`; every other `installed` value (`dir` items) is an absolute path with no `~`. A `~` form found in an existing registry is expanded when read and rewritten as an absolute path on the next write.

### migration-report.md

Written by the bootstrap after the run; the final answer carries only what the user needs to review and verify, plus the path of this file (`BOOTSTRAP.md` section 13). Fixed headings:

```
# Migration report: <tool-id>
## Run             date, repo commit (short), previous version used (yes/no), backup path, approved scope (item count)
## Results         table: kind | name | result | reason; result is installed, adopted, replaced, imported, skipped, excluded or pending
## Replacements    per cause: what changed in plain words (old wording, new wording), item names, backup path
## Capability map  capability | tool value; capabilities mapped to null with the items that use them
## Foreign items   count and names
## Verification    each verify checklist item with its result; approved scope count versus registry count; INCOMPLETE when they differ
## Decisions       each question asked, in the words shown to the user, and the answer
## Rollback        how to restore the backup and remove the per-machine files
```

## 3. Hash recipes

The agent runs these at run time, by hand or through a bundled skill script that declares its runtime (§ 1); without that runtime the manual procedure applies. Hashes are of exact bytes, so every rendered file ends with a single newline and has no trailing spaces; the agent renders twice (or re-reads its own output) and compares hashes before it registers an item. Rendering choices that affect bytes are normative once written in `profile.md` § Rendering rules (`adaptation.md` § 2).

- File: `sha256sum <file> | cut -d' ' -f1`.
- Skill directory (canonical or installed): `(cd <dir> && find . -type f -not -path './assets/*' | LC_ALL=C sort | xargs sha256sum) | sha256sum | cut -d' ' -f1`.
- Managed block (`file` mechanism): sha256 of the block text, from the begin marker line through the end marker line, each with its newline.
- `map_hash`: compact JSON of only the `placeholders.json` entries the item uses, keys sorted (`jq -S -c`), then `sha256sum`; `null` when the item uses no placeholder. Entries used include the `tool:*` entries of the `readonly` capability set (`placeholders.md`) for an agent with `readonly: true`. List and `null` values are hashed as they stand.

## 4. Sync states (per registry item, per run, current tool only)

Inputs: `S` = hash of the canonical source now, `I` = hash of the installed item now, `M` = map hash now. The registry holds `S0`, `I0`, `M0`.

| Condition | Meaning | Action | Confirm? |
| --- | --- | --- | --- |
| `S=S0, M=M0, I!=I0` and only the `model:`/`effort:` lines differ from the map | local override | report, refresh `I0` | no |
| `S=S0, I=I0, M=M0` | in sync | none | no |
| `S!=S0, I=I0` or `M!=M0, I=I0` | repo or map changed | re-adapt, write installed, refresh hashes | no (hash refresh) |
| `S=S0, M=M0, I!=I0` | installed edited | reverse-adapt to canonical, show diff, write repo | yes (changes repo) |
| `S=S0, M!=M0, I!=I0` | map changed, installed edited | reverse-adapt, three-way merge with the repo version and the re-rendered result (`adaptation.md` § 4); clean and unambiguous: apply and report; overlap or doubt: ask; never overwrite the installed edit silently | only on overlap or doubt |
| `S!=S0` and `I!=I0` | both changed | three-way merge from the `S0` version (`adaptation.md` § 4), ask on conflict | yes |
| installed missing | deleted locally | ask: restore or drop entry | yes |
| in repo, not in registry, name free in tool | new item | list; install after the user confirms scope | yes |
| in repo, not in registry, name exists in tool | collision | decide by the rule below: adopt, replace after backup, or ask when local edits exist | only when local edits exist |
| in registry, not in repo | removal candidate | list; delete installed item and drop entry after confirmation | yes |
| listed in `profile.md` § Excluded items (`<kind>:<name>` or `<kind>:*`) | excluded | registry entry kept, no adapt, no write, listed as excluded | no |
| in tool, not in registry, not in repo | foreign (including items an old install list names) | never adopted, registered, edited or deleted; reported as a count, listed by name only at bootstrap | n/a |

Ownership changes (import, delete, restore) need user confirmation; hash refreshes, adopting an identical item and replacing an unedited collision (below) do not.

### Collisions

Verbs, each with one meaning:

- **adopt**: register the installed item as it is, without writing. Valid only when `I` equals the hash of the fresh render `R` of the canonical item.
- **replace**: copy the installed item to `<xdg>/ai/backups/<tool-id>-<timestamp>/` (section 2), then overwrite it with the fresh render `R` and register it.
- **skip**: leave the item unmanaged: no write, no registry entry, listed again on the next run.
- **import**: reverse-adapt the installed item into the repo (`adaptation.md` § 4), then register it. A repo write, so it needs confirmation.

Default rule per collision (items 3 and 4 ask):

1. `I` equals `R`: adopt.
2. `I` differs from `R` and equals the previous render `P`: replace after backup. `P` is the output the previous version produced for that item: equal to the installed bytes means no local edits. `P` is established from the previous version's record of what it installed (a hash or file list that matches the installed bytes), or by reproducing the previous render from the repo history with the previous install procedure.
3. `I` differs from both `R` and `P`: local edits. Ask (`adaptation.md` § 8), grouped, with default replace after backup, and show the plain diff; import is offered per item.
4. `P` cannot be established: the item is treated as possibly edited. One grouped question, default replace after backup, with the diff.

The report afterwards states every replacement per cause and the backup path.
