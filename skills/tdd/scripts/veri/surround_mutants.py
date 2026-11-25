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


class Malformed(ValueError):
    """A `MUTANT:` line without three non-empty fields."""


def rows(text):
    """The (file, old, new) of every `MUTANT: <file> | <old> | <new>` line of a report's text; Malformed names the
    first line without three non-empty fields."""
    found = []
    for line in MUTANT.findall(text):
        fields = tuple(field.strip() for field in line.split(" | "))
        if len(fields) != 3 or not all(fields):
            raise Malformed(f"MUTANT: {line}")
        found.append(fields)
    return found


def refuse(message):
    write(sys.stderr, f"surround-mutants: {message}", before=False, after=False)
    return 2


def probe(row, command):
    """'red', 'survived' or 'no-answer': mutation-probe.sh's answer for one row, its stderr relayed."""
    ran = subprocess.run([os.path.join(paths.scripts_of(__file__), "mutation-probe.sh"), *row, "--", *command],
                         stdin=subprocess.DEVNULL, capture_output=True)
    if ran.returncode not in RESULTS and ran.stderr:
        write(sys.stderr, ran.stderr.decode("utf-8", "replace").rstrip("\n"), before=False, after=False)
    return RESULTS.get(ran.returncode, "no-answer")


def main(argv):
    split = argv.index("--") if "--" in argv else len(argv)
    reports, command = argv[:split], argv[split + 1:]
    if not reports or not command:
        write(sys.stderr, USAGE, before=False, after=False)
        return 2
    owed, bad = tunables.resolve("VERI_SURROUND_MUTANTS")
    if bad:
        return refuse(f"VERI_SURROUND_MUTANTS must be {bad[1]}, got '{bad[0]}'")
    table = []
    for report in reports:
        try:
            with open(report, "rb") as handle:
                table += rows(handle.read().decode("utf-8", "replace"))
        except OSError as error:
            return refuse(f"cannot read the report {report}: {error.strerror}")
        except Malformed as error:
            return refuse(f"{report}: a MUTANT: line needs three non-empty fields, <file> | <old> | <new>: {error}")
    table = list(dict.fromkeys(table))
    results = []
    for row in table:
        results.append(probe(row, command))
        write(sys.stdout, f"{' | '.join(row)} {results[-1]}", before=False, after=False)
    if "no-answer" in results:
        return 2
    if "survived" in results:
        return 1
    if len(table) < owed:
        write(sys.stdout, f"short {len(table)} of {owed}", before=False, after=False)
        return 1
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
