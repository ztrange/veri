"""pin-reject-route.sh's routing, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import add_ledger_step
import event
import ledger
import os
import tick_ledger
from report import report_values

USAGE = ("usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher> <target-test>\n"
         "       pin-reject-route.sh --recheck <reason-file> <ledger-file> <matcher>")


def repin_step(path):
    """The re-pin step's text, before its ` turns it red` tail, for the pin on <path>."""
    return ledger.REPIN_STEP + path + " so its recorded mutation"


def red_case(ledger_file, case):
    """<case>, or a bare case name joined to the TEST_PATH of develop-red.out beside the ledger when that file holds it."""
    if "::" in case or "/" in case:
        return case
    red_out = os.path.join(os.path.dirname(ledger_file), "develop-red.out")
    if not os.path.exists(red_out):
        return case
    with open(red_out, encoding="utf-8") as handle:
        path = report_values(handle.read(), "TEST_PATH", occurrence="last")
    if path is None or not holds(path, case):
        return case
    return path + "::" + case


def holds(path, name):
    """Whether the file at <path> names <name> as a whole word."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return re.search(r"\b" + re.escape(name) + r"\b", handle.read()) is not None
    except OSError:
        return False


def recheck(argv):
    with open(argv[0], encoding="utf-8") as handle:
        reason = handle.read()
    unchecked = re.search(r"not checked: (\S+) \(old text in no file of its package\)", reason)
    if unchecked is not None:
        print("not-checked " + unchecked.group(1))
        return 1
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
    case = red_case(argv[1], argv[3])
    code = tick_ledger.tick(argv[1], argv[2], case=case, retire="unpinnable", reason_file=argv[0])
    if code == 1 and missing:
        code = tick_ledger.tick(argv[1], argv[2], case=case, retire="already-holds", reason_file=argv[0])
    if code == 0:
        print("retired")
    elif code == 1:
        print("revise")
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
