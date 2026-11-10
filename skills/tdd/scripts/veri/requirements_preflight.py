"""requirements-preflight.sh's check of an issue's requirements rows, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import entry
import skill_edit_guard
import skill_edit_step

USAGE = "usage: requirements-preflight.sh <issue-body-file> [<ledger>]\n"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE)
        return 2
    issue = argv[0]
    units = []
    for heading, line in skill_edit_step._requirements_lines(issue):
        if line.startswith("### ") and heading not in units:
            units.append(heading)
    defects = []
    for unit in units:
        texts = skill_edit_step._listed_texts(skill_edit_guard.list_path(unit), unit)
        defects += [skill_edit_step._row_id(r) for r in skill_edit_step.clashes(skill_edit_step._issue_rows(issue, unit), texts)]
    if len(argv) > 1:
        for line in open(argv[1]):
            m = re.search(r"`([^`]+)`", line) if line.startswith("- [") and "⟦skill-edit⟧" in line else None
            if m and not any(skill_edit_step._names_unit(h, m.group(1)) for h in units):
                sys.stderr.write("## Requirements has no ### heading for unit: %s\n" % m.group(1))
                defects.append(None)
    for row_id in filter(None, defects):
        sys.stderr.write("Requirement row ID already held with different text: %s\n" % row_id)
    return 2 if defects else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
