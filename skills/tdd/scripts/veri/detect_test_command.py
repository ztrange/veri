"""detect-test-command.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import re
import sys

SPACE = b" \t\n\v\f\r"


class Answer(Exception):
    def __init__(self, command):
        self.command = command


def read(path):
    with open(path, "rb") as f:
        return f.read()


def lines_of(path):
    lines = read(path).split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def unwrapped(text):
    if text.startswith(b"`"):
        return text[1:].split(b"`", 1)[0]
    return text


def answer_from(line, marker):
    rest, seen = line, b""
    while marker in rest:
        before, rest = rest.split(marker, 1)
        seen += before
        if seen.count(b"`") % 2 == 1:
            continue
        command = unwrapped(rest.lstrip(SPACE))
        if command:
            raise Answer(command)


def answer_from_file(path, marker):
    for line in lines_of(path):
        answer_from(line, marker)


def declares(path, pattern):
    if not os.path.isfile(path):
        return False
    return re.search(pattern, read(path), re.M) is not None


def selects_subset(command, root):
    if not os.path.isfile(root + "/CLAUDE.md"):
        return False
    try:
        answer_from_file(root + "/CLAUDE.md", b"veri: all tests:")
    except Answer as found:
        return command.startswith(found.command + b" TESTS=")
    return False


# The tiers a repo declares only in its CLAUDE.md, as `veri: <tier>: <command>`: never inferred, never from the issue.
DECLARED_ONLY = ("one test file", "lint")
# The tiers whose CLAUDE.md marker ends in a bare colon, `veri: <tier>: <command>`, not ` tests:`.
COLON_MARKED = DECLARED_ONLY + ("quiet test files",)
# The tiers an issue's `Test command:` never answers.
NEVER_FROM_ISSUE = ("fast", "quiet test files") + DECLARED_ONLY


def decide(tier, issue, root, claude_md=None):
    def at(name):
        return root + "/" + name

    def has(name):
        return os.path.isfile(at(name))

    def pytest_configured():
        return (has("pytest.ini")
                or declares(at("pyproject.toml"), rb"^\[tool\.pytest")
                or declares(at("setup.cfg"), rb"^\[tool:pytest\]"))

    if tier not in NEVER_FROM_ISSUE and issue and os.path.isfile(issue):
        try:
            answer_from_file(issue, b"Test command:")
        except Answer as found:
            if found.command != resolved("fast", issue, root) and not selects_subset(found.command, root):
                raise
    declared_only = tier in DECLARED_ONLY or claude_md is not None
    if tier and claude_md is None and has("CLAUDE.md"):
        claude_md = read(at("CLAUDE.md"))
    if tier and claude_md is not None:
        suffix = b":" if tier in COLON_MARKED else b" tests:"
        for line in claude_md.split(b"\n"):
            answer_from(line, b"veri: " + os.fsencode(tier) + suffix)
    if declared_only:
        return
    if tier == "quiet test files":
        if pytest_configured():
            raise Answer(b"pytest -q --no-header -rf")
        if declares(at("package.json"), rb'"scripts"\s*:\s*\{[^}]*"test"\s*:\s*"[^"]*\bjest\b'):
            raise Answer(b"npx jest --silent")
        return
    if has("package.json") and re.search(rb'"scripts":\{[^}]*"test":',
                                         bytes(b for b in read(at("package.json")) if b not in SPACE)):
        if has("pnpm-lock.yaml"):
            raise Answer(b"pnpm test")
        if has("yarn.lock"):
            raise Answer(b"yarn test")
        raise Answer(b"npm test")
    if declares(at("Makefile"), rb"^test[ \t\v\f\r]*:"):
        raise Answer(b"make test")
    if pytest_configured():
        raise Answer(b"pytest -q")
    if has("go.mod"):
        raise Answer(b"go test ./...")
    if has("Cargo.toml"):
        raise Answer(b"cargo test")
    if any(os.path.isfile(f) for f in glob.glob(glob.escape(root) + "/tests/test_*.py")):
        raise Answer(b"python3 -m unittest discover -q")


def resolved(tier, issue, root, claude_md=None):
    try:
        decide(tier, issue, root, claude_md)
    except Answer as found:
        return found.command
    return None


def option(args, flag):
    if args[:1] != [flag]:
        return "", args
    if len(args) < 2:
        return None, args
    return args[1], args[2:]


USAGE = ('usage: detect-test-command.sh [--tier fast|all|"one test file"|"quiet test files"|lint] [--issue <body-file>]'
         ' [--at <commit>] [repo-root]')
# Every file decide() reads at a root, besides the tests/ directory's test_*.py files.
READ_AT = ("CLAUDE.md", "package.json", "pnpm-lock.yaml", "yarn.lock", "Makefile", "pytest.ini", "pyproject.toml",
           "setup.cfg", "go.mod", "Cargo.toml")


class Unresolved(Exception):
    """<commit> names no commit git resolves in <root>."""


def at_commit(tier, issue, root, commit):
    """resolved(), its every repo file read from the tree <commit> holds in <root>'s repository, never from <root>'s
    working tree (#4263): the files decide() reads are copied out of <commit> into a scratch directory, which stands in
    for <root>. Raises Unresolved when git resolves no such commit there."""
    import tempfile  # git pulls subprocess, tempfile random and shutil: only this path needs either

    import git

    if not git.ok("rev-parse", "--verify", "--quiet", commit + "^{commit}", cwd=root):
        raise Unresolved(commit)
    with tempfile.TemporaryDirectory() as snapshot:
        os.mkdir(os.path.join(snapshot, "tests"))
        listed = git.git("ls-tree", "-z", commit, "--", *READ_AT, "tests/", cwd=root, capture_output=True).stdout
        for entry in filter(None, listed.split(b"\0")):
            meta, path = entry.split(b"\t", 1)
            _, kind, blob = meta.split()
            if kind != b"blob":
                continue
            with open(os.path.join(snapshot, os.fsdecode(path)), "wb") as f:
                f.write(git.git("cat-file", "blob", os.fsdecode(blob), cwd=root, capture_output=True).stdout)
        return resolved(tier, issue, snapshot)


def main(argv):
    tier, args = option(list(argv), "--tier")
    if tier is None:
        return 2
    issue, args = option(args, "--issue")
    if issue is None:
        return 2
    pinned = args[:1] == ["--at"]
    commit, args = option(args, "--at")
    if commit is None:
        return 2
    root = args[0] if args and args[0] else "."
    if pinned:
        try:
            command = at_commit(tier, issue, root, commit)
        except Unresolved:
            print("detect-test-command.sh: --at %r names no commit git can resolve in %s" % (commit, root),
                  file=sys.stderr)
            return 2
    else:
        command = resolved(tier, issue, root)
    if command is None:
        return 3
    sys.stdout.buffer.write(command + b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
