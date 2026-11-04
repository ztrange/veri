"""suite-flakes.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys


def main(argv):
    if not argv:
        sys.stderr.write("usage: suite-flakes.sh <run-dir> [<run-dir>...]\n")
        return 2
    logs = {run_dir: os.path.join(run_dir, ".tdd", "events.jsonl") for run_dir in argv}
    for run_dir, path in logs.items():
        if not os.path.isfile(path):
            sys.stderr.write(f"suite-flakes.sh: no .tdd/events.jsonl in {run_dir}\n")
            return 2
    runs = {}
    for run_dir, path in logs.items():
        with open(path) as log:
            for line in log:
                for name in json.loads(line)["files"].split(","):
                    runs.setdefault(name, []).append(os.path.basename(run_dir))
    listed = {name: sorted(seen) for name, seen in runs.items() if len(seen) > 1}
    for name in listed:
        sys.stdout.write(f"{name}: {', '.join(listed[name])}\n")
    return 0 if listed else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
