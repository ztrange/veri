"""production-frozen.sh's range check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from transform_touches_tests import TEST_FILE, changed_paths, refuse

USAGE = "usage: production-frozen.sh <base-sha>"


def main(argv):
    if not argv:
        return refuse(usage=USAGE)
    base = argv[0]
    paths = changed_paths(base)
    if paths is None:
        return 2
    changed = sorted({line for line in paths if line and not TEST_FILE.search(line)})
    if not changed:
        return 0
    print("production changed while frozen: " + "\n".join(path.decode() for path in changed))
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
