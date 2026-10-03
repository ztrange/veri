"""detect-test-command.sh's computations, run in-process."""
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


def decide(tier, issue, root):
    if tier != "fast" and issue and os.path.isfile(issue):
        answer_from_file(issue, b"Test command:")
    if tier and os.path.isfile(root + "/CLAUDE.md"):
        answer_from_file(root + "/CLAUDE.md", b"veri: " + os.fsencode(tier) + b" tests:")
    override = root + "/.veri/test-command"
    if os.path.isfile(override):
        for line in lines_of(override):
            if line:
                raise Answer(line)
    pkg = root + "/package.json"
    if os.path.isfile(pkg) and re.search(rb'"scripts":\{[^}]*"test":', bytes(b for b in read(pkg) if b not in SPACE)):
        if os.path.isfile(root + "/pnpm-lock.yaml"):
            raise Answer(b"pnpm test")
        if os.path.isfile(root + "/yarn.lock"):
            raise Answer(b"yarn test")
        raise Answer(b"npm test")
    if declares(root + "/Makefile", rb"^test[ \t\v\f\r]*:"):
        raise Answer(b"make test")
    if (os.path.isfile(root + "/pytest.ini")
            or declares(root + "/pyproject.toml", rb"^\[tool\.pytest")
            or declares(root + "/setup.cfg", rb"^\[tool:pytest\]")):
        raise Answer(b"pytest -q")
    if os.path.isfile(root + "/go.mod"):
        raise Answer(b"go test ./...")
    if os.path.isfile(root + "/Cargo.toml"):
        raise Answer(b"cargo test")
    if any(os.path.isfile(f) for f in glob.glob(glob.escape(root) + "/tests/test_*.py")):
        raise Answer(b"python3 -m unittest discover -q")


def main(argv):
    args = list(argv)
    tier = ""
    if args[:1] == ["--tier"]:
        if len(args) < 2:
            return 1
        tier, args = args[1], args[2:]
    issue = ""
    if args[:1] == ["--issue"]:
        if len(args) < 2:
            return 1
        issue, args = args[1], args[2:]
    root = args[0] if args and args[0] else "."
    try:
        decide(tier, issue, root)
    except Answer as found:
        sys.stdout.buffer.write(found.command + b"\n")
        sys.stdout.buffer.flush()
        return 0
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
