"""transform-touches-tests.sh's range check, run in-process."""
import re
import subprocess
import sys

USAGE = "usage: transform-touches-tests.sh <base-sha>"
TEST_FILE = re.compile(rb"(^|/)tests/|\.test\.")
REFACTOR_OWED = re.compile(rb"\.tdd/issue-[0-9]+-refactor-owed\.md")


def refuse(message=None, usage=None):
    if message:
        print(message, file=sys.stderr)
    print(usage or USAGE, file=sys.stderr)
    return 2


def changed_paths(base):
    log = subprocess.run(["git", "log", "--format=", "--name-only", f"{base}..HEAD"],
                         stdout=subprocess.PIPE)
    if log.returncode != 0:
        return None
    return log.stdout.split(b"\n")


def sorted_names(lines):
    matched = b"".join(line + b"\n" for line in lines)
    return subprocess.run(["sort", "-u"], input=matched, stdout=subprocess.PIPE).stdout.rstrip(b"\n").decode()


def main(argv):
    base = argv[0] if argv else ""
    if not base:
        return refuse()
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        return refuse(f"transform-touches-tests.sh: base-sha does not resolve to a commit: {base}")
    paths = changed_paths(base)
    if paths is None:
        return 2
    touched = sorted_names(line for line in paths if TEST_FILE.search(line))
    if touched:
        print(f"transform changed a test file: {touched}")
        return 1
    bound = set(argv[1].encode().split(b",")) if len(argv) > 1 and argv[1] else None
    if bound is None:
        return 0
    outside = sorted_names(line for line in paths if line and line not in bound and not REFACTOR_OWED.fullmatch(line))
    if not outside:
        return 0
    print(f"transform changed a file outside its bound: {outside}")
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
