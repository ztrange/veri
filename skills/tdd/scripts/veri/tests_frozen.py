"""tests-frozen.sh's record and check, run in-process."""
import ast
import hashlib
import os
import re
import subprocess
import sys
import tempfile

import replaces_case
from entry import write
from ledger import KIND_RE, carries_mark, trailing_markers
from transform_touches_tests import TEST_FILE

USAGE = ("usage: tests-frozen.sh record <record-file>|--step <step-text> <test-file>... | "
         "check <record-file>|--step <step-text> | "
         "check-earlier <ledger> --step <step-text> [--except <case>]... | path <step-text>")
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
        for raw in subprocess.run(command, stdout=subprocess.PIPE).stdout.split(b"\0"):
            if raw and TEST_FILE.search(raw):
                names.append(os.fsdecode(raw))
    return names


_CASE = re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)|^\s*name=\"([^\"]+)\"", re.M)


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


def _old_cut_cases(text):
    found, starts, ends = _spans(text)
    return {m.group(1) or m.group(2): text[start:end].rstrip() for m, start, end in zip(found, starts, ends)}


def _cases(text):
    found, starts, ends = _spans(text)
    lines, def_ends = text.splitlines(keepends=True), _def_ends(text)
    cases = []
    for m, start, end in zip(found, starts, ends):
        body = text[start:end]
        span = def_ends.get(text.count("\n", 0, start) + 1)
        if m.group(1) and span:
            body = "".join(lines[span[0] - 1:span[1]]).rstrip()
        else:
            cut = None if m.group(1) else _module_level_cut(body)
            body = body[:cut.start()] if cut else body
            body = _DECORATORS.sub("", body.rstrip()).rstrip()
        cases.append((m.group(1) or m.group(2), body))
    return cases


def _cases_at(rev, name):
    shown = subprocess.run(["git", "show", "%s:%s" % (rev, name)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return dict(_cases(shown.stdout.decode("utf-8", "replace")))


def _head_and_new_cases(name):
    with open(name, encoding="utf-8", errors="replace") as handle:
        new = handle.read()
    return _cases_at("HEAD", name), _cases(new)


def _added_cases(name):
    before, new = _head_and_new_cases(name)
    return [(case, body) for case, body in new if before.get(case) != body]


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


def _earlier_records(lines, step):
    for line in lines:
        match = re.match(r"\s*- \[.\] (.*)", line)
        if not match or match.group(1) == step:
            continue
        path = _record_path(match.group(1))
        try:
            with open(path, encoding="utf-8") as handle:
                records = handle.read().splitlines()
        except OSError:
            continue
        yield match.group(1), path, records


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
    for owner, _, records in _earlier_records(lines, step):
        bodies = [r for r in map(_body_record, records) if r]
        marked = "format: 2" in records
        for name, case, digest in bodies:
            latest[(name, case)] = (digest, owner, marked)
    changed = []
    for (name, case), (digest, owner, marked) in latest.items():
        try:
            with open(name, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            now = dict(_cases(text)).get(case)
            old = _old_cut_cases(text).get(case)
        except OSError:
            now = old = None
        if case not in exempt and not (fixture and name == fixture.group(1)) and (
                now is None or digest not in ((_body_digest(now),) if marked else (_body_digest(now), _body_digest(old)))):
            changed.append("%s (%s)" % (case, owner))
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
    kind = KIND_RE.search(line)
    return bool(kind) and kind.group(1) == "diff-checked"


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
    os.chdir(root)
    base = subprocess.run(["git", "log", "-1", "--format=%H", "--", os.path.abspath(ledger)],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().strip()
    before, after = {}, {}
    for _, path, records in _earlier_records(lines, step):
        out = []
        for record in records:
            parsed = _body_record(record)
            if parsed:
                name, case, _ = parsed
                if name not in after:
                    before[name], after[name] = _cases_at(base, name), _cases_at("HEAD", name)
                now = after[name].get(case)
                if now is not None and now != before[name].get(case):
                    record = "body: %s\t%s\t%s" % (name, case, _body_digest(now))
            out.append(record + "\n")
        with open(path, "w", encoding="utf-8") as handle:
            handle.writelines(out)
    return 0


def main(argv):
    rest = argv[4:]
    if argv[:1] == ["rerecord-earlier"] and len(argv) == 4 and argv[2] == "--step" and argv[3]:
        return rerecord_earlier(argv[1], argv[3])
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
        if by_step and _refused_outside_repository():
            return 2
        deleted = []
        if by_step:
            record, files = _enter_root(record, files)
            for name in _differing_tests():
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
                    for case, body in added + kept:
                        lines += ["case: %s\n" % case,
                                  "body: %s\t%s\t%s\n" % (name, case, _body_digest(body))]
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
                           if line.strip() and not line.startswith(("case: ", "body: ", "format: "))]
        except OSError:
            write(sys.stderr, "tests-frozen.sh: record %s is missing" % record)
            return 2
        if not entries or any(len(entry) != 2 for entry in entries):
            write(sys.stderr, "tests-frozen.sh: record %s is malformed" % record)
            return 2
        changed = []
        for expected, name in entries:
            if expected == "deleted":
                if os.path.exists(name):
                    changed.append(name)
                continue
            try:
                if _digest(name) != expected:
                    changed.append(name)
            except OSError:
                changed.append(name)
        if by_step:
            recorded = {name for _, name in entries}
            parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
            exempt = {parsed[1]} if parsed else set()
            fixture = _FIXTURE_FILE.search(step) if carries_mark(trailing_markers(step), "fixture-repair") else None
            if fixture:
                exempt.add(fixture.group(1))
            subjects = re.findall(r"⟦guard-subject: ([^⟧]+)⟧", trailing_markers(step))
            exempt.update(subjects)
            changed += [name for name in _differing_tests()
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
