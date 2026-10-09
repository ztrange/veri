"""affected-suites.sh's computations, run in-process."""
import fnmatch
import glob
import os
import re
import subprocess
import sys

try:
    from git import git
except ImportError:
    from .git import git

USAGE = "usage: affected-suites.sh <base>..<head>"
SCRIPTS = "skills/tdd/scripts"
SPACE = rb"[ \t\n\v\f\r]"


class Unplaced(Exception):
    pass


def refuse(message=None):
    if message is not None:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def suites(pattern):
    return sorted(glob.glob(pattern))


def every_suite():
    return [s for s in suites(SCRIPTS + "/tests/*.test.sh") + suites(SCRIPTS + "/tests/unit/*.test.sh")
            if os.path.isfile(s)]


def suites_matching(pattern):
    return [s for s in every_suite() if re.search(pattern, read(s) or b"")]


def suites_naming(*needles):
    return suites_matching(b"|".join(re.escape(n.encode()) for n in needles))


def has_line(path, pattern):
    text = read(path)
    return text is not None and any(pattern.search(line) for line in text.split(b"\n"))


def sourcing(lib, tail=b""):
    return re.compile(
        rb"^" + SPACE + rb"*(source|\.)" + SPACE + rb".*lib/" + lib + rb"\"?" + SPACE + rb"*" + tail + rb"$")


def basename(path, suffix=""):
    name = os.path.basename(path)
    if suffix and name.endswith(suffix) and name != suffix:
        name = name[: -len(suffix)]
    return name


def existing(path):
    return [path] if os.path.isfile(path) else []


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def heading(line):
    return line.split(" ", 1)[1].strip() if line.startswith(("## ", "### ")) else None


def enclosing(lines):
    names = []
    for line in reversed(lines):
        name = heading(line)
        if name is None:
            continue
        if line.startswith("## "):
            return tuple(names + [name])
        if not names:
            names.append(name)
    return None


def edited_section(f, revisions):
    code, diff = output("diff", "-U0", revisions, "--", f)
    text = read(f)
    if code != 0 or text is None:
        return None
    lines = text.decode(errors="replace").split("\n")
    numbers = []
    for line in diff.split("\n"):
        hunk = HUNK.match(line)
        if hunk:
            start, count = int(hunk.group(1)), int(hunk.group(2) or "1")
            numbers += range(start, start + count) if count else [start]
    sections = set()
    for n in numbers:
        section = enclosing(lines[:n])
        if section is None:
            return None
        sections.add(section)
    return sections.pop() if len(sections) == 1 else None


def quoted(*names):
    return ["%s%s%s" % (q, n, q) for n in names for q in "'\""]


def headings(f):
    text = (read(f) or b"").decode(errors="replace")
    return [h for h in map(heading, text.split("\n")) if h is not None]


def suite_of(f, revisions=None):
    def match(*patterns):
        return any(fnmatch.fnmatchcase(f, p) for p in patterns)

    if match("CLAUDE.md", "Makefile", "skills/*/SKILL.md"):
        naming = suites_naming('"%s"' % f, '/%s"' % f)
        section = match("skills/*/SKILL.md") and revisions and edited_section(f, revisions)
        if section:
            readers = suites_naming(*quoted(*section))
            slicers = suites_naming(*quoted(*headings(f)))
            return [s for s in naming if s in readers or s not in slicers]
        return naming
    if match(SCRIPTS + "/tests/*.test.sh", SCRIPTS + "/tests/py/test_*.py"):
        return existing(f)
    if f == SCRIPTS + "/tests/lib/harness.sh":
        return [s for s in every_suite() if has_line(s, sourcing(rb"harness\.sh"))]
    if match(SCRIPTS + "/tests/fixtures/*"):
        return suites_naming(f[len(SCRIPTS + "/tests/"):])
    if match(SCRIPTS + "/prompts/*.md"):
        return suites_naming(f[len(SCRIPTS + "/"):]) + existing(SCRIPTS + "/tests/unit/emitted-text.test.sh")
    if match(SCRIPTS + "/lib/*.sh"):
        line = sourcing(basename(f).encode(), rb"(\\)?")
        found = []
        for script in suites(SCRIPTS + "/*.sh"):
            if has_line(script, line):
                found += suite_of(script)
        return found
    if match(SCRIPTS + "/veri/*.py"):
        name = basename(f, ".py")
        return (existing("%s/tests/py/test_%s.py" % (SCRIPTS, name))
                + suite_of("%s/%s.sh" % (SCRIPTS, name.replace("_", "-"))))
    if match(SCRIPTS + "/*.sh"):
        name = basename(f, ".sh")
        return (existing("%s/tests/unit/%s.test.sh" % (SCRIPTS, name))
                or existing("%s/tests/%s.test.sh" % (SCRIPTS, name))
                or suites_matching(rb"(?<!lib)/" + re.escape(name.encode()) + rb"\.sh"))
    if match(".tdd/*"):
        return []
    raise Unplaced(f)


def output(*args):
    out = git(*args, stdout=subprocess.PIPE, text=True)
    return out.returncode, out.stdout.rstrip("\n")


def changed(revisions, *args):
    return output("diff", "--name-only", *args[:1], revisions, *args[1:])


def untracked(*args):
    return output("ls-files", "--others", "--exclude-standard", *args)


def main(argv):
    if not argv or not argv[0]:
        return refuse()
    revisions = argv[0]
    for rev in revisions.split("..", 1):
        if git("rev-parse", "--verify", "--quiet", rev + "^{commit}", stdout=subprocess.DEVNULL).returncode != 0:
            return refuse("affected-suites: cannot resolve revision '%s'" % rev)

    working_tree = ".." not in revisions
    if not working_tree:
        revisions = revisions.replace("..", "...", 1)
    code, files = changed(revisions)
    if code != 0:
        return code if code in (1, 2, 3) else 2
    if working_tree:
        _, new = untracked()
        files = "\n".join(f for f in [files, new] if f)
    if not files:
        return 3

    placed, unplaced = [], []
    for f in files.split("\n"):
        try:
            placed += suite_of(f, revisions)
        except Unplaced:
            unplaced.append(f)

    counting = ("--", SCRIPTS + "/tests", ":(glob)%s/*.sh" % SCRIPTS)
    _, counted = changed(revisions, "--diff-filter=AD", *counting)
    if working_tree and not counted:
        _, counted = untracked(*counting)
    if counted:
        placed.append(SCRIPTS + "/tests/claude-md-counts.test.sh")

    if unplaced:
        print("affected-suites: no rule places %s; widening to every suite" % ",".join(unplaced), file=sys.stderr)
        placed = every_suite()
    elif not placed:
        return 3
    sys.stdout.write("".join(s + "\n" for s in sorted(set(placed))))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
