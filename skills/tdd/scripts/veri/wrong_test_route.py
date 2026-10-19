"""wrong-test-route.sh's decision, run in-process."""
import fnmatch
import hashlib
import json
import os
import re
import sys
import tunables

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id>"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


SKIPPED = (".git", ".tdd", ".venv", "node_modules")


def is_test_file(name):
    return fnmatch.fnmatch(name, "test_*.py") or name.endswith("_test.py")


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _exists(case):
    py = re.compile(r"def %s\(" % re.escape(case))
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIPPED]
        for name in files:
            if not name.endswith((".py", ".test.sh")):
                continue
            text = _read(os.path.join(root, name))
            if is_test_file(name) and case.startswith("test_") and py.search(text):
                return True
            if name.endswith(".test.sh") and ('name="%s"' % case) in text:
                return True
    return False


def _wrong_test_lines(report):
    return [l for l in _read(report).splitlines() if l.startswith("WRONG_TEST:")]


def _test_names(line):
    return re.findall(r"\btest_\w+", line)


def route(report, own_id):
    for line in _wrong_test_lines(report):
        names = _test_names(line) + re.findall(r"`([^`]+)`", line)
        for case in names:
            if case != own_id.rpartition("::")[2] and _exists(case):
                return case
    return None


def _recorded_case(report, step):
    record = ".tdd/tests-frozen-%s.record" % hashlib.sha256(os.fsencode(step)).hexdigest()[:16]
    try:
        rows = _read(record).splitlines()
        files = [l.split(None, 1)[1].strip() for l in rows if len(l.split(None, 1)) == 2 and not l.startswith("#")]
        added = [l.split(":", 1)[1].strip() for l in rows if l.startswith("# case:")]
        lines = _wrong_test_lines(report)
    except OSError:
        return None
    for name in files:
        try:
            text = _read(name)
        except OSError:
            continue
        for line in lines:
            for case in _test_names(line):
                if added and case not in added:
                    continue
                if re.search(r"def %s\(" % re.escape(case), text):
                    return case
    return None


def _rerouted(step):
    try:
        lines = _read(".tdd/events.jsonl").splitlines()
    except OSError:
        return False
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("event") == "reroute" and event.get("step") == step:
            return True
    return False


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        _write(sys.stderr, USAGE)
        return 2
    step = tunables.read("VERI_STEP")
    rerouted = _rerouted(step)
    repaired = None if rerouted else _recorded_case(argv[0], step)
    if repaired is not None:
        _write(sys.stdout, "repair " + repaired)
        return 0
    case = None if rerouted else route(argv[0], argv[1])
    if case is None:
        _write(sys.stdout, "revise")
        return 3
    _write(sys.stdout, "red " + case)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
