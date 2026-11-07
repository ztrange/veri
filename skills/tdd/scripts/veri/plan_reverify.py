"""plan-reverify.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

try:
    from event_log import read_events
    from git import git
except ImportError:
    from .event_log import read_events
    from .git import git

USAGE = "usage: plan-reverify.sh <ledger-file>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    events = os.path.join(os.path.dirname(argv[0]), "events.jsonl")
    if not os.path.exists(events):
        return 0
    issue = int(re.match(r"issue-(\d+)", os.path.basename(argv[0])).group(1))
    passes = [e["ts"] for e in read_events(events)
              if e.get("issue", issue) == issue and e.get("event") == "verdict" and e.get("phase") == "plan" and e.get("verdict") == "PASS"]
    if not passes:
        return 0
    plan = git("log", "-1", "--format=%at", "--grep=^plan:", "--",argv[0], capture_output=True, text=True)
    if int(plan.stdout) < max(passes):
        return 3
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
