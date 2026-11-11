"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import stat
import sys

SNAPSHOT_PREFIX = "veri-snapshot-"
SNAPSHOT_MARKER = ".veri-snapshot"


def snapshot_gone(recorded):
    """Whether <recorded> is a well-formed absolute path to nothing: a snapshot the conductor already removed."""
    return os.path.isabs(recorded) and "\n" not in recorded and not os.path.lexists(recorded)


def snapshot_made_for(recorded, worktree):
    """Whether <recorded>, the text of a .snapshot-dir file, names a directory whose marker names <worktree>."""
    if not os.path.isabs(recorded) or not os.path.basename(recorded).startswith(SNAPSHOT_PREFIX):
        return False
    try:
        if not stat.S_ISDIR(os.lstat(recorded).st_mode):
            return False
        with open(os.path.join(recorded, SNAPSHOT_MARKER)) as served:
            named = served.read().rstrip("\n")
    except OSError:
        return False
    return os.path.realpath(named) == os.path.realpath(worktree)


def main(argv):
    if not argv:
        print("usage: pinned-scripts.sh <n>", file=sys.stderr)
        return 2
    tdd = os.path.join(os.getcwd(), ".tdd")
    here = os.path.join(tdd, "pinned-scripts")
    if not os.path.isdir(here):
        here = os.path.join(tdd, "wt", argv[0], ".tdd", "pinned-scripts")
    pin_name = "issue-%s-skill-commit" % argv[0]
    pin_file = os.path.join(os.path.dirname(here), pin_name)
    if not os.path.isfile(pin_file):
        pin_file = os.path.join(tdd, pin_name)
    if not os.path.isdir(here) and os.path.isfile(pin_file):
        with open(pin_file) as f:
            pin = f.read().strip()
        print("pinned scripts for run %s are gone; pinned commit %s; recover with: git archive %s skills/tdd/scripts"
              % (argv[0], pin, pin), file=sys.stderr)
        return 2
    if not os.path.isdir(here):
        print("pinned scripts for run %s are gone and no pin is recorded" % argv[0], file=sys.stderr)
        return 2
    print(here)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
