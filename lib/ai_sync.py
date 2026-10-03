#!/usr/bin/env python3
"""Convert canonical ai-config rules/agents to Cursor and Claude Code formats.

Canonical formats (repo):
  rules/<stem>.md   frontmatter: description, alwaysApply, globs   (Cursor-style superset)
  agents/<name>.md  frontmatter: name, description, cursor-model, claude-model,
                    optional: readonly, is_background, tools
  skills/<name>/    copied verbatim to both tools
  targets.json      optional {"skills"|"agents"|"rules": {"<name>": ["cursor"] | ["claude"]}};
                    unlisted items go to both tools

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

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DISPLAY_TITLE_RE = re.compile(r"^#\s+([^\n]+)\n\n")

CURSOR_TO_CLAUDE_MODEL = {
    "claude-opus-5-thinking-high": "opus",
    "claude-opus-5": "opus",
    "claude-sonnet-5-5": "sonnet",
    "composer-2.5": "sonnet",
}
CLAUDE_TO_CURSOR_MODEL = {
    "opus": "claude-opus-5-thinking-high",
    "sonnet": "composer-2.5",
    "haiku": "composer-2.5",
}


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


def tree_hash(path: Path) -> str:
    """Hash of a skill dir (file names + contents). machine-local `assets/` is ignored."""
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file() and "assets" not in p.relative_to(path).parts[:1]):
        h.update(str(f.relative_to(path)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


# ---- install (repo -> machine) -------------------------------------------

def read_dir(path: Path, suffix: str = ".md") -> list[Doc]:
    return [parse(p.read_text(encoding="utf-8"), p.stem) for p in sorted(path.glob(f"*{suffix}"))] if path.is_dir() else []


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
    """Write repo skills/agents (and Claude rules) to the tool's user dirs. Never deletes; `only` limits to named items."""
    out: dict[str, list[str]] = {k: [] for k in KINDS}
    dirs, targets = tool_dirs(tool, home), read_targets(repo)
    for s in repo_skills(repo):
        if wanted("skills", s.name, tool, targets, skip, only):
            ensure_dir(dirs["skills"])
            shutil.copytree(s, dirs["skills"] / s.name, dirs_exist_ok=True)
            out["skills"].append(s.name)
    for d in read_dir(repo / "agents"):
        if wanted("agents", d.name, tool, targets, skip, only):
            ensure_dir(dirs["agents"])
            (dirs["agents"] / f"{d.name}.md").write_text(render_agent(d, tool), encoding="utf-8")
            out["agents"].append(d.name)
    if "rules" in dirs:
        for d in read_dir(repo / "rules"):
            if wanted("rules", d.name, tool, targets, skip, only):
                ensure_dir(dirs["rules"])
                (dirs["rules"] / f"{d.name}.md").write_text(rule_to_claude(d), encoding="utf-8")
                out["rules"].append(d.name)
    return out


def inventory(repo: Path, home: Path, skip: dict[str, set[str]]) -> dict:
    """Per kind/name: which sides have it and whether each machine copy equals what install would write."""
    targets = read_targets(repo)
    rules_repo = {d.name: d for d in read_dir(repo / "rules")}
    agents_repo = {d.name: d for d in read_dir(repo / "agents")}
    skills_repo = {s.name: s for s in repo_skills(repo)}
    repo_items = {"skills": skills_repo, "agents": agents_repo, "rules": rules_repo}
    res: dict[str, dict] = {k: {} for k in KINDS}
    for tool in ("claude", "cursor"):
        dirs = tool_dirs(tool, home)
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
                if name in repo_items[k] and tool not in targets_for(targets, k, name):
                    e[tool] = "not-targeted" if name not in found[k] else "present-but-not-targeted"
                    continue
                if name not in found[k]:
                    e[tool] = "missing"
                elif name not in repo_items[k]:
                    e[tool] = "tool-specific"
                elif k == "skills":
                    e[tool] = "same" if tree_hash(skills_repo[name]) == tree_hash(found[k][name]) else "differs"
                else:
                    want = render_agent(agents_repo[name], tool) if k == "agents" else rule_to_claude(rules_repo[name])
                    e[tool] = "same" if found[k][name].read_text(encoding="utf-8") == want else "differs"
    return res


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

    i = sub.add_parser("install", help="Write repo skills/agents (and Claude rules) to a tool's user dirs")
    common(i)
    i.add_argument("--tool", choices=["claude", "cursor", "both"], required=True)

    v = sub.add_parser("inventory", help="JSON: per skill/agent/rule, state on repo vs claude vs cursor machine dirs")
    common(v)

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
                          for d in read_dir(a.repo / "rules") if wanted("rules", d.name, "cursor", t, skip, only)], indent=2))
    elif a.cmd == "install":
        tools = ["claude", "cursor"] if a.tool == "both" else [a.tool]
        print(json.dumps({t: install(a.repo, t, a.home, skip, only) for t in tools}, indent=2))
    else:
        print(json.dumps(inventory(a.repo, a.home, skip), indent=2))


if __name__ == "__main__":
    main()
