"""wrong-test-route.sh's decision, run in-process."""
import fnmatch
import json
import os
import re
import sys
import tests_frozen
import tunables

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, repair <case>, supersede <cases> or revise)"


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


def _lines_with(report, prefix):
    with open(report, encoding="utf-8", errors="replace") as handle:
        return [l.lstrip() for l in handle.read().splitlines() if l.lstrip().startswith(prefix)]


def _named_cases(report):
    for line in _lines_with(report, "WRONG_TEST:"):
        yield from re.findall(r"\btest_\w+", line)
        yield from re.findall(r"`([^`]+)`", line)


def route(report, own_id):
    for case in _named_cases(report):
        if case != own_id.rpartition("::")[2] and _exists(case):
            return case
    return None


def _recorded_cases(step):
    try:
        with open(tests_frozen._record_path(step), encoding="utf-8", errors="replace") as handle:
            return {l[6:].strip() for l in handle.read().splitlines() if l.startswith("case: ")}
    except OSError:
        return set()


def _recorded(report, step):
    cases = _recorded_cases(step)
    for case in _named_cases(report):
        if case in cases:
            return case
    return None


def _superseded(report, step):
    own = _recorded_cases(step)
    cases = []
    for line in _lines_with(report, "SUPERSEDED:"):
        words = line[11:].strip().strip("`").split()
        case = words[0].strip("`") if words else ""
        if case and case not in own and case not in cases and _exists(case):
            cases.append(case)
    return cases


def _rerouted(step):
    try:
        with open(".tdd/events.jsonl", encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
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


def _missing(report):
    lines = _lines_with(report, "MISSING_TEST:")
    for line in lines:
        behaviour = line.partition(":")[2].strip()
        if behaviour:
            return behaviour
    if lines:
        _write(sys.stderr, "no well-formed MISSING_TEST: line was found")
    return None


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        _write(sys.stderr, USAGE)
        return 2
    step = tunables.read("VERI_STEP")
    rerouted = _rerouted(step)
    missing = None if rerouted else _missing(argv[0])
    if missing:
        _write(sys.stdout, "missing " + missing)
        return 0
    repair = None if rerouted else _recorded(argv[0], step)
    if repair is not None:
        _write(sys.stdout, "repair " + repair)
        return 0
    older = [] if rerouted else _superseded(argv[0], step)
    if len(older) >= 2:
        if any(c not in older and _exists(c) for c in _named_cases(argv[0])):
            _write(sys.stdout, "revise")
            return 3
        _write(sys.stdout, "supersede " + " ".join(older))
        return 0
    case = None if rerouted else route(argv[0], argv[1])
    if case is None and len(older) == 1:
        case = older[0]
    if case is None:
        _write(sys.stdout, "revise")
        return 3
    _write(sys.stdout, "red " + case)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
