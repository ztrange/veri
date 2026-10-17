"""timed-test-run.sh's command run and its one test-run event, run in-process."""
import os
import subprocess
import sys
import time

import event

USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"


def _refuse(message):
    sys.stderr.write(message)
    sys.stderr.flush()
    return 2


def main(argv):
    if len(argv) < 3 or not argv[0] or not argv[2]:
        return _refuse(USAGE)
    tier, suites, command = argv[0], argv[1], argv[2:]
    if tier == "affected" and command[:2] == ["make", "test"] and not any(a.startswith("TESTS=") for a in command[2:]):
        return _refuse("timed-test-run.sh: affected tier refuses 'make test' naming no TESTS= suites\n")
    started = int(time.time())
    try:
        code = subprocess.call(command)
    except FileNotFoundError:
        code = 127
    except PermissionError:
        code = 126
    if code < 0:
        code = 128 - code
    ended = int(time.time())
    event.mark("", event.context(os.environ), "test-run", [f"tier={tier}", f"suites={suites}",
                                                           f"seconds={ended - started}", f"status={code}"], ended)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
