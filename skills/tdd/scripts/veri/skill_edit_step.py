"""skill-edit-step.sh's entry point, run in-process."""
import os
import sys

import requirements

USAGE = "usage: skill-edit-step.sh <issue-body-file> <unit-file>"


def _issue_rows(issue, name):
    rows = []
    in_requirements = in_unit = False
    for line in requirements.read_lines(issue):
        if line.startswith("## "):
            in_requirements, in_unit = line[3:].strip() == "Requirements", False
        elif line.startswith("### "):
            in_unit = in_requirements and line[4:].strip() == name
        elif in_unit and line.startswith("|"):
            rows.append(line)
    return rows[2:]


def apply(issue, unit):
    name = os.path.basename(unit)
    path = os.path.join(os.path.dirname(unit), "REQUIREMENTS.md")
    have = {row.split("\t")[0] for row in requirements.claims(path, name).splitlines()}
    rows = _issue_rows(issue, name)
    new = [r for r in rows if requirements.split_cells(r)[1] not in have]
    reworded = {requirements.split_cells(r)[1]: r for r in rows}
    lines = requirements.read_lines(path)
    last = None
    in_unit = False
    for number, line in enumerate(lines):
        if line.startswith("## "):
            in_unit = line[3:] == name
        elif in_unit and line.startswith("|"):
            last = number
            lines[number] = reworded.get(requirements.split_cells(line)[1], line)
    lines[last + 1:last + 1] = new
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
