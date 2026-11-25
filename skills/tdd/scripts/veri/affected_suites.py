"""affected-suites.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import fnmatch
import glob
import os
import re
import subprocess
import sys

import case_reader
import entry
from git import git

import markdown_sections
import run_line
import stem_walk

USAGE = "usage: affected-suites.sh <base>..<head>"
SCRIPTS = "skills/tdd/scripts"
PYTEST_DIRS = (SCRIPTS + "/tests/py", SCRIPTS + "/tests/py/unit")
PYFLAKES_GATE = SCRIPTS + "/tests/py/test_ruff_tree_audit_process.py"
SKILL_DOCS = ("skills/tdd/SCRIPTS.md", "skills/tdd/STOPPING.md", "skills/tdd/RECONCILE.md",
              "skills/tdd/BAIL.md", "skills/tdd/PIN.md", "skills/tdd/RESUME.md",
              "skills/tdd/REVISE.md", "skills/tdd/SKILL-EDIT.md", "skills/tdd/STRUCTURAL.md",
              "skills/tdd/PHASED.md", "skills/tdd/REFACTOR-KIND.md", "skills/tdd/PREFLIGHT.md",
              "skills/tdd/DRAFT-PR.md", "skills/tdd/SUITE-REPAIR.md",
              "skills/tdd/DIFF-CHECKED.md", "skills/tdd/LEGACY.md")
SPACE = rb"[ \t\n\v\f\r]"


class Unplaced(Exception):
    pass


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def suites(pattern):
    return sorted(glob.glob(pattern))


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
    flat = "\n".join(" ".join(line.splitlines()) for line in lines)
    for line, fenced in zip(lines, markdown_sections.fenced_lines(flat)):
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
    """The test files of module <name>: test_<name>.py, unit/test_<name>.py, test_<name>_process.py, and every process
    test file naming the module (#4425)."""
    return [s for d in PYTEST_DIRS for s in existing("%s/test_%s.py" % (d, name))] + existing(
        "%s/test_%s_process.py" % (PYTEST_DIRS[0], name)) + process_files_of(name)


IMPORT = re.compile(rb"^[ \t]*(?:import|from)[ \t]+(\w+)", re.M)
SHIM_EXEC = re.compile(rb"^[ \t]*exec[ \t][^\n]*\bveri/(\w+)\.py\b", re.M)
TREES = {}


def tree_index():
    """Read once per working directory and run, since a range of modules asks again and again: the process test files'
    texts (`-` read as `_`), the modules under veri/ and tests/leg/ importing each name, the shims whose exec line names
    each module, and the answers given so far."""
    cwd = os.getcwd()
    if cwd not in TREES:
        imports = {}
        for p in suites(SCRIPTS + "/veri/*.py") + suites(SCRIPTS + "/tests/leg/*.py"):
            for imported in dict.fromkeys(IMPORT.findall(read(p) or b"")):
                imports.setdefault(imported.decode(), []).append(basename(p, ".py"))
        shims = {}
        for p in suites(SCRIPTS + "/*.sh"):
            for module in dict.fromkeys(SHIM_EXEC.findall(read(p) or b"")):
                shims.setdefault(module.decode(), []).append(stem_walk.stem(p))
        TREES[cwd] = (stem_walk.texts(suites(PYTEST_DIRS[0] + "/test_*_process.py")), imports, shims, {})
    return TREES[cwd]


def process_files_naming(name):
    """The tests/py/test_*_process.py files that import or run module <name> (`-` read as `_`) by name: `veri.<name>`,
    `<name>.py`, `<name>.sh` or `<shim>.sh` for each shim whose exec line names `veri/<name>.py` (`report.sh` for
    `prd_report`), as a whole word."""
    processes, _, shims, found = tree_index()
    if name not in found:
        needles = ["veri." + name, name + ".py", name + ".sh"] + [shim + ".sh" for shim in shims.get(name, [])]
        found[name] = stem_walk.naming_in(needles, processes)
    return found[name]


def importers(name):
    """The modules under veri/ and tests/leg/ whose own line imports module <name> (`import <name>` or
    `from <name> import`)."""
    return [user for user in tree_index()[1].get(name, []) if user != name]


def process_files_of(name):
    """The process test files of module <name>: those naming it, or, when none does, those naming a module that imports
    it directly, one hop and no further, so a helper with no process file of its own is still run (#4425)."""
    return process_files_naming(name) or [p for user in importers(name) for p in process_files_naming(user)]


def suite_of(f, revisions=None):
    def match(*patterns):
        return any(fnmatch.fnmatchcase(f, p) for p in patterns)

    if match("CLAUDE.md", "Makefile", "skills/*/SKILL.md"):
        section = f == "skills/tdd/SKILL.md" and revisions and edited_section(f, revisions)
        if section:
            return pytest_readers(forms(*section)) + pytest_whole_readers()
        return pytest_skill_readers() if f == "skills/tdd/SKILL.md" and revisions else []
    if f == "README.md":
        return [p for p, text in pytest_texts() if b"README.md" in text]
    if f in SKILL_DOCS:
        name = basename(f).encode()
        return [p for p, text in pytest_texts() if name in text]
    if match(*[d + "/test_*.py" for d in PYTEST_DIRS]):
        return existing(f)
    if match(SCRIPTS + "/tests/fixtures/*"):
        return []
    if match(SCRIPTS + "/prompts/*.md"):
        names = ("py/test_build_develop_prompt_process.py", "py/test_build_verify_prompt_process.py",
                 "py/unit/test_build_develop_prompt.py", "py/unit/test_build_verify_prompt.py")
        renderers = [existing(SCRIPTS + "/tests/" + n) for n in names]
        return [s for found in renderers for s in found]
    if match(SCRIPTS + "/lib/*.sh"):
        line = sourcing(basename(f).encode(), rb"(\\)?")
        found = []
        for script in suites(SCRIPTS + "/*.sh"):
            if has_line(script, line):
                found += suite_of(script)
        return found
    if match(SCRIPTS + "/veri/*.py", SCRIPTS + "/tests/leg/*.py"):  # tests/leg/: the pytest leg, out of veri/ (#4051)
        name = basename(f, ".py")
        return pytest_files_of(name)
    if match(SCRIPTS + "/*.sh"):
        return pytest_files_of(basename(f, ".sh").replace("-", "_"))
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


def unquoted(path):
    """<path> as git names it with core.quotePath on: a name holding a non-ASCII byte, a quote, a backslash or a control
    character comes double-quoted with C escapes (`"tests/test_caf\\303\\251.py"`); any other name is unchanged."""
    if len(path) < 2 or not (path.startswith('"') and path.endswith('"')):
        return path
    raw = path[1:-1].encode("latin-1", "backslashreplace").decode("unicode_escape").encode("latin-1")
    return raw.decode("utf-8", "surrogateescape")


def is_test_file(path):
    """Whether the file at <path> is itself a Python, Go or JavaScript test file by its name, not a helper, fixture or
    snapshot that only sits among the tests."""
    root, name = os.path.split(path)
    return (case_reader.is_test_file(name) or case_reader.is_go_test_file(name)
            or bool(case_reader.is_js_test_file(name, root)))


def foreign(files):
    """The selection outside veri's own tree (no `skills/tdd/scripts/tests/py` directory at the base commit, whatever
    the working tree holds): exit code, suites printed."""
    files = [f for f in files if not f.startswith(".tdd/")]
    placed = [f for f in files if case_reader.is_test_path(f) and os.path.isfile(f)]
    sources = [f for f in files if not case_reader.is_test_path(f)]
    if sources:
        listed = [p for p in stem_walk.tree_files() if case_reader.is_test_path(p)]
        tests = [p for p in listed if is_test_file(p)] or listed
        unnamed = []
        for f in sources:
            naming = stem_walk.naming(stem_walk.stem(f), tests)
            placed += naming
            if not naming:
                unnamed.append(f)
        if unnamed:
            print("affected-suites: no test names %s; no test file covers them, so the full suite at the PR runs them"
                  % ",".join(unnamed), file=sys.stderr)
    if not placed:
        return 3
    sys.stdout.write("".join(s + "\n" for s in sorted(set(placed))))
    return 0


def main(argv):
    if not argv or not argv[0]:
        return entry.refuse(usage=USAGE)
    TREES.clear()
    revisions = argv[0]
    for rev in revisions.split("..", 1):
        if git("rev-parse", "--verify", "--quiet", rev + "^{commit}", stdout=subprocess.DEVNULL).returncode != 0:
            return entry.refuse("affected-suites: cannot resolve revision '%s'" % rev, usage=USAGE)

    base = revisions.split("..", 1)[0]
    working_tree = ".." not in revisions
    if not working_tree:
        revisions = revisions.replace("..", "...", 1)
    code, files = changed(revisions)
    if code != 0:
        return entry.to_contract(code)
    if working_tree:
        _, new = untracked()
        files = "\n".join(f for f in [files, new] if f)
    if not files:
        return 3

    if not run_line.own_tree_at(base):
        return foreign([unquoted(f) for f in files.split("\n")])

    placed, unplaced = [], []
    for f in files.split("\n"):
        if unquoted(f).endswith(".py"):  # the pyflakes gate checks every .py file, a test file's included (#4746)
            placed += existing(PYFLAKES_GATE)
        try:
            placed += suite_of(f, revisions)
        except Unplaced:
            unplaced.append(f)

    if unplaced:
        print("affected-suites: no rule places %s; no test file covers them, so the full suite at the PR runs them"
              % ",".join(unplaced), file=sys.stderr)
    if not placed:
        return 3
    sys.stdout.write("".join(s + "\n" for s in sorted(set(placed))))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
