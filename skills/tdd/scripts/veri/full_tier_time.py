"""full-tier-time.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

RECORD = ".tdd/full-tier-time.json"
USAGE = "usage: full-tier-time.sh [--record <seconds>] <command>"


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    if not argv:
        return refuse()
    if argv[0] == "--record":
        if len(argv) < 3 or not argv[1].isascii() or not argv[1].isdigit():
            return refuse()
        os.makedirs(".tdd", exist_ok=True)
        with open(RECORD, "w") as f:
            json.dump({argv[2]: argv[1]}, f)
        return 0
    if not os.path.exists(RECORD):
        return 3
    with open(RECORD) as f:
        print(json.load(f)[argv[0]])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
