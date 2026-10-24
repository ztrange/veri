"""suite-red-resume.sh's check, run in-process."""
import json
import os
import sys

try:
    from . import add_ledger_step
    from .ledger import STEP_RE, read_ledger
except ImportError:
    import add_ledger_step
    from ledger import STEP_RE, read_ledger

USAGE = "usage: suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>"
SEPARATOR = " — "


def complain(message):
    print(f"suite-red-resume.sh: {message}", file=sys.stderr)


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def suites(text):
    return [line.split(SEPARATOR)[0] for line in text.splitlines()]


def last_bail_cause(path):
    cause = None
    with open(path, encoding="utf-8") as events:
        for line in events:
            event = json.loads(line)
            if event.get("event") == "bail":
                cause = event.get("cause")
    return cause


def insert(ledger, branch_file):
    try:
        text = read_text(branch_file)
    except OSError as error:
        complain(f"{error.filename}: {error.strerror}")
        return 2
    if not text.strip():
        complain(f"{branch_file}: empty")
        return 2
    reds = text.splitlines()
    steps = [line for line in read_ledger(ledger).split("\n") if STEP_RE.fullmatch(line)]
    unchecked = [line for line in steps if STEP_RE.fullmatch(line).group(2) == " "]
    where, anchor = ("before", unchecked[0]) if unchecked else ("after", steps[-1])
    step = "fix the full-suite failure: " + "; ".join(reds) + " ⟦suite-repair⟧"
    return add_ledger_step.main([ledger, where, anchor, step])


def main(argv):
    if len(argv) == 3 and argv[0] == "insert":
        return insert(argv[1], argv[2])
    if len(argv) != 4 or argv[0] != "check":
        print(USAGE, file=sys.stderr)
        return 2
    _, ledger, branch_file, default_file = argv
    try:
        cause = last_bail_cause(os.path.join(os.path.dirname(ledger), "events.jsonl"))
        branch = read_text(branch_file)
        default = read_text(default_file)
        if not branch.strip():
            complain(f"{branch_file}: empty")
            return 2
    except OSError as error:
        complain(f"{error.filename}: {error.strerror}")
        return 2
    if cause != "suite-red":
        complain("the last bail was not suite-red")
        return 1
    red_on_default = set(suites(default))
    shared = [suite for suite in suites(branch) if suite in red_on_default]
    if shared:
        for suite in shared:
            complain(f"{suite} is red on the default branch too")
        return 1
    sys.stdout.write(branch)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
