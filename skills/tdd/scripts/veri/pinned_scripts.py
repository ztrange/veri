"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import stat
import sys
import tempfile

import run_dir

SNAPSHOT_PREFIX = "veri-snapshot-"
SNAPSHOT_MARKER = ".veri-snapshot"


def make_snapshot():
    """A new, empty snapshot directory; write_snapshot_marker names its worktree once it is extracted."""
    return tempfile.mkdtemp(prefix=SNAPSHOT_PREFIX)


def write_snapshot_marker(snapshot, worktree):
    with open(os.path.join(snapshot, SNAPSHOT_MARKER), "w") as serving:
        serving.write(os.path.realpath(worktree) + "\n")


WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH


def make_read_only(tree):
    """Remove the write bits of every file and directory under <tree>, <tree> included, so a write into it fails."""
    for root, dirs, files in os.walk(tree, topdown=False):
        for name in files + dirs:
            take_bits(os.path.join(root, name), WRITE_BITS)
    take_bits(tree, WRITE_BITS)


def take_bits(path, bits):
    """Remove <bits> from the mode of <path>, through a descriptor of it."""
    handle = os.open(path, os.O_RDONLY)
    try:
        os.fchmod(handle, stat.S_IMODE(os.fstat(handle).st_mode) & ~bits)
    finally:
        os.close(handle)


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


USAGE = "usage: pinned-scripts.sh <n>"


def main(argv):
    if not argv:
        print("usage: pinned-scripts.sh <n>", file=sys.stderr)
        return 2
    run = os.getcwd()
    here = run_dir.run_file(run, "pinned-scripts")
    if not os.path.isdir(here):
        run = run_dir.worktree(os.getcwd(), argv[0])
        here = run_dir.run_file(run, "pinned-scripts")
    pin_file = run_dir.issue_file(run, argv[0], "-skill-commit")
    if not os.path.isfile(pin_file):
        pin_file = run_dir.issue_file(os.getcwd(), argv[0], "-skill-commit")
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
