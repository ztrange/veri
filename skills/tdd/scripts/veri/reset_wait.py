"""reset-wait.sh's waits, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

from veri import tunables
from veri.full_tier_time import main_tree

USAGE = "usage: reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]"


def poll():
    time.sleep(float(os.environ.get("VERI_POLL", "1")))


def role_key(role, lane=None):
    return role + ("-" + lane if lane else "")


def marker_path(tdd, key):
    return os.path.join(tdd, "reset-request-" + key)


def state_field(tdd, key, name):
    with open(os.path.join(tdd, "role-%s.state" % key)) as f:
        values = [l.strip().split("=", 1)[1] for l in f if l.startswith(name + "=")]
    return values[-1] if values else None


def main(argv):
    if argv[:1] == ["marker"] and len(argv) in (2, 4):
        path = marker_path(os.path.join(main_tree(os.getcwd()), ".tdd"), role_key(argv[1], argv[3] if len(argv) == 4 else None))
        while not os.path.exists(path):
            poll()
        with open(path) as f:
            print("reset-request %s %s" % (argv[1], f.read().strip()))
        return 0
    if argv[:1] == ["recovered"] and len(argv) in (2, 3, 5):
        tdd = os.path.join(main_tree(os.getcwd()), ".tdd")
        role = role_key(argv[1], argv[3] if len(argv) == 5 else None)
        try:
            with open(marker_path(tdd, role)) as f:
                since = f.read().strip()
        except FileNotFoundError:
            return 3
        deadline = time.monotonic() + float(argv[-1] if len(argv) in (3, 5) else tunables.read("VERI_RESET_ACK_TIMEOUT", "300"))
        while time.monotonic() < deadline:
            poll()
            at = state_field(tdd, role, "recovered-at")
            if at and at > since:
                print("recovered %s %s" % (argv[1], at))
                return 0
        print("not-recovered %s" % argv[1])
        return 1
    if argv[:1] == ["idle"] and len(argv) in (3, 5):
        tdd = os.path.join(main_tree(os.getcwd()), ".tdd")
        transcript = state_field(tdd, role_key(argv[1], argv[3] if len(argv) == 5 else None), "transcript")
        while time.time() - os.path.getmtime(transcript) < float(argv[-1]):
            poll()
        print("idle %s %s" % (argv[1], argv[-1]))
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
