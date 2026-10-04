#!/usr/bin/env python3
"""Convert canonical ai-config rules/agents to Cursor and Claude Code formats.

Canonical formats (repo):
  rules/<stem>.md   frontmatter: description, alwaysApply, globs   (Cursor-style superset)
  agents/<name>.md  frontmatter: name, description, cursor-model, claude-model,
                    optional: claude-effort, readonly, is_background, tools
  skills/<name>/    every text file rendered per tool; binaries copied unchanged
  models.json       model id maps, template placeholders per tool, Claude deny-list
  targets.json      optional {"skills"|"agents"|"rules": {"<name>": ["cursor"] | ["claude"]}};
                    unlisted items go to both tools

Templating (rules, agent description/body, all skill text files):
  {{#cursor}}...{{/cursor}}  kept only in the Cursor render
  {{#claude}}...{{/claude}}  kept only in the Claude render
  {{name}}                   placeholder from models.json "placeholders"[tool]
A block whose tags sit alone on their lines drops those lines; otherwise it is inline. Blocks do not nest.
  \\{{ writes a literal {{ (escape for documenting the syntax).

Machine-local state lives in ~/.ai-config/ (repo-path, local.md); see read_local().
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import re

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = json.loads((REPO_ROOT / "models.json").read_text(encoding="utf-8"))
CURSOR_TO_CLAUDE_MODEL: dict[str, str] = MODELS["cursor_to_claude"]
CLAUDE_TO_CURSOR_MODEL: dict[str, str] = MODELS["claude_to_cursor"]
TOOLS = ("claude", "cursor")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DISPLAY_TITLE_RE = re.compile(r"^#\s+([^\n]+)\n\n")

BLOCK_LINE_RE = re.compile(
    r"^[ \t]*\{\{#(cursor|claude)\}\}[ \t]*\n(.*?)^[ \t]*\{\{/\1\}\}[ \t]*(?:\n|\Z)", re.DOTALL | re.MULTILINE)
BLOCK_INLINE_RE = re.compile(r"\{\{#(cursor|claude)\}\}(.*?)\{\{/\1\}\}", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")
ESCAPED_OPEN = "\x00"
LEFTOVER_TAG_RE = re.compile(r"\{\{[#/](?:cursor|claude)\}\}")


def render_text(text: str, tool: str, label: str = "") -> str:
    def keep(m: re.Match) -> str:
        return m.group(2) if m.group(1) == tool else ""

    text = text.replace("\\{{", ESCAPED_OPEN)
    text = BLOCK_INLINE_RE.sub(keep, BLOCK_LINE_RE.sub(keep, text))
    values = MODELS["placeholders"][tool]
    text = PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), text)
    if LEFTOVER_TAG_RE.search(text):
        raise ValueError(f"unbalanced or nested template tag in {label or 'text'}")
    return text.replace(ESCAPED_OPEN, "{{")


@dataclass
class Doc:
    name: str
    fm: dict[str, str] = field(default_factory=dict)
    body: str = ""


BLOCK_SCALAR_RE = re.compile(r"^[>|][+-]?$")


def parse(text: str, name: str) -> Doc:
    """Parse `key: value` frontmatter; folded/literal block scalars (`>-`, `|`) become one line."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return Doc(name, {}, text.strip())
    fm: dict[str, str] = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if ":" not in line or line.startswith((" ", "-", "\t")):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if BLOCK_SCALAR_RE.match(v):
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                block.append(lines[i].strip())
                i += 1
            v = " ".join(b for b in block if b)
        fm[k.strip()] = v
    return Doc(name, fm, text[m.end():].strip())


def dump(fm: dict[str, str], body: str) -> str:
    head = "---\n" + "\n".join(f"{k}: {v}" for k, v in fm.items()) + "\n---\n\n" if fm else ""
    return head + body.strip() + "\n"


def globs_list(value: str) -> list[str]:
    """Split a comma-separated glob string, keeping commas inside {a,b} braces."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    parts, buf, depth = [], "", 0
    for ch in value:
        depth += ch == "{"
        depth -= ch == "}"
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [g.strip().strip("'\"") for g in parts if g.strip()]


def is_true(value: str | None) -> bool:
    return (value or "").strip().lower() == "true"


# ---- rules ----------------------------------------------------------------

def rule_to_cursor_user_rule(d: Doc) -> str:
    """Content for Cursor User Rules (title is separate): H1 + frontmatter + body."""
    return f"# {d.name}\n\n" + dump(d.fm, d.body)


def rule_to_claude(d: Doc) -> str:
    """~/.claude/rules/<stem>.md: `paths:` only when scoped by globs."""
    fm: dict[str, str] = {}
    globs = globs_list(d.fm.get("globs", ""))
    if globs and not is_true(d.fm.get("alwaysApply")):
        fm["paths"] = "[" + ", ".join(f'"{g}"' for g in globs) + "]"
    desc = d.fm.get("description")
    body = d.body if not desc else f"<!-- {desc} -->\n\n{d.body}"
    return dump(fm, body)


def rule_from_cursor_user_rule(title: str, content: str) -> Doc:
    content = DISPLAY_TITLE_RE.sub("", content, count=1)
    return parse(content, title)


def rule_from_claude(d: Doc) -> Doc:
    """Claude rule -> canonical. Lossy: alwaysApply inferred from absence of `paths`."""
    body = d.body
    m = re.match(r"<!--\s*(.*?)\s*-->\s*\n\n", body)
    desc = ""
    if m:
        desc, body = m.group(1), body[m.end():]
    fm = {"description": desc or d.name}
    paths = d.fm.get("paths")
    if paths:
        fm["alwaysApply"] = "false"
        fm["globs"] = '"' + ", ".join(globs_list(paths)) + '"'
    else:
        fm["alwaysApply"] = "true"
    return Doc(d.name, fm, body)


# ---- agents ---------------------------------------------------------------

def agent_to_cursor(d: Doc) -> str:
    fm = {"name": d.fm.get("name", d.name), "description": d.fm.get("description", "")}
    model = d.fm.get("cursor-model") or CLAUDE_TO_CURSOR_MODEL.get(d.fm.get("claude-model", ""), "inherit")
    fm["model"] = model
    fm["is_background"] = d.fm.get("is_background", "false")
    fm["readonly"] = d.fm.get("readonly", "false")
    return dump(fm, d.body)


def agent_to_claude(d: Doc) -> str:
    fm = {"name": d.fm.get("name", d.name), "description": d.fm.get("description", "")}
    model = d.fm.get("claude-model") or CURSOR_TO_CLAUDE_MODEL.get(d.fm.get("cursor-model", ""), "inherit")
    fm["model"] = model
    if d.fm.get("claude-effort"):
        fm["effort"] = d.fm["claude-effort"]
    if "tools" in d.fm:
        fm["tools"] = d.fm["tools"]
    elif is_true(d.fm.get("readonly")):
        fm["tools"] = "Read, Grep, Glob, Bash"
    if is_true(d.fm.get("is_background")):
        fm["background"] = "true"
    return dump(fm, d.body)


def agent_from_cursor(d: Doc) -> Doc:
    fm = {"name": d.fm.get("name", d.name), "description": d.fm.get("description", "")}
    model = d.fm.get("model", "")
    if model and model != "inherit":
        fm["cursor-model"] = model
        if model in CURSOR_TO_CLAUDE_MODEL:
            fm["claude-model"] = CURSOR_TO_CLAUDE_MODEL[model]
    for k in ("is_background", "readonly"):
        if k in d.fm:
            fm[k] = d.fm[k]
    return Doc(d.name, fm, d.body)


def agent_from_claude(d: Doc) -> Doc:
    fm = {"name": d.fm.get("name", d.name), "description": d.fm.get("description", "")}
    model = d.fm.get("model", "")
    if model and model != "inherit":
        fm["claude-model"] = model
        if model in CLAUDE_TO_CURSOR_MODEL:
            fm["cursor-model"] = CLAUDE_TO_CURSOR_MODEL[model]
    if d.fm.get("effort"):
        fm["claude-effort"] = d.fm["effort"]
    if "tools" in d.fm:
        fm["tools"] = d.fm["tools"]
    if is_true(d.fm.get("background")):
        fm["is_background"] = "true"
    return Doc(d.name, fm, d.body)


# ---- repo config / machine-local state --------------------------------------

KINDS = ("skills", "agents", "rules")


def read_targets(repo: Path) -> dict[str, dict[str, list[str]]]:
    f = repo / "targets.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def targets_for(targets: dict, kind: str, name: str) -> list[str]:
    return targets.get(kind, {}).get(name, ["claude", "cursor"])


def read_local(path: Path | None) -> dict[str, set[str]]:
    """Parse ~/.ai-config/local.md: names under `## Skills|Agents|Rules`, one per line."""
    out: dict[str, set[str]] = {k: set() for k in KINDS}
    if not path or not path.is_file():
        return out
    kind = None
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    for line in text.splitlines():
        h = re.match(r"^##\s+(\w+)", line)
        if h:
            kind = h.group(1).lower() if h.group(1).lower() in KINDS else None
        elif kind and (name := line.strip().lstrip("-* ").strip()):
            out[kind].add(name)
    return out


def tool_dirs(tool: str, home: Path) -> dict[str, Path]:
    if tool == "claude":
        c = home / ".claude"
        return {"skills": c / "skills", "agents": c / "agents", "rules": c / "rules"}
    return {"skills": home / ".agents" / "skills", "agents": home / ".cursor" / "agents"}


def ensure_dir(path: Path) -> None:
    if path.is_symlink() and not path.exists():
        sys.exit(f"error: {path} is a broken symlink -> {path.readlink()}; remove it (bootstrap.sh does) and retry")
    path.mkdir(parents=True, exist_ok=True)


def skill_files(src: Path, tool: str) -> dict[str, bytes]:
    """Skill dir as it would be installed for `tool`: text files rendered, binaries unchanged."""
    out: dict[str, bytes] = {}
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = f.relative_to(src).as_posix()
        data = f.read_bytes()
        try:
            out[rel] = render_text(data.decode("utf-8"), tool, f"{src.name}/{rel}").encode("utf-8")
        except UnicodeDecodeError:
            out[rel] = data
    return out


def hash_files(files: dict[str, bytes]) -> str:
    """Hash of file names + contents. machine-local top-level `assets/` is ignored."""
    h = hashlib.sha256()
    for rel in sorted(r for r in files if r.split("/", 1)[0] != "assets"):
        h.update(rel.encode())
        h.update(files[rel])
    return h.hexdigest()


def tree_hash(path: Path) -> str:
    return hash_files({f.relative_to(path).as_posix(): f.read_bytes() for f in path.rglob("*") if f.is_file()})


# ---- install (repo -> machine) -------------------------------------------

def read_dir(path: Path, tool: str | None = None, suffix: str = ".md") -> list[Doc]:
    """Parse docs in `path`; with `tool`, render templates for that tool first."""
    def load(p: Path) -> Doc:
        text = p.read_text(encoding="utf-8")
        return parse(render_text(text, tool, str(p)) if tool else text, p.stem)

    return [load(p) for p in sorted(path.glob(f"*{suffix}"))] if path.is_dir() else []


def wanted(kind: str, name: str, tool: str, targets: dict, skip: dict[str, set[str]],
           only: set[str] | None = None) -> bool:
    if only is not None and f"{kind}:{name}" not in only:
        return False
    return name not in skip[kind] and tool in targets_for(targets, kind, name)


def parse_only(values: list[str]) -> set[str] | None:
    """`--only skills:foo --only rules:base` -> {"skills:foo", "rules:base"}; none given -> None (everything)."""
    for v in values:
        if v.split(":", 1)[0] not in KINDS or ":" not in v:
            sys.exit(f"error: --only expects <skills|agents|rules>:<name>, got {v!r}")
    return set(values) or None


def repo_skills(repo: Path) -> list[Path]:
    src = repo / "skills"
    return sorted(p for p in src.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()) if src.is_dir() else []


def render_agent(d: Doc, tool: str) -> str:
    return agent_to_claude(d) if tool == "claude" else agent_to_cursor(d)


def install(repo: Path, tool: str, home: Path, skip: dict[str, set[str]],
            only: set[str] | None = None) -> dict[str, list[str]]:
    """Write rendered repo skills/agents (and Claude rules) to the tool's user dirs. Never deletes; `only` limits to named items."""
    out: dict[str, list[str]] = {k: [] for k in KINDS}
    dirs, targets = tool_dirs(tool, home), read_targets(repo)
    for s in repo_skills(repo):
        if wanted("skills", s.name, tool, targets, skip, only):
            ensure_dir(dirs["skills"])
            for rel, data in skill_files(s, tool).items():
                dest = dirs["skills"] / s.name / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            out["skills"].append(s.name)
    for d in read_dir(repo / "agents", tool):
        if wanted("agents", d.name, tool, targets, skip, only):
            ensure_dir(dirs["agents"])
            (dirs["agents"] / f"{d.name}.md").write_text(render_agent(d, tool), encoding="utf-8")
            out["agents"].append(d.name)
    if "rules" in dirs:
        for d in read_dir(repo / "rules", tool):
            if wanted("rules", d.name, tool, targets, skip, only):
                ensure_dir(dirs["rules"])
                (dirs["rules"] / f"{d.name}.md").write_text(rule_to_claude(d), encoding="utf-8")
                out["rules"].append(d.name)
    return out


def excluded_by_targets(targets: dict) -> dict[str, list[str]]:
    return {t: sorted(f"{k}:{n}" for k in KINDS for n in targets.get(k, {}) if t not in targets_for(targets, k, n))
            for t in TOOLS}


def inventory(repo: Path, home: Path, skip: dict[str, set[str]]) -> dict:
    """Per kind/name: which sides have it and whether each machine copy equals what install would write."""
    targets = read_targets(repo)
    skills_repo = {s.name: s for s in repo_skills(repo)}
    res: dict[str, dict] = {k: {} for k in KINDS}
    for tool in TOOLS:
        dirs = tool_dirs(tool, home)
        rules_repo = {d.name: d for d in read_dir(repo / "rules", tool)}
        agents_repo = {d.name: d for d in read_dir(repo / "agents", tool)}
        repo_items = {"skills": skills_repo, "agents": agents_repo, "rules": rules_repo}
        found: dict[str, dict[str, Path]] = {k: {} for k in KINDS}
        for k, base in dirs.items():
            if not base.is_dir():
                continue
            if k == "skills":
                found[k] = {p.name: p for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}
            else:
                found[k] = {p.stem: p for p in base.glob("*.md")}
        for k in KINDS:
            for name in set(repo_items[k]) | set(found[k]):
                if name in skip[k]:
                    continue
                e = res[k].setdefault(name, {"repo": name in repo_items[k]})
                if name in found[k]:
                    e[f"{tool}_path"] = str(found[k][name])
                if name in repo_items[k] and tool not in targets_for(targets, k, name):
                    e[tool] = "not-targeted" if name not in found[k] else "present-but-not-targeted"
                    continue
                if name not in found[k]:
                    e[tool] = "missing"
                elif name not in repo_items[k]:
                    e[tool] = "tool-specific"
                elif k == "skills":
                    same = hash_files(skill_files(skills_repo[name], tool)) == tree_hash(found[k][name])
                    e[tool] = "same" if same else "differs"
                else:
                    want = render_agent(agents_repo[name], tool) if k == "agents" else rule_to_claude(rules_repo[name])
                    e[tool] = "same" if found[k][name].read_text(encoding="utf-8") == want else "differs"
    res["excluded"] = excluded_by_targets(targets)
    return res


# ---- verify ---------------------------------------------------------------

def self_check() -> list[str]:
    errors = []
    sample = "a{{#cursor}}C{{/cursor}}{{#claude}}L{{/claude}} {{impl_agent_model}}\n{{#cursor}}\nonly\n{{/cursor}}\nend\n"
    got = {t: render_text(sample, t) for t in TOOLS}
    want = {"cursor": f"aC {MODELS['placeholders']['cursor']['impl_agent_model']}\nonly\nend\n",
            "claude": f"aL {MODELS['placeholders']['claude']['impl_agent_model']}\nend\n"}
    for t in TOOLS:
        if got[t] != want[t]:
            errors.append(f"self-check: template render for {t} gave {got[t]!r}")
    try:
        render_text("{{#cursor}}x", "claude")
        errors.append("self-check: unbalanced tag was not rejected")
    except ValueError:
        pass
    return errors


SOURCE_MODEL_ID_RE = re.compile(r"composer-[\w.\[\]=-]+|gpt-5[\w.\[\]=-]*|gemini-[\w.\[\]=-]+|claude-(?:opus|sonnet|haiku)-[\w.\[\]=-]+")


def lint_source_model_ids(repo: Path) -> tuple[list[str], list[str]]:
    errors, notes = [], []
    files = [p for sub in ("rules", "agents", "skills") for p in sorted((repo / sub).rglob("*")) if p.is_file() and p.suffix in {".md", ".txt", ".json", ".yaml", ".yml"}]
    for f in files:
        rel = f.relative_to(repo)
        text = f.read_text(encoding="utf-8", errors="ignore")
        text = "\n".join(l for l in text.split("\n") if not re.match(r"\s*(cursor|claude)-model:", l))
        shared = BLOCK_INLINE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), BLOCK_LINE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text))
        for n, line in enumerate(shared.split("\n"), 1):
            for m in SOURCE_MODEL_ID_RE.finditer(line):
                if m.group(0).startswith("composer-"):
                    errors.append(f"shared-source: {rel}:{n} hardcodes model id {m.group(0)!r} outside a template block")
        for m in BLOCK_LINE_RE.finditer(text):
            if m.group(1) == "cursor":
                base = text.count("\n", 0, m.start())
                for off, line in enumerate(m.group(0).split("\n")):
                    for mm in SOURCE_MODEL_ID_RE.finditer(line):
                        notes.append(f"review: {rel}:{base + off + 1} hardcodes model id {mm.group(0)!r} in a cursor block (prefer a placeholder if the text is shared)")
    return errors, notes


def verify(repo: Path, tool: str, home: Path, skip: dict[str, set[str]],
           only: set[str] | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, notes) for `tool`: deny-list on rendered output, missing items, installed-vs-rendered drift."""
    errors, notes = self_check(), []
    src_errors, src_notes = lint_source_model_ids(repo)
    errors += src_errors
    notes += src_notes
    targets, dirs = read_targets(repo), tool_dirs(tool, home)
    deny = [re.compile(p, re.IGNORECASE) for p in MODELS.get("deny", {}).get(tool, [])]

    def lint(label: str, text: str) -> None:
        for rx in deny:
            if m := rx.search(text):
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"deny-list: {label}:{line} matches {rx.pattern!r} ({m.group(0)!r})")

    for ident in excluded_by_targets(targets)[tool]:
        notes.append(f"intentionally excluded from {tool} (targets.json): {ident}")

    expected: dict[tuple[str, str], dict[str, bytes]] = {}
    try:
        for s in repo_skills(repo):
            if wanted("skills", s.name, tool, targets, skip, only):
                expected[("skills", s.name)] = skill_files(s, tool)
        for d in read_dir(repo / "agents", tool):
            if wanted("agents", d.name, tool, targets, skip, only):
                expected[("agents", d.name)] = {f"{d.name}.md": render_agent(d, tool).encode("utf-8")}
        if "rules" in dirs:
            for d in read_dir(repo / "rules", tool):
                if wanted("rules", d.name, tool, targets, skip, only):
                    expected[("rules", d.name)] = {f"{d.name}.md": rule_to_claude(d).encode("utf-8")}
    except ValueError as exc:
        return errors + [f"template: {exc}"], notes

    for (kind, name), files in sorted(expected.items()):
        for rel, data in files.items():
            lint(f"source {kind}/{name}/{rel}", data.decode("utf-8", errors="ignore"))
        base = dirs[kind]
        root = base / name if kind == "skills" else base
        if not (root.is_dir() if kind == "skills" else (base / f"{name}.md").is_file()):
            errors.append(f"missing: {kind}:{name} is targeted at {tool} but not installed in {base}")
            continue
        for rel, data in files.items():
            f = root / rel
            if not f.is_file():
                errors.append(f"missing: {f}")
                continue
            if f.read_bytes() != data:
                errors.append(f"differs: {f} (installed file does not equal rendered output)")
            lint(f"installed {f}", f.read_text(encoding="utf-8", errors="ignore"))
    if tool == "cursor":
        notes.append("Cursor User Rules are not files: verify them from Cursor via export-rules")
    return errors, notes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--repo", type=Path, required=True)
        p.add_argument("--home", type=Path, default=Path.home())
        p.add_argument("--local-file", type=Path, default=None, help="default: <home>/.ai-config/local.md")
        p.add_argument("--only", action="append", default=[], metavar="KIND:NAME",
                       help="limit to named items, e.g. --only skills:commit --only rules:base (repeatable)")

    e = sub.add_parser("export-rules", help="Print repo rules as JSON [{title, content}] for Cursor User Rules (cursor_dialog MCP)")
    common(e)

    i = sub.add_parser("install", help="Write rendered repo skills/agents (and Claude rules) to a tool's user dirs")
    common(i)
    i.add_argument("--tool", choices=["claude", "cursor", "both"], required=True)

    v = sub.add_parser("inventory", help="JSON: per skill/agent/rule, state on repo vs claude vs cursor machine dirs")
    common(v)

    f = sub.add_parser("verify", help="Fail on deny-listed terms, missing targeted items, or installed files that differ from rendered output")
    common(f)
    f.add_argument("--tool", choices=list(TOOLS), required=True)

    c = sub.add_parser("import", help="Convert one machine file to canonical form on stdout")
    c.add_argument("kind", choices=["rule-claude", "agent-claude", "agent-cursor", "rule-cursor"])
    c.add_argument("path", type=Path)

    a = ap.parse_args()
    if a.cmd == "import":
        d = parse(a.path.read_text(encoding="utf-8"), a.path.stem)
        conv = {"rule-claude": rule_from_claude, "agent-claude": agent_from_claude, "agent-cursor": agent_from_cursor,
                "rule-cursor": lambda x: rule_from_cursor_user_rule(x.name, a.path.read_text(encoding="utf-8"))}[a.kind](d)
        sys.stdout.write(dump(conv.fm, conv.body))
        return
    skip = read_local(a.local_file or a.home / ".ai-config" / "local.md")
    only = parse_only(a.only)
    if a.cmd == "export-rules":
        t = read_targets(a.repo)
        print(json.dumps([{"title": d.name, "content": rule_to_cursor_user_rule(d)}
                          for d in read_dir(a.repo / "rules", "cursor") if wanted("rules", d.name, "cursor", t, skip, only)], indent=2))
    elif a.cmd == "install":
        tools = ["claude", "cursor"] if a.tool == "both" else [a.tool]
        print(json.dumps({t: install(a.repo, t, a.home, skip, only) for t in tools}, indent=2))
    elif a.cmd == "verify":
        errors, notes = verify(a.repo, a.tool, a.home, skip, only)
        for n in notes:
            print(n)
        for err in errors:
            print(f"ERROR {err}")
        print(f"verify {a.tool}: {'FAILED, ' + str(len(errors)) + ' error(s)' if errors else 'OK'}")
        sys.exit(1 if errors else 0)
    else:
        print(json.dumps(inventory(a.repo, a.home, skip), indent=2))


if __name__ == "__main__":
    main()
