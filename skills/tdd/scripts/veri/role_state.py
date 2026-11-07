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
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def append(path, text):
    try:
        with open(path) as f:
            text = f.read() + text
    except FileNotFoundError:
        pass
    replace(path, text)


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    if name not in ("coord", "dev"):
        sys.stderr.write(USAGE)
        return 2
    if argv[1] == "--lane":
        name += "-" + argv[2]
        argv = [argv[0]] + argv[3:]
    path = os.path.join(main_tree(os.getcwd()), ".tdd", "role-%s.state" % name)
    if argv[1] == "recovered" and not os.environ.get("CLAUDE_CODE_SESSION_ID"):
        sys.stderr.write(USAGE)
        return 2
    if argv[1] in ("set", "add") and len(argv) == 4 or argv[1] == "recovered":
        os.makedirs(os.path.dirname(path), exist_ok=True)
    if argv[1] == "recovered":
        append(path, "recovered-at=%s\nsession-id=%s\n" % (now(), os.environ["CLAUDE_CODE_SESSION_ID"]))
        return 0
    if argv[1] == "set" and len(argv) == 4:
        append(path, "%s=%s\n" % (argv[2], argv[3]))
        return 0
    if argv[1] == "add" and len(argv) == 4:
        try:
            with open(path) as f:
                item = str(max([int(l.split()[1]) for l in f if " " in l] + [0]) + 1)
        except FileNotFoundError:
            item = "1"
        append(path, "%s %s %s %s\n" % (argv[2], item, now(), argv[3]))
        print(item)
        return 0
    if argv[1] == "drop":
        with open(path) as f:
            lines = f.readlines()
        replace(path, "".join(l for l in lines if l.split()[:2] != argv[2:4]))
        return 0
    if argv[1] == "show":
        try:
            with open(path) as f:
                sys.stdout.write(f.read())
        except FileNotFoundError:
            return 3
        return 0
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
