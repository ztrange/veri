"""unreachable.sh's reachability walk, run in-process."""
import glob
import os
import re
import sys

BUILT = re.compile(rb"[A-Za-z0-9_.-]*(?:\$\{?[A-Za-z0-9_]+\}?[A-Za-z0-9_.-]*)+\.(?:sh|md)")
PIECE = re.compile(rb"(\$\{?[A-Za-z0-9_]+\}?)")
KNOB = re.compile(rb"VERI_[A-Z0-9_]+")
PROMISED = re.compile(rb"(?:^|[^A-Za-z0-9_.${}-])([A-Za-z0-9_-]+\.sh)")


def read(path):
    with open(path, "rb") as f:
        return f.read()


def whole(name):
    return re.compile(rb"(?:^|[^A-Za-z0-9_.-])" + re.escape(name) + rb"(?:$|[^A-Za-z0-9_-])", re.M)


def built_patterns(text):
    patterns = []
    for built in BUILT.findall(text):
        pieces = PIECE.split(built)
        patterns.append(re.compile(b"".join(
            rb"[A-Za-z0-9_-]+" if i % 2 else re.escape(piece) for i, piece in enumerate(pieces))))
    return patterns


def mentions(path, nodes):
    text = read(path)
    patterns = built_patterns(text)
    for name in nodes:
        if whole(name).search(text) or any(p.fullmatch(name) for p in patterns):
            yield name


def files_under(top):
    for parent, dirs, files in os.walk(top):
        for f in files:
            yield os.path.join(parent, f)


def basenames(top, pattern):
    return [os.path.basename(f) for f in sorted(glob.glob(glob.escape(top) + pattern))]


def listing(root):
    scripts = root + b"/skills/tdd/scripts"
    names = basenames(scripts, b"/*.sh")
    libs = [b"lib/" + name for name in basenames(scripts, b"/lib/*.sh")]
    docs = basenames(root, b"/skills/tdd/*.md")
    nodes = names + libs + docs

    def path_of(name):
        return root + b"/skills/tdd/" + name if name.endswith(b".md") else scripts + b"/" + name

    reached = set()
    queue = []

    def reach_from(path):
        for name in mentions(path, nodes):
            if name not in reached:
                reached.add(name)
                queue.append(name)

    hooks = sorted(glob.glob(glob.escape(root) + b"/docs/hooks/*"))
    for entry in [root + b"/skills/tdd/SKILL.md", root + b"/Makefile"] + hooks:
        if os.path.isfile(entry):
            reach_from(entry)
    while queue:
        reach_from(path_of(queue.pop(0)))

    out = []
    tests = [read(f) for f in files_under(scripts + b"/tests")]
    for name in names:
        if name in reached:
            continue
        pattern = whole(name)
        if any(pattern.search(text) for text in tests):
            out.append(b"test-only: " + name)
        else:
            out.append(name)

    promises = [read(d) for d in (root + b"/skills/tdd/SKILL.md", root + b"/CLAUDE.md") if os.path.isfile(d)]
    readers = [read(scripts + b"/" + n) for n in names + libs]
    for knob in sorted({k for text in promises for k in KNOB.findall(text)}):
        word = re.compile(rb"(?<![A-Za-z0-9_])" + re.escape(knob) + rb"(?![A-Za-z0-9_])")
        if not any(word.search(text) for text in readers):
            out.append(b"promised-unread: " + knob)
    promised = set()
    for text in promises:
        for line in text.split(b"\n"):
            promised.update(PROMISED.findall(line))
    for name in sorted(promised):
        if not os.path.exists(scripts + b"/" + name):
            out.append(b"promised-unread: " + name)
    return out


def main(argv):
    if not argv or not argv[0]:
        print("usage: unreachable.sh <repo-root>", file=sys.stderr)
        return 2
    for line in listing(os.fsencode(argv[0])):
        sys.stdout.buffer.write(line + b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
