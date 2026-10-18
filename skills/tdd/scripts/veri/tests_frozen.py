"""tests-frozen.sh's record and check, run in-process."""
import hashlib
import os
import subprocess
import sys

import replaces_case
from ledger import trailing_markers
from transform_touches_tests import TEST_FILE

USAGE = ("usage: tests-frozen.sh record <record-file>|--step <step-text> <test-file>... | "
         "check <record-file>|--step <step-text> | path <step-text>")
REPAIR_MARKS = ("\u27e6suite-repair\u27e7", "\u27e6ci-repair\u27e7")


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _record_path(step):
    return ".tdd/tests-frozen-%s.record" % hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


def _differing_tests():
    names = []
    for command in (["git", "diff", "--name-only", "-z", "HEAD"],
                    ["git", "ls-files", "--others", "--exclude-standard", "-z"]):
        for raw in subprocess.run(command, stdout=subprocess.PIPE).stdout.split(b"\0"):
            if raw and TEST_FILE.search(raw):
                names.append(os.fsdecode(raw))
    return names


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
        if any(mark in trailing_markers(step) for mark in REPAIR_MARKS):
            return 0
        argv = [mode, _record_path(step)] + argv[3:]
        record = argv[1]
    if mode == "record":
        files = argv[2:]
        if by_step and os.path.exists(".git"):
            files += [name for name in _differing_tests()
                      if name not in files and os.path.exists(name)]
        if not files:
            _write(sys.stderr, "tests-frozen.sh: record needs at least one test file")
            return 2
        try:
            lines = ["%s  %s\n" % (_digest(name), name) for name in files]
            with open(record, "w") as handle:
                handle.writelines(lines)
        except OSError as error:
            _write(sys.stderr, "tests-frozen.sh: %s" % error)
            return 2
        return 0
    if mode == "check":
        try:
            with open(record) as handle:
                entries = [line.rstrip("\n").split("  ", 1) for line in handle if line.strip()]
        except OSError:
            _write(sys.stderr, "tests-frozen.sh: record %s is missing" % record)
            return 2
        if not entries or any(len(entry) != 2 for entry in entries):
            _write(sys.stderr, "tests-frozen.sh: record %s is malformed" % record)
            return 2
        changed = []
        for expected, name in entries:
            try:
                if _digest(name) != expected:
                    changed.append(name)
            except OSError:
                changed.append(name)
        if by_step and os.path.exists(".git"):
            recorded = {name for _, name in entries}
            parsed = replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None
            exempt = {parsed[1]} if parsed else set()
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
