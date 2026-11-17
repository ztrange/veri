"""surround-mutants.sh's mutant table run, in-process: every `MUTANT:` row of the reports through mutation-probe.sh."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import paths
import tunables
from entry import write

USAGE = "usage: surround-mutants.sh <report-file>… -- <command…>"
MUTANT = re.compile(r"^MUTANT:[ \t]*(.*?)[ \t\r]*$", re.MULTILINE)
RESULTS = {0: "red", 1: "survived"}


def rows(text):
    """The (file, old, new) of every `MUTANT: <file> | <old> | <new>` line of a report's text."""
    return [tuple(field.strip() for field in line.split(" | ")) for line in MUTANT.findall(text)]


def probe(row, command):
    """'red', 'survived' or 'no-answer': mutation-probe.sh's answer for one row, its stderr relayed."""
    ran = subprocess.run([os.path.join(paths.scripts_of(__file__), "mutation-probe.sh"), *row, "--", *command],
                         stdin=subprocess.DEVNULL, capture_output=True, env=tunables.without("VERI_MUTATION_RECORD"))
    return RESULTS.get(ran.returncode, "no-answer")


def main(argv):
    split = argv.index("--")
    reports, command = argv[:split], argv[split + 1:]
    table = []
    for report in reports:
        with open(report, "rb") as handle:
            table += rows(handle.read().decode("utf-8", "replace"))
    for row in table:
        write(sys.stdout, f"{' | '.join(row)} {probe(row, command)}", before=False, after=False)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
