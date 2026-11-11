"""adjudicate.sh's budget and record commands, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

USAGE = "usage: adjudicate.sh --check-budget | left <n> | record <n> <cause> <leaf-output>"


def main(argv):
    if argv == ["--check-budget"]:
        budget = os.environ.get("VERI_ADJUDICATE_BUDGET", "2")
        if not budget.isdigit():
            print(f"VERI_ADJUDICATE_BUDGET must be a non-negative whole number, got {budget!r}", file=sys.stderr)
            return 2
        return 0
    if len(argv) == 2 and argv[0] == "left":
        spent = 0
        with open(".tdd/events.jsonl") as f:
            for line in f:
                e = json.loads(line)
                if str(e.get("issue")) != argv[1]:
                    continue
                if e.get("event") == "conductor-start":
                    spent = 0
                elif e.get("event") == "adjudicated":
                    spent += 1
        if spent < int(os.environ.get("VERI_ADJUDICATE_BUDGET", "2")):
            return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
