"""skill-edit-step.sh's entry point, run in-process."""
import os
import sys

import requirements

USAGE = "usage: skill-edit-step.sh <issue-body-file> <unit-file>"


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


def _create(unit, path, name, rows):
    open(unit, "w").close()
    head = ["## " + name, "", "| ID | Requirement | Why |", "|---|---|---|"]
    existing = requirements.read_lines(path) if os.path.exists(path) else []
    while existing and existing[-1] == "":
        existing.pop()
    lines = existing + [""] * bool(existing) + head + rows + [""]
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines))


def apply(issue, unit):
    name = os.path.basename(unit)
    path = os.path.join(os.path.dirname(unit), "REQUIREMENTS.md")
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
    lines = [l for l in lines if l is not None]
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines))


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    apply(*argv)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
