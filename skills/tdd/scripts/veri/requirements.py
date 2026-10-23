"""requirements.sh's computations, run in-process."""
import os
import re
import sys

try:
    from .markdown_sections import fenced_lines
except ImportError:
    from markdown_sections import fenced_lines

COLUMNS = ["ID", "Requirement", "Why"]
USAGE = "usage: requirements.sh units <file> | claims <file> <unit>"


def read_lines(path):
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        return f.read().split("\n")


def split_cells(line):
    cells, cell, start = [], [], 0
    for m in re.finditer(r"\\\||\|", line):
        if m.group() == "|":
            cells.append("".join(cell) + line[start:m.start()])
            cell, start = [], m.end()
        else:
            cell.append(line[start:m.start()] + m.group().replace("\\|", "|"))
            start = m.end()
    cells.append("".join(cell) + line[start:])
    return [c.strip() for c in cells]


def table_cells(line):
    line = line.strip()
    cells = split_cells(line)
    if line.startswith("|"):
        cells = cells[1:]
    if line.endswith("|"):
        cells = cells[:-1]
    return cells


def is_row(line):
    return re.search(r"(?<!\\)\|", line) is not None


def starts_table(line):
    return line.startswith("|") or table_cells(line) == COLUMNS


def headings(path):
    return [l[3:] for l in read_lines(path) if l.startswith("## ")]


def units(path):
    found = []
    for unit in headings(path):
        try:
            claims(path, unit)
        except ValueError:
            continue
        found.append(unit)
    return found


def listed_units(path):
    found = []
    for unit in headings(path):
        try:
            claims(path, unit)
        except ValueError as e:
            if not str(e).endswith("unit has no table"):
                raise
            continue
        found.append(unit)
    return found


def fail(path, number, msg):
    raise ValueError("%s:%d: %s" % (path, number, msg))


def claims(path, unit):
    rows = []
    seen = set()
    inunit = intable = skip = done = tabled = False
    head = 0
    lines = read_lines(path)
    fenced = fenced_lines("\n".join(lines)) + [False]
    for number, line in enumerate(lines, 1):
        if fenced[number - 1]:
            if inunit and intable:
                intable, done = False, True
        elif line.startswith("## "):
            inunit, intable, done = line[3:] == unit, False, False
            if inunit:
                head, tabled = number, False
        elif not inunit:
            continue
        elif re.match(r" {4}|\t", line):
            continue
        elif done and starts_table(line):
            fail(path, number, "second table")
        elif not intable and starts_table(line):
            cells = table_cells(line)
            if cells != COLUMNS:
                fail(path, number, "header lacks a column")
            intable, skip, tabled = True, True, True
        elif intable and not is_row(line):
            intable, done = False, True
        elif intable and skip:
            skip = False
        elif intable and is_row(line):
            cells = table_cells(line)
            cells += [""] * (2 - len(cells))
            if cells[0] == "":
                fail(path, number, "empty ID")
            if cells[1] == "":
                fail(path, number, "empty Requirement for " + cells[0])
            if cells[0] in seen:
                fail(path, number, "duplicate ID " + cells[0])
            seen.add(cells[0])
            rows.append("%s\t%s\n" % (cells[0], cells[1]))
    if head and not tabled:
        number = head
        fail(path, number, "unit has no table")
    return "".join(rows)


def main(argv):
    if len(argv) == 2 and argv[0] == "units":
        sys.stdout.write("".join(u + "\n" for u in units(argv[1])))
        return 0
    if len(argv) == 3 and argv[0] == "claims":
        path, unit = argv[1], argv[2]
        if not os.path.isfile(path):
            sys.stderr.write("requirements.sh: file is missing: %s\n" % path)
            return 2
        if unit not in headings(path):
            sys.stderr.write("requirements.sh: unit is not declared: %s\n" % unit)
            return 2
        try:
            out = claims(path, unit)
        except ValueError as e:
            sys.stderr.write(str(e) + "\n")
            return 2
        sys.stdout.write(out)
        return 0
    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
