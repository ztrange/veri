"""suite-flakes.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys


def main(argv):
    if not argv:
        sys.stderr.write("usage: suite-flakes.sh <run-dir> [<run-dir>...]\n")
        return 2
    for run_dir in argv:
        if not os.path.isfile(os.path.join(run_dir, ".tdd", "events.jsonl")):
            sys.stderr.write(f"suite-flakes.sh: no .tdd/events.jsonl in {run_dir}\n")
            return 2
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
