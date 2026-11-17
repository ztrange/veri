"""unwired.sh: the non-test files a range adds that no other non-test file names (PRD 032.6, WN1 to WN3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import case_reader
import entry
import git
import stem_walk

USAGE = "usage: unwired.sh [--accepted <record>] <branch-base>"
NOT_CODE = frozenset((".md", ".txt", ".rst", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".lock", ".csv"))


def code(path):
    """Whether <path> is code this gate checks: not a test file, not under `.tdd/` or `.github/`, and not of a prose,
    config or data extension."""
    return (not path.startswith((".tdd/", ".github/")) and not case_reader.is_test_path(path)
            and os.path.splitext(path)[1] not in NOT_CODE)


def added(base):
    """The code paths <base>..HEAD adds."""
    listed = git.out("diff", "--diff-filter=A", "--name-only", "-z", base + "..HEAD")
    return [p for p in listed.split("\0") if p and code(p)]


def unnamed(paths):
    """The paths among <paths> whose stem no other non-test file git does not ignore holds as a whole word."""
    sources = [p for p in stem_walk.tree_files() if not case_reader.is_test_path(p)]
    return [p for p in paths if not stem_walk.naming(stem_walk.stem(p), [s for s in sources if s != p])]


def work_tree():
    """Whether git answers `true` for the current directory being inside a work tree (exit 0 alone is not enough:
    inside a `.git` directory it prints `false`)."""
    try:
        return git.out("rev-parse", "--is-inside-work-tree") == "true"
    except git.GitFailed:
        return False


def accepted(record):
    """The paths <record> lists, one per line; a missing record accepts none."""
    try:
        with open(record, errors="surrogateescape") as lines:
            return set(lines.read().splitlines())
    except FileNotFoundError:
        return set()


def main(argv):
    record = None
    if argv[:1] == ["--accepted"] and len(argv) > 1:
        record, argv = os.path.abspath(argv[1]), argv[2:]
    if len(argv) != 1 or not argv[0]:
        return entry.refuse(usage=USAGE)
    if not work_tree():
        return entry.refuse("unwired: not a git work tree")
    os.chdir(git.out("rev-parse", "--show-toplevel"))
    if not git.ok("rev-parse", "--verify", "--quiet", argv[0] + "^{commit}"):
        return entry.refuse("unwired: cannot resolve '%s'" % argv[0])
    paths = added(argv[0])
    if not paths:
        return 3
    found = unnamed(paths)
    if record is not None:
        found = [p for p in found if p not in accepted(record)]
    sys.stdout.write("".join(p + "\n" for p in found))
    return 1 if found else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
