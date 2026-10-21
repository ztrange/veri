"""skill-edit-step.sh's entry point, run in-process."""
import contextlib
import io
import os
import subprocess
import tempfile
import sys

import event
import grade_prose
import skill_edit_guard
import tunables
import requirements
from run_verdict import SCRIPTS

USAGE = "usage: skill-edit-step.sh <issue-body-file> <unit-file>"
TABLE_HEAD = ["| ID | Requirement | Why |", "|---|---|---|"]


def _row_id(row):
    return requirements.split_cells(row)[1]


def _requirements_lines(issue):
    heading = None
    in_requirements = False
    for line in requirements.read_lines(issue):
        if line.startswith("## "):
            in_requirements, heading = line[3:].strip() == "Requirements", None
        elif in_requirements:
            if line.startswith("### "):
                heading = line[4:].strip()
            yield heading, line


def _issue_rows(issue, unit):
    rows = [line for heading, line in _requirements_lines(issue)
            if heading in (unit, unit + " (new)") and line.startswith("|")]
    return rows[2:]


def _unknown_heading(issue):
    for heading, line in _requirements_lines(issue):
        if line.startswith("### ") and not heading.endswith(" (new)") and not os.path.exists(heading):
            return heading
    return None


def _write(path, lines):
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines))


def _trimmed(lines):
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def _claimed(path, unit):
    return os.path.exists(path) and requirements.claims(path, unit)


def _append_section(path, unit, table):
    existing = _trimmed(requirements.read_lines(path)) if os.path.exists(path) else []
    _write(path, existing + [""] * bool(existing) + ["## " + unit, ""] + table + [""])


def _write_list(path, unit, rows):
    _append_section(path, unit, TABLE_HEAD + rows)


def _create(unit, path, rows):
    os.makedirs(os.path.dirname(unit) or ".", exist_ok=True)
    open(unit, "w").close()
    _write_list(path, unit, rows)


def _move_table(unit, path):
    lines = requirements.read_lines(unit)
    start = next((n for n, l in enumerate(lines) if l.strip() == "## Requirements"), None)
    if start is None:
        return False
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    table = [l for l in lines[start:end] if l.startswith("|")]
    if not table:
        return False
    _append_section(path, unit, table)
    _write(unit, _trimmed(lines[:start] + lines[end:]) + [""])
    return True


def apply(issue, unit):
    path = skill_edit_guard.list_path(unit)
    moved = not _claimed(path, unit) and os.path.exists(unit) and _move_table(unit, path)
    rows = _issue_rows(issue, unit)
    if rows and not os.path.exists(unit):
        _create(unit, path, rows)
        return True
    claimed = _claimed(path, unit)
    if not rows and not claimed:
        return moved
    if not claimed:
        _write_list(path, unit, rows)
        return moved
    have = {row.split("\t")[0] for row in claimed.splitlines()}
    new = [r for r in rows if _row_id(r) not in have]
    reworded = {_row_id(r): r for r in rows}
    lines = requirements.read_lines(path)
    last = None
    in_unit = False
    for number, line in enumerate(lines):
        if line.startswith("## "):
            in_unit = line[3:] == unit
        elif in_unit and line.startswith("|"):
            last = number
            row = reworded.get(_row_id(line), line)
            lines[number] = None if requirements.split_cells(row)[2] == "(dropped)" else row
    lines[last + 1:last + 1] = new
    _write(path, [l for l in lines if l is not None])
    return moved


_attempt = [1]


def _author(unit, path, reasons):
    rows = "".join("%s: %s\n" % tuple(r.split("\t", 1)) for r in requirements.claims(path, unit).splitlines())
    text = ("You edit the prose of %s so that it satisfies every requirement below.\n\nUnit: %s\n\n%s\n\n"
            "Requirements:\n%s\nGrader FAIL reasons:\n%s\n"
            % (unit, unit, grade_prose.unit_text(unit), rows, reasons))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    env = dict(os.environ)
    env["PATH"] = grade_prose.modern_python_dir() + env.get("PATH", "")
    try:
        return subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), "author-skill-edit-%d" % _attempt[0],
                               os.path.join(SCRIPTS, "run-leaf.sh"), f.name,
                               "--permission-mode", "bypassPermissions"], stdout=subprocess.PIPE,
                              env=env).returncode
    finally:
        os.unlink(f.name)


def _captured(main, argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(argv)
    return code, out.getvalue()


def _grade(path, unit):
    return _captured(grade_prose.main, [path, unit])


def _guard(unit, base, issue):
    code, out = _captured(skill_edit_guard.main, [unit, base])
    if code == 2:
        return 2, out
    offending = [p for p in out.splitlines() if p != issue]
    return int(bool(offending)), "".join(p + "\n" for p in offending)


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    issue, unit = argv
    budget = tunables.read("VERI_SKILL_EDIT_BUDGET", "3")
    if not (budget.isdecimal() and int(budget) >= 1):
        print("VERI_SKILL_EDIT_BUDGET must be a whole number >= 1: " + budget, file=sys.stderr)
        return 2
    unknown = _unknown_heading(issue)
    if unknown:
        print("Requirements heading names no existing unit: " + unknown, file=sys.stderr)
        return 2
    base = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    moved = apply(issue, unit)
    path = skill_edit_guard.list_path(unit)
    if not _claimed(path, unit):
        return 3
    graded, said = _grade(path, unit)
    authored = graded == 1
    with open(unit, "rb") as f:
        before = f.read()
    for attempt in range(1, int(budget) + 1):
        if graded != 1:
            break
        _attempt[0] = attempt
        if _author(unit, path, said):
            return 2
        graded, said = _guard(unit, base, issue)
        if not graded:
            graded, said = _grade(path, unit)
        if graded == 1:
            with open(unit, "wb") as f:
                f.write(before)
    if graded == 1:
        sys.stdout.write(said)
        return 1
    if graded:
        return graded
    if not authored:
        event.append(".", {}, "skill-edit-no-author", ["unit=" + unit])
    files = [path, grade_prose.graded_path(unit)] + [unit] * (authored or moved)
    subprocess.run(["git", "add", *files], check=True)
    subprocess.run(["git", "commit", "-q", "-m", "docs: requirements for %s, graded" % unit, *files], check=True)
    return 0 if authored else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
