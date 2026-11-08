"""role-state.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

from full_tier_time import main_tree

USAGE = "usage: role-state.sh <coord|dev> set <field> <value> | show\n"


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
    if argv[1] == "--lane":
        name += "-" + argv[2]
        argv = [argv[0]] + argv[3:]
    path = os.path.join(main_tree(os.getcwd()), ".tdd", "role-%s.state" % name)
    if argv[1] == "recovered" and not os.environ.get("CLAUDE_CODE_SESSION_ID"):
        return usage()
    if argv[1] == "set" and len(argv) == 4 and argv[2] not in ("n", "lane"):
        return usage()
    if argv[1] in ("add", "drop") and argv[2] not in ("decision", "message", "override", "timed-n"):
        return usage()
    if argv[1] == "recovered":
        append(path, "recovered-at=%s\nsession-id=%s\n" % (now(), os.environ["CLAUDE_CODE_SESSION_ID"]))
        return 0
    if argv[1] == "set" and len(argv) == 4:
        append(path, "%s=%s\n" % (argv[2], argv[3]))
        return 0
    if argv[1] == "add" and len(argv) == 4:
        item = str(max([int(l.split()[1]) for l in (read(path) or "").splitlines() if " " in l] + [0]) + 1)
        append(path, "%s %s %s %s\n" % (argv[2], item, now(), argv[3]))
        print(item)
        return 0
    if argv[1] == "drop":
        with open(path) as f:
            lines = f.readlines()
        replace(path, "".join(l for l in lines if l.split()[:2] != argv[2:4]))
        return 0
    if argv[1] == "show":
        text = read(path)
        if text is None:
            return 3
        sys.stdout.write(text)
        return 0
    return usage()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
