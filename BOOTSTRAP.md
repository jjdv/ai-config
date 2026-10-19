# Bootstrap

## 1. Purpose and invocation

The user says "read BOOTSTRAP.md and bootstrap this tool". Bootstrap runs once per tool. This repo is the custom harness config, the single source of truth for the harness: its items (today agents, rules and skills; the set may grow) and the processes that sync and maintain them. You adapt that canonical harness to the tool you run in, using only the generic discovery guidelines below, and you bring the whole approved scope over in the same run. Nothing tool-specific is stored in this repo: all tool-specific facts go to `${XDG_CONFIG_HOME:-$HOME/.config}/ai/<tool-id>/` (called `<xdg>/ai/<tool-id>/` below). On a system without XDG, use the platform's user config directory with the same relative layout and show it in the preview.

Minimum capability: the running agent must be able to read and write files and run shell commands; otherwise stop and say so. If the tool has no ask-the-user mechanism, ask in plain chat and stop until the answer arrives.

Formats, the placeholder vocabulary, the capability vocabulary, the block contracts, the hash recipes, the sync-state table, the collision rule, the rendering layout, the verify checklist and the rules for talking to the user are specified in `skills/update-harness/references/{formats,placeholders,adaptation}.md`. This file points to them and does not restate them; read them before Step 4.

## 2. Agent rules (mandatory)

- Ask the user only what you cannot infer. Everything that section 8 or the referenced specs define as a default is applied and reported, not asked.
- Talk to the user as `adaptation.md` § 8 says: plain language, no step or gate labels, no item numbers, the full data next to every question, one decision per question.
- Before writing anything to `<xdg>/ai/`, the tool's config or the repo, show the setup preview (section 11) in full and get one yes. The backup (section 7) is the only earlier write.
- Never invent a placeholder value: derive it from discovery, show it in the preview, write only what the preview showed.
- The tool id is the user's choice. Never assume, suggest or hard-code an id, in your questions, in prompts to subagents or in examples.
- The bootstrap is agent-driven and has no script. Skills may bundle scripts that declare their runtime and fall back to the manual procedure (`formats.md` § 1). A throwaway helper in a scratch directory is allowed for bulk rendering and diffing; it follows `adaptation.md` § 2 and hashes are computed with `sha256sum` (recipes in `formats.md` § 3).
- No hooks are required (`formats.md` § 1).
- Ask with the tool's ask-the-user mechanism in the main thread (plain chat, then stop until the answer arrives, when the tool has none). Reads and writes may be delegated only with the exact approved payload. A subagent's report is relayed under the reply-length limits of section 13.
- Anything outside the repo's items is foreign: never touch it.

## 3. Step 1: Identify

- Tool id: one free-text question, no preset options, no suggestions: "What short name should this tool's config folder have? Lowercase letters, digits and hyphens; it is only the folder name under the shared config directory." `repo-path` and `backups` are reserved: reject them and ask again. The id is written into no repo file; it goes into `profile.md` (Step 8).
- Repo path: the git root of the clone that contains this file. If the file was read from outside a clone, ask for the clone path.
- Run `git fetch` there. If the clone is behind its upstream, ask whether to pull first and, if yes, follow the procedure of the `pull-ai-config` skill up to its merge step (which needs a bootstrapped tool), then continue.
- If the working tree is dirty, ask whether to continue; commit first is recommended. When the user continues, record "dirty" in `profile.md` § Tool and in the migration report's Run section; later merges use the two-way fallback of `adaptation.md` § 4.

## 4. Step 2: Guard

Compute `<xdg>/ai/<tool-id>/`. If `<xdg>/ai/<tool-id>/profile.md` exists: stop, tell the user to run `merge-ai-config` (or `update-harness` for named items), and do nothing else. A model change never re-runs bootstrap. If the directory exists without `profile.md`, an earlier run was incomplete: ask whether to remove it or to resume. The directory is included in the backup of Step 5; a removal is carried out in Step 8 after the preview.

## 5. Step 3: Previous version?

Detect it; do not ask. Evidence: installed items that carry the names of repo items, and records of an earlier install (an install list, a state directory, hashes) that you find or the user points to. State the result in one line ("An earlier version of this harness was installed here: 26 items match repo items" or "Nothing from this harness was installed here before"). Ask only when the evidence is ambiguous, in plain words: whether the installed items came from an earlier version of this harness. Below, "migration" means an earlier version was used and "fresh install" means it was not.

## 6. Step 4: Discovery guidelines

These are generic. For each topic: how to find it, what to record, and what to do when it cannot be found (ask the user, with the evidence you have). Use the tool's own documentation, its settings, and the filesystem including existing installed items. Do not assume any value.

1. **Config locations and mechanism.** Find where the tool keeps user-level agents, skills and rules, the user-level instruction file and the settings. Determine per kind the mechanism of the Targets scheme (`formats.md` § 2): `dir`, `file` or `none`, and record the Targets entry. If only project-level locations exist for a kind, ask once which project root to use, record it in Targets, and add the installed paths to that project's ignore file only after approval. For `file`, find the size cap of the shared instructions file, in bytes; if the tool documents none, ask, and if the user does not know, assume none (`formats.md` § 2, Single-file mechanism).
2. **Format rules.** Find the frontmatter dialect per kind by reading existing installed items and the tool's documentation. Record the mapping from each canonical key to the tool's key, the keys that are dropped, the keys that are derived, how rules are scoped, and how `invocation`, model, effort, read-only and background are expressed (canonical keys: `formats.md` § 1). Copy the rule format already used by installed rules; the layout rules of `adaptation.md` § 2 decide whatever the installed items do not show.
3. **Bundled skill files.** Find whether the tool installs the files bundled with a skill, and record the answer in the rendering rules of `profile.md`. If it does not, bundled files stay in the repo and are read from the repo path (`adaptation.md` § 2, § 6).
4. **Invoking a custom agent by name.** Find how the tool spawns a custom agent: the name of the spawn mechanism and its argument form, whether the call must also carry a model, how one agent is selected among several, and whether built-in agents, plugin agents or other reserved selectors collide with canonical agent names. For each collision, choose a stable, non-conflicting tool-local installed name and filename, preserve the canonical repo name, and ensure the selector resolves to the custom definition rather than the built-in. Record each canonical-to-installed name and filename mapping under `profile.md` § Rendering rules and use the existing `agent:<canonical-name>` entry for the actual selector; keep the installed name, filename, rendered agent references and selector consistent during bootstrap and later adaptation or sync. This determines the `agent:<name>` and `tool:spawn-agent` entries and the `block:spawn-rule` value (contracts: `placeholders.md`).
5. **Models and effort.** Find which models and effort levels the tool offers: its picker, its documentation, a listing command. In a migration take each agent's `model` and `effort` from the installed agent definitions. In a fresh install propose one per agent by comparing its role description with the available models and show the reasoning; the user changes it in the preview. Ask a separate question only when no suitable model is available. An agent for which the tool has no per-agent model or effort uses the inherit form.
6. **Tool and permission model.** Find which of the tool's built-in tools implement each capability of the closed vocabulary in `placeholders.md`, and how the tool restricts them (an allowlist key, permission keys, a native read-only flag), including whether it can restrict an agent's tools at all (the `readonly` layout). Record per capability the exact key as the tool spells it, a list where one capability maps to several keys, and `null` where the tool has no equivalent. Propose these as `tool:<capability>` entries of `placeholders.json` (exact values, copied verbatim at render time). Only the `readonly` layout rule and the rationale of unusual mappings go into `profile.md`; `profile.md` has no capability table. Never put a tool key into a repo file.
7. **Other placeholders.** Find the tool's ask-the-user mechanism, its browser tooling, the installed directories, the temporary subdirectory used for browser output, and the literal prefix the tool puts before a skill name typed in chat (`tool:skill-prefix`; empty when it invokes by bare name). Author each `block:*` value from discovered facts, following the contracts in `placeholders.md`.
8. **Foreign items.** Recognize as foreign: the tool's built-in agents and skills, plugin and third-party directories, tool-managed settings and instruction files, legacy backups, and old ai-config state. Put them on the skip list in `profile.md`. Never merge, sync or delete them. If unsure whether an item is foreign, treat it as foreign and mention it in the preview.
9. **Unsupported kinds.** A kind with mechanism `none` degrades as `placeholders.md` § Degradation says. Skills of kind `none` install as that section describes. A tool without subagents has `tool:spawn-agent` set to `null`, its agent kind is `none` and is excluded through `agent:*` in `profile.md` § Excluded items, and delegation renders as main-thread work. A rule kind of `none` is excluded through `rule:*`.

## 7. Step 5: Backup

Automatic, no question. In every case back up the skills, agents and rules locations, the instruction file and the settings to `<xdg>/ai/backups/<tool-id>-<timestamp>/` (layout and properties: `formats.md` § 2), print the path and the file list with sha256 sums, and do not continue until the backup exists. This is the only backup of the run: do not create a second one elsewhere.

## 8. Defaults (applied and reported, never asked)

1. Every `agent:`, `model:`, `effort:`, `tool:`, `path:` and `block:` value: derived by discovery and shown as tables in the preview.
2. A capability with no tool equivalent maps to `null`; the report lists the items that use it (`formats.md` § 2). Ask only when two or more plausible tools exist.
3. Rule rendering: the format found in the tool's installed rules (comment style for the description, mapping of `globs`, a rule that is always loaded needs no frontmatter), else `adaptation.md` § 2.
4. An agent with no model or effort entry gets the tool's inherit form.
5. A capability that no item uses stays unmapped.
6. `skills/update-harness/references/` is installed verbatim and never placeholder-linted (`formats.md` § 1).
7. The backup (Step 5) is taken without asking.
8. A kind with mechanism `none` degrades or is excluded as Discovery topic 9 says, and the preview lists it.
9. An installed item identical to the fresh render is adopted (`formats.md` § 4).
10. An installed item equal to the previous render is replaced after the backup, with no question; the report states the replacements per cause (`formats.md` § 4).
11. Data the user is asked to approve is never compressed; the final report follows section 13.

## 9. Step 6 (migration): analyse, an earlier version was used

1. Identify the items the earlier version installed: match installed names against the repo's items, and read the install records you found. Carry over the earlier install's exclusions from its exclusion record, or ask which items were left out when it has no such record; the result is shown in the preview.
2. An installed item that an old list names but that has no counterpart in the repo is foreign: list it, and never adopt, register, import or delete it.
3. For each matched item: render it freshly from the canonical source following `adaptation.md` § 2, then apply the collision rule of `formats.md` § 4 (Collisions): identical items are adopted, items equal to the previous render are replaced after the backup, and only items with local edits (or whose previous render cannot be established) go into one grouped question shaped as `adaptation.md` § 8 shows, default replace after backup. Put what the rule decided into the preview as a per-cause list so the user sees it before writing.
4. Never overwrite without the backup. Every replacement appears in the report.

## 10. Step 6 (fresh install): analyse

All existing tool items without a repo counterpart are foreign. List them. A tool built-in or plugin item that has the name of a repo item remains foreign and is never replaced; list it and skip the repo item, except for canonical agents. For a canonical agent with a colliding built-in or plugin name, follow Discovery topic 4 to install it under a tool-local alias. The user may nominate items to import into the repo; this is the only tool-to-repo direction in bootstrap. Before importing, show the reverse-adapted canonical text and any new placeholder proposals. Repo edits stay uncommitted and must pass the canonical-write checks in `adaptation.md` § 6. Any other unmanaged tool item that has the name of a repo item is a collision: apply the rule of `formats.md` § 4 (without a previous render it becomes the grouped question).

## 11. Step 7: Setup preview and questions

One message, in plain language, before any write; one yes covers the whole run. It contains, in full and not summarized:

- the previous-version finding and the backup path with its file list;
- the full proposed `placeholders.json` as a table (key, value, how it was found), including the `tool:<capability>` rows, the capabilities mapped to `null` with the items that use them, and the authored `block:*` texts;
- the config directory in use, the detected locations with their mechanism (Targets entries) and format rules (including the `readonly` layout), the skip list, and the tool's foreign items by name (never adopted, registered, imported or deleted);
- each canonical-to-installed agent name and filename mapping and its actual selector, including any built-in name collisions;
- the scope: every repo item, all brought over by default; ask once whether any item should be left out (per-tool exclusion is the only restriction mechanism: the repo has no key that restricts an item to a tool), recorded under Excluded items in `profile.md`;
- the kinds the tool does not support and every degradation applied (Discovery topic 9);
- when a mechanism is `file`: the size in bytes of the default selection (the two maintenance skills and every always-on rule), the size of each other item and the cap; the other items that still fit are offered, and if the default selection alone exceeds the cap, the preview says so and asks which always-on rules to drop (`formats.md` § 2, Single-file mechanism);
- per agent with `readonly: true` on a tool that cannot restrict an agent's tools: keep it, drop it, or accept it without the restriction (`adaptation.md` § 2);
- the defaults of section 8 that were applied and anything that differs from what is installed, including collisions (sections 9 and 10);
- the one decision it needs: "Set this up as shown?" with the corrections the user can make.

Genuine questions, each asked only when discovery cannot settle it and each in plain words (what is decided, why, what each option does, a recommended default): the tool id, whether installed items came from an earlier version, a tool that offers two plausible keys for a capability, a missing or ambiguous config location or rule storage, the project root when only project-level locations exist, no suitable model, an incomplete earlier run, a dirty or outdated clone, the size-cap and `readonly` questions above, and installed items with local edits (section 9). Record the date, the question as shown, the options and the answer in `profile.md` under Confirmed decisions.

## 12. Step 8: Write (after the preview is approved)

1. Carry out an approved removal of an incomplete earlier directory (Step 2), then create `<xdg>/ai/<tool-id>/`.
2. Write `placeholders.json`, `profile.md` (including the `Tool id:` line under Tool, its Confirmed decisions section, the rendering choices of `adaptation.md` § 2 and, when relevant, a migrated-from note) and an empty `registry.json`, in the formats of `formats.md`.
3. Write `<xdg>/ai/repo-path` if it is absent; never overwrite a different value without asking.
4. Adapt `merge-ai-config` and `update-harness`, install them and register them first, so the tool has the maintenance processes. The `references/` of `update-harness` are installed verbatim where the tool installs bundled skill files; otherwise they stay in the repo and are read from the repo path (`adaptation.md` § 6).
5. Bring over the rest of the approved scope by the procedure of the `merge-ai-config` skill (its steps for new items and collisions, writing, registry and verify). The scope was approved in the preview; do not ask it again.
6. Run the verify checklist of `adaptation.md` § 7. Its first item compares the number of items the user approved with the number registered: a difference is reported as INCOMPLETE with the missing items and the run is not called done. A check that needs a missing tool (for example a JSON processor for the registry check) is reported as skipped with the reason, never failed silently.
7. Write `<xdg>/ai/<tool-id>/migration-report.md` (format: `formats.md` § 2).

## 13. Step 9: Hand-off

The full migration report is in `<xdg>/ai/<tool-id>/migration-report.md`. The final answer follows the reply-length rule of the base rule: it contains only what the user needs to review and verify, namely the result counts, every replacement per cause, items that need a decision, the verification result with both counts, the backup path and the path of the report file; everything else (per-item results, capability map, foreign items, decisions) stays in the file. Then tell the user: restart or reload the tool if needed; to roll back, delete the installed paths listed in `registry.json` and in the report's installed list (for `file` items, remove only their managed blocks), then restore the backup, then delete `<xdg>/ai/<tool-id>/`. Later pulls and edits go through `merge-ai-config` and `update-harness`.

## 14. Adapting merge-ai-config and update-harness

These two items use no placeholder beyond what the approved map covers. Adapt them following `adaptation.md`. A placeholder with no entry in the approved map triggers the unmapped protocol in that file: stop, propose an entry, and write it only after the user approves.
