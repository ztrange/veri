"""wrong-test-route.sh's decision, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import event_log
import fnmatch
import os
import re
import sys
import tests_frozen
import tunables
from js_tests import CALL, is_js_test_file
from entry import write

USAGE = "usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, repair <case> <superseded>…, supersede <cases> or revise)"


SKIPPED = (".git", ".tdd", ".venv", "node_modules")


def is_test_file(name):
    return fnmatch.fnmatch(name, "test_*.py") or name.endswith("_test.py")


def _live_call(pattern, text):
    def code(prefix):
        return re.sub(r"\"[^\"]*\"|'[^']*'|`[^`]*`", "", prefix)
    return [m.group(2) for m in pattern.finditer(text)
            if "//" not in code(text[text.rfind("\n", 0, m.start()) + 1:m.start()])]


def _cut_prefix(case):
    return case[:-1] if case.endswith("…") else case[:-3] if case.endswith("...") else None


def _js_title_pattern(case):
    prefix = _cut_prefix(case)
    gap = "(?:(?!\\1).)*"
    if prefix is not None:
        title = "(%s%s)" % (re.escape(prefix), gap)
    else:
        title = "(%s)" % gap.join(re.escape(part) for part in re.split(r"…|\.\.\.", case))
    return re.compile(CALL + r"(['\"])" + title + r"\1")


def _files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIPPED]
        for name in files:
            yield root, name


def _exists(case):
    cut = _cut_prefix(case)
    py = re.compile(r"def (%s\w*)\(" % re.escape(cut)) if cut else re.compile(r"def (%s)\(" % re.escape(case))
    go = re.compile(r"func (%s)\(" % re.escape(case))
    js = _js_title_pattern(case)
    titles = set()
    for root, name in _files():
        js_file = is_js_test_file(name, root)
        go_file = name.endswith("_test.go")
        if not name.endswith((".py", ".test.sh")) and not js_file and not go_file:
            continue
        with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        match = (go.search(text) if go_file else
                 py.search(text) if is_test_file(name) and case.startswith("test_") else None)
        if match:
            return match.group(1)
        found = _live_call(js, re.sub(r"/\*.*?\*/", "", text, flags=re.S)) if js_file else []
        if found and cut is None:
            return found[0]
        titles.update(found)
        if name.endswith(".test.sh") and ('name="%s"' % case) in text:
            return case
    return titles.pop() if len(titles) == 1 else None


def _fixture(report):
    for name in _named_cases(report):
        if name.startswith("test_"):
            continue
        escaped = re.escape(name)
        helper = re.compile(r"^def %s\(" % escaped, re.M)
        js_helper = re.compile(
            r"^\s*(?:export\s+)?(?:(?:async\s+)?function\s+{0}\(|const\s+{0}\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>))".format(escaped), re.M)
        for root, file in _files():
            py_file = is_test_file(file)
            if not py_file and not is_js_test_file(file, root):
                continue
            path = os.path.join(root, file)
            with open(path, encoding="utf-8", errors="replace") as handle:
                if (helper if py_file else js_helper).search(handle.read()):
                    return os.path.normpath(path), name
    return None


def _lines_with(report, prefix):
    with open(report, encoding="utf-8", errors="replace") as handle:
        return [l for l in handle.read().splitlines() if l.startswith(prefix)]


def _named_cases(report):
    for line in _lines_with(report, "WRONG_TEST:"):
        yield from re.findall(r"\btest_\w+", line)
        yield from re.findall(r"\bTest[A-Z]\w*", line)
        yield from re.findall(r"`([^`]+)`", line)
        yield from re.findall(r'"([^"]+)"', line)
        yield from re.findall(r"“([^”]+)”", line)
        yield from re.findall(r"\S\s+›\s+(\S.*?)\s*$", line)


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
        case = case.rpartition(" > ")[2]
        if case in cases:
            return case
    return None


def _superseded_case(body):
    quoted = re.match(r'(?:`[^`]+`\s+)?(?:"([^"]+)"|“([^”]+)”)', body)
    if quoted:
        return quoted.group(1) or quoted.group(2)
    separated = re.match(r'\S+\s+›\s+(?:"([^"]+)"$|(\S.*)$)', body)
    if separated:
        return (separated.group(1) or separated.group(2)).strip()
    if _exists(body.strip()):
        return body.strip()
    prose = re.sub(r"^#\d+\s+", "", body).strip()
    if _exists(prose):
        return prose
    words = body.strip("`").split()
    return words[0].strip("`").rpartition("::")[2] if words else ""


def _superseded(report, step, own_id=None):
    own = _recorded_cases(step)
    cases = []
    for line in _lines_with(report, "SUPERSEDED:"):
        body = re.sub(r"^[-*]\s+", "", line[11:].strip())
        case = _superseded_case(body)
        if case in own:
            continue
        if not case:
            write(sys.stderr, "the line carried no case name: " + line)
            continue
        found = _exists(case)
        if found is None:
            write(sys.stderr, "no defined test case resolves: " + line)
        if found and found not in cases and not (own_id and _is_own(found, own_id)):
            cases.append(found)
    return cases


def _reroutes(step):
    try:
        events = event_log.read_events(".tdd/events.jsonl", skip_unreadable=True)
    except OSError:
        return []
    latest_resume = max((i for i, e in enumerate(events) if e.get("event") == "resume"), default=-1)
    return [e for i, e in enumerate(events) if i > latest_resume and e.get("event") == "reroute" and e.get("step") == step]


def _rerouted(step):
    return bool(_reroutes(step))


def _missing_reroutes(step):
    return sum(1 for e in _reroutes(step) if e.get("kind") == "missing")


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
    missing = _missing(argv[0])
    if missing:
        budget = tunables.read("VERI_MISSING_REROUTE_BUDGET", unless_empty="3")
        if _missing_reroutes(step) >= int(budget):
            write(sys.stdout, "missing-exhausted " + missing)
            return 1
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
    fixture = None if case is not None or rerouted else _fixture(argv[0])
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
