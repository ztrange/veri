"""pinned-scripts.sh: the directory holding a run's pinned scripts."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import errno
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import unicodedata

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
    """Remove the write bits of every file and directory under <tree>, <tree> included, so a write into it fails.
    A file with a second hard link is left as it is: the other name may lie outside the tree."""
    for root, dirs, files in os.walk(tree, topdown=False):
        for name in files + dirs:
            path = os.path.join(root, name)
            found = plain_entry(path)
            if stat.S_ISREG(found.st_mode) and found.st_nlink > 1:
                continue
            take_bits(path, WRITE_BITS)
    take_bits(tree, WRITE_BITS)


def remove_tree(tree):
    """Give the owner back the write bit of every directory under <tree>, then remove it all. Raises OSError,
    touching nothing, unless <tree> itself is a real directory (a symlink to one is refused, never followed)."""
    if not stat.S_ISDIR(os.lstat(tree).st_mode):
        raise NotADirectoryError(errno.ENOTDIR, "not a real directory, so not removed", tree)
    writable_directories(tree)
    shutil.rmtree(tree)


def writable_directories(tree):
    """Give the owner read, write and search on every directory under <tree>, <tree> first, so each can be listed
    and its entries added and removed, a directory a leaf set to mode 000 included; a symlink is never followed."""
    owner_may_enter(tree)
    for root, dirs, _ in os.walk(tree, onerror=raise_error):
        for name in dirs:
            owner_may_enter(os.path.join(root, name))


def owner_may_enter(path):
    """Add S_IRWXU to the directory <path>'s mode, by path, since a mode-000 directory cannot be opened; checked
    with lstat first, so a symlink is left as it is."""
    found = os.lstat(path)
    if stat.S_ISDIR(found.st_mode):
        os.chmod(path, stat.S_IMODE(found.st_mode) | stat.S_IRWXU)


def copy_writable(source, destination):
    """Copy the tree <source> to the new directory <destination>: a symlink as a symlink, a file with its content
    and its mode plus the owner's write bit, a directory writable, so the copy can be added to and removed."""
    os.makedirs(destination)
    for root, dirs, files in os.walk(source, onerror=raise_error):
        target = os.path.join(destination, os.path.relpath(root, source))
        for name in dirs + files:
            path, copy = os.path.join(root, name), os.path.join(target, name)
            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode):
                os.symlink(os.readlink(path), copy)
            elif stat.S_ISDIR(mode):
                os.mkdir(copy)
            else:
                shutil.copyfile(path, copy)
                change_mode(copy, lambda _, mode=mode: stat.S_IMODE(mode) | stat.S_IWUSR)


def take_bits(path, bits):
    """Remove <bits> from the mode of <path>."""
    change_mode(path, lambda mode: mode & ~bits)


def change_mode(path, new_mode):
    """Set the mode of <path> to new_mode(its mode), through a descriptor of it; a symlink is left as it is, never
    followed."""
    if stat.S_ISLNK(os.lstat(path).st_mode):
        return
    handle = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        os.fchmod(handle, new_mode(stat.S_IMODE(os.fstat(handle).st_mode)))
    finally:
        os.close(handle)


def snapshot_digest(snapshot):
    """Every entry of <snapshot>, the marker included (deleting it must show), as a list of (path relative to it,
    token) tuples sorted by path: a directory's token is `directory`; a file's, the sha256 of its content and its
    owner executable bit; a symlink's, the sha256 of its target, never followed. Raises OSError on what it cannot
    read and on a name holding a line break or a control character."""
    lines = []
    for root, dirs, files in os.walk(snapshot, onerror=raise_error):
        for name in files + dirs:
            path = os.path.join(root, name)
            relative = os.path.relpath(path, snapshot)
            if not plain_name(name):
                raise OSError(errno.EINVAL, "a name holding a line break or a control character", path)
            found = plain_entry(path)
            mode = found.st_mode
            if stat.S_ISREG(mode) and found.st_nlink > 1:
                raise OSError(errno.EMLINK, "a file with a second hard link, which may lie outside the snapshot", path)
            if stat.S_ISDIR(mode):
                lines.append((relative, "directory"))
                continue
            if stat.S_ISLNK(mode):
                token = hashlib.sha256(b"symlink " + os.fsencode(os.readlink(path))).hexdigest()
            else:
                token = regular_sha256(path, b" x" if mode & stat.S_IXUSR else b" -")
            lines.append((relative, token))
    return sorted(lines)


def digest_text(entries):
    """The file form of a digest: one JSON list of [path, token] pairs, then a newline."""
    return json.dumps([[path, token] for path, token in entries]) + "\n"


def parse_digest(text):
    """The entries of the file form <text>; ValueError for any text digest_text does not write."""
    pairs = json.loads(text)
    if not isinstance(pairs, list) or not all(
            isinstance(pair, list) and len(pair) == 2 and all(isinstance(part, str) for part in pair)
            for pair in pairs):
        raise ValueError("not a snapshot digest")
    return [tuple(pair) for pair in pairs]


def first_change(recorded, snapshot):
    """The first path under <snapshot>, sorted, whose token differs from the one the entries <recorded> hold, an
    entry added or removed included, or that <recorded> names twice, joined to <snapshot>; None when none does.
    OSError propagates."""
    paths = [path for path, _ in recorded]
    twice = sorted(path for path in set(paths) if paths.count(path) > 1)
    if twice:
        return os.path.join(snapshot, twice[0])
    before, now = dict(recorded), dict(snapshot_digest(snapshot))
    for path in sorted(set(before) | set(now)):
        if before.get(path) != now.get(path):
            return os.path.join(snapshot, path)
    return None


def plain_name(name):
    """Whether <name> holds no character str.splitlines breaks on and no control character."""
    return len(name.splitlines()) == 1 and not any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in name)


def plain_entry(path):
    """os.lstat(<path>), or OSError when it is neither a regular file, a directory nor a symlink (a FIFO, a socket,
    a device), which is never opened."""
    found = os.lstat(path)
    if not (stat.S_ISREG(found.st_mode) or stat.S_ISDIR(found.st_mode) or stat.S_ISLNK(found.st_mode)):
        raise OSError(errno.EINVAL, "neither a file, a directory nor a symlink", path)
    return found


def regular_sha256(path, trailer):
    """The sha256 hex of the regular file <path>'s bytes then <trailer>, read in chunks, opened without following a
    symlink or blocking; OSError otherwise."""
    handle = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(handle).st_mode):
            raise OSError(errno.EINVAL, "not a regular file", path)
        digest = hashlib.sha256()
        while chunk := os.read(handle, 1 << 20):
            digest.update(chunk)
    finally:
        os.close(handle)
    digest.update(trailer)
    return digest.hexdigest()


def raise_error(error):
    raise error


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
