"""pin-reject-route.sh's routing, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import event
import ledger
import os
import tick_ledger

USAGE = "usage: pin-reject-route.sh [--missing-reroute] <reason-file> <ledger-file> <matcher> <target-test>"


def main(argv):
    missing = argv[:1] == ["--missing-reroute"]
    if missing:
        argv = argv[1:]
    if len(argv) < 4:
        print(USAGE, file=sys.stderr)
        return 2
    if missing:
        with open(argv[0], encoding="utf-8") as handle:
            reason = handle.read()
        if "stays green" in reason:
            text = ledger.read_ledger(argv[1])
            _, new = ledger.ledger_tick(text, argv[2], False)
            if new == text:
                return 3
            step = tick_ledger.changed_line(text, new).split("] ", 1)[1]
            tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(argv[1])))
            event.append(tdd_parent, event.context(os.environ), "unpinnable-missing", ["step=" + step])
            print("unpinnable-missing")
            return 2
    code = tick_ledger.main(["--unpinnable", argv[0], "--case", argv[3], argv[1], argv[2]])
    if code == 1 and missing:
        code = tick_ledger.main(["--already-holds", argv[0], "--case", argv[3], argv[1], argv[2]])
    if code == 0:
        print("retired")
    elif code == 1:
        print("revise")
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
