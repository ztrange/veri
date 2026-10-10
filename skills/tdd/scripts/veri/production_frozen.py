"""production-frozen.sh's range check, run in-process."""
import sys

from transform_touches_tests import TEST_FILE, changed_paths

USAGE = "usage: production-frozen.sh <base-sha>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    base = argv[0]
    log = changed_paths(base)
    if log.returncode != 0:
        return 2
    changed = sorted({line for line in log.stdout.split(b"\n") if line and not TEST_FILE.search(line)})
    if not changed:
        return 0
    print("production changed while frozen: " + "\n".join(path.decode() for path in changed))
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
