"""plan-reverify.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

try:
    from git import git
except ImportError:
    from .git import git

USAGE = "usage: plan-reverify.sh <ledger-file>"


def main(argv):
    if argv:
        events = os.path.join(os.path.dirname(argv[0]), "events.jsonl")
        if not os.path.exists(events):
            return 0
        with open(events) as f:
            passes = [e["ts"] for e in map(json.loads, f)]
        plan = git("log", "-1", "--format=%ct", "--", argv[0], capture_output=True, text=True)
        if int(plan.stdout) < max(passes):
            return 3
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
