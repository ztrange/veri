"""coupling.sh: the pairs of code files, one changed in a range, that import or invoke each other (PRD 032.8, #4556)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
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


def importing(stem_, text):
    """Whether <text>, as stem_walk.texts reads it, holds an import statement of the module <stem_>."""
    word = re.escape(os.fsencode(stem_))
    return any(re.search(pattern, text, re.MULTILINE) for pattern in (
        rb"^[ \t]*import[ \t]+(?:[\w.]+(?:[ \t]+as[ \t]+\w+)?[ \t]*,[ \t]*)*(?:[\w.]+\.)?" + word + rb"(?![\w.])",
        rb"^[ \t]*from[ \t]+(?:[\w.]*\.)?" + word + rb"(?:\.[\w.]+)?[ \t]+import\b",
        rb"^[ \t]*from[ \t]+[\w.]+[ \t]+import[ \t]+(?:\([\s\w,]*?|[\w, \t]*?)(?<![\w.])" + word + rb"(?![\w.])",
    ))


def invoking(stem_, ext, text):
    """Whether <text> names the script <stem_> by path: quoted or after a `/`, with a `.sh`, `.py` or <ext> extension,
    or extensionless after a `/` and closing a quoted module path."""
    word = re.escape(os.fsencode(stem_))
    extension = b"|".join(re.escape(e) for e in {b"sh", b"py", os.fsencode(ext.lstrip("."))} if e)
    return bool(re.search(rb"[/'\"]" + word + rb"\.(?:" + extension + rb")(?!\w)", text)
                or re.search(rb"/" + word + rb"['\"]", text))


def refers(path, other):
    """Whether the file <path> imports the module of <other> or invokes its script by path."""
    stem_, ext = stem_walk.stem(other), os.path.splitext(other)[1]
    return any(importing(stem_, text) or invoking(stem_, ext, text) for _, text in stem_walk.texts([path]))


def pairs(changed, files):
    """Each pair, in byte order, of a path in <changed> and another of <files> of its extension, each importing or
    invoking the other."""
    found = set()
    for path in changed:
        ext = os.path.splitext(path)[1]
        peers = [f for f in files if f != path and os.path.splitext(f)[1] == ext]
        for other in stem_walk.naming(stem_walk.stem(path), peers):
            if refers(other, path) and refers(path, other):
                found.add(tuple(sorted((path, other), key=os.fsencode)))
    return sorted(found, key=lambda pair: tuple(map(os.fsencode, pair)))


def main(argv):
    if len(argv) != 1 or not argv[0]:
        return entry.refuse(usage=USAGE)
    if not git.ok("rev-parse", "--verify", "--quiet", argv[0] + "^{commit}"):
        return entry.refuse("coupling: cannot resolve '%s'" % argv[0])
    os.chdir(git.out("rev-parse", "--show-toplevel"))
    files = [f for f in stem_walk.tree_files() if code(f)]
    listed = git.out("diff", "--name-only", "-z", argv[0] + "..HEAD").split("\0")
    known = set(files)
    found = pairs([p for p in listed if p in known], files)
    sys.stdout.write("".join("mutual: %s %s\n" % pair for pair in found))
    return 0 if found else 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
