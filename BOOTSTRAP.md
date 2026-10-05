# Bootstrap

## 1. Purpose and invocation

The user says "read BOOTSTRAP.md and bootstrap this tool". Bootstrap runs once per tool. This repo is the custom harness config, the single source of truth for the harness: its items (today agents, rules and skills; the set may grow) and the processes that sync and maintain them. You adapt that canonical harness to the tool you run in, using only the generic discovery guidelines below. Nothing tool-specific is stored in this repo: all tool-specific facts go to `${XDG_CONFIG_HOME:-$HOME/.config}/ai/<tool-id>/` (called `<xdg>/ai/<tool-id>/` below).

Formats, the placeholder vocabulary, the capability vocabulary, the block contracts, the hash recipes, the sync-state table and the adaptation procedure are specified in `skills/update-harness/references/{formats,placeholders,adaptation}.md`. This file points to them and does not restate them; read them before Step 4.

## 2. Agent rules (mandatory)

- Confirm with the user before writing anything: see section 8, Confirmation gates.
- Never invent a placeholder value. Propose it, show it, and write only the approved map.
- When the tool lacks an equivalent of something the harness needs: ask the user; never choose a fallback.
- Run no scripts. Compute hashes with `sha256sum` (recipes in `skills/update-harness/references/formats.md`).
- Ask confirmations with the tool's ask-the-user mechanism in the main thread. Reads and writes may be delegated only with the exact approved payload.
- Anything outside the repo's items is foreign: never touch it.

## 3. Step 1: Guard

Compute `<xdg>/ai/<tool-id>/` once the tool id is known (Step 2). If that directory exists: stop, tell the user to use `update-harness`, and do nothing else. A model change never re-runs bootstrap.

## 4. Step 2: Identify

- Tool id: ask the user to name it (short kebab-case). It is used only as the directory name under `<xdg>/ai/`; it is not written into any repo file. Do not pick it from a list.
- Repo path: the directory of this file. Check whether `git status` is clean; report only, change nothing.

## 5. Step 3: Case

Ask which applies: (a) a previous ai-config version was used in this tool, or (b) ai-config was never used in this tool.

## 6. Step 4: Discovery guidelines

These are generic. For each topic: how to find it, what to record, and what to do when it is unknown (ask the user). Use the tool's own documentation, its settings, and the filesystem including existing installed items. Do not assume any value.

1. **Config locations.** Find where the tool keeps user-level agents, skills and rules, the user-level instruction file and the settings. Record per kind the layout: a file, a directory, or a non-file mechanism (for example a settings store or a protocol server). If a location or mechanism cannot be established, ask the user.
2. **Format rules.** Find the frontmatter dialect per kind by reading existing installed items and the tool's documentation. Record the mapping from each canonical key to the tool's key, the keys that are dropped, the keys that are derived, how rules are scoped, and how model, effort, read-only and background are expressed (canonical keys: `skills/update-harness/references/formats.md`). If the dialect is unclear, ask the user.
3. **Invoking a custom agent by name.** Find how the tool spawns a custom agent: the name of the spawn mechanism and its argument form, whether the call must also carry a model, and how one agent is selected among several. This determines the `agent:<name>` and `tool:spawn-agent` entries and the `block:spawn-rule` value (contracts: `skills/update-harness/references/placeholders.md`). If it cannot be determined, ask the user.
4. **Models.** Find which models the tool offers: its picker, its documentation, a listing command, or ask the user. Propose a `model:<name>` and an `effort:<name>` entry per agent in `agents/` by comparing each agent's role description with the available models. Show the reasoning for each proposal; the user decides. If a suitable model is not available, ask.
5. **Tool and permission model.** Find which of the tool's built-in tools implement each capability of the closed vocabulary in `skills/update-harness/references/placeholders.md`, and how the tool restricts them (an allowlist key, permission keys, a native read-only flag). Record per capability the exact key as the tool spells it, a list where one capability maps to several keys, how read-only is expressed, and every capability the tool lacks (value `null`, only after the user confirms there is no equivalent). Propose these as `tool:<capability>` entries of `placeholders.json` (exact values, copied verbatim at render time) as part of the `placeholders.json` confirmation at gate G1. Only the `readonly` layout rule and the rationale of unusual mappings go into `profile.md`; `profile.md` has no capability table. Never put a tool key into a repo file. If a capability cannot be matched, ask the user.
6. **Other placeholders.** Find the tool's ask-the-user mechanism, its browser tooling, the installed directories and the temporary subdirectory used for browser output. Author each `block:*` value from discovered facts, following the contracts in `skills/update-harness/references/placeholders.md`. Show the authored text at G1.
7. **Foreign items.** Recognize as foreign: the tool's built-in agents and skills, plugin and third-party directories, tool-managed settings and instruction files, legacy backups, and old ai-config state. Put them on the skip list in `profile.md`. Never merge, sync or delete them. If unsure whether an item is foreign, treat it as foreign and ask.

When the tool has no equivalent for a harness feature: ask the user whether to skip the feature or how to emulate it, never choose for them, and record the answer (G4).

## 7. Step 5: Backup

Show the paths and sizes to back up (the skills, agents and rules locations, the instruction file, the settings, and any non-file rule export) and the backup location `<xdg>/ai/backups/<tool-id>-<timestamp>/`. The backup is mandatory in case (a) and recommended in case (b). Do not continue until the backup exists and its file list has been shown.

## 8. Confirmation gates

Each gate: show the data, wait for an explicit yes, record the question, the options shown and the answer in `profile.md` under Confirmed decisions. Nothing is written to `<xdg>/ai/`, the tool's config, or the repo before G1 through G5 are all confirmed (the backup in Step 5 is the only earlier write).

- **G1.** The full proposed `placeholders.json`, one row per entry with key, value, why, and how it was discovered. This includes the `tool:<capability>` rows (exact keys, lists, `null` where the tool has no equivalent) as part of the same confirmation. Also show the `readonly` layout rule that goes into `profile.md`.
- **G2.** Detected targets and format rules, the skip list, and the excluded items.
- **G3.** Import scope: every repo item is listed, and the user may exclude any of them; exclusions are recorded under Excluded items in `profile.md`. Per-tool exclusion is the only restriction mechanism: the repo has no key that restricts an item to a tool. Also list the tool's foreign items that match nothing in the repo, including items an old install list names: they are never adopted, registered, imported or deleted.
- **G4.** Every non-obvious decision: a feature with no equivalent (ask, no fallback), an ambiguous path, how rules are stored, a model that is unavailable.
- **G5.** The case-specific lists of Step 6.

## 9. Step 6, case (a): a previous version was used

1. Identify the items the old version installed: match installed names against the repo's items, and read old install lists or state the user points to or you find. Carry over old exclusions (shown at G2).
2. An installed item that an old list names but that has no counterpart in the repo is foreign: list it, and never adopt, register, import or delete it.
3. For each matched item: adapt it freshly from the canonical source following `skills/update-harness/references/adaptation.md`, compare the result with the installed item, and show every difference. Per differing item the user picks one of: keep the installed version and propose it to the repo, replace it with the adapted output, or skip it (it stays foreign).
4. Identical items are adopted after a single batch confirmation.
5. Never overwrite silently.

## 10. Step 6, case (b): never used

All existing tool items are foreign. List them. The user may nominate items to import into the repo; this is the only tool-to-repo direction in bootstrap. Before importing, show the reverse-adapted canonical text and any new placeholder proposals. Repo edits stay uncommitted and must pass the canonical-write checks in `skills/update-harness/references/adaptation.md`.

## 11. Collisions

An unmanaged tool item that has the name of a repo item: ask the user whether to skip it, adopt it after a diff, or replace it after a backup. Never overwrite or adopt it silently.

## 12. Step 7: Write (only after G1 through G5)

1. Create `<xdg>/ai/<tool-id>/`.
2. Write `placeholders.json`, `profile.md` (including its Confirmed decisions section and, when relevant, a migrated-from note) and an empty `registry.json`, in the formats of `skills/update-harness/references/formats.md`.
3. Write `<xdg>/ai/repo-path` if it is absent; never overwrite a different value without asking.
4. Adapt only `merge-ai-config` and `update-harness` (with its `references/`), install them, and register them.
5. Show all final files and the registry.

## 13. Step 8: Hand-off

Tell the user: restart or reload the tool if needed; run `merge-ai-config` to import the rest of the harness; to roll back, restore the backup and delete `<xdg>/ai/<tool-id>/`.

## 14. Adapting merge-ai-config and update-harness

These two items use no placeholder beyond what the approved map covers. Adapt them following `skills/update-harness/references/adaptation.md`. A placeholder with no entry in the approved map triggers the unmapped protocol in that file: stop, propose an entry, and write it only after the user approves.
