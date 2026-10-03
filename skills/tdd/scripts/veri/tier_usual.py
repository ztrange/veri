"""tier-usual.sh's median, run in-process."""
import sys

from event_log import read_events

WINDOW = 10


def main(argv):
    if not argv:
        print("usage: tier-usual.sh <tier>", file=sys.stderr)
        return 2
    tier = argv[0]
    seconds = [float(line["seconds"]) for line in read_events(".tdd/events.jsonl")
               if line.get("event") == "test-run" and line.get("tier") == tier]
    window = sorted(seconds[-WINDOW:])
    middle = len(window) // 2
    usual = (window[middle - 1] + window[middle]) / 2
    print(usual)
    return 0
