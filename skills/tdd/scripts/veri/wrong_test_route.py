"""wrong-test-route.sh's decision, run in-process."""
import event_log
import fnmatch
import os
import re
import sys
import tests_frozen
import tunables
from entry import write

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, repair <case> <superseded>…, supersede <cases> or revise)"


SKIPPED = (".git", ".tdd", ".venv", "node_modules")


def is_test_file(name):
    return fnmatch.fnmatch(name, "test_*.py") or name.endswith("_test.py")


JS_EXT = r"\.(?:jsx?|tsx?|mjs|cjs)$"


def is_js_test_file(name, root=""):
    if name.endswith(".d.ts"):
        return False
    if re.search(r"\.(?:test|spec)" + JS_EXT, name):
        return True
    in_tests = "__tests__" in root.replace("\\", "/").split("/")
    return in_tests and re.search(JS_EXT, name) is not None


def _live_call(pattern, text):
    def code(prefix):
        return re.sub(r"\"[^\"]*\"|'[^']*'|`[^`]*`", "", prefix)
    return [m.group(2) for m in pattern.finditer(text)
            if "//" not in code(text[text.rfind("\n", 0, m.start()) + 1:m.start()])]


def _cut_prefix(case):
    return case[:-1] if case.endswith("…") else case[:-3] if case.endswith("...") else None


def _js_title_pattern(case):
    prefix = _cut_prefix(case)
    title = "(%s(?:(?!\\1).)*)" % re.escape(prefix) if prefix is not None else "(%s)" % re.escape(case)
    return re.compile(r"\b(?:it|test)(?:\.(?:only|skip))?(?:\.each(?:\([^)]*\)|`[^`]*`))?\(\s*(['\"])" + title + r"\1")


def _exists(case):
    py = re.compile(r"def %s\(" % re.escape(case))
    js = _js_title_pattern(case)
    titles = set()
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIPPED]
        for name in files:
            js_file = is_js_test_file(name, root)
            if not name.endswith((".py", ".test.sh")) and not js_file:
                continue
            with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            if is_test_file(name) and case.startswith("test_") and py.search(text):
                return case
            found = _live_call(js, re.sub(r"/\*.*?\*/", "", text, flags=re.S)) if js_file else []
            if found and _cut_prefix(case) is None:
                return found[0]
            titles.update(found)
            if name.endswith(".test.sh") and ('name="%s"' % case) in text:
                return case
    return titles.pop() if len(titles) == 1 else None


def _fixture(report):
    for name in _named_cases(report):
        if name.startswith("test_"):
            continue
        helper = re.compile(r"^def %s\(" % re.escape(name), re.M)
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in SKIPPED]
            for file in files:
                if not is_test_file(file):
                    continue
                path = os.path.join(root, file)
                with open(path, encoding="utf-8", errors="replace") as handle:
                    if helper.search(handle.read()):
                        return os.path.normpath(path), name
    return None


def _lines_with(report, prefix):
    with open(report, encoding="utf-8", errors="replace") as handle:
        return [l for l in handle.read().splitlines() if l.startswith(prefix)]


def _named_cases(report):
    for line in _lines_with(report, "WRONG_TEST:"):
        yield from re.findall(r"\btest_\w+", line)
        yield from re.findall(r"`([^`]+)`", line)
        yield from re.findall(r'"([^"]+)"', line)
        yield from re.findall(r"“([^”]+)”", line)


def _case_name(test_id):
    return test_id.rpartition("::")[2]


def _is_own(case, own_id):
    tail = _case_name(own_id)
    if case == tail:
        return True
    if not tail.endswith(" " + case):
        return False
    words = tail.split(" ")
    longer = (" ".join(words[i:]) for i in range(len(words)))
    return not any(len(t) > len(case) and t != tail and _exists(t) for t in longer)


def route(report, own_id):
    for case in _named_cases(report):
        if not _is_own(case, own_id):
            found = _exists(case)
            if found and not _is_own(found, own_id):
                return found
    return None


def _recorded_cases(step):
    try:
        with open(tests_frozen._record_path(step), encoding="utf-8", errors="replace") as handle:
            return {l[6:].strip() for l in handle.read().splitlines() if l.startswith("case: ")}
    except OSError:
        return set()


def _recorded(report, step, own_id):
    cases = _recorded_cases(step)
    own = _case_name(own_id)
    if own in set(_named_cases(report)) and route(report, own_id) is not None:
        cases.add(own)
    for case in _named_cases(report):
        if case in cases:
            return case
    return None


def _superseded(report, step, own_id=None):
    own = _recorded_cases(step)
    cases = []
    for line in _lines_with(report, "SUPERSEDED:"):
        body = re.sub(r"^[-*]\s+", "", line[11:].strip())
        quoted = re.match(r'"([^"]+)"', body)
        words = body.strip("`").split()
        case = quoted.group(1) if quoted else words[0].strip("`") if words else ""
        found = _exists(case) if case and case not in own else None
        if found and found not in cases and not (own_id and _is_own(found, own_id)):
            cases.append(found)
    return cases


def _rerouted(step):
    try:
        events = event_log.read_events(".tdd/events.jsonl", skip_unreadable=True)
    except (OSError, UnicodeDecodeError):
        return False
    return any(event.get("event") == "reroute" and event.get("step") == step for event in events)


def _missing(report):
    lines = _lines_with(report, "MISSING_TEST:")
    for line in lines:
        behaviour = line.partition(":")[2].strip()
        if behaviour == "NONE":
            return None
        if behaviour:
            return behaviour
    if lines:
        write(sys.stderr, "no well-formed MISSING_TEST: line was found")
    return None


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        write(sys.stderr, USAGE)
        return 2
    step = tunables.read("VERI_STEP")
    rerouted = _rerouted(step)
    missing = None if rerouted else _missing(argv[0])
    if missing:
        write(sys.stdout, "missing " + missing)
        return 0
    repair = None if rerouted else _recorded(argv[0], step, argv[1])
    if repair is not None:
        superseded = _superseded(argv[0], step)
        if superseded != _superseded(argv[0], step, argv[1]):
            write(sys.stdout, "revise")
            return 3
        write(sys.stdout, " ".join(["repair", repair] + [c for c in superseded if c != repair and c not in _recorded_cases(step)]))
        return 0
    recorded = _recorded_cases(step)
    older = [] if rerouted else [c for c in _superseded(argv[0], step, argv[1]) if c not in recorded]
    if len(older) >= 2:
        if any(c not in older and _exists(c) for c in _named_cases(argv[0])):
            write(sys.stdout, "revise")
            return 3
        write(sys.stdout, "supersede " + " ".join(older))
        return 0
    case = None if rerouted else route(argv[0], argv[1])
    if case is None and len(older) == 1:
        case = older[0]
    fixture = None if case is not None else _fixture(argv[0])
    if fixture is not None:
        write(sys.stdout, "fixture %s %s" % fixture)
        return 0
    if case is None:
        write(sys.stdout, "revise")
        return 3
    write(sys.stdout, "red " + case)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
