"""adjudicate.sh's budget and record commands, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import event
import event_log
import parse_adjudication
import tunables

USAGE = "usage: adjudicate.sh --check-budget | left <n> | record <n> <cause> <leaf-output>"


def budget():
    return tunables.get("VERI_ADJUDICATE_BUDGET")


def main(argv):
    if argv == ["--check-budget"]:
        if entry.whole_number(budget(), minimum=0) is None:
            print(f"VERI_ADJUDICATE_BUDGET must be a non-negative whole number, got {budget()!r}", file=sys.stderr)
            return 2
        return 0
    if len(argv) == 2 and argv[0] == "left":
        spent = 0
        for e in event_log.read_events(event_log.path(".")):
            if str(e.get("issue")) != argv[1]:
                continue
            if e.get("event") == "conductor-start":
                spent = 0
            elif e.get("event") == "adjudicated":
                spent += 1
        return 0 if spent < int(budget()) else 3
    if len(argv) == 4 and argv[0] == "record":
        parsed = parse_adjudication.parse(argv[3], argv[2])
        if parsed is not None and parsed[0] == "deviate" and parse_adjudication.waivable_rule(argv[2]) is None:
            parsed = ("unparsed", "deviate for a cause no waivable rule names")
        elif parsed is None:
            parsed = ("unparsed", "no ADJUDICATION line")
        outcome, reason = parsed
        code = 2 if outcome == "unparsed" else 0
        event.mark(".", event.context(tunables.with_values(VERI_ISSUE=argv[1])), "adjudicated",
                   ["cause=" + argv[2], "outcome=" + outcome.split()[0], "reason=" + reason])
        print(outcome)
        if code:
            return 2
        return {"retry": 0, "deviate": 4}.get(outcome, 1)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
