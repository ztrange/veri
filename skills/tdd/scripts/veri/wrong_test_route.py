"""wrong-test-route.sh's decision, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import event_log
import frozen_record
from case_reader import cut_prefix, defined_name, defines_helper, live_titles, is_go_test_file, is_js_test_file, is_test_file
import ledger as ledger_file
import os
import re
import sys
import tunables
from entry import write

USAGE = "usage: wrong-test-route.sh --spec <spec-file> <green-report> <red-test-id> (prints red <case>, missing <behaviour>, later <step>, repair <case> <superseded>…, supersede <cases> or revise; repair-exhausted <case> on exit 1; a WRONG_TEST naming no case gets one extra repair after the free reroute, then repair-exhausted and exit 1)"


SKIPPED = (".git", ".tdd", ".venv", "node_modules")


def _files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIPPED]
        for name in files:
            yield root, name


def _test_files():
    for root, name in _files():
        py = is_test_file(name)
        go = is_go_test_file(name)
        js = is_js_test_file(name, root)
        if py or go or js or name.endswith(".test.sh"):
            yield root, name, py, go, js


def _defining_files(case):
    found = []
    for root, name, py_file, go_file, _ in _test_files():
        with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
            if defined_name(case, handle.read(), py_file, go_file):
                found.append(os.path.relpath(os.path.join(root, name)))
    return found


def _defining_file(case):
    found = _defining_files(case)
    return found[0] if found else None


def _exists(case):
    cut = cut_prefix(case)
    titles = set()
    for root, name, py_file, go_file, js_file in _test_files():
        with open(os.path.join(root, name), encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        defined = defined_name(case, text, py_file, go_file)
        if defined:
            return defined
        found = live_titles(case, text) if js_file else []
        if found and cut is None:
            return found[0]
        titles.update(found)
        if name.endswith(".test.sh") and ('name="%s"' % case) in text:
            return case
    return titles.pop() if len(titles) == 1 else None


def _fixture(report, own_id):
    own_file = os.path.normpath(own_id.partition("::")[0]) if "::" in own_id else None
    for name in _named_cases(report):
        if name.startswith(("test_", "Test")):
            continue
        for root, file, py_file, go_file, js_file in _test_files():
            if not py_file and not go_file and not js_file:
                continue
            path = os.path.join(root, file)
            if own_file is not None and os.path.normpath(path) != own_file:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                if defines_helper(name, handle.read(), py_file, go_file):
                    return os.path.normpath(path), name
    return None


def _report_lines(report):
    with open(report, encoding="utf-8", errors="replace") as handle:
        return handle.read().splitlines()


def _lines_with(report, prefix):
    return [l for l in _report_lines(report) if l.startswith(prefix)]


def _spellings(line):
    yield from re.findall(r"\btest_\w+", line)
    yield from re.findall(r"\bTest[A-Z]\w*", line)
    yield from re.findall(r"`([^`]+)`", line)
    yield from re.findall(r'"([^"]+)"', line)
    yield from re.findall(r"“([^”]+)”", line)
    yield from re.findall(r"\S\s+›\s+(\S.*?)\s*$", line)


def _contradicted(report):
    for line in _lines_with(report, "CONTRADICTS:"):
        yield from _spellings(line.partition(":")[2])


def _named_cases(report):
    yield from _contradicted(report)
    for line in _lines_with(report, "WRONG_TEST:"):
        yield from _spellings(line)


def _is_none(body):
    return re.match(r"none\b", body, re.IGNORECASE)


def _unparseable_claim(report):
    if any(True for _ in _named_cases(report)):
        return False
    for line in _lines_with(report, "WRONG_TEST:"):
        if not _is_none(line.partition(":")[2].strip()):
            return True
    return any(_prose_claim(l) and not any(True for _ in _spellings(l)) for l in _report_lines(report))


def _prose_claim(line):
    if line.startswith("WRONG_TEST:"):
        return False
    return any(not re.search(r'\bnot\s+(a\s+)?$', line[:m.start()])
               and not re.search(r'[\'"`“‘]$', line[:m.start()])
               for m in re.finditer("WRONG_TEST", line))


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


def _existing_other(cases, own_id):
    for case in cases:
        if not _is_own(case, own_id):
            found = _exists(case)
            if found and not _is_own(found, own_id):
                return found
    return None


def route(report, own_id):
    return _existing_other(_contradicted(report), own_id)


def _recorded_cases(step):
    return frozen_record.recorded_cases(step)


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
        if _is_none(behaviour):
            return None
        if behaviour:
            return behaviour
    if lines:
        write(sys.stderr, "no well-formed MISSING_TEST: line was found")
    return None


def _open_after():
    with open(ledger_file.ledger_path(".", tunables.read("VERI_ISSUE")), encoding="utf-8") as ledger:
        steps = ledger_file.ledger_steps(ledger.read())
    current = tunables.read("VERI_STEP")
    names = [step[6].strip() for step in steps]
    return [step[6].strip() for step in steps[names.index(current) + 1:] if step[1] == "open"] if current in names else []


def _criterion(spec, name):
    marker = re.search(r"⟦criterion (\d+)⟧", name)
    if marker is None:
        return None
    with open(spec, encoding="utf-8") as handle:
        body = handle.read().partition("## Acceptance criteria")[2]
    boxes = [m.group(2) for m in ledger_file.ledger_items(body)]
    index = int(marker.group(1)) - 1
    return boxes[index] if index < len(boxes) else None


def _later(report, behaviour, spec):
    for line in _lines_with(report, "LATER_STEP:"):
        named = line.partition(":")[2].strip()
        return named if named in _open_after() else None
    try:
        after = _open_after()
    except OSError:
        return None
    wanted = behaviour.lower()
    for name in after:
        text = (_criterion(spec, name) or "").lower()
        if text and (text in wanted or wanted in text):
            return name
    return None


def main(argv):
    if len(argv) != 4 or argv[0] != "--spec" or not all(argv[1:]):
        write(sys.stderr, USAGE)
        return 2
    spec, argv = argv[1], argv[2:]
    step = tunables.read("VERI_STEP")
    rerouted = _rerouted(step)
    missing = _missing(argv[0])
    if missing:
        later = _later(argv[0], missing, spec)
        if later:
            write(sys.stdout, "later " + later)
            return 0
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
        own = _case_name(argv[1])
        if own in recorded:
            write(sys.stdout, "supersede-diff " + " ".join(older))
        else:
            write(sys.stdout, "supersede " + " ".join(_defining_file(c) + "::" + c for c in older))
        return 0
    case = None if rerouted else route(argv[0], argv[1])
    where = _defining_file(case) if case is not None and "::" not in case else None
    if where is not None:
        ambiguous = len(_defining_files(case)) > 1
        for line in _lines_with(argv[0], "CONTRADICTS:"):
            given = re.search(r"(\S+)::" + re.escape(case) + r"\s*$", line)
            if given:
                where = given.group(1)
            elif ambiguous:
                return 2
    if case is None and len(older) == 1:
        case = older[0]
    fixture = None if case is not None or rerouted else _fixture(argv[0], argv[1])
    if fixture is not None:
        write(sys.stdout, "fixture %s %s" % fixture)
        return 0
    if _unparseable_claim(argv[0]) and any(e.get("kind") == "repair" for e in _reroutes(step)[1:]):
        write(sys.stdout, "repair-exhausted " + _case_name(argv[1]))
        return 1
    if case is None and not rerouted and any(not _is_own(c, argv[1]) and not _exists(c) for c in _contradicted(argv[0])):
        return 2
    if case is None and (_unparseable_claim(argv[0]) or not rerouted and (_existing_other(_named_cases(argv[0]), argv[1]) or any(_is_own(c, argv[1]) for c in _contradicted(argv[0])))):
        file, sep, _ = argv[1].partition("::")
        write(sys.stdout, "repair " + (file + sep if sep else "") + _case_name(argv[1]))
        return 0
    if case is None:
        write(sys.stdout, "revise")
        return 3
    write(sys.stdout, "red " + (where + "::" + case if where else case))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
