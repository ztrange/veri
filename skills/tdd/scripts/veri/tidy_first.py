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
import run_records
from entry import no_arguments
from report import report_values

USAGE = "usage: tidy-first.sh < green-report.txt"
SMELLS = os.path.join(os.path.dirname(paths.scripts_of(__file__)), "SMELLS.md")
ANSWER_RE = re.compile(
    r"(?P<refactoring>[^|]+?) *\| *(?P<file>[\w./-]+)::(?P<symbol>[A-Za-z_][\w.]*) *\| *(?P<why>\S[^|]*)")


def catalogue(path=None):
    """[(smell, [refactoring, ...])] in SMELLS.md's smell table order: its first and third columns, never the
    threshold."""
    with open(path or SMELLS, encoding="utf-8") as f:
        rows = [line.split("|") for line in f if line.startswith("| ")]
    return [(cells[1].strip(), [name.strip() for name in cells[3].split(",") if name.strip()])
            for cells in rows[1:] if len(cells) > 4]


def catalogue_refactorings(path=None):
    """Every refactoring name the third column of SMELLS.md's smell table lists."""
    return {name for _, names in catalogue(path) for name in names}


def catalogue_names(path=None):
    """The develop-green prompt's list of the catalogue's names: one `- <smell>: <refactorings>` line per smell, the
    catalogue's path first, so the leaf names a refactoring as tidy-first.sh reads it without the thresholds' bytes."""
    return (f"The smell catalogue, `{path or SMELLS}` (`Read` it for a smell's threshold), names these smells and the"
            " refactorings that answer them:\n\n"
            + "\n".join(f"- {smell}: {', '.join(names)}" for smell, names in catalogue(path)))


def _refuse(why, line):
    """The stderr line naming `line`, redacted: it becomes a verify-green REJECT's reason, which may be posted."""
    line = run_records.redact_local(line, os.getcwd())
    sys.stderr.buffer.write(f"tidy-first.sh: {why}: {line}\n".encode("utf-8", "surrogateescape"))
    sys.stderr.buffer.flush()
    return 2


def _refuse_answer(why, line):
    """Exit 1: the leaf answered, wrongly. Its line is named on stderr, nothing on stdout."""
    _refuse(why, line)
    return 1


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
        return _refuse_answer("two or more TIDY_FIRST: lines", lines[1])
    line = lines[0]
    answer = ANSWER_RE.fullmatch(report_values(line, "TIDY_FIRST", occurrence="first").strip())
    if answer is None:
        return _refuse_answer("is not <refactoring> | <file>::<symbol> | <why>", line)
    refactoring, file, symbol = answer["refactoring"].strip(), answer["file"], answer["symbol"]
    try:
        listed = catalogue_refactorings()
    except OSError as error:
        sys.stderr.write(f"tidy-first.sh: cannot read the smell catalogue {SMELLS}: {error.strerror}\n")
        return 2
    if refactoring not in listed:
        return _refuse_answer("names a refactoring SMELLS.md does not list", line)
    if file.startswith("/"):
        return _refuse_answer("names an absolute path, not one relative to the working tree", line)
    if not _in_tree(file):
        return _refuse_answer("names a file absent from the working tree", line)
    step = (f"apply {refactoring} to `{file}::{symbol}`, so the step after it is one small change;"
            " the step changes no behaviour and no test file ⟦diff-checked⟧\n")
    sys.stdout.buffer.write(step.encode())
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
