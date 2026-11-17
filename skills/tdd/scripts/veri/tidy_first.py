"""tidy-first.sh's reading of a green leaf's `TIDY_FIRST:` answer, run in-process (#4118, PRD 032.4 TI2).

The one reader of the answer, as exhausted_outcome is for the exhausted leaf: it checks the line and prints the
`⟦diff-checked⟧` step it asks for. The step carries the refactoring, the file and the symbol, never the leaf's
`<why>`: the text reaches the blind diff verifier's --step, and the why is the developer's rationale.
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import paths
from entry import no_arguments
from report import report_values

USAGE = "usage: tidy-first.sh < <green-report>"
SMELLS = os.path.join(os.path.dirname(paths.scripts_of(__file__)), "SMELLS.md")
ANSWER_RE = re.compile(r"(?P<refactoring>[^|]+?) *\| *(?P<file>[\w./-]+)::(?P<symbol>[A-Za-z_][\w.]*) *\| *(?P<why>\S[^|]*)")


def catalogue_refactorings(path=SMELLS):
    """Every refactoring name the third column of SMELLS.md's smell table lists."""
    with open(path, encoding="utf-8") as f:
        rows = [line.split("|") for line in f if line.startswith("| ")]
    return {name.strip() for cells in rows[1:] if len(cells) > 4 for name in cells[3].split(",") if name.strip()}


def _refuse(why, line):
    sys.stderr.buffer.write(f"tidy-first.sh: {why}: {line}\n".encode("utf-8", "surrogateescape"))
    sys.stderr.buffer.flush()
    return 2


def _in_tree(file):
    """True when `file` is a regular file inside the working tree, symlinks resolved."""
    return os.path.realpath(file).startswith(os.path.realpath(".") + os.sep) and os.path.isfile(file)


def main(argv):
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    data = getattr(sys.stdin, "buffer", sys.stdin).read()
    text = data.decode("utf-8", "surrogateescape") if isinstance(data, bytes) else data
    lines = [line for line in text.split("\n") if report_values(line, "TIDY_FIRST", occurrence="first") is not None]
    if not lines:
        return 3
    if len(lines) > 1:
        return _refuse("two or more TIDY_FIRST: lines", lines[1])
    line = lines[0]
    answer = ANSWER_RE.fullmatch(report_values(line, "TIDY_FIRST", occurrence="first").strip())
    if answer is None:
        return _refuse("is not <refactoring> | <file>::<symbol> | <why>", line)
    refactoring, file, symbol = answer["refactoring"].strip(), answer["file"], answer["symbol"]
    if refactoring not in catalogue_refactorings():
        return _refuse("names a refactoring SMELLS.md does not list", line)
    if not _in_tree(file):
        return _refuse("names a file absent from the working tree", line)
    step = (f"apply {refactoring} to `{file}::{symbol}`, so the step after it is one small change;"
            " the step changes no behaviour and no test file ⟦diff-checked⟧\n")
    sys.stdout.buffer.write(step.encode())
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
