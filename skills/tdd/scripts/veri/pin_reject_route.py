"""pin-reject-route.sh's routing, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import add_ledger_step
import event
import ledger
import os
import re
import tick_ledger

USAGE = ("usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher> <target-test>\n"
         "       pin-reject-route.sh --recheck <reason-file> <ledger-file> <matcher>")


def repin_step(path):
    """The re-pin step's text, before its ` turns it red` tail, for the pin on <path>."""
    return ledger.REPIN_STEP + path + " so its recorded mutation"


def recheck(argv):
    with open(argv[0], encoding="utf-8") as handle:
        reason = handle.read()
    found = re.search(r"pin stayed green (?:under its mutation|on the before-state): (\S+)", reason)
    if found is None:
        print("revise")
        return 1
    path = found.group(1)
    step = repin_step(path)
    text = step + " turns it red"
    held = ledger.TICKED_STEP + " " + step
    if held in ledger.read_ledger(argv[1]):
        print("repin-failed " + path)
        return 1
    add_ledger_step.add(argv[1], "after", argv[2], [text])
    print("repin " + path)
    return 0


def main(argv):
    if argv[:1] == ["--recheck"]:
        return recheck(argv[1:])
    missing = argv[:1] == ["--missing-reroute"]
    if missing:
        argv = argv[1:]
    if len(argv) < 4:
        print(USAGE, file=sys.stderr)
        return 2
    if missing:
        with open(argv[0], encoding="utf-8") as handle:
            reason = handle.read()
        if ledger.BEFORE_STATE_GREEN.search(reason):
            text = ledger.read_ledger(argv[1])
            _, new = ledger.ledger_tick(text, argv[2], False)
            if new == text:
                return 3
            step = tick_ledger.changed_line(text, new).split("] ", 1)[1]
            tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(argv[1])))
            event.append(tdd_parent, event.context(os.environ), "unpinnable-missing", ["step=" + step])
            print("unpinnable-missing")
            return 2
        if "stays green" in reason:
            print("revise")
            return 1
    code = tick_ledger.tick(argv[1], argv[2], case=argv[3], retire="unpinnable", reason_file=argv[0])
    if code == 1 and missing:
        code = tick_ledger.tick(argv[1], argv[2], case=argv[3], retire="already-holds", reason_file=argv[0])
    if code == 0:
        print("retired")
    elif code == 1:
        print("revise")
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
