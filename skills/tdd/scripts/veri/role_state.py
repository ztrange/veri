"""role-state.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import sys
import time

from full_tier_time import main_tree
import timed_n_format
import tunables

USAGE = ("usage: role-state.sh <coord|dev> [--lane <lane>] set <n|lane|coordinator> <value>"
         " | add <decision|message|override|timed-n> <text>"
         " | drop <decision|message|override|timed-n> <id> | drop coordinator | show | recovered\n")


def state_path(tree, role, lane=None):
    name = role if lane is None else "%s-%s" % (role, lane)
    return os.path.join(tree, ".tdd", "role-%s.state" % name)


STAMP = "%Y-%m-%dT%H:%M:%S"


def marker_path(path):
    name = os.path.basename(path)[len("role-"):-len(".state")]
    return os.path.join(os.path.dirname(path), "reset-request-" + name)


def now():
    return time.strftime(STAMP)


def epoch(stamp):
    return time.mktime(time.strptime(stamp, STAMP))


def replace(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None


def append(path, text):
    replace(path, (read(path) or "") + text)


def usage():
    sys.stderr.write(USAGE)
    return 2


def main(argv):
    if len(argv) < 2:
        return usage()
    name = argv[0]
    if name not in ("coord", "dev"):
        return usage()
    lane = None
    if argv[1] == "--lane":
        if len(argv) < 4:
            return usage()
        lane = argv[2]
        argv = [argv[0]] + argv[3:]
    path = state_path(main_tree(os.getcwd()), name, lane)
    verb = VERBS.get(argv[1])
    return verb(path, argv) if verb else usage()


def do_recovered(path, argv):
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        return usage()
    kept = [l for l in (read(path) or "").splitlines(True) if not l.startswith("refused-at=")]
    replace(path, "".join(kept) + "recovered-at=%s\nsession-id=%s\n" % (now(), session))
    try:
        os.remove(marker_path(path))
    except FileNotFoundError:
        pass
    return 0


def launched_since(path, recovered):
    since = epoch(recovered)
    tdd = os.path.dirname(path)
    journals = [os.path.join(tdd, "events.jsonl")] + sorted(glob.glob(os.path.join(tdd, "wt", "*", ".tdd", "events.jsonl")))
    events = [json.loads(l) for j in journals for l in (read(j) or "").splitlines()]
    return any(e.get("event") in ("conductor-start", "merged") and e.get("ts", 0) > since for e in events)


def refusal(path, lines, stamp):
    recovered = [l.split("=", 1)[1] for l in lines if l.startswith("recovered-at=")]
    decided = any(l.split()[2] > recovered[-1] for l in lines if l.startswith(("decision ", "dropped-decision ")))
    if not decided and not launched_since(path, recovered[-1]):
        return "request-reset refused: nothing launched, merged or decided since the last recovery"
    hour_ago = epoch(stamp) - 3600
    recent = [l for l in lines if l.startswith("reset-at=") and epoch(l.split("=", 1)[1]) > hour_ago]
    if len(recent) >= int(tunables.read("VERI_RESET_MAX_PER_HOUR", "2")):
        return "request-reset refused: %d resets in the last hour" % len(recent)
    return None


def do_request_reset(path, argv):
    lines = (read(path) or "").splitlines()
    stamp = now()
    reason = refusal(path, lines, stamp)
    if reason:
        sys.stderr.write(reason + "\n")
        return 1
    append(path, "reset-at=%s\n" % stamp)
    replace(marker_path(path), stamp + ("\nidle\n" if argv[2:] == ["--idle"] else "\n"))
    return 0


def do_set(path, argv):
    if len(argv) != 4 or argv[2] not in SET_FIELDS:
        return usage()
    if argv[2] == "n" and not argv[3].isdigit():
        return usage()
    append(path, "%s=%s\n" % (argv[2], argv[3]))
    return 0


def do_add(path, argv):
    if argv[2] not in LISTS or len(argv) != 4:
        return usage()
    if argv[2] == "timed-n":
        try:
            timed_n_format.parse(argv[3])
        except ValueError:
            sys.stderr.write("timed-n text must be: <n> until <ISO-8601 datetime>\n")
            return 2
    item = str(max([int(l.split()[1]) for l in (read(path) or "").splitlines() if l.partition(" ")[0] in LISTS] + [0]) + 1)
    append(path, "%s %s %s %s\n" % (argv[2], item, now(), argv[3]))
    print(item)
    return 0


def drop_lines(path, doomed):
    lines = (read(path) or "").splitlines(True)
    kept = [l for l in lines if not doomed(l)]
    if kept == lines:
        return 3
    replace(path, "".join(kept))
    return 0


def do_drop(path, argv):
    if argv[2:] == ["coordinator"]:
        return drop_lines(path, lambda l: l.startswith("coordinator="))
    if argv[2] not in LISTS:
        return usage()
    code = drop_lines(path, lambda l: l.split()[:2] == argv[2:4])
    if code == 0 and argv[2] == "decision":
        append(path, "dropped-decision %s %s\n" % (argv[3], now()))
    return code


def do_show(path, argv):
    text = read(path)
    if text is None:
        return 3
    sys.stdout.write(text)
    return 0


SET_FIELDS = ("n", "lane", "coordinator", "session", "transcript", "baseline", "baseline-at", "refused-at", "resetter")
LISTS = ("decision", "message", "override", "timed-n")
VERBS = {"recovered": do_recovered, "request-reset": do_request_reset, "set": do_set, "add": do_add, "drop": do_drop, "show": do_show}


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
