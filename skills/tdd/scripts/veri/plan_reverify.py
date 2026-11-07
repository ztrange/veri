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
    named = re.match(r"issue-(\d+)", os.path.basename(argv[0]))
    if not named:
        print("plan-reverify.sh: ledger name must match issue-<n>: " + argv[0], file=sys.stderr)
        return 2
    issue = int(named.group(1))
    events = os.path.join(os.path.dirname(argv[0]), "events.jsonl")
    if not os.path.exists(events):
        return 0
    passes = [e["ts"] for e in read_events(events)
              if e.get("issue", issue) == issue and e.get("event") == "verdict" and e.get("phase") == "plan" and e.get("verdict") == "PASS"]
    if not passes:
        return 0
    plan = git("log", "-1", "--format=%at", "--grep=^plan:", "--",argv[0], capture_output=True, text=True)
    if not plan.stdout.strip():
        print("plan-reverify.sh: no plan: commit in the history of " + argv[0], file=sys.stderr)
        return 2
    # A tie counts as newer (exit 0, re-verify): a plan: commit in the PASS's own second may postdate it.
    if int(plan.stdout) < max(passes):
        return 3
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
