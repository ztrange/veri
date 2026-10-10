"""production-frozen.sh's range check, run in-process."""
import subprocess
import sys

from transform_touches_tests import TEST_FILE

USAGE = "usage: production-frozen.sh <base-sha>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    base = argv[0]
    log = subprocess.run(["git", "log", "--format=", "--name-only", f"{base}..HEAD"],
                         stdout=subprocess.PIPE)
    changed = sorted({line for line in log.stdout.split(b"\n") if line and not TEST_FILE.search(line)})
    if not changed:
        return 0
    print("production changed while frozen: " + "\n".join(path.decode() for path in changed))
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
