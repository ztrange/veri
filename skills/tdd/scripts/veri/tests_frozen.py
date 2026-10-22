"""tests-frozen.sh's record and check, run in-process."""
import hashlib
import os
import re
import subprocess
import sys

import replaces_case
from entry import write
from ledger import carries_mark, trailing_markers
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


def _record_path(step):
    return ".tdd/tests-frozen-%s.record" % hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


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


def _cases(text):
    found = list(_CASE.finditer(text))
    trailer = re.search(r"^finish\b.*\s*\Z", text, re.M)
    starts = [m.end() - len(m.group().lstrip()) for m in found]
    ends = starts[1:] + [trailer.start() if trailer and found and trailer.start() > found[-1].start() else len(text)]
    return [(m.group(1) or m.group(2), text[start:end].rstrip()) for m, start, end in zip(found, starts, ends)]


def _added_cases(name):
    old = subprocess.run(["git", "show", "HEAD:" + name], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL).stdout.decode("utf-8", "replace")
    with open(name, encoding="utf-8", errors="replace") as handle:
        new = handle.read()
    before = dict(_cases(old))
    return [(case, body) for case, body in _cases(new) if before.get(case) != body]


def _check_earlier(ledger, step, exempt=()):
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
    parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
    exempt = list(exempt) + (parsed[0] if parsed else [])
    fixture = _FIXTURE_FILE.search(step) if carries_mark(trailing_markers(step), "fixture-repair") else None
    latest = {}
    for line in lines:
        match = re.match(r"\s*- \[.\] (.*)", line)
        if not match or match.group(1) == step:
            continue
        try:
            with open(_record_path(match.group(1)), encoding="utf-8") as handle:
                bodies = [l.rstrip("\n")[6:].split("\t") for l in handle if l.startswith("body: ")]
        except OSError:
            continue
        for name, case, digest in bodies:
            latest[(name, case)] = (digest, match.group(1))
    changed = []
    for (name, case), (digest, owner) in latest.items():
        try:
            with open(name, encoding="utf-8", errors="replace") as handle:
                now = dict(_cases(handle.read())).get(case)
        except OSError:
            now = None
        if case not in exempt and not (fixture and name == fixture.group(1)) and (now is None or _body_digest(now) != digest):
            changed.append("%s (%s)" % (case, owner))
    for entry in changed:
        write(sys.stdout, entry)
    return 1 if changed else 0


def main(argv):
    rest = argv[4:]
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
                for name in files:
                    for case, body in _added_cases(name):
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
                           if line.strip() and not line.startswith(("case: ", "body: "))]
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
