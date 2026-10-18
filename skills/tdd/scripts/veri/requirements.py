"""requirements.sh's computations, run in-process."""
import os
import sys

COLUMNS = ["ID", "Requirement", "Why"]
USAGE = "usage: requirements.sh units <file> | claims <file> <unit>"


def read_lines(path):
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        return f.read().split("\n")


def split_cells(line):
    return [c.strip() for c in line.split("|")]


def is_header(line):
    cells = split_cells(line)
    return line.startswith("|") and len(cells) > 1 and (
        cells[1] == "ID" or "Requirement" in cells and ("Why" in cells or "ID" in cells))


def units(path):
    heading = ""
    found = []
    for line in read_lines(path):
        if line.startswith("## "):
            heading = line[3:]
        elif line.startswith("|") and split_cells(line)[1:4] == COLUMNS:
            if heading:
                found.append(heading)
            heading = ""
    return found


def claims(path, unit):
    rows = []
    seen = set()
    inunit = intable = skip = False
    for number, line in enumerate(read_lines(path), 1):
        def fail(msg):
            raise ValueError("%s:%d: %s" % (path, number, msg))
        if line.startswith("## "):
            inunit, intable = line[3:] == unit, False
        elif not inunit:
            continue
        elif is_header(line):
            cells = split_cells(line)
            if cells[1:4] != COLUMNS:
                fail("header lacks a column")
            intable, skip = True, True
        elif intable and skip:
            skip = False
        elif intable and line.startswith("|"):
            cells = split_cells(line)
            cells += [""] * (3 - len(cells))
            if cells[1] == "":
                fail("empty ID")
            if cells[2] == "":
                fail("empty Requirement for " + cells[1])
            if cells[1] in seen:
                fail("duplicate ID " + cells[1])
            seen.add(cells[1])
            rows.append("%s\t%s\n" % (cells[1], cells[2]))
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
        if unit not in [l[3:] for l in read_lines(path) if l.startswith("## ")]:
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
