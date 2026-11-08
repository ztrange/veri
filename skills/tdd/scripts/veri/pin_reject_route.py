"""pin-reject-route.sh's routing, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import tick_ledger

USAGE = "usage: pin-reject-route.sh <reason-file> <ledger-file> <matcher>"


def main(argv):
    if len(argv) < 3:
        print(USAGE, file=sys.stderr)
        return 2
    code = tick_ledger.main(["--unpinnable", argv[0], argv[1], argv[2]])
    if code == 0:
        print("retired")
    elif code == 1:
        print("revise")
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
