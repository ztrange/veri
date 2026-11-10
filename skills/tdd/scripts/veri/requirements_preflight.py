"""requirements-preflight.sh's check of an issue's requirements rows, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
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
    for row_id in defects:
        sys.stderr.write("Requirement row ID already held with different text: %s\n" % row_id)
    return 2 if defects else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
