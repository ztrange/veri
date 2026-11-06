"""plan-reverify.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

try:
    from event_log import read_events
    from git import git
except ImportError:
    from .event_log import read_events
    from .git import git

USAGE = "usage: plan-reverify.sh <ledger-file>"


def main(argv):
    if argv:
        events = os.path.join(os.path.dirname(argv[0]), "events.jsonl")
        if not os.path.exists(events):
            return 0
        passes = [e["ts"] for e in read_events(events)
                  if e.get("event") == "verdict" and e.get("phase") == "plan" and e.get("verdict") == "PASS"]
        plan = git("log", "-1", "--format=%at", "--grep=^plan:", "--",argv[0], capture_output=True, text=True)
        if int(plan.stdout) < max(passes):
            return 3
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
