"""timed-test-run.sh's command run and its one test-run event, run in-process."""
import os
import subprocess
import sys
import time

USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"
EVENT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "event.sh")


def main(argv):
    if len(argv) < 3 or not argv[0] or not argv[2]:
        sys.stderr.write(USAGE)
        sys.stderr.flush()
        return 2
    tier, suites, command = argv[0], argv[1], argv[2:]
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
    try:
        subprocess.call([EVENT, "test-run", f"tier={tier}", f"suites={suites}",
                         f"seconds={ended - started}", f"status={code}"])
    except OSError:
        pass
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
