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

try:
    from . import markdown_sections
except ImportError:
    import markdown_sections

USAGE = "usage: affected-suites.sh <base>..<head>"
SCRIPTS = "skills/tdd/scripts"
PYTEST_DIRS = (SCRIPTS + "/tests/py", SCRIPTS + "/tests/py/unit")
SKILL_DOCS = ("skills/tdd/SCRIPTS.md", "skills/tdd/STOPPING.md", "skills/tdd/RECONCILE.md",
              "skills/tdd/BAIL.md", "skills/tdd/PIN.md", "skills/tdd/RESUME.md",
              "skills/tdd/REVISE.md", "skills/tdd/SKILL-EDIT.md")
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


LEVELS = {"##": 2, "###": 3}


def split_heading(line):
    prefix, space, title = line.partition(" ")
    return (prefix, title) if space else (line, None)


def heading(line):
    prefix, title = split_heading(line)
    if title is None or prefix not in LEVELS:
        return None
    return LEVELS[prefix], title.strip()


def unfenced(lines):
    for line, fenced in zip(lines, markdown_sections.fenced_lines("\n".join(lines))):
        if not fenced:
            yield line


def enclosing(lines):
    names = []
    for line in reversed(list(unfenced(lines))):
        parsed = heading(line)
        if parsed is None:
            continue
        if parsed[0] == 2:
            return tuple(names + [line])
        if not names:
            names.append(line)
    return None


def edited_section(f, revisions):
    code, diff = output("diff", "-U0", revisions, "--", f)
    text = read(f)
    if code != 0 or text is None:
        return None
    lines = text.decode(errors="replace").split("\n")
    numbers = []
    for line in diff.split("\n"):
        if line.startswith("-") and not line.startswith("--- ") and heading(line[1:]) is not None:
            return None
        hunk = HUNK.match(line)
        if hunk:
            start, count = int(hunk.group(1)), int(hunk.group(2) or "1")
            numbers += range(start, start + count) if count else [start]
    sections = set()
    for n in numbers:
        section = enclosing(lines[:n])
        if section is None or heading(lines[n - 1]) is not None:
            return None
        sections.add(section)
    return sections.pop() if len(sections) == 1 else None


def quoted(*names):
    return ["%s%s%s" % (q, n, q) for n in names for q in "'\""]


def forms(*lines):
    found = []
    for line in lines:
        prefix, title = split_heading(line)
        words = title.split()
        for k in range(1, len(words) + 1):
            form = " ".join(words[:k])
            found += quoted(form, prefix + " " + form)
    return found


def lines_of(path):
    return (read(path) or b"").decode(errors="replace").split("\n")


def headings(f):
    return [line for line in lines_of(f) if heading(line) is not None]


SLICERS = ("section", "section_records")
FUNCTION = re.compile(r"^(\w+)\(\)\s*\{")
BOUNDED = re.compile(r"NR >= s && NR <= e|NR < s \|\| NR > e|sed -n \"\$\{\w+\}(,\$\{\w+\})?p\"")


def sliced_lines(lines):
    found, body, name = set(), [], None
    for i, line in enumerate(lines):
        start = FUNCTION.match(line) if name is None else None
        if start:
            name, body = start.group(1), []
        if name is None:
            continue
        body.append(i)
        if line.startswith("}") or (start and line.rstrip().endswith("}")):
            if name in SLICERS or any(BOUNDED.search(lines[k]) for k in body):
                found.update(body)
            name = None
    return found


def reads_only_through_slicers(suite, f):
    lines = lines_of(suite)
    names = []
    for line in lines:
        alternatives = "|".join([re.escape(f)] + [r"\$\{?%s\}?" % n for n in names])
        assigned = re.match(r"^\s*(?:local\s+)?(\w+)=\"?.*?(?:%s)\"?$" % alternatives, line)
        if assigned:
            names.append(assigned.group(1))
    if not names:
        return False
    either = "|".join(names)
    assignment = re.compile(r"^\s*(?:local\s+)?(?:%s)=" % either)
    reading = re.compile(r"\"(?:\$\{?\w+\}?/)*\$\{?(?:%s)\}?\"" % either)
    sliced = sliced_lines(lines)
    return all(i in sliced
               for i, line in enumerate(lines)
               if reading.search(line) and not assignment.match(line))


def pytest_texts():
    return [(p, read(p) or b"") for d in PYTEST_DIRS for p in suites(d + "/test_*.py")]


SECTION_CALL = rb"section\("
ALIASED_SECTION_IMPORT = rb"\bsection\s+as\s+\w+"
OTHER_READ = rb"open\(|read_text\(|read_bytes\("
LITERAL_SECTION_CALL = rb"section\(\s*\w+,\s*(['\"])[^'\"]*\1\s*,?\s*\)"


def pytest_readers(needles):
    def names(text, forms_):
        return any(n.encode() in text for n in forms_)

    def all_literal(text):
        return (len(re.findall(SECTION_CALL, text)) == len(re.findall(LITERAL_SECTION_CALL, text))
                and not re.search(ALIASED_SECTION_IMPORT, text)
                and not re.search(OTHER_READ, text))

    return [p for p, text in pytest_texts()
            if (re.search(SECTION_CALL, text) or re.search(ALIASED_SECTION_IMPORT, text))
            and (names(text, needles) or not all_literal(text))]


def pytest_whole_readers():
    return [p for p, text in pytest_texts()
            if b"SKILL.md" in text
            and (not re.search(SECTION_CALL, text) or re.search(rb"open\(|read_text\(", text))]


def pytest_skill_readers():
    return [p for p, text in pytest_texts() if b"SKILL.md" in text or re.search(SECTION_CALL, text)]


def pytest_files_of(name):
    return [s for d in PYTEST_DIRS for s in existing("%s/test_%s.py" % (d, name))]


def bash_suite_of(name):
    return (existing("%s/tests/unit/%s.test.sh" % (SCRIPTS, name))
            or existing("%s/tests/%s.test.sh" % (SCRIPTS, name))
            or suites_matching(rb"(?<!lib)/" + re.escape(name.encode()) + rb"\.sh"))


def suite_of(f, revisions=None):
    def match(*patterns):
        return any(fnmatch.fnmatchcase(f, p) for p in patterns)

    if match("CLAUDE.md", "Makefile", "skills/*/SKILL.md"):
        naming = suites_naming('"%s"' % f, '/%s"' % f)
        section = f == "skills/tdd/SKILL.md" and revisions and edited_section(f, revisions)
        if section:
            readers = suites_naming(*forms(*section))
            slicers = [s for s in suites_naming(*forms(*headings(f))) if reads_only_through_slicers(s, f)]
            return ([s for s in naming if s in readers or s not in slicers]
                    + pytest_readers(forms(*section)) + pytest_whole_readers())
        return naming + pytest_skill_readers() if f == "skills/tdd/SKILL.md" and revisions else naming
    if f == "README.md":
        return [p for p, text in pytest_texts() if b"README.md" in text]
    if f in SKILL_DOCS:
        name = basename(f).encode()
        return suites_naming(name.decode()) + [p for p, text in pytest_texts() if name in text]
    if match(SCRIPTS + "/tests/*.test.sh", *[d + "/test_*.py" for d in PYTEST_DIRS]):
        return existing(f)
    if match(SCRIPTS + "/tests/fixtures/*"):
        return suites_naming(f[len(SCRIPTS + "/tests/"):])
    if match(SCRIPTS + "/prompts/*.md"):
        names = ("py/test_build_develop_prompt_process.py", "py/test_build_verify_prompt_process.py",
                 "py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py",
                 "py/unit/test_emitted_text.py")
        renderers = [existing(SCRIPTS + "/tests/" + n) for n in names]
        return (suites_naming(f[len(SCRIPTS + "/"):])
                + [s for found in renderers for s in found])
    if match(SCRIPTS + "/lib/*.sh"):
        line = sourcing(basename(f).encode(), rb"(\\)?")
        found = []
        for script in suites(SCRIPTS + "/*.sh"):
            if has_line(script, line):
                found += suite_of(script)
        return found
    if match(SCRIPTS + "/veri/*.py"):
        name = basename(f, ".py")
        return pytest_files_of(name) + bash_suite_of(name.replace("_", "-"))
    if match(SCRIPTS + "/*.sh"):
        name = basename(f, ".sh")
        return pytest_files_of(name.replace("-", "_")) or bash_suite_of(name)
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
        placed.append(SCRIPTS + "/tests/py/unit/test_claude_md_counts.py")

    if unplaced:
        print("affected-suites: no rule places %s; widening to every suite" % ",".join(unplaced), file=sys.stderr)
        placed = [p for p, _ in pytest_texts()]
    elif not placed:
        return 3
    sys.stdout.write("".join(s + "\n" for s in sorted(set(placed))))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
