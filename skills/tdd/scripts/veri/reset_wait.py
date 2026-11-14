"""reset-wait.sh's waits, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

from veri.full_tier_time import main_tree

USAGE = "usage: reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]"


def main(argv):
    if argv[:1] == ["marker"] and len(argv) in (2, 4):
        name = "reset-request-" + argv[1]
        if len(argv) == 4:
            name += "-" + argv[3]
        path = os.path.join(main_tree(os.getcwd()), ".tdd", name)
        while not os.path.exists(path):
            time.sleep(float(os.environ.get("VERI_POLL", "1")))
        with open(path) as f:
            print("reset-request %s %s" % (argv[1], f.read().strip()))
        return 0
    if argv[:1] == ["recovered"] and len(argv) == 3:
        tdd = os.path.join(main_tree(os.getcwd()), ".tdd")
        with open(os.path.join(tdd, "reset-request-" + argv[1])) as f:
            since = f.read().strip()
        while True:
            time.sleep(float(os.environ.get("VERI_POLL", "1")))
            with open(os.path.join(tdd, "role-%s.state" % argv[1])) as f:
                at = [l.strip().split("=", 1)[1] for l in f if l.startswith("recovered-at=")]
            if at and at[-1] > since:
                print("recovered %s %s" % (argv[1], at[-1]))
                return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
