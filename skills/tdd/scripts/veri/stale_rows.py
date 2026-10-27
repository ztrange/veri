"""stale-rows.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import github

MARKER = "As is: these rows describe the unit's current text."


def marked_units(body):
    units, unit, lines = {}, None, []
    for line in body.splitlines() + ["## end"]:
        if line.startswith("#"):
            if unit and lines[:1] == [MARKER]:
                units[unit] = "\n".join(lines[1:])
            unit, lines = line[4:].strip(), []
        elif line.strip() or lines:
            lines.append(line)
    return units


def grade(unit, rows):
    raise NotImplementedError


def main(argv):
    number, code = argv[0], 0
    for unit, rows in marked_units(github.gh_issue_view(number, "body")).items():
        unit_code, lines = grade(unit, rows)
        code = code or unit_code
        for line in lines.splitlines():
            print("%s\t%s\t%s\t%s" % (number, line.split(":")[0], unit, line))
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
