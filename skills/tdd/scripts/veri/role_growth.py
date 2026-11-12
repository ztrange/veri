"""role-growth.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import sys

from full_tier_time import main_tree
import role_state

USAGE = "usage: role-growth.sh <coord|dev> [--lane <lane>]\n"


def main(argv):
    if len(argv) != 1 or argv[0] not in ("coord", "dev"):
        sys.stderr.write(USAGE)
        return 2
    session = os.environ["CLAUDE_CODE_SESSION_ID"]
    pattern = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session + ".jsonl")
    transcript = glob.glob(pattern)[0]
    path = role_state.state_path(main_tree(os.getcwd()), argv[0])
    role_state.append(path, "session=%s\ntranscript=%s\n" % (session, transcript))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
