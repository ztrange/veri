"""role-state.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

from full_tier_time import main_tree

USAGE = "usage: role-state.sh <coord|dev> set <field> <value> | show\n"


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    if argv[1] == "--lane":
        name += "-" + argv[2]
        argv = [argv[0]] + argv[3:]
    path = os.path.join(main_tree(os.getcwd()), ".tdd", "role-%s.state" % name)
    if argv[1] == "set" and len(argv) == 4:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write("%s=%s\n" % (argv[2], argv[3]))
        return 0
    if argv[1] == "show":
        with open(path) as f:
            sys.stdout.write(f.read())
        return 0
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
