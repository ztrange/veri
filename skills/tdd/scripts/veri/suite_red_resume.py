"""suite-red-resume.sh's check, run in-process."""
import json
import os
import sys

USAGE = "usage: suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>"
SEPARATOR = " — "


def complain(message):
    print(f"suite-red-resume.sh: {message}", file=sys.stderr)


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


def main(argv):
    if len(argv) != 4 or argv[0] != "check":
        print(USAGE, file=sys.stderr)
        return 2
    _, ledger, branch_file, default_file = argv
    try:
        cause = last_bail_cause(os.path.join(os.path.dirname(ledger), "events.jsonl"))
        with open(branch_file, encoding="utf-8") as handle:
            branch = handle.read()
        with open(default_file, encoding="utf-8") as handle:
            default = handle.read()
    except OSError as error:
        complain(f"{error.filename}: {error.strerror}")
        return 2
    if cause != "suite-red":
        complain("the last bail was not suite-red")
        return 1
    shared = [suite for suite in suites(branch) if suite in set(suites(default))]
    if shared:
        for suite in shared:
            complain(f"{suite} is red on the default branch too")
        return 1
    sys.stdout.write(branch)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
