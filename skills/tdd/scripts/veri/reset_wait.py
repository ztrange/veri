"""reset-wait.sh's waits, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

from full_tier_time import main_tree
import tunables

USAGE = "usage: reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]"


def poll():
    time.sleep(float(tunables.read("VERI_POLL", "1")))


def tdd_dir():
    return os.path.join(main_tree(os.getcwd()), ".tdd")


def role_key(role, lane=None):
    return role + ("-" + lane if lane else "")


def parse(argv):
    """(verb, role, key, seconds) for a well-formed argv, else None. Nothing touches a file before this."""
    if len(argv) < 2 or argv[0] not in ("marker", "recovered", "idle") or argv[1] not in ("coord", "dev"):
        return None
    rest, lane, seconds = argv[2:], None, None
    if rest[:1] == ["--lane"]:
        if len(rest) < 2 or not rest[1]:
            return None
        lane, rest = rest[1], rest[2:]
    if rest and argv[0] != "marker":
        seconds, rest = rest[0], rest[1:]
        if not (seconds.isascii() and seconds.isdigit() and int(seconds) >= 1):
            return None
    if rest:
        return None
    return argv[0], argv[1], role_key(argv[1], lane), seconds


def marker_path(tdd, key):
    return os.path.join(tdd, "reset-request-" + key)


def state_field(tdd, key, name):
    try:
        with open(os.path.join(tdd, "role-%s.state" % key)) as f:
            values = [l.strip().split("=", 1)[1] for l in f if l.startswith(name + "=")]
    except FileNotFoundError:
        return None
    return values[-1] if values else None


def main(argv):
    parsed = parse(argv)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 2
    verb, role, key, seconds = parsed
    tdd = tdd_dir()
    if verb == "marker":
        path = marker_path(tdd, key)
        while not os.path.exists(path):
            poll()
        with open(path) as f:
            print("reset-request %s %s" % (role, f.read().strip()))
        return 0
    if verb == "recovered":
        try:
            with open(marker_path(tdd, key)) as f:
                since = f.read().strip()
        except FileNotFoundError:
            return 3
        deadline = time.monotonic() + float(seconds or tunables.read("VERI_RESET_ACK_TIMEOUT", "300"))
        while time.monotonic() < deadline:
            poll()
            at = state_field(tdd, key, "recovered-at")
            if at and at > since:
                print("recovered %s %s" % (role, at))
                return 0
        print("not-recovered %s" % role)
        return 1
    transcript = state_field(tdd, key, "transcript")
    if not transcript:
        print("reset-wait.sh: no transcript recorded for %s" % role, file=sys.stderr)
        return 2
    seconds = seconds or tunables.read("VERI_RESET_IDLE", "3000")
    try:
        while time.time() - os.path.getmtime(transcript) < float(seconds):
            poll()
    except FileNotFoundError:
        print("reset-wait.sh: recorded transcript %s is missing" % transcript, file=sys.stderr)
        return 2
    print("idle %s %s" % (role, seconds))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
