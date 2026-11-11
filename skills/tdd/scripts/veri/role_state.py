"""role-state.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

from full_tier_time import main_tree
import timed_n_format

USAGE = ("usage: role-state.sh <coord|dev> [--lane <lane>] set <n|lane|coordinator> <value>"
         " | add <decision|message|override|timed-n> <text>"
         " | drop <decision|message|override|timed-n> <id> | drop coordinator | show | recovered\n")


def state_path(tree, role, lane=None):
    name = role if lane is None else "%s-%s" % (role, lane)
    return os.path.join(tree, ".tdd", "role-%s.state" % name)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


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
        if len(argv) < 3:
            return usage()
        lane = argv[2]
        argv = [argv[0]] + argv[3:]
        if len(argv) < 2:
            return usage()
    path = state_path(main_tree(os.getcwd()), name, lane)
    verb = VERBS.get(argv[1])
    return verb(path, argv) if verb else usage()


def do_recovered(path, argv):
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        return usage()
    append(path, "recovered-at=%s\nsession-id=%s\n" % (now(), session))
    return 0


def do_set(path, argv):
    if len(argv) != 4 or argv[2] not in ("n", "lane", "coordinator"):
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
    item = str(max([int(l.split()[1]) for l in (read(path) or "").splitlines() if " " in l] + [0]) + 1)
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
    return drop_lines(path, lambda l: l.split()[:2] == argv[2:4])


def do_show(path, argv):
    text = read(path)
    if text is None:
        return 3
    sys.stdout.write(text)
    return 0


LISTS = ("decision", "message", "override", "timed-n")
VERBS = {"recovered": do_recovered, "set": do_set, "add": do_add, "drop": do_drop, "show": do_show}


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
