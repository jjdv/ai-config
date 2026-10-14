# Adaptation procedure

How an agent renders canonical items for the current tool, reverse-adapts installed edits, and verifies the result. Formats: `formats.md`. Placeholder meanings: `placeholders.md`. The tool is identified by `profile.md`; this file names no tool.

## 1. Inputs

Repo path from `<xdg>/ai/repo-path`; the current tool's `placeholders.json`, `profile.md`, `registry.json` in `<xdg>/ai/<tool-id>/`. A missing profile means the tool was never bootstrapped: stop and point the user to `BOOTSTRAP.md` in the repo.

## 2. Rendering (repo to tool)

1. Read the canonical item. Skip it when it is in `profile.md` § Excluded items (`<kind>:<name>` or `<kind>:*`).
2. Resolve every `{{kind:name}}` from `placeholders.json` verbatim (`tool:<capability>` too: string as is, list joined with `, `, `null` applies the recorded decision, section 5). `\{{` becomes a literal `{{`.
3. Follow each `> **Adapt for tool:**` note using `profile.md` § Rendering rules, then drop the note line. Notes and unresolved placeholders never reach installed output.
4. Apply `profile.md` § Frontmatter rules per kind (rename, drop, derive keys; omit keys the tool lacks). Expand `readonly` into the keys of the `tool:*` entries for the read-only capability set (`placeholders.md`) laid out as `profile.md` § Frontmatter rules says; a `null` entry contributes no key. A capability with no entry in `placeholders.json` follows the unmapped protocol (section 5). A `readonly: true` agent on a tool that lays out no read-only restriction is a question (in the bootstrap preview, or in the run's scope question for a new agent), never installed silently: keep it, drop the agent, or accept it without the restriction.
5. Bundled skill files are copied with the same placeholder resolution (text) or unchanged (binary); `assets/` is never copied. Where the tool installs no bundled files (`profile.md` § Rendering rules), they stay in the repo and a pointer to one in the rendered text becomes its path under the repo path. The files of `skills/update-harness/references/` are the exception: copied byte for byte with no resolution and no note handling (`formats.md` § 1).
6. Items of a `file` mechanism (`formats.md` § 2, Single-file mechanism) are written as managed blocks in the shared file `profile.md` § Targets names; the registry `installed` value is `file:<kind>:<name>`.
7. Write, re-hash (`formats.md` § 3), update the registry entry (`source_hash`, `installed_hash`, `map_hash`).

### Output layout (normative)

Byte-exact output keeps hashes stable between runs. For every rendered text file:

- LF line endings, exactly one newline at the end of the file, no trailing spaces, body bytes unchanged apart from placeholder resolution and dropped note lines. A dropped note line is removed together with one adjacent blank line when that would otherwise leave two blank lines in a row.
- Frontmatter, when the tool uses it, sits between `---` lines; keys in the order of `formats.md` § 1; a list value is written as a flow list with each element double-quoted; a scalar is written as in the canonical source unless the tool's dialect requires otherwise.
- A rule's description is written in the form `profile.md` § Frontmatter rules gives, with exactly one blank line before it (after the frontmatter) and one after it; with no frontmatter it comes first, followed by one blank line.
- An agent whose canonical source has no `model` or `effort` line, or whose map has no entry, renders the inherit form `profile.md` states for the tool (or no line when the tool has none). When the tool has no per-agent model or effort at all, the agent's `## Model` body section is omitted as well.
- Where this list does not decide a layout choice, the choice is written into `profile.md` § Rendering rules before the first write, as a default (reported, not asked); from then on `profile.md` is normative and the same choice is made every run.

An agent may use a throwaway helper in a scratch directory (never in the repo) to render or diff many items, provided it follows this section and the hashes are computed with the recipes of `formats.md` § 3.

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

Stop, except for an agent's `model:` or `effort:` placeholder with no map entry, which renders the inherit form (section 2). Show the item, the placeholder or capability and a proposed entry (for a capability: the exact tool key, a list when several keys apply). Write the entry to `placeholders.json` only after the user approves, and log the approval in `profile.md` § Confirmed decisions (with the rationale when the mapping is unusual). A placeholder or capability that is not in the vocabulary (`placeholders.md`) is a canonical defect: do not map it, report it. A capability the tool lacks: write `null` to `placeholders.json` for it, log the reason in `profile.md` § Confirmed decisions and name the affected items in the report; ask (which tool, or `null`) only when two or more plausible tools exist. No fallback is substituted. The map hash changes, so every item that uses the entry is re-adapted on the next run. Never invent a value.

## 6. Canonical-write checks

Run on every canonical file written or changed:

- Only vocabulary placeholders; `{{model:*}}` and `{{effort:*}}` only in agent frontmatter. The files of `skills/update-harness/references/` are exempt: they document the placeholder grammar and note syntax (`formats.md` § 1); every other check still applies to them.
- No tool name, vendor name, model name, tool-native tool name, tool key, MCP tool id, permission key or tool-specific action name (layering rule: maintainer guide). Capabilities are plain wording or `{{tool:<capability>}}`; third-party products are named, their tool keys never. Adaptation notes name none either.
- Frontmatter uses only canonical keys (`formats.md` § 1); no leftover `> **Adapt for tool:**` handling text beyond the note itself.
- Self-contained: no inline `@path` includes and no "see shared file" pointers (agents do not follow references). Where the tool installs bundled files (`profile.md` § Rendering rules), a pointer to a bundled file of the same item is allowed. Otherwise the pointer is replaced by the referenced content (for `update-harness` references: a read of the file from the repo path, `<xdg>/ai/repo-path`) when it can be resolved; otherwise ask.
- Frontmatter parses; `description` parses to one string (a `>-` folded block is allowed); `name` (skills, agents) equals the skill folder or agent file stem. Invalid frontmatter: ask.

## 7. Verify checklist

Run after writing; report each item.

1. Scope check: the items of the run's approved scope (named items for `update-harness`; every non-excluded repo item, minus items the user chose to skip, for the bootstrap and `merge-ai-config`) are all in the registry and installed. Count the scope, count the registered items of that scope, and report both numbers. Any difference is an error: report INCOMPLETE and list the missing items; never report the checklist as passed, and never as passed with exceptions.
2. No `{{` placeholder or `> **Adapt for tool:**` note in any installed item or in any canonical file written this run, except the verbatim files of `skills/update-harness/references/`.
3. Every placeholder used has a `placeholders.json` entry (except an agent's `model:` or `effort:`, whose absence is the inherit form) and every capability used (including the read-only set for a `readonly` agent) has a `tool:*` entry in `placeholders.json`, a key or a confirmed `null`.
4. Recomputed `I` equals the registry `installed_hash` and recomputed `S` equals `source_hash` for items written; installed-side edits found elsewhere are flagged, not overwritten.
5. Registry entries without a repo item are listed as removal candidates.
6. Foreign items are unchanged (count and hash spot-check of a sample).
7. Items of a `file` mechanism are re-read from their managed blocks and compared by hash; an unreadable file is reported as pending.
8. Name and tool-token sweep over every repo item (all files under `skills/`, `agents/`, `rules/`, not only those written this run), using the machine-local name lint of `AGENTS.md` section 6 in the repo (repo path from `<xdg>/ai/repo-path`). Report hits; never auto-fix.

## 8. Talking to the user

Applies to every question and report of the bootstrap, `merge-ai-config` and `update-harness`.

- Ask only what cannot be inferred. Whatever the specs define as a default (this file, `formats.md`, the bootstrap) is applied and reported, not asked.
- Plain language, never internal labels: no step, gate, check or item numbers, no letters standing for options. Say what is decided, why it matters, what each option does and which one is recommended (listed first, marked).
- One decision per question. A question that is free text (a name) is asked without preset options or suggestions.
- Show the data the answer is about in full, in the same message as the question: the values, the diff or the list. Never compress it to a summary the user cannot check.
- Group by cause, not by item number: name the items of each group. Per-item questions only for items with local edits.
- Name the backup path before asking about anything that overwrites. Option "keep what is installed" is always offered and leaves the item unmanaged.
- Lead with what is true (who changed what), then the group, then the recommended action. Report afterwards what was done: the reply carries only what the user needs to review or verify, the rest goes to a file whose path the reply gives (the reply-length rule of the base rule).

Collision question, shape (placeholders in angle brackets):

```
<N> of your installed <kinds> are older versions of what the repo now contains. I compared them
with the <previous version / recorded install>: <all match it exactly, so nothing was edited by you | M differ from it: your edits>.
Backup of the current files: <backup path>

<Group name> (<count>: <names>)
  Before: "<old wording>"   After: "<new wording>"
  [Update (recommended) / Keep what is installed / Show the full diff]
...
<K> more items are identical and are simply registered, nothing changes.
```

