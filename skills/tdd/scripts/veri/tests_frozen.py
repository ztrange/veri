"""tests-frozen.sh's record and check, run in-process."""
import hashlib
import os
import sys

USAGE = "usage: tests-frozen.sh record <record-file> <test-file>... | check <record-file>"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main(argv):
    mode = argv[0] if argv else ""
    record = argv[1] if len(argv) > 1 else ""
    if not record:
        _write(sys.stderr, USAGE)
        return 2
    if mode == "record":
        files = argv[2:]
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
            return 2
        if not entries or any(len(entry) != 2 for entry in entries):
            return 2
        changed = []
        for expected, name in entries:
            try:
                if _digest(name) != expected:
                    changed.append(name)
            except OSError:
                changed.append(name)
        for name in changed:
            _write(sys.stdout, name)
        return 1 if changed else 0
    _write(sys.stderr, USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
