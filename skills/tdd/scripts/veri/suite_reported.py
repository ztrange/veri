"""suite-reported.sh's computation, run in-process."""
import os
import sys

import event

USAGE = "usage: suite-reported.sh <leaf-name>"


def main(argv):
    if len(argv) != 1 or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(f".tdd/{argv[0]}.out", encoding="utf-8", errors="replace") as out:
            accepted = ("SUITE:", "SPLIT:") if argv[0] == "develop-green" else ("SUITE:",)
            if any(line.startswith(accepted) for line in out):
                return 0
    except OSError:
        pass
    event.mark("", event.context(os.environ), "report-missing", ["name=" + argv[0], "missing=SUITE"])
    print(f"suite-reported.sh: {argv[0]} left no SUITE: line", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
