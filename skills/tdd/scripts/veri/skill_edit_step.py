"""skill-edit-step.sh's entry point, run in-process."""
import os
import subprocess
import sys

import event
import grade_prose
import requirements

USAGE = "usage: skill-edit-step.sh <issue-body-file> <unit-file>"


def _list_path(unit):
    return os.path.join(os.path.dirname(unit), "REQUIREMENTS.md")


def _row_id(row):
    return requirements.split_cells(row)[1]


def _issue_rows(issue, name):
    rows = []
    in_requirements = in_unit = False
    for line in requirements.read_lines(issue):
        if line.startswith("## "):
            in_requirements, in_unit = line[3:].strip() == "Requirements", False
        elif line.startswith("### "):
            in_unit = in_requirements and line[4:].strip() in (name, name + " (new)")
        elif in_unit and line.startswith("|"):
            rows.append(line)
    return rows[2:]


def _write(path, lines):
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines))


def _create(unit, path, name, rows):
    open(unit, "w").close()
    head = ["## " + name, "", "| ID | Requirement | Why |", "|---|---|---|"]
    existing = requirements.read_lines(path) if os.path.exists(path) else []
    while existing and existing[-1] == "":
        existing.pop()
    _write(path, existing + [""] * bool(existing) + head + rows + [""])


def apply(issue, unit):
    name = os.path.basename(unit)
    path = _list_path(unit)
    rows = _issue_rows(issue, name)
    if rows and not os.path.exists(unit):
        _create(unit, path, name, rows)
        return
    have = {row.split("\t")[0] for row in requirements.claims(path, name).splitlines()}
    new = [r for r in rows if _row_id(r) not in have]
    reworded = {_row_id(r): r for r in rows}
    lines = requirements.read_lines(path)
    last = None
    in_unit = False
    for number, line in enumerate(lines):
        if line.startswith("## "):
            in_unit = line[3:] == name
        elif in_unit and line.startswith("|"):
            last = number
            row = reworded.get(_row_id(line), line)
            lines[number] = None if requirements.split_cells(row)[2] == "(dropped)" else row
    lines[last + 1:last + 1] = new
    _write(path, [l for l in lines if l is not None])


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    issue, unit = argv
    apply(issue, unit)
    path = _list_path(unit)
    graded = grade_prose.main([path, unit])
    if graded:
        return graded
    event.append(".", {}, "skill-edit-no-author", ["unit=" + unit])
    files = [path, grade_prose.graded_path(unit)]
    subprocess.run(["git", "add", *files], check=True)
    subprocess.run(["git", "commit", "-q", "-m", "docs: requirements for %s, graded" % unit, *files], check=True)
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
