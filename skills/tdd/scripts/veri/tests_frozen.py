"""tests-frozen.sh's record and check, run in-process."""
import hashlib
import os
import re
import subprocess
import sys

import replaces_case
from ledger import carries_mark, trailing_markers
from transform_touches_tests import TEST_FILE

USAGE = ("usage: tests-frozen.sh record <record-file>|--step <step-text> <test-file>... | "
         "check <record-file>|--step <step-text> | path <step-text>")
REPAIR_MARKS = ("suite-repair", "ci-repair", "fixture-repair")


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _record_path(step):
    return ".tdd/tests-frozen-%s.record" % hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


def _in_repository():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def _differing_tests():
    names = []
    for command in (["git", "diff", "--name-only", "-z", "HEAD"],
                    ["git", "ls-files", "--others", "--exclude-standard", "-z"]):
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
    return [case for case, body in _cases(new) if before.get(case) != body]


def main(argv):
    mode = argv[0] if argv else ""
    record = argv[1] if len(argv) > 1 else ""
    if not record:
        _write(sys.stderr, USAGE)
        return 2
    if mode == "path":
        _write(sys.stdout, _record_path(record))
        return 0
    by_step = record == "--step"
    if by_step:
        step = argv[2] if len(argv) > 2 else ""
        if not step:
            _write(sys.stderr, USAGE)
            return 2
        if any(carries_mark(trailing_markers(step), mark) for mark in REPAIR_MARKS if mark != "fixture-repair"):
            return 0
        argv = [mode, _record_path(step)] + argv[3:]
        record = argv[1]
    if mode == "record":
        files = argv[2:]
        in_step_repository = by_step and _in_repository()
        deleted = []
        if in_step_repository:
            for name in _differing_tests():
                if name in files or name in deleted:
                    continue
                (files if os.path.exists(name) else deleted).append(name)
        if not files and not deleted:
            _write(sys.stderr, "tests-frozen.sh: record needs at least one test file")
            return 2
        try:
            lines = ["%s  %s\n" % (_digest(name), name) for name in files]
            lines += ["deleted  %s\n" % name for name in deleted]
            if in_step_repository:
                lines += ["case: %s\n" % case for name in files for case in _added_cases(name)]
            with open(record, "w") as handle:
                handle.writelines(lines)
        except OSError as error:
            _write(sys.stderr, "tests-frozen.sh: %s" % error)
            return 2
        return 0
    if mode == "check":
        try:
            with open(record) as handle:
                entries = [line.rstrip("\n").split("  ", 1) for line in handle
                           if line.strip() and not line.startswith("case: ")]
        except OSError:
            _write(sys.stderr, "tests-frozen.sh: record %s is missing" % record)
            return 2
        if not entries or any(len(entry) != 2 for entry in entries):
            _write(sys.stderr, "tests-frozen.sh: record %s is malformed" % record)
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
            if not _in_repository():
                _write(sys.stderr, "tests-frozen.sh: not inside a git repository")
                return 2
            recorded = {name for _, name in entries}
            parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
            exempt = {parsed[1]} if parsed else set()
            fixture = _FIXTURE_FILE.search(step) if carries_mark(trailing_markers(step), "fixture-repair") else None
            if fixture:
                exempt.add(fixture.group(1))
            changed += [name for name in _differing_tests()
                        if name not in recorded and name not in exempt]
        for name in changed:
            _write(sys.stdout, name)
        return 1 if changed else 0
    _write(sys.stderr, USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
