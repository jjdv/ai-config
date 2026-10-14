---
name: update-harness
description: >-
  MANDATORY after creating, updating, renaming, or deleting any harness item (rule, skill, agent)
  in this tool or in the ai-config harness repo. Syncs only the named items between the repo and
  this tool in the same turn (adapt, write, hash, register, verify). Also on update-harness
  (bare sweep of this tool's registry). Narrower than merge-ai-config.
---

# update-harness

Targeted sync of **named** harness items (rules, skills, agents) between the repo and the **current tool**. Run it **in the same turn** you create, update, rename or delete one; do not ask "should I sync?". Other tools catch up when their own `merge-ai-config` runs. Unknown drift across many items, or a repo that gained items elsewhere: use `merge-ai-config`.

## Where things live

- Repo path, first match wins: (1) the workspace contains the `skills/merge-ai-config` and `skills/update-harness` directories (confirm before rewriting `repo-path`); (2) the single line of `${XDG_CONFIG_HOME:-$HOME/.config}/ai/repo-path`; (3) ask the user.
- Per-tool files in `<xdg>/ai/<tool-id>/`: `placeholders.json`, `profile.md`, `registry.json`. The tool is identified by the profile whose `## Tool` section (display name, `Tool id:` line) is the tool you run in; if more than one plausibly is, ask. Formats: `references/formats.md` § 2.
- Read `profile.md` and `registry.json` first. No profile: the tool was never bootstrapped; stop and point the user to `BOOTSTRAP.md` in the repo.
- Vocabulary: `references/placeholders.md`. Rendering, reverse adaptation, unmapped protocol, canonical-write checks, verify checklist: `references/adaptation.md`. Hash recipes and sync states: `references/formats.md` §§ 3-4. This file restates none of them.

## Scope

- Managed = listed in `registry.json`. Anything else in the tool is foreign: never read for sync, adopted, registered, edited or deleted. This holds for items in `profile.md` § Skip list and for unregistered tool items that have no repo counterpart.
- Items in `profile.md` § Excluded items get no adapt and no write: their registry entry is kept and they are listed as "excluded". An excluded item already installed stays put.
- Act only on repo items or on items the user names. A named item that exists only in the tool and not in the repo is a user-nominated import (reverse adaptation).
- Installed files are rendered output: edit the canonical repo file, not the installed copy, unless the user edited the installed copy on purpose.

### Named items with no registry entry

- No installed counterpart in this tool: `new`. Adapt, install and register only after the scope confirmation of `references/formats.md` § 4, asked in the same turn with the item names listed (not a "should I sync?" question).
- Unmanaged installed counterpart of the same name: `collision`, decided per `references/formats.md` § 4 (Collisions); any question is shaped by `references/adaptation.md` § 8. Replacements are always reported.
- In `profile.md` § Excluded items: skipped, listed as "excluded". Not in the repo and not named by the user: foreign, skipped.
- Create then sync: an item created in the repo this chat is `new`. An item created in the tool this chat and named is an import (`references/adaptation.md` § 4): canonical diff and checks first, repo written after confirmation, then registered with the installed copy.

## Modes

- **Named items** (default after an edit): the items created, changed, renamed or deleted this chat, or the names given. Ambiguous: ask once.
- **Bare run** (no item named): sweep of every registry item of this tool. Classify each, report states, apply the safe re-adaptations (repo or map changed, installed untouched), and list removal candidates, installed edits, merge cases (both changed; map changed, installed edited) and excluded items. Ownership changes wait for confirmation. Do not scan for new repo items; that is `merge-ai-config`.

## Per-item procedure

1. **Hash.** Compute `S` (canonical source), `I` (installed) and `M` (map hash) with the recipes in `references/formats.md` § 3, using `sha256sum`, `find` and `jq`; no maintained script is required (a throwaway scratch helper is allowed under `references/adaptation.md` § 2).
2. **State.** Compare with the registry's `S0`, `I0`, `M0` and read the state and action from the table in `references/formats.md` § 4.
3. **Direction.** The edit made in this chat wins. Repo or map changed: adapt repo to tool. Installed edited: reverse-adapt tool to repo. Both changed, or map changed and installed edited: merge per `references/adaptation.md` § 4 (including the fallback when `S0` cannot be recovered), ask on conflict or doubt.
4. **Adapt** per `references/adaptation.md` §§ 2-3. Capability keys come from the `tool:*` entries of `placeholders.json` (exact values) and nowhere else. A capability or placeholder without an entry follows the unmapped protocol (`references/adaptation.md` § 5): stop, propose, write only after approval and log it in `profile.md` § Confirmed decisions. A confirmed capability change re-adapts every affected item through the map hash.
5. **Reverse adaptation** (installed edit or user-nominated import): `references/adaptation.md` § 4, including tool keys found in installed text returning to capabilities. Show the full canonical diff first.
6. **Canonical-write checks.** Run `references/adaptation.md` § 6 on every canonical file written or changed; fix the text before writing (the checks include self-containment and frontmatter validity). A tool-specific token with no mapping triggers the unmapped protocol.
7. **Write** the repo file for a repo-bound change, then the installed item (a directory, a file, or a managed block in the shared file that `profile.md` § Targets names). Never write an unrendered placeholder or adaptation note to the tool.
8. **Re-hash** the written files and compare with the expected content.
9. **Registry.** Update `source_hash`, `installed_hash`, `map_hash` of the item; add an entry for a newly confirmed item; drop the entry of a deleted item.
10. **Verify** with the checklist in `references/adaptation.md` § 7 over the named items (all registry items in a sweep). An error fails the update: fix the canonical item and re-run.

Rename and delete: apply the same change to the repo item, the installed item and the registry entry in one pass (`git rm` in the repo; a managed block is removed from the shared file).

## Confirmation rules

- Ask before every ownership change: importing an installed item into the repo, replacing a colliding unmanaged item that has local edits, deleting an installed item or dropping its entry, restoring a locally deleted item, and any write to the repo that comes from an installed edit (the clean merge of `map changed, installed edited` is applied and reported instead, `references/formats.md` § 4).
- Do not ask for hash refreshes: re-adapting after a repo or map change, refreshing hashes, updating registry entries for items you just wrote.
- Never silently overwrite an installed edit: states with `I!=I0` are shown first.
- Ask with the tool's ask-user mechanism, one focused question per decision, in the main thread. Show the diff or the list that the answer is about.
- No tool equivalent for a capability the item needs: record `null` for it and report the affected items (`references/adaptation.md` § 5); ask only when two or more plausible tools exist. Never pick an emulation silently.
- Wording of every question and report follows `references/adaptation.md` § 8: plain language, no step or item numbers, data shown in full, a safe default.

## Removal candidates

An item in the registry with no repo counterpart is a removal candidate. List it with its installed path. After the user confirms, delete the installed item (file, directory or managed block) and drop its registry entry. Items the user declines stay registered and are listed again on the next run. Never delete an unregistered or foreign item.

## Errors

- Unmapped placeholder or capability: unmapped protocol (`references/adaptation.md` § 5). A placeholder or capability outside the vocabulary is a canonical defect: report it, do not map it.
- Hash mismatch after a write: stop, show both sides, do not update the registry; retry once after re-reading the files.
- Merge conflict or doubt, or `S0` not recoverable (`references/adaptation.md` § 4): ask; never guess.
- Shared file (`file` mechanism) unreadable or unwritable: retry once, then report the item as **pending** and leave its registry entry untouched; the next `merge-ai-config` or `update-harness` run applies it.
- Missing repo path or missing profile: stop and say what is missing; point to `BOOTSTRAP.md` for the profile.
- A repo that is not clean in the files you must write: report it, write only the named items.

## Report

Per item: kind, name, operation, state found, repo written or unchanged, installed written or removed, registry updated. Then the verify checklist result (each of the eight items), pending shared-file items, local overrides (model or effort differing from the map), excluded items, the foreign item count, removal candidates and open questions. End with a reminder to commit and push the repo changes so other tools can catch up through their own `merge-ai-config`.
