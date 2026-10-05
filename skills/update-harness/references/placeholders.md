# Placeholder vocabulary

Canonical rules, skills and agents contain placeholders only where the text must differ per tool. The adapting agent resolves each placeholder from the tool's `placeholders.json` (format: `formats.md`) when it renders an item for a tool, and turns resolved text back into placeholders when it reverse-adapts an installed edit (procedure: `adaptation.md`). This file defines what each placeholder means; the values live only in `~/.config/ai/<tool-id>/placeholders.json`.

## Grammar

- Form: `{{kind:name}}`. `kind` is one of `agent`, `model`, `effort`, `tool`, `path`, `block`; `name` is kebab-case. Kind `tool` carries the capability vocabulary below.
- `\{{` writes a literal `{{`. No block tags, no nesting, no conditionals.
- The key in `placeholders.json` is the text inside the braces (for example `agent:senior`).
- Every placeholder used by a canonical item needs an entry in the map. This file and its siblings in `skills/update-harness/references/` are installed verbatim and are exempt from the placeholder lints (`formats.md` § 1). An unmapped placeholder stops the run (protocol in `adaptation.md`).

## Vocabulary (closed set)

| Placeholder | Meaning: what the value must be | Allowed in |
| --- | --- | --- |
| `{{agent:<name>}}`, one per agent in `agents/` | Argument text that selects that agent inside a spawn call, including a model argument when the tool requires one at the call site | spawn-call examples and delegation instructions only; prose names the agent in plain text |
| `{{model:<name>}}`, one per agent | The tool's model identifier for that agent | `model:` frontmatter of `agents/*.md` only |
| `{{effort:<name>}}`, one per agent | The tool's effort value for that agent; empty string means omit the line | `effort:` frontmatter of `agents/*.md` only |
| `{{tool:<capability>}}` | the capability table below | skills, rules, agents; only where the exact tool key must appear |
| `{{path:agents}}`, `{{path:skills}}` | Installed directories of the tool for agents and skills; values never end in a slash, call sites add the separator | skills, agents |
| `{{path:browser-tmp}}` | Subdirectory name under `.tmp/` for output of the tool's browser tooling | rules, skills |
| `{{block:tool-note}}` | Block contract below | skills that carry a tool note under the title |
| `{{block:tool-mapping}}` | Block contract below | the rule that holds the tool-mapping table |
| `{{block:spawn-rule}}` | Block contract below | delegation skills |

### Capability vocabulary (`tool:<capability>`, closed set)

Tool keys and ids are tool-specific and never appear in canonical items: no tool allowlists, no tool ids of integrations, no permission or allowlist keys, no tool-specific action names. A canonical item says what it needs semantically. In prose it uses the plain wording of the capability ("read files", "run shell commands"); plain wording needs no translation. Where the rendered text must carry the exact tool key (a spawn-call example, a tool-mapping row, an allowlist), the item uses `{{tool:<capability>}}`. The mapping is exact and lives in `placeholders.json` (entry `tool:<capability>`, rule of thumb: exact values the agent copies verbatim go in `placeholders.json`, prose rules and recorded decisions go in `profile.md`). The value is the tool's exact key text, a list of keys when one capability maps to several keys, or `null` when the user confirmed that the tool has no equivalent (format: `formats.md`). `profile.md` records only the rationale for unusual mappings, never a mapping table.

| Capability | Plain wording in prose | Meaning |
| --- | --- | --- |
| `{{tool:read-files}}` | read files | read the content of a file |
| `{{tool:search-files}}` | find files | list or match files by name or pattern |
| `{{tool:search-code}}` | search code | search file contents |
| `{{tool:write-files}}` | write files | create or overwrite a file |
| `{{tool:edit-files}}` | edit files | replace text inside an existing file |
| `{{tool:delete-files}}` | delete files | remove a file |
| `{{tool:run-shell}}` | run shell commands | run a shell command |
| `{{tool:spawn-agent}}` | spawn a subagent | start a subagent, including the argument form the tool requires |
| `{{tool:await-agent}}` | wait for a subagent | wait for or poll a running subagent |
| `{{tool:ask-user}}` | ask the user | ask the user structured questions |
| `{{tool:browser}}` | browser automation | the tool's built-in or IDE browser tooling |
| `{{tool:pencil-read-nodes}}` | read design nodes | read nodes of a Pencil design document |
| `{{tool:pencil-apply-operations}}` | apply design operations | change a Pencil design document |
| `{{tool:pencil-read-variables}}` | read design variables | read the variables of a Pencil design document |
| `{{tool:pencil-open-document}}` | reload the design document from disk | open or reload a Pencil document |

Product capabilities use `tool:<product>-<action>`: the product is named, its tool ids never are. Capability sets: `readonly` (agent frontmatter) means the capabilities `read-files`, `search-files`, `search-code` and `run-shell`; the keys come from the `tool:*` entries of those four capabilities in `placeholders.json` (an entry that is `null` contributes no key), and `profile.md` § Frontmatter rules says only how the tool lays them out (allowlist, permission keys, a native read-only flag). A capability that has no entry in `placeholders.json` is unmapped (stop, propose, approve, `adaptation.md`). A capability the tool lacks is never replaced by a fallback: it is `null` in `placeholders.json` with the reason in `profile.md` § Confirmed decisions, and the report names the items that use it (ask only when two or more plausible tools exist; `formats.md` § 2).

### Block contracts

A `block:*` value is multi-line text the adapting agent authors from the tool's discovered facts and the user's confirmed decisions, shown in full in the bootstrap setup preview. It must be accurate for the tool and contain no model identifiers.

- `block:tool-note`: one paragraph placed under a skill title. It maps the generic terms the skill uses (spawn a subagent, ask the user, browser, skills location) to the tool's own names, and says how the tool selects a model when spawning.
- `block:tool-mapping`: a table `| Term in this rule | <tool> |` with one row per term the rest of the rule text uses (subagent spawn, implementation subagent, ask the user, context tools, harness sync, skill location, and any other term the rule defines), each cell the tool-native equivalent; the context-tools row lists the tool keys of the capabilities read, search, write, edit, delete, shell, browser, taken from the `tool:*` entries of `placeholders.json`. A term with no equivalent is not filled with a fallback: the cell states that the tool has no equivalent and the report names the term.
- `block:spawn-rule`: how to treat the model when spawning an agent in this tool: whether the agent definition pins the model (do not pass one) or the call must carry it, which model variants are never allowed, and what to do when a requested model is not permitted (stop and report). Includes any user policy recorded in `profile.md`.

## Authoring rules

- Use a placeholder only when the text must change per tool. Plain agent names (`standard`) stay plain in prose, and capabilities stay plain wording unless the exact key must appear (capability vocabulary above).
- Third-party products (for example a browser automation product, a design tool) may be named; their tool keys and ids may not.
- `{{model:*}}` and `{{effort:*}}` never appear outside agent frontmatter.
- Adaptation note: a line starting `> **Adapt for tool:** <instruction>` tells the adapting agent what to render at that spot (rules come from `profile.md`). The agent applies it and drops the line. Notes name no tool and no model.
- Do not add placeholder kinds, capabilities or names without a maintainer decision (see the repo's maintainer guide), and update this table in the same change.
