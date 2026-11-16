"""Sets each file git tracks in the working tree to an mtime derived from its blob id, run by CI before `make test`."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import hashlib
import os
import subprocess
import sys

from entry import write

USAGE = "usage: content_mtimes.py"
# Every stamp lies between 2001-09-09 and 2010-01-04: in the past, so the leg's record of a .pyc never takes its
# source for one modified after the run began, and within the 32-bit mtime a .pyc header holds.
EPOCH = 1_000_000_000


def blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def stamp(data):
    """The mtime of a file holding <data>: two files with the same content get the same one."""
    return EPOCH + int(blob_id(data)[:7], 16)


def main(argv):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        write(sys.stderr, "content_mtimes: not inside a git working tree; changed no file.")
        return 2
    root = top.stdout.rstrip("\n")
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    for name in filter(None, listed.split(b"\0")):
        path = os.path.join(os.fsencode(root), name)
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            mtime = stamp(f.read())
        os.utime(path, (mtime, mtime))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
