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


def decide(tier, issue, root):
    def at(name):
        return root + "/" + name

    def has(name):
        return os.path.isfile(at(name))

    def pytest_configured():
        return (has("pytest.ini")
                or declares(at("pyproject.toml"), rb"^\[tool\.pytest")
                or declares(at("setup.cfg"), rb"^\[tool:pytest\]"))

    if tier != "fast" and tier not in DECLARED_ONLY and issue and os.path.isfile(issue):
        try:
            answer_from_file(issue, b"Test command:")
        except Answer as found:
            if found.command != resolved("fast", issue, root) and not selects_subset(found.command, root):
                raise
    if tier and has("CLAUDE.md"):
        suffix = b":" if tier in COLON_MARKED else b" tests:"
        answer_from_file(at("CLAUDE.md"), b"veri: " + os.fsencode(tier) + suffix)
    if tier in DECLARED_ONLY:
        return
    if tier == "quiet test files":
        if pytest_configured():
            raise Answer(b"pytest -q --no-header -rf")
        if declares(at("package.json"), rb'"scripts"\s*:\s*\{[^}]*"test"\s*:\s*"[^"]*\bjest\b'):
            raise Answer(b"npx jest --silent")
    if has("package.json") and re.search(rb'"scripts":\{[^}]*"test":', bytes(b for b in read(at("package.json")) if b not in SPACE)):
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


def resolved(tier, issue, root):
    try:
        decide(tier, issue, root)
    except Answer as found:
        return found.command
    return None


def option(args, flag):
    if args[:1] != [flag]:
        return "", args
    if len(args) < 2:
        return None, args
    return args[1], args[2:]


USAGE = 'usage: detect-test-command.sh [--tier fast|all|"one test file"|"quiet test files"|lint] [--issue <body-file>] [repo-root]'


def main(argv):
    tier, args = option(list(argv), "--tier")
    if tier is None:
        return 2
    issue, args = option(args, "--issue")
    if issue is None:
        return 2
    root = args[0] if args and args[0] else "."
    command = resolved(tier, issue, root)
    if command is None:
        return 3
    sys.stdout.buffer.write(command + b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
