"""timed-test-run.sh's command run and its one test-run event, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys
import time

import entry
import event
import tunables

TIERS = ("fast", "changed", "all", "target")
USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"


def main(argv):
    if len(argv) < 3 or not argv[0] or not argv[2]:
        return entry.refuse(usage=USAGE)
    tier, suites, command = argv[0], argv[1], argv[2:]
    if tier not in TIERS:
        return entry.refuse(f"timed-test-run.sh: tier {tier!r} is not one of {', '.join(TIERS)}")
    if tier == "changed" and command[:2] == ["make", "test"] and not any(a.startswith("TESTS=") for a in command[2:]):
        return entry.refuse("timed-test-run.sh: changed tier refuses 'make test' naming no TESTS= suites")
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
    event.mark("", event.context(tunables.environment()), "test-run", [f"tier={tier}", f"suites={suites}",
                                                           f"seconds={ended - started}", f"status={code}"], ended)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
