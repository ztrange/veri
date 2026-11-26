"""suite-flakes.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import event_log

USAGE = "usage: suite-flakes.sh <run-dir> [<run-dir>...]"


def main(argv):
    if not argv:
        sys.stderr.write("usage: suite-flakes.sh <run-dir> [<run-dir>...]\n")
        return 2
    for run_dir in argv:
        if not os.path.isfile(event_log.path(run_dir)):
            sys.stderr.write(f"suite-flakes.sh: no .tdd/events.jsonl in {run_dir}\n")
            return 2
    runs = {}
    for run_dir in argv:
        for event in event_log.events(run_dir, "suite-flake", skip_unreadable=True, errors="strict"):
            for name in event["files"].split(","):
                runs.setdefault(name, set()).add(os.path.basename(run_dir))
    listed = {name: sorted(seen, key=int) for name, seen in runs.items() if len(seen) > 1}
    for name in sorted(listed):
        sys.stdout.write(f"{name}: {', '.join(listed[name])}\n")
    return 0 if listed else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
