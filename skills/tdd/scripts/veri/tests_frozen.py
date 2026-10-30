"""tests-frozen.sh's record and check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import ast
import hashlib
import os
import re
import subprocess
import sys
import tempfile

import renamed_case
import replaces_case
from entry import write
from js_tests import CALL, is_js_test_file
from ledger import KIND_RE, carries_mark, trailing_markers
from transform_touches_tests import TEST_FILE

USAGE = ("usage: tests-frozen.sh record <record-file>|--step <step-text> <test-file>... | "
         "check <record-file>|--step <step-text> | "
         "check-earlier <ledger> --step <step-text> [--except <case>]... | "
         "rerecord-earlier <ledger> --step <step-text> | "
         "rerecord-rebased <ledger> <pre-rebase-sha> | "
         "rerecord-refactored <ledger> --step <step-text> <base-sha> <verdict-log> | path <step-text>")
REPAIR_MARKS = ("suite-repair", "ci-repair", "fixture-repair")


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _body_digest(body):
    return hashlib.sha256(body.encode()).hexdigest()


def _step_key(step):
    return hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


def _record_path(step):
    return ".tdd/tests-frozen-%s.record" % _step_key(step)


def _pass_marker_path(step):
    return ".tdd/check-earlier-%s.pass" % _step_key(step)


def _work_tree_hash():
    # An ignored .tdd/ is already left out by `add -A`, and naming it in an exclude
    # pathspec makes git refuse ("paths are ignored"), so the exclude is passed only
    # when .tdd is not ignored as a whole (#2230).
    ignored = subprocess.run(["git", "check-ignore", "-q", ".tdd"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL).returncode == 0
    with tempfile.TemporaryDirectory() as scratch:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(scratch, "index"))
        added = subprocess.run(["git", "add", "-A", "--", "."] + ([] if ignored else [":(exclude).tdd"]), env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        done = subprocess.run(["git", "write-tree"], env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL)
    if added.returncode != 0 or done.returncode != 0:
        return ""
    return os.fsdecode(done.stdout).strip()


def _write_pass_marker(step, tree):
    done = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if done.returncode != 0:
        return
    os.makedirs(".tdd", exist_ok=True)
    with open(_pass_marker_path(step), "w", encoding="utf-8") as handle:
        handle.write("step: %s\nhead: %s\ntree: %s\n" % (step, os.fsdecode(done.stdout).strip(), tree))


def _remove_pass_marker(step):
    try:
        os.remove(_pass_marker_path(step))
    except OSError:
        pass


def _toplevel():
    done = subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL)
    return os.fsdecode(done.stdout).rstrip("\n") if done.returncode == 0 else None


def _has_head():
    return subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"],
                          stdout=subprocess.DEVNULL).returncode == 0


def _enter_root(record, files):
    root = _toplevel()
    record = os.path.abspath(record)
    files = [os.path.relpath(os.path.realpath(name), os.path.realpath(root)) for name in files]
    os.chdir(root)
    return record, files


def _refused_outside_repository():
    if _toplevel() is not None:
        return False
    write(sys.stderr, "tests-frozen.sh: not inside a git repository")
    return True


def _differing_tests():
    names = []
    for command in (["git", "diff", "--name-only", "--no-renames", "-z", "HEAD"],
                    ["git", "ls-files", "--others", "--exclude-standard", "--full-name", "-z", ":/"]):
        done = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if done.returncode != 0:
            # A failed listing is no answer: an empty one would read as "no test files".
            raise OSError("git %s failed: %s" % (command[1], " ".join(os.fsdecode(done.stderr).split())))
        for raw in done.stdout.split(b"\0"):
            name = os.fsdecode(raw)
            if raw and (TEST_FILE.search(raw) or is_js_test_file(os.path.basename(name), os.path.dirname(name))):
                names.append(name)
    return names


_CASE = re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)|^\s*name=\"([^\"]+)\"|^\s*" + CALL + r"([\"'])(.+?)\3", re.M)


_FIXTURE_FILE = re.compile(r"repairs the fixture '[^']*' in (\S+?),")


_MODULE_LEVEL = re.compile(r"\n[ \t]*\n(?:[ \t]*\n)*(?:#|\w+[ \t]*\(\))")


_DECORATORS = re.compile(r"(?:\n[ \t]*(?:@[^\n]*)?)+\Z")


def _def_ends(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    return {node.lineno: (min([d.lineno for d in node.decorator_list] + [node.lineno]), node.end_lineno)
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _helpers_only(tail):
    in_function = False
    for line in tail.splitlines():
        if in_function:
            in_function = line.rstrip() != "}"
        elif not line.strip() or line.lstrip().startswith("#"):
            continue
        elif re.match(r"\w+[ \t]*\(\)", line):
            in_function = not line.rstrip().endswith("}")
        else:
            return False
    return True


def _module_level_cut(body):
    for cut in _MODULE_LEVEL.finditer(body):
        if _helpers_only(body[cut.start():]):
            return cut
    return None


def _spans(text):
    found = list(_CASE.finditer(text))
    trailer = re.search(r"^finish\b.*\s*\Z", text, re.M)
    starts = [m.end() - len(m.group().lstrip()) for m in found]
    ends = starts[1:] + [trailer.start() if trailer and found and trailer.start() > found[-1].start() else len(text)]
    return found, starts, ends


def _old_cut_cases_all(text, call_form_only=False):
    found, starts, ends = _spans(text)
    return [(m.group(1) or m.group(2) or m.group(4), text[start:end].rstrip()) for m, start, end in zip(found, starts, ends)
            if m.group(4) or not call_form_only]


def _accepted_per_digest(digests, nows, olds):
    """Each recorded digest's accepted bodies: the n-th digest for a name against that name's n-th case.

    Same-named twins are matched by order, never through a dict, whose last twin would hide the others.
    When the counts differ (a step recorded only the twin it edited), a digest is accepted against any twin."""
    def accepted(*bodies):
        return {_body_digest(body) for body in bodies if body is not None}
    if len(digests) == len(nows):
        return [accepted(now, olds[i] if i < len(olds) else None) for i, now in enumerate(nows)]
    return [accepted(*nows, *olds)] * len(digests)


def _call_end(text, opening):
    depth = 0
    for i in range(opening, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _cases(text):
    found, starts, ends = _spans(text)
    lines, def_ends = text.splitlines(keepends=True), _def_ends(text)
    cases = []
    for m, start, end in zip(found, starts, ends):
        body = text[start:end]
        span = def_ends.get(text.count("\n", 0, start) + 1)
        closed = _call_end(text, text.rfind("(", start, m.start(4))) if m.group(4) else None
        if m.group(1) and span:
            body = "".join(lines[span[0] - 1:span[1]]).rstrip()
        elif closed:
            body = text[start:closed]
        else:
            cut = None if m.group(1) else _module_level_cut(body)
            body = body[:cut.start()] if cut else body
            body = _DECORATORS.sub("", body.rstrip()).rstrip()
        cases.append((m.group(1) or m.group(2) or m.group(4), body))
    return cases


def _cases_at(rev, name):
    shown = subprocess.run(["git", "show", "%s:%s" % (rev, name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if shown.returncode != 0:
        # A file absent from a readable revision has no cases there; any other failure is no answer.
        listed = subprocess.run(["git", "ls-tree", "--name-only", rev, "--", name], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        if listed.returncode == 0 and not listed.stdout.strip():
            return {}
        raise OSError("git show %s:%s failed: %s" % (rev, name, " ".join(os.fsdecode(shown.stderr).split())))
    return dict(_cases(shown.stdout.decode("utf-8", "replace")))


def _head_cases_all(name):
    shown = subprocess.run(["git", "show", "HEAD:%s" % name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return _cases(shown.stdout.decode("utf-8", "replace"))


def _head_and_new_cases(name):
    with open(name, encoding="utf-8", errors="replace") as handle:
        new = handle.read()
    return _cases_at("HEAD", name), _cases(new)


def _added_cases(name):
    before, new = _head_and_new_cases(name)
    names = [case for case, _ in new]
    if len(set(names)) == len(names):
        return [(case, body) for case, body in new if before.get(case) != body]
    held = {}
    for case, body in _head_cases_all(name):
        held.setdefault(case, set()).add(body)
    return [(case, body) for case, body in new if body not in held.get(case, ())]


def _body_line(name, case, body):
    return "body: %s\t%s\t%s" % (name, case, _body_digest(body))


def _body_record(line):
    return line[6:].split("\t") if line.startswith("body: ") else None


def _kept_cases(record, name):
    try:
        with open(record, encoding="utf-8") as handle:
            held = {r[1] for r in map(_body_record, handle.read().splitlines()) if r and r[0] == name}
    except OSError:
        return []
    before, new = _head_and_new_cases(name)
    return [(case, body) for case, body in new if case in held and before.get(case) == body]


def _held_digests(record, name):
    try:
        with open(record, encoding="utf-8") as handle:
            return {r[1]: r[2] for r in map(_body_record, handle.read().splitlines()) if r and r[0] == name}
    except OSError:
        return {}


def _claimed_elsewhere(record, name):
    claimed = set()
    tdd = os.path.dirname(record)
    for entry in os.listdir(tdd):
        path = os.path.join(tdd, entry)
        if entry.startswith("tests-frozen-") and entry.endswith(".record") and path != record:
            claimed |= set(_held_digests(path, name))
    return claimed


def _branch_base():
    done = subprocess.run(["git", "merge-base", "HEAD", "refs/remotes/origin/HEAD"], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL)
    return os.fsdecode(done.stdout).strip() if done.returncode == 0 else None


def _owned_on_head(record, name):
    """A step's cases on an unchanged file: those it held, the successors of those renamed, and the
    cases the branch added that no other step holds, a later pin of this step among them."""
    held = _held_digests(record, name)
    if not held:
        return []
    with open(name, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    now = dict(_cases(text))
    owned = {case for case in held if case in now}
    consumed = set()
    for case, digest in held.items():
        if case not in now:
            successor = _renamed_to(name, case, digest, text, consumed)
            if successor:
                owned.add(successor)
    base = _branch_base()
    if base:
        before = _cases_at(base, name)
        owned |= {case for case in now if case not in before} - _claimed_elsewhere(record, name)
    return [(case, body) for case, body in now.items() if case in owned]


def _recorded_cases_intact(record, name):
    with open(record, encoding="utf-8") as handle:
        held = [r for r in map(_body_record, handle.read().splitlines()) if r and r[0] == name]
    with open(name, encoding="utf-8", errors="replace") as handle:
        now = _cases(handle.read())
    return bool(held) and all(digest in {_body_digest(body) for c, body in now if c == case} for _, case, digest in held)


def _earlier_records(lines, step, strict=False):
    for line in lines:
        match = re.match(r"\s*- \[(.)\] (.*)", line)
        if not match or match.group(1) == " " or match.group(2) == step:
            continue
        path = _record_path(match.group(2))
        try:
            with open(path, encoding="utf-8") as handle:
                records = handle.read().splitlines()
        except FileNotFoundError:
            continue
        except OSError:
            if strict:
                raise
            continue
        yield match.group(2), path, records


def _revisions(name):
    listed = subprocess.run(["git", "log", "--format=%H", "--", name], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    return os.fsdecode(listed.stdout).split()


def _renamed_to(name, case, digest, text, consumed):
    for rev in _revisions(name):
        held = _cases_at(rev, name)
        if case in held and _body_digest(held[case]) == digest:
            shown = subprocess.run(["git", "show", "%s:%s" % (rev, name)], stdout=subprocess.PIPE)
            other = renamed_case.renamed_to(case, shown.stdout.decode("utf-8", "replace"), text, set(held) | consumed)
            if other:
                consumed.add(other)
            return other
    return None


_ASSERTION = re.compile(r"\bassert\w*\b|\bexpect\b|\.should\b|\braises\b")


def _assertion_lines(body):
    return ["".join(line.split()) for line in body.splitlines() if _ASSERTION.search(line)]


def _assertions_digest(body):
    return _body_digest("\n".join(_assertion_lines(body)))


def _recorded_assertions(records):
    return {tuple(line[12:].split("\t")[:2]): line.rsplit("\t", 1)[1] for line in records if line.startswith("assertions: ")}


def _check_earlier(ledger, step, exempt=()):
    root = _toplevel()
    if root is None:
        _remove_pass_marker(step)
        write(sys.stderr, "tests-frozen.sh: not inside a git repository\n%s" % USAGE)
        return 2
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        os.chdir(root)
        _remove_pass_marker(step)
        write(sys.stderr, "tests-frozen.sh: %s\n%s" % (error, USAGE))
        return 2
    os.chdir(root)
    parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
    exempt = list(exempt) + (parsed[0] if parsed else [])
    fixture = _FIXTURE_FILE.search(step) if carries_mark(trailing_markers(step), "fixture-repair") else None
    latest = {}
    assertions = {}
    for owner, _, records in _earlier_records(lines, step):
        assertions.update(_recorded_assertions(records))
        bodies = [r for r in map(_body_record, records) if r]
        marked = "format: 2" in records
        for name, case, digest in bodies:
            held = latest.get((name, case))
            latest[(name, case)] = (held[0] + [digest] if held and held[1] == owner else [digest], owner, marked)
    changed = []
    consumed = set()
    for (name, case), (digests, owner, marked) in latest.items():
        try:
            with open(name, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            nows = [body for c, body in _cases(text) if c == case]
            olds = [body for c, body in _old_cut_cases_all(text, marked) if c == case]
            digest = digests[-1]
            if not nows:
                other = _renamed_to(name, case, digest, text, consumed)
                if other:
                    nows = olds = [dict(_cases(text))[other].replace(other, case, 1)]
                elif not any(case in _cases_at(rev, name) for rev in _revisions(name)):
                    write(sys.stderr, "tests-frozen.sh: %s (%s, %s) is in no revision of this branch: skipped"
                          % (case, owner, _record_path(owner)))
                    continue
        except OSError:
            nows = olds = []
        accepted = _accepted_per_digest(digests, nows, olds) if nows else []
        if case not in exempt and not (fixture and name == fixture.group(1)) and (
                not nows or any(d not in held for d, held in zip(digests, accepted))):
            changed.append("%s (%s)" % (case, owner))
            if nows and assertions.get((name, case)) in {_assertions_digest(now) for now in nows}:
                write(sys.stderr, "tests-frozen.sh: %s (%s): the record is stale, not edited: its title and assertion "
                      "lines match the recorded body, so a refactor moved it; `%s` re-records it after verify-refactor's PASS"
                      % (case, owner, "tests-frozen.sh rerecord-refactored"))
    for entry in changed:
        write(sys.stdout, entry)
    if not changed:
        tree = _work_tree_hash()
        if not tree:
            _remove_pass_marker(step)
            write(sys.stderr, "tests-frozen.sh: the work-tree hash could not be computed: git add -A or git write-tree failed")
            return 2
        _write_pass_marker(step, tree)
    else:
        _remove_pass_marker(step)
    return 1 if changed else 0


def is_diff_checked(line):
    kind = KIND_RE.search(trailing_markers(line))
    return bool(kind) and kind.group(1) == "diff-checked"


def _write_record(path, out):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.writelines(out)
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: the record %s could not be written: %s" % (path, error))
        return False
    return True


def _rewrite_records(earlier, rewrite):
    for owner, path, records in earlier:
        out = []
        for record in records:
            parsed = _body_record(record)
            if parsed:
                record = rewrite(owner, record, *parsed)
            out.append(record + "\n")
        if not _write_record(path, out):
            return False
    return True


def rerecord_earlier(ledger, step):
    if not is_diff_checked(step):
        return 3
    root = _toplevel()
    if root is None:
        write(sys.stderr, "tests-frozen.sh: not inside a git repository\n%s" % USAGE)
        return 2
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s\n%s" % (error, USAGE))
        return 2
    ledger = os.path.abspath(ledger)
    os.chdir(root)
    base = subprocess.run(["git", "log", "-1", "--format=%H", "--", ledger],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().strip()
    if not base:
        write(sys.stderr, "tests-frozen.sh: no commit touches the ledger %s, so the step base is unknown" % ledger)
        return 2
    before, after = {}, {}

    def rewrite(_, record, name, case, __):
        if name not in after:
            before[name], after[name] = _cases_at(base, name), _cases_at("HEAD", name)
        now = after[name].get(case)
        if now is not None and now != before[name].get(case):
            return _body_line(name, case, now)
        return record
    try:
        return 0 if _rewrite_records(_earlier_records(lines, step), rewrite) else 2
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s" % error)
        return 2


def _final_verdict(log):
    with open(log, encoding="utf-8", errors="replace") as handle:
        verdicts = re.findall(r"^VERDICT: (\w+)", handle.read(), re.M)
    return verdicts[-1] if verdicts else None


def rerecord_refactored(ledger, step, base, log):
    try:
        verdict = _final_verdict(log)
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s\n%s" % (error, USAGE))
        return 2
    if verdict != "PASS":
        write(sys.stderr, "tests-frozen.sh: no final verify-refactor PASS in %s: nothing re-recorded" % log)
        return 1
    root = _toplevel()
    if root is None:
        write(sys.stderr, "tests-frozen.sh: not inside a git repository\n%s" % USAGE)
        return 2
    os.chdir(root)
    before, after = {}, {}

    def rewrite(_, record, name, case, digest):
        if name not in after:
            before[name], after[name] = _cases_at(base, name), _cases_at("HEAD", name)
        old, now = before[name].get(case), after[name].get(case)
        if (old is None or now is None or _body_digest(old) != digest
                or _assertion_lines(old) != _assertion_lines(now)):
            return record
        return _body_line(name, case, now)
    own = _record_path(step)
    try:
        earlier = list(_earlier_records(lines, step, strict=True))
        if os.path.exists(own):
            with open(own, encoding="utf-8") as handle:
                earlier.append((step, own, handle.read().splitlines()))
        return 0 if _rewrite_records(earlier, rewrite) else 2
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s" % error)
        return 2


def rerecord_rebased(ledger, pre):
    with open(ledger, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    os.chdir(_toplevel())
    upstream = os.fsdecode(subprocess.run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
                                          stdout=subprocess.PIPE, check=True).stdout).strip()
    refused, stale = [], False
    try:
        earlier = list(_earlier_records(lines, "", strict=True))
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: a record could not be read: %s" % error)
        return 2

    def rewrite(owner, record, name, case, digest):
        nonlocal stale
        head = _cases_at("HEAD", name)[case]
        if _body_digest(head) == digest:
            return record
        if (_body_digest(_cases_at(pre, name).get(case, "")) != digest
                or head != _cases_at(upstream, name).get(case)):
            refused.append("%s (%s)" % (case, owner))
            return record
        stale = True
        return _body_line(name, case, head)
    if not _rewrite_records(earlier, rewrite):
        return 2
    for line in refused:
        write(sys.stdout, line)
    return 1 if refused else 0 if stale else 3


def _take_red_case(files):
    if "--red-case" not in files:
        return None
    at = files.index("--red-case")
    if at + 1 == len(files):
        write(sys.stderr, "tests-frozen.sh: --red-case needs a <red-test-id>\n%s" % USAGE)
        return 2
    value = files[at + 1]
    if not all(value.partition("::")[::2]):
        write(sys.stderr, "tests-frozen.sh: --red-case %s needs a path and a case around '::'" % value)
        return 2
    path, _, case = value.partition("::")
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            present = case in dict(_cases(handle.read()))
    except FileNotFoundError:
        present = False
    if not present:
        write(sys.stdout, "tests-frozen.sh: red case %s::%s no longer exists\n" % (path, case))
        return 1
    del files[at:at + 2]
    return None


def main(argv):
    rest = argv[4:]
    if argv[:1] == ["rerecord-earlier"] and len(argv) == 4 and argv[2] == "--step" and argv[3]:
        return rerecord_earlier(argv[1], argv[3])
    if argv[:1] == ["rerecord-refactored"] and len(argv) == 6 and argv[2] == "--step" and argv[3]:
        return rerecord_refactored(argv[1], argv[3], argv[4], argv[5])
    if argv[:1] == ["rerecord-rebased"] and len(argv) == 3:
        return rerecord_rebased(argv[1], argv[2])
    if (argv[:1] == ["check-earlier"] and len(argv) >= 4 and argv[2] == "--step" and argv[3]
            and len(rest) % 2 == 0 and all(flag == "--except" and name for flag, name in zip(rest[::2], rest[1::2]))):
        return _check_earlier(argv[1], argv[3], rest[1::2])
    mode = argv[0] if argv else ""
    if mode == "check-earlier":
        write(sys.stderr, USAGE)
        return 2
    record = argv[1] if len(argv) > 1 else ""
    if not record:
        write(sys.stderr, USAGE)
        return 2
    if mode == "path":
        write(sys.stdout, _record_path(record))
        return 0
    by_step = record == "--step"
    if by_step:
        step = argv[2] if len(argv) > 2 else ""
        if not step:
            write(sys.stderr, USAGE)
            return 2
        if any(carries_mark(trailing_markers(step), mark) for mark in REPAIR_MARKS if mark != "fixture-repair"):
            return 0
        argv = [mode, _record_path(step)] + argv[3:]
        record = argv[1]
    if mode == "record":
        files = argv[2:]
        refused = _take_red_case(files)
        if refused is not None:
            return refused
        if by_step and _refused_outside_repository():
            return 2
        deleted = []
        if by_step:
            record, files = _enter_root(record, files)
            try:
                differing = _differing_tests()
            except OSError as error:
                write(sys.stderr, "tests-frozen.sh: %s" % error)
                return 2
            for name in differing:
                if name in files or name in deleted:
                    continue
                (files if os.path.exists(name) else deleted).append(name)
        if not files and not deleted:
            write(sys.stderr, "tests-frozen.sh: record needs at least one test file")
            return 2
        try:
            lines = ["%s  %s\n" % (_digest(name), name) for name in files]
            lines += ["deleted  %s\n" % name for name in deleted]
            if by_step:
                if files:
                    lines.append("format: 2\n")
                for name in files:
                    added = _added_cases(name)
                    kept = [c for c in _kept_cases(record, name) if c[0] not in {a[0] for a in added}]
                    if not added:
                        kept = _owned_on_head(record, name)
                    for case, body in added + kept:
                        lines += ["case: %s\n" % case,
                                  "body: %s\t%s\t%s\n" % (name, case, _body_digest(body)),
                                  "assertions: %s\t%s\t%s\n" % (name, case, _assertions_digest(body))]
            with open(record, "w") as handle:
                handle.writelines(lines)
        except OSError as error:
            write(sys.stderr, "tests-frozen.sh: %s" % error)
            return 2
        return 0
    if mode == "check":
        if by_step and _refused_outside_repository():
            return 2
        if by_step and not _has_head():
            write(sys.stderr, "tests-frozen.sh: repository has no HEAD commit")
            return 2
        if by_step:
            record, _ = _enter_root(record, [])
        try:
            with open(record) as handle:
                entries = [line.rstrip("\n").split("  ", 1) for line in handle
                           if line.strip() and not line.startswith(("case: ", "body: ", "assertions: ", "format: "))]
        except OSError:
            write(sys.stderr, "tests-frozen.sh: record %s is missing" % record)
            return 2
        if not entries or any(len(entry) != 2 for entry in entries):
            write(sys.stderr, "tests-frozen.sh: record %s is malformed" % record)
            return 2
        fixture = _FIXTURE_FILE.search(step) if by_step and carries_mark(trailing_markers(step), "fixture-repair") else None
        loose = fixture.group(1) if fixture else None
        subjects = re.findall(r"⟦guard-subject: ([^⟧]+)⟧", trailing_markers(step)) if by_step else []
        changed = []
        for expected, name in entries:
            if expected == "deleted":
                if os.path.exists(name):
                    changed.append(name)
                continue
            try:
                if _digest(name) != expected and not (name == loose and _recorded_cases_intact(record, loose)) and name not in subjects:
                    changed.append(name)
            except OSError:
                changed.append(name)
        if by_step:
            recorded = {name for _, name in entries}
            parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
            exempt = {parsed[1]} if parsed else set()
            if fixture:
                exempt.add(fixture.group(1))
            exempt.update(subjects)
            try:
                differing = _differing_tests()
            except OSError as error:
                write(sys.stderr, "tests-frozen.sh: %s" % error)
                return 2
            changed += [name for name in differing
                        if name not in recorded
                        and (name not in exempt
                             or (name in subjects and not os.path.exists(name)))]
        for name in changed:
            write(sys.stdout, name)
        return 1 if changed else 0
    write(sys.stderr, USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
