#!/usr/bin/env python3
import glob
import os
import re
import sys

TASK_ID = re.compile(r"^\d+\.\d+$")
DECISION_ID = re.compile(r"D\d+")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ORDER_ITEM = re.compile(r"^\s*\d+\.\s+`([^`]+)`")
ORDER_LOOSE = re.compile(r"^\s*\d+\.\s")
BACKTICK_SPAN = re.compile(r"`([^`]+)`")
EMPTY_VALUES = {"", "-", "—", "none", "n/a"}
SCOUT_SUMMARY = re.compile(r"^(Scout|Retro|Final)\b", re.IGNORECASE)

findings = []


def add(check, location, message):
    findings.append((check, location, message))


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().split("\n")


def sections(lines):
    result = {}
    current = None
    for number, line in enumerate(lines, 1):
        match = re.match(r"^##\s+(.*?)\s*$", line)
        if match:
            current = match.group(1)
            result.setdefault(current, [])
            continue
        if current is not None:
            result[current].append((number, line))
    return result


def find_section(secs, name):
    for title, body in secs.items():
        if title.lower().startswith(name.lower()):
            return body
    return None


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_rows(body):
    header = None
    for number, line in body:
        if not line.lstrip().startswith("|"):
            continue
        cells = split_row(line)
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells if cell):
            continue
        if header is None:
            header = [cell.lower() for cell in cells]
            continue
        yield number, header, cells


def column(header, name):
    for index, title in enumerate(header):
        if title == name:
            return index
    return None


def classify_status(status):
    lowered = status.lower()
    if "supersed" in lowered or "❌" in status or "🚫" in status:
        return "superseded"
    if "✅" in status:
        return "complete"
    if "⏸" in status:
        return "blocked"
    if "🔄" in status or "⬜" in status:
        return "open"
    return None


def parse_project_root(lines, plan_path):
    for line in lines:
        match = re.search(r"\*\*Project root:\*\*\s*`([^`]+)`", line)
        if match:
            return match.group(1)
    parts = os.path.abspath(plan_path).split(os.sep)
    if ".local" in parts:
        return os.sep.join(parts[: parts.index(".local")]) or os.sep
    return os.path.dirname(os.path.abspath(plan_path))


def parse_tasks(secs, plan_loc):
    body = find_section(secs, "Phases")
    tasks = {}
    if body is None:
        add("PARSE", plan_loc, "no `## Phases` section")
        return tasks
    phase = None
    pending = []
    headings = {}
    for number, line in body:
        heading = re.match(r"^###\s+Phase\s+(\d+)\b", line)
        if heading:
            phase = heading.group(1)
            headings.setdefault(phase, number)
        pending.append((number, line, phase))
    by_phase = {}
    for number, line, phase in pending:
        by_phase.setdefault(phase, []).append((number, line))
    for phase, rows in by_phase.items():
        for number, header, cells in table_rows(rows):
            ids = column(header, "task id")
            if ids is None:
                continue
            summary = column(header, "summary")
            status = column(header, "status")
            details = column(header, "details")
            if None in (summary, status, details) or len(cells) != len(header):
                add("PARSE", f"{plan_loc}:{number}", "phase table row does not match its header columns")
                continue
            task_id = cells[ids].strip("` ")
            location = f"{plan_loc}:{number} task {task_id}"
            if not TASK_ID.match(task_id):
                add("A5", location, f"task ID `{task_id}` is not <phase>.<sequence>")
            elif phase is not None and task_id.split(".")[0] != phase:
                add("A5", location, f"task ID `{task_id}` sits under Phase {phase}")
            if task_id in tasks:
                add("A5", location, f"duplicate task ID `{task_id}` (first at line {tasks[task_id]['line']})")
                continue
            state = classify_status(cells[status])
            if state is None:
                add("PARSE", location, f"unrecognised status `{cells[status]}`")
                state = "open"
            tasks[task_id] = {
                "line": number,
                "summary": cells[summary],
                "state": state,
                "details": cells[details],
            }
    if not headings:
        add("A5", plan_loc, "no `### Phase N` heading under `## Phases`")
    for phase, number in headings.items():
        if not any(task_id.split(".")[0] == phase for task_id in tasks):
            add("A5", f"{plan_loc}:{number}", f"Phase {phase} has no task table rows")
    if not tasks:
        add("A5", plan_loc, "no task rows found under `## Phases`")
    return tasks


def parse_order(secs, plan_loc):
    body = find_section(secs, "Implementation order")
    if body is None:
        add("A6", plan_loc, "no `## Implementation order` section")
        return []
    order = []
    for number, line in body:
        if not ORDER_LOOSE.match(line):
            continue
        match = ORDER_ITEM.match(line)
        if not match:
            add("PARSE", f"{plan_loc}:{number}", "Implementation order item is not a numbered backticked task ID")
            continue
        order.append((number, match.group(1)))
    return order


def check_order(tasks, order, plan_loc):
    seen = {}
    for number, task_id in order:
        location = f"{plan_loc}:{number} task {task_id}"
        if task_id in seen:
            add("A6", location, f"`{task_id}` listed twice in Implementation order")
            continue
        seen[task_id] = number
        task = tasks.get(task_id)
        if task is None:
            add("A7", location, f"`{task_id}` is in Implementation order but not in Phases")
        elif task["state"] in ("complete", "superseded"):
            add("A6", location, f"`{task_id}` is {task['state']} but still in Implementation order")
    for task_id, task in tasks.items():
        if task["state"] == "open" and task_id not in seen:
            add("A6", f"{plan_loc}:{task['line']} task {task_id}", f"open task `{task_id}` is missing from Implementation order")


def parse_decisions(secs, plan_loc):
    body = find_section(secs, "Decisions")
    if body is None:
        add("A8", plan_loc, "no `## Decisions` section")
        return set()
    ids = set()
    for number, header, cells in table_rows(body):
        first = cells[0].strip("` ")
        if not DECISION_ID.fullmatch(first):
            continue
        if first in ids:
            add("A8", f"{plan_loc}:{number}", f"duplicate Decision ID `{first}`")
        ids.add(first)
    return ids


def check_context_references(secs, root, plan_loc):
    body = find_section(secs, "Context references")
    if body is None:
        add("B1", plan_loc, "no `## Context references` section")
        return
    for number, header, cells in table_rows(body):
        if not header or header[0] != "file":
            continue
        location = f"{plan_loc}:{number}"
        match = re.search(r"`([^`]+)`", cells[0])
        if not match:
            add("PARSE", location, f"Context references row has no backticked path: {cells[0]}")
            continue
        path = match.group(1)
        purpose = cells[1] if len(cells) > 1 else ""
        if path.startswith(("~", "../")) or "<" in path or purpose.lower().startswith("target"):
            continue
        full = os.path.join(root, path)
        exists = bool(glob.glob(full)) if "*" in path else os.path.exists(full)
        if not exists:
            add("B1", location, f"linked path does not exist: {path}")


def note_paths(value):
    return [span for span in BACKTICK_SPAN.findall(value) if span.endswith(".md")]


def parse_reference(lines, label):
    for number, line in enumerate(lines, 1):
        match = re.match(rf"^\s*-\s*{label}:\s*(.*)$", line)
        if match:
            return number, match.group(1).strip()
    return None, None


def check_tasks(tasks, order, decisions, root, plan_dir, notes_dir, plan_loc):
    position = {task_id: index for index, (_, task_id) in enumerate(order)}
    parsed = {}
    for task_id, task in tasks.items():
        if task["state"] in ("complete", "superseded"):
            continue
        details = task["details"]
        location = f"{plan_loc}:{task['line']} task {task_id}"
        if details.strip("` ") in EMPTY_VALUES:
            continue
        link = LINK.search(details)
        if not link:
            add("PARSE", location, f"Details cell is neither `—` nor a markdown link: {details}")
            continue
        target = os.path.normpath(os.path.join(plan_dir, link.group(1)))
        if not target.endswith(".md") or not os.path.isfile(target):
            add("B4", location, f"task file not readable: {link.group(1)}")
            continue
        if os.path.commonpath([os.path.abspath(root), os.path.abspath(target)]) != os.path.abspath(root):
            add("B4", location, f"task file is outside the project root: {link.group(1)}")
            continue
        parsed[task_id] = (target, read_lines(target))

    produced = {}
    for task_id, (target, lines) in parsed.items():
        number, value = parse_reference(lines, "Notes out")
        if value is None or value.lower() in EMPTY_VALUES:
            continue
        for path in note_paths(value):
            full = os.path.normpath(os.path.join(os.path.dirname(target), path))
            produced.setdefault(full, []).append(task_id)
            if os.path.commonpath([notes_dir, full]) != notes_dir:
                add("C11", f"task {task_id} {target}:{number}", f"Notes out outside the plan notes/ folder: {path}")
        if not note_paths(value):
            add("PARSE", f"task {task_id} {target}:{number}", f"Notes out has no backticked .md path: {value}")

    for task_id, (target, lines) in parsed.items():
        task = tasks[task_id]
        where = f"task {task_id} {target}"
        number, value = parse_reference(lines, "Decisions")
        if value is not None and value.lower() not in EMPTY_VALUES:
            cited = DECISION_ID.findall(value)
            leftover = DECISION_ID.sub("", value)
            if not cited or re.sub(r"[\s,;]+", "", leftover):
                add("PARSE", f"{where}:{number}", f"Decisions line is not a list of D<n> IDs: {value}")
            for decision in cited:
                if decision not in decisions:
                    add("C9", f"{where}:{number}", f"cited Decision `{decision}` does not exist in the plan")
        number, value = parse_reference(lines, "Notes in")
        if value is not None and value.lower() not in EMPTY_VALUES:
            paths = note_paths(value)
            if not paths:
                add("PARSE", f"{where}:{number}", f"Notes in has no backticked .md path: {value}")
            for path in paths:
                full = os.path.normpath(os.path.join(os.path.dirname(target), path))
                if os.path.exists(full):
                    continue
                producers = produced.get(full, [])
                if not producers:
                    add("C10", f"{where}:{number}", f"note does not exist and no task lists it in Notes out: {path}")
                    continue
                if task_id not in position:
                    continue
                if not any(position.get(p, len(position)) < position[task_id] for p in producers):
                    add("C10", f"{where}:{number}", f"note {path} is produced only by later tasks ({', '.join(producers)})")
        report_only = SCOUT_SUMMARY.match(task["summary"]) or any("report-only" in line.lower() for line in lines)
        number_out, value_out = parse_reference(lines, "Notes out")
        if report_only and (value_out is None or value_out.lower() in EMPTY_VALUES):
            add("C11", where, "scout, retro or report-only task has no Notes out")


def main(argv):
    if len(argv) != 2:
        print("usage: check_plan_mechanical.py <plan-path>", file=sys.stderr)
        return 2
    plan_path = os.path.abspath(argv[1])
    if not os.path.isfile(plan_path):
        print(f"PARSE | {plan_path} | plan file not found")
        return 1
    lines = read_lines(plan_path)
    plan_loc = plan_path
    secs = sections(lines)
    root = parse_project_root(lines, plan_path)
    plan_dir = os.path.dirname(plan_path)
    slug = re.sub(r"-plan\.md$", "", os.path.basename(plan_path))
    notes_dir = os.path.join(plan_dir, slug, "notes")

    tasks = parse_tasks(secs, plan_loc)
    order = parse_order(secs, plan_loc)
    decisions = parse_decisions(secs, plan_loc)
    check_order(tasks, order, plan_loc)
    check_context_references(secs, root, plan_loc)
    check_tasks(tasks, order, decisions, root, plan_dir, notes_dir, plan_loc)

    for check, location, message in findings:
        print(f"{check} | {location} | {message}")
    print(f"{len(findings)} finding(s); {len(tasks)} tasks, {len(order)} in order, {len(decisions)} decisions", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
