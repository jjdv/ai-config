# Bootstrap

## 1. Purpose and invocation

The user says "read BOOTSTRAP.md and bootstrap this tool". Bootstrap runs once per tool. This repo is the custom harness config, the single source of truth for the harness: its items (today agents, rules and skills; the set may grow) and the processes that sync and maintain them. You adapt that canonical harness to the tool you run in, using only the generic discovery guidelines below, and you bring the whole approved scope over in the same run. Nothing tool-specific is stored in this repo: all tool-specific facts go to `${XDG_CONFIG_HOME:-$HOME/.config}/ai/<tool-id>/` (called `<xdg>/ai/<tool-id>/` below).

Formats, the placeholder vocabulary, the capability vocabulary, the block contracts, the hash recipes, the sync-state table, the collision rule, the rendering layout, the verify checklist and the rules for talking to the user are specified in `skills/update-harness/references/{formats,placeholders,adaptation}.md`. This file points to them and does not restate them; read them before Step 4.

## 2. Agent rules (mandatory)

- Ask the user only what you cannot infer. Everything that section 8 or the referenced specs define as a default is applied and reported, not asked.
- Talk to the user as `adaptation.md` § 8 says: plain language, no step or gate labels, no item numbers, the full data next to every question, one decision per question.
- Before writing anything to `<xdg>/ai/`, the tool's config or the repo, show the setup preview (section 9) in full and get one yes. The backup (section 7) is the only earlier write.
- Never invent a placeholder value: derive it from discovery, show it in the preview, write only what the preview showed.
- The tool id is the user's choice. Never assume, suggest or hard-code an id, in your questions, in prompts to subagents or in examples.
- No script is maintained in the repo. A throwaway helper in a scratch directory is allowed for bulk rendering and diffing; it follows `adaptation.md` § 2 and hashes are computed with `sha256sum` (recipes in `formats.md` § 3).
- Ask with the tool's ask-the-user mechanism in the main thread. Reads and writes may be delegated only with the exact approved payload. A subagent's report is relayed under the reply-length limits of section 13.
- Anything outside the repo's items is foreign: never touch it.

## 3. Step 1: Guard

Compute `<xdg>/ai/<tool-id>/` once the tool id is known (Step 2). If that directory exists: stop, tell the user to use `update-harness`, and do nothing else. A model change never re-runs bootstrap.

## 4. Step 2: Identify

- Tool id: one free-text question, no preset options, no suggestions: "What short name should this tool's config folder have? Lowercase letters, digits and hyphens; it is only the folder name under the shared config directory." It is not written into any repo file.
- Repo path: the directory of this file. Check whether `git status` is clean; report only, change nothing.

## 5. Step 3: Previous version?

Detect it; do not ask. Evidence: installed items that carry the names of repo items, and records of an earlier install (an install list, a state directory, hashes) that you find or the user points to. State the result in one line ("An earlier version of this harness was installed here: 26 items match repo items" or "Nothing from this harness was installed here before"). Ask only when the evidence is ambiguous, in plain words: whether the installed items came from an earlier version of this harness. Below, "migration" means an earlier version was used and "fresh install" means it was not.

## 6. Step 4: Discovery guidelines

These are generic. For each topic: how to find it, what to record, and what to do when it cannot be found (ask the user, with the evidence you have). Use the tool's own documentation, its settings, and the filesystem including existing installed items. Do not assume any value.

1. **Config locations.** Find where the tool keeps user-level agents, skills and rules, the user-level instruction file and the settings. Record per kind the layout: a file, a directory, or a non-file mechanism (for example a settings store or a protocol server).
2. **Format rules.** Find the frontmatter dialect per kind by reading existing installed items and the tool's documentation. Record the mapping from each canonical key to the tool's key, the keys that are dropped, the keys that are derived, how rules are scoped, and how model, effort, read-only and background are expressed (canonical keys: `formats.md` § 1). Copy the rule format already used by installed rules; the layout rules of `adaptation.md` § 2 decide whatever the installed items do not show.
3. **Invoking a custom agent by name.** Find how the tool spawns a custom agent: the name of the spawn mechanism and its argument form, whether the call must also carry a model, and how one agent is selected among several. This determines the `agent:<name>` and `tool:spawn-agent` entries and the `block:spawn-rule` value (contracts: `placeholders.md`).
4. **Models.** Find which models the tool offers: its picker, its documentation, a listing command. In a migration take each agent's `model` and `effort` from the installed agent definitions. In a fresh install propose one per agent by comparing its role description with the available models and show the reasoning; the user changes it in the preview. Ask a separate question only when no suitable model is available.
5. **Tool and permission model.** Find which of the tool's built-in tools implement each capability of the closed vocabulary in `placeholders.md`, and how the tool restricts them (an allowlist key, permission keys, a native read-only flag). Record per capability the exact key as the tool spells it, a list where one capability maps to several keys, and `null` where the tool has no equivalent. Propose these as `tool:<capability>` entries of `placeholders.json` (exact values, copied verbatim at render time). Only the `readonly` layout rule and the rationale of unusual mappings go into `profile.md`; `profile.md` has no capability table. Never put a tool key into a repo file.
6. **Other placeholders.** Find the tool's ask-the-user mechanism, its browser tooling, the installed directories and the temporary subdirectory used for browser output. Author each `block:*` value from discovered facts, following the contracts in `placeholders.md`.
7. **Foreign items.** Recognize as foreign: the tool's built-in agents and skills, plugin and third-party directories, tool-managed settings and instruction files, legacy backups, and old ai-config state. Put them on the skip list in `profile.md`. Never merge, sync or delete them. If unsure whether an item is foreign, treat it as foreign and mention it in the preview.

## 7. Step 5: Backup

Automatic, no question. In both cases back up the skills, agents and rules locations, the instruction file, the settings and any non-file rule export to `<xdg>/ai/backups/<tool-id>-<timestamp>/` (layout and properties: `formats.md` § 2), print the path and the file list with sizes, and do not continue until the backup exists. This is the only backup of the run: do not create a second one elsewhere.

## 8. Defaults (applied and reported, never asked)

1. Tool id: asked as free text (Step 2).
2. Previous version: detected (Step 3).
3. Every `agent:`, `model:`, `effort:`, `tool:`, `path:` and `block:` value: derived by discovery and shown as tables in the preview.
4. A capability with no tool equivalent maps to `null`; the report lists the items that use it (`formats.md` § 2). Ask only when two or more plausible tools exist.
5. Rule rendering: the format found in the tool's installed rules (comment style for the description, mapping of `globs`, a rule that is always loaded needs no frontmatter), else `adaptation.md` § 2.
6. An agent with no model or effort entry gets the tool's inherit form.
7. A capability that no item uses stays unmapped.
8. `skills/update-harness/references/` is installed verbatim and never placeholder-linted (`formats.md` § 1).
9. The backup (Step 5) is taken without asking.
10. An installed item identical to the fresh render is adopted (`formats.md` § 4).
11. An installed item equal to the previous render is replaced after the backup, with no question; the report states the replacements per cause (`formats.md` § 4).
12. Data the user is asked to approve is never compressed; the final report follows section 13.

## 9. Setup preview and questions

One message, in plain language, before any write. It contains, in full and not summarized:

- the previous-version finding and the backup path with its file list;
- the full proposed `placeholders.json` as a table (key, value, how it was found), including the `tool:<capability>` rows, the capabilities mapped to `null` with the items that use them, and the authored `block:*` texts;
- the detected locations and format rules (including the `readonly` layout), the skip list, and the tool's foreign items by name (never adopted, registered, imported or deleted);
- the scope: every repo item, all brought over by default; ask once whether any item should be left out (per-tool exclusion is the only restriction mechanism: the repo has no key that restricts an item to a tool), recorded under Excluded items in `profile.md`;
- the defaults of section 8 that were applied and anything that differs from what is installed (section 10);
- the one decision it needs: "Set this up as shown?" with the corrections the user can make.

Genuine questions, each asked only when discovery cannot settle it and each in plain words (what is decided, why, what each option does, a recommended default): the tool id, whether installed items came from an earlier version, a tool that offers two plausible keys for a capability, a missing or ambiguous config location or rule storage, no suitable model, and installed items with local edits (section 10). Record the date, the question as shown, the options and the answer in `profile.md` under Confirmed decisions.

## 10. Step 6, migration: an earlier version was used

1. Identify the items the earlier version installed: match installed names against the repo's items, and read the install records you found. Carry over old exclusions (shown in the preview).
2. An installed item that an old list names but that has no counterpart in the repo is foreign: list it, and never adopt, register, import or delete it.
3. For each matched item: render it freshly from the canonical source following `adaptation.md` § 2, then apply the collision rule of `formats.md` § 4 (Collisions): identical items are adopted, items equal to the previous render are replaced after the backup, and only items with local edits (or whose previous render cannot be established) go into one grouped question shaped as `adaptation.md` § 8 shows, default replace after backup. Put what the rule decided into the preview as a per-cause list so the user sees it before writing.
4. Never overwrite without the backup. Every replacement appears in the report.

## 11. Step 6, fresh install

All existing tool items are foreign. List them. The user may nominate items to import into the repo; this is the only tool-to-repo direction in bootstrap. Before importing, show the reverse-adapted canonical text and any new placeholder proposals. Repo edits stay uncommitted and must pass the canonical-write checks in `adaptation.md` § 6. An unmanaged tool item that has the name of a repo item is a collision: apply the rule of `formats.md` § 4 (without a previous render it becomes the grouped question).

## 12. Step 7: Write (after the preview is approved)

1. Create `<xdg>/ai/<tool-id>/`.
2. Write `placeholders.json`, `profile.md` (including its Confirmed decisions section, the rendering choices of `adaptation.md` § 2 and, when relevant, a migrated-from note) and an empty `registry.json`, in the formats of `formats.md`.
3. Write `<xdg>/ai/repo-path` if it is absent; never overwrite a different value without asking.
4. Adapt `merge-ai-config` and `update-harness` (with its `references/`, verbatim), install them and register them first, so the tool has the maintenance processes.
5. Bring over the rest of the approved scope by the procedure of the `merge-ai-config` skill (its steps for new items and collisions, writing, registry and verify). The scope was approved in the preview; do not ask it again.
6. Run the verify checklist of `adaptation.md` § 7. Its first item compares the number of items the user approved with the number registered: a difference is reported as INCOMPLETE with the missing items and the run is not called done.
7. Write `<xdg>/ai/<tool-id>/migration-report.md` (format: `formats.md` § 2).

## 13. Step 8: Hand-off

The full migration report is in `<xdg>/ai/<tool-id>/migration-report.md`. The final answer follows the reply-length rule of the base rule: it contains only what the user needs to review and verify, namely the result counts, every replacement per cause, items that need a decision, the verification result with both counts, the backup path and the path of the report file; everything else (per-item results, capability map, foreign items, decisions) stays in the file. Then tell the user: restart or reload the tool if needed; to roll back, restore the backup and delete `<xdg>/ai/<tool-id>/`. Later pulls and edits go through `merge-ai-config` and `update-harness`.

## 14. Adapting merge-ai-config and update-harness

These two items use no placeholder beyond what the approved map covers. Adapt them following `adaptation.md`. A placeholder with no entry in the approved map triggers the unmapped protocol in that file: stop, propose an entry, and write it only after the user approves.
