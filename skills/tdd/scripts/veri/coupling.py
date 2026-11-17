"""coupling.sh: the pairs of code files, one changed in a range, that name each other (PRD 032.8, CU1)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import case_reader
import entry
import git
import stem_walk

USAGE = "usage: coupling.sh <branch-base>"
PROSE = frozenset((".md", ".txt", ".rst"))


def code(path):
    """Whether <path> is a non-test file whose extension is not a prose one."""
    return not case_reader.is_test_path(path) and os.path.splitext(path)[1] not in PROSE


def pairs(changed, files):
    """Each pair, in byte order, of a path in <changed> and another of <files> of its extension, naming each other."""
    found = set()
    for path in changed:
        ext = os.path.splitext(path)[1]
        peers = [f for f in files if f != path and os.path.splitext(f)[1] == ext]
        for other in stem_walk.naming(stem_walk.stem(path), peers):
            if stem_walk.naming(stem_walk.stem(other), [path]):
                found.add(tuple(sorted((path, other), key=os.fsencode)))
    return sorted(found, key=lambda pair: tuple(map(os.fsencode, pair)))


def main(argv):
    if len(argv) != 1 or not argv[0]:
        return entry.refuse(usage=USAGE)
    files = [f for f in stem_walk.tree_files() if code(f)]
    listed = git.out("diff", "--name-only", "-z", argv[0] + "..HEAD").split("\0")
    found = pairs([p for p in listed if p in files], files)
    sys.stdout.write("".join("mutual: %s %s\n" % pair for pair in found))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
