"""reset-wait.sh's waits, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

from veri.full_tier_time import main_tree

USAGE = "usage: reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]"


def main(argv):
    if argv[:1] == ["marker"] and len(argv) == 2:
        with open(os.path.join(main_tree(os.getcwd()), ".tdd", "reset-request-" + argv[1])) as f:
            print("reset-request %s %s" % (argv[1], f.read().strip()))
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
