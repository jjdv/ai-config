---
name: merge-ai-config
description: >-
  Reconcile every item of the ai-config repo with this tool, driven by this tool's registry:
  inventory by sync state, adapt, reverse-adapt installed edits, write repo, tool and registry,
  list removal candidates, verify. Use after git pull, after local edits, or on a new machine.
  Direct invocation only: /merge-ai-config (or /merge-ai-config import <name>).
disable-model-invocation: true
---

# merge-ai-config

Full reconcile between the repo and the **current tool**. Narrower runs of the same procedure for named items: `update-harness`. Formats and the sync-state table: `update-harness/references/formats.md` (§ 2 files, § 3 hashes, § 4 states). Placeholders: `update-harness/references/placeholders.md`. Adaptation, reverse adaptation, unmapped protocol, canonical-write checks and the verify checklist: `update-harness/references/adaptation.md`. This file restates none of them.

## 1. Scope

- Runs against **this tool's registry only**. Other tools catch up through their own `merge-ai-config` run; never read or write another tool's directory under `<xdg>/ai/`.
- Managed = listed in `registry.json`. A repo item that is not in the registry is **new**. Anything in the tool that is neither registered nor in the repo is **foreign**: never adopted, registered, edited or deleted, whatever an old install list says; report only a count.
- Items in `profile.md` § Excluded items are skipped: not installed, not adapted, not registered. An excluded item that is already installed stays put and is listed as "excluded". There is no per-item tool restriction key; exclusion is per tool and machine-local.
- **Import** of a foreign item into the repo happens only on explicit user nomination (`/merge-ai-config import <name>`, or the user naming it). Never automatic, never inferred from the inventory.
- Installed files are rendered output: edit canonical repo files, not installed copies, unless the user edited the installed copy on purpose (that is the "installed edited" state below).

## 2. Step 0: repo root and intent

1. Repo path: `${XDG_CONFIG_HOME:-$HOME/.config}/ai/repo-path`. If the current workspace is the repo clone (contains `skills/merge-ai-config/` and `BOOTSTRAP.md`) and differs from the file, confirm with the user before rewriting it. Missing and no workspace match: ask.
2. Read `<xdg>/ai/<tool-id>/profile.md` and `registry.json` for the tool you run in. No profile: the tool was never bootstrapped; stop and point to `BOOTSTRAP.md` in the repo.
3. `git -C <repo> status --short` and `git -C <repo> log --oneline -5` to see deliberate recent changes. Read the content of changes for items that turn out to differ, not just file names. A deleted repo item with a registry entry is a removal candidate, never silently restored.

## 3. Step 1: inventory

1. Compute `S`, `I`, `M` for every registry item with the recipes in `formats.md` § 3 (`sha256sum`, `find`, `jq`; no script) and compare with the registry's `S0`, `I0`, `M0`.
2. List repo items missing from the registry (respecting Excluded items), registry items whose repo source is gone, and repo items whose name already exists unmanaged in the tool.
3. Count foreign tool items. Do not list them by name.
4. Print a compact table: kind, name, state. Non-file items (rules stored by a mechanism that `profile.md` § Targets describes) are read through that mechanism; if it is unreachable, mark them pending and continue with the rest.

## 4. Step 2: classify and ask

Classify each item with the state table in `formats.md` § 4 and act as follows:

| State | Action |
| --- | --- |
| in sync | nothing |
| repo or map changed (`I=I0`) | re-adapt, write installed, refresh hashes; no confirmation |
| installed edited (`S=S0`, `M=M0`, `I!=I0`) | reverse-adapt, show canonical diff, write repo after yes |
| map changed, installed edited (`S=S0`, `M!=M0`, `I!=I0`) | reverse-adapt, three-way merge with the repo version and the re-rendered result (`adaptation.md` § 4); clean and unambiguous: apply and report; overlap or doubt: ask |
| both changed (`S!=S0` and `I!=I0`) | three-way merge from the `S0` version (`adaptation.md` § 4), ask on conflict, write after yes |
| installed missing | ask: restore or drop the entry |
| new (in repo, not registered, name free) | list; install and register after the user confirms scope |
| collision (in repo, not registered, name exists in tool) | ask per item: skip, adopt after diff, or replace after backup; never silent |
| removal candidate (registered, not in repo) | list with installed path; delete installed item and drop entry only after yes |
| foreign | never touched; count only |

Show the plan, then batch the ownership questions into as few asks as possible: scope of new items, collisions, removals, restores, reverse imports and merge conflicts. One focused ask per decision type, 2-4 concrete options, naming each item and showing the diff or list the answer is about. Ask with the tool's ask-user mechanism in the main thread. Do not ask about hash refreshes or about re-adapting after a repo or map change.

No tool equivalent for something an item needs: ask (skip or how to emulate); never pick a fallback.

## 5. Step 3: reverse-adapt and merge

For installed-edited, map-changed-installed-edited, both-changed and nominated-import items:

- Reverse-adapt per `adaptation.md` § 4: tool keys found in installed text return to capabilities by lookup in the `tool:*` entries of `placeholders.json` (§§ 4-5 there cover a key with no entry: unmapped protocol). Model and effort handling: `adaptation.md` § 3; a model or effort that differs from the map is a local override, never written to the repo.
- Show the full canonical diff before writing. Run the canonical-write checks (`adaptation.md` § 6) on every canonical file changed; fix the text, not the check.
- Merge per `adaptation.md` § 4: the base is the `S0` version from the repo's git history; no recoverable `S0` means a two-way comparison and a question on every difference.
- A nominated import of a foreign item: show the reverse-adapted canonical text and any new placeholder proposals first; the repo edit stays uncommitted.

## 6. Step 4: write

Only after every ask is resolved, in this order:

1. **Repo** (after the `adaptation.md` § 6 checks): canonical files under `skills/`, `agents/`, `rules/`; `git rm` for superseded paths the user confirmed.
2. **Tool**: adapted output per `adaptation.md` §§ 2-3 for files and directories; non-file items through the mechanism in `profile.md` § Targets. Never write an unrendered placeholder or adaptation note to the tool.
3. **Registry**: re-hash the written files and compare with the expected content; then update `source_hash`, `installed_hash`, `map_hash`, add entries for newly confirmed items, drop entries of deleted ones. A hash mismatch after a write: stop, show both sides, do not update that entry.

Non-file items that cannot be reached: retry once, report as **pending**, leave their registry entries untouched.

## 7. Step 5: removal candidates

Registered items with no repo counterpart: delete the installed item (file, directory or non-file entry) and its registry entry only after the user confirms. Declined ones stay registered and are listed again next run. Never delete an unregistered or foreign item.

## 8. Step 6: verify

Run the verify checklist in `adaptation.md` § 7 over every registry item. Any error fails the merge: fix the canonical item (never the installed copy) and re-run. Do not restate the checklist here.

## 9. Step 7: report

- Counts per sync state and per action taken; new, collision, removal and import decisions; items left pending (non-file); local overrides; excluded items; foreign item count.
- Verify checklist result (each item).
- `git -C <repo> status --short`.
- Remind the user to commit and push so other tools can catch up through their own `merge-ai-config`.

## 10. Self-merge

`merge-ai-config`, `update-harness` and the other maintenance skills are ordinary repo items: reconcile them like any other, with the same states and confirmations.
