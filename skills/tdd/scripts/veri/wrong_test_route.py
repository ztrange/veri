"""wrong-test-route.sh's decision, run in-process."""
import os
import re
import sys

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id>"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def _exists(case):
    pattern = re.compile(r"def %s\(" % re.escape(case))
    for root, _dirs, files in os.walk("tests"):
        for name in files:
            if not name.endswith(".py"):
                continue
            with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
                if pattern.search(handle.read()):
                    return True
    return False


def route(report, own_id):
    with open(report, encoding="utf-8", errors="replace") as handle:
        lines = [l for l in handle.read().splitlines() if l.startswith("WRONG_TEST:")]
    for line in lines:
        for case in re.findall(r"\btest_\w+", line):
            if case != own_id and _exists(case):
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
