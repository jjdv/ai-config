# Adaptation procedure

How an agent renders canonical items for the current tool, reverse-adapts installed edits, and verifies the result. Formats: `formats.md`. Placeholder meanings: `placeholders.md`. The tool is identified by `profile.md`; this file names no tool.

## 1. Inputs

Repo path from `<xdg>/ai/repo-path`; the current tool's `placeholders.json`, `profile.md`, `registry.json` in `<xdg>/ai/<tool-id>/`. A missing profile means the tool was never bootstrapped: stop and point the user to `BOOTSTRAP.md` in the repo.

## 2. Rendering (repo to tool)

1. Read the canonical item. Skip it when it is in `profile.md` § Excluded items.
2. Resolve every `{{kind:name}}` from `placeholders.json` verbatim (`tool:<capability>` too: string as is, list joined with `, `, `null` applies the recorded decision, section 5). `\{{` becomes a literal `{{`.
3. Follow each `> **Adapt for tool:**` note using `profile.md` § Rendering rules, then drop the note line. Notes and unresolved placeholders never reach installed output.
4. Apply `profile.md` § Frontmatter rules per kind (rename, drop, derive keys; omit keys the tool lacks). Expand `readonly` into the keys of the `tool:*` entries for the read-only capability set (`placeholders.md`) laid out as `profile.md` § Frontmatter rules says; a `null` entry contributes no key. A capability with no entry in `placeholders.json` follows the unmapped protocol (section 5).
5. Bundled skill files are copied with the same placeholder resolution (text) or unchanged (binary); `assets/` is never copied.
6. Items stored through a non-file mechanism are written through that mechanism as `profile.md` § Targets describes; the installed path is `<mechanism>:<title>`.
7. Write, re-hash (`formats.md` § 3), update the registry entry (`source_hash`, `installed_hash`, `map_hash`).

## 3. Model and effort

- Fresh install: values come from the map (`model:<name>`, `effort:<name>`; empty effort means omit the line).
- Re-adaptation of an installed agent: the installed `model` and `effort` values are kept unless that map entry changed (`M!=M0`). An installed value that differs from the map is a local override: report it, do not treat it as drift.
- Reverse adaptation: `model:` and `effort:` lines always return to `{{model:<name>}}` and `{{effort:<name>}}`, whatever the installed value. A model change is a local edit; it never reaches the repo.

## 4. Reverse adaptation and merges (tool to repo)

Only for an installed item with local edits (the states with `I!=I0`, `formats.md` § 4) or an item the user nominates for import.

1. Invert the map (value back to placeholder) only where the value text is unambiguous. Undo frontmatter renames and re-add dropped canonical keys from the repo version.
2. Tool keys and ids found in the installed text return to the capability they implement by a reverse lookup in the `tool:*` entries of `placeholders.json` (value, or one element of a list value, back to `tool:<capability>`): the capability's plain wording or `{{tool:<capability>}}`, following the form the repo version at `S0` used at that spot. A key that two capabilities share is ambiguous: ask. Any tool-specific token with no entry triggers the unmapped protocol: propose a capability or placeholder, plain text, or an adaptation note.
3. Merge states:
   - Both changed (`S!=S0`): three-way merge of the reverse-adapted installed copy and the current repo version over the `S0` version. Keep helpful changes from both sides, never undo an intended repo change, ask on conflict.
   - Map changed, installed edited (`S=S0`, `M!=M0`): three-way merge of the reverse-adapted installed copy, the repo version and the re-rendered result (section 2 with the current map). Installed text that the old map produced and the current map cannot invert is ambiguous: ask. Edit and map change touch different text and nothing is in doubt: apply the merge, write repo and installed, and tell the user what was merged. Any overlap or doubt: ask. Never overwrite the installed edit silently.
   - The `S0` version is the commit of the item's repo history whose hash (`formats.md` § 3) equals `source_hash`. No commit matches (never committed, rewritten or shallow history): fall back to a two-way comparison of repo and installed and ask on every difference. Report uncommitted changes (`git status --short`) in the files read as base before merging.
4. Run the canonical-write checks (section 6), show the full canonical diff, and write the repo only after the user confirms (the clean merge above is reported instead).

## 5. Unmapped placeholder protocol

Stop. Show the item, the placeholder or capability and a proposed entry (for a capability: the exact tool key, a list when several keys apply). Write the entry to `placeholders.json` only after the user approves, and log the approval in `profile.md` § Confirmed decisions (with the rationale when the mapping is unusual). A placeholder or capability that is not in the vocabulary (`placeholders.md`) is a canonical defect: do not map it, report it. A capability the tool lacks: ask the user (skip, or how to emulate it), no fallback; write `null` to `placeholders.json` for it, and log the decision. The map hash changes, so every item that uses the entry is re-adapted on the next run. Never invent a value.

## 6. Canonical-write checks

Run on every canonical file written or changed:

- Only vocabulary placeholders; `{{model:*}}` and `{{effort:*}}` only in agent frontmatter.
- No tool name, vendor name, model name, tool-native tool name, tool key, MCP tool id, permission key or tool-specific action name (layering rule: maintainer guide). Capabilities are plain wording or `{{tool:<capability>}}`; third-party products are named, their tool keys never. Adaptation notes name none either.
- Frontmatter uses only canonical keys (`formats.md` § 1); no leftover `> **Adapt for tool:**` handling text beyond the note itself.
- Self-contained: no inline `@path` includes and no "see shared file" pointers (agents do not follow references). Replace a pointer with the referenced content when it can be resolved; otherwise ask.
- Frontmatter parses; `description` is a single line; `name` (skills, agents) equals the skill folder or agent file stem. Invalid frontmatter: ask.

## 7. Verify checklist

Run after writing; report each item.

1. Every canonical item not excluded for this tool is in the registry and installed.
2. No `{{` placeholder or `> **Adapt for tool:**` note in any installed item or in any canonical file written this run.
3. Every placeholder used has a `placeholders.json` entry and every capability used (including the read-only set for a `readonly` agent) has a `tool:*` entry in `placeholders.json`, a key or a confirmed `null`.
4. Recomputed `I` equals the registry `installed_hash` and recomputed `S` equals `source_hash` for items written; installed-side edits found elsewhere are flagged, not overwritten.
5. Registry entries without a repo item are listed as removal candidates.
6. Foreign items are unchanged (count and hash spot-check of a sample).
7. Items stored through a non-file mechanism are re-listed through that mechanism and compared by hash; an unreachable mechanism is reported as pending.
8. Name and tool-token sweep over every repo item (all files under `skills/`, `agents/`, `rules/`, not only those written this run), using the machine-local name lint of the maintainer guide § 6. Report hits; never auto-fix.
