"""wrong-test-route.sh's decision, run in-process."""
import fnmatch
import os
import re
import sys

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id>"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


SKIPPED = (".git", ".tdd", ".venv", "node_modules")


def is_test_file(name):
    return fnmatch.fnmatch(name, "test_*.py") or name.endswith("_test.py")


def _exists(case):
    py = re.compile(r"def %s\(" % re.escape(case))
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIPPED]
        for name in files:
            if not name.endswith((".py", ".test.sh")):
                continue
            with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            if is_test_file(name) and case.startswith("test_") and py.search(text):
                return True
            if name.endswith(".test.sh") and ('name="%s"' % case) in text:
                return True
    return False


def route(report, own_id):
    with open(report, encoding="utf-8", errors="replace") as handle:
        lines = [l for l in handle.read().splitlines() if l.startswith("WRONG_TEST:")]
    for line in lines:
        names = re.findall(r"\btest_\w+", line) + re.findall(r"`([^`]+)`", line)
        for case in names:
            if case != own_id.rpartition("::")[2] and _exists(case):
                return case
    return None


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        _write(sys.stderr, USAGE)
        return 2
    case = route(argv[0], argv[1])
    if case is None:
        _write(sys.stdout, "revise")
        return 3
    _write(sys.stdout, "red " + case)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
