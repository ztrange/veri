"""requirements-preflight.sh's check of an issue's requirements rows, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import entry
import ledger
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
    clashing = []
    for unit in units:
        texts = skill_edit_step._listed_texts(skill_edit_guard.list_path(unit), unit)
        clashing += [skill_edit_step._row_id(r) for r in skill_edit_step.clashes(skill_edit_step._issue_rows(issue, unit), texts)]
    missing = []
    if len(argv) > 1:
        for line in open(argv[1]):
            step = re.sub(r"^- \[.\] ", "", line.rstrip("\n"))
            marked = step.startswith("⟦skill-edit⟧") or ledger.carries_mark(ledger.trailing_markers(step), "skill-edit")
            first = re.search(r"`([^`]+)`", line)
            unit = (ledger.unit_of(line) or (first and first.group(1))) if line.startswith("- [") and marked else None
            if unit and not any(skill_edit_step._names_unit(h, unit) for h in units):
                missing.append(unit)
    for unit in missing:
        sys.stderr.write("## Requirements has no ### heading for unit: %s\n" % unit)
    for row_id in clashing:
        sys.stderr.write("Requirement row ID already held with different text: %s\n" % row_id)
    return 2 if clashing or missing else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
