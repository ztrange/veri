"""exhausted-outcome.sh's transform, run in-process.

Reads and writes bytes, reproducing the script's C locale behaviour whatever the
caller's locale, not the UTF-8 one: an invalid UTF-8 byte still matches, and only
ASCII whitespace is stripped after the colon, so a no-break space is kept.
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

from entry import no_arguments
from case_reader import file_defines

MARKER_RE = re.compile(rb"^(SPLIT|NEEDS_USER):\s*(.*)$")
STEP_AHEAD_RE = re.compile(rb"^STEP_AHEAD:\s*(.*?)\s*$")
# Every character of a step-ahead id reaches the diff verifier's --step, so the whole id is checked:
# a path, one or more ::-separated identifiers, an optional [param] of word characters, dots and dashes.
STEP_AHEAD_ID_RE = re.compile(rb"([\w./-]+)((?:::[A-Za-z_]\w*)+)(\[[\w.-]*\])?", re.ASCII)


def _read_stdin():
    data = getattr(sys.stdin, "buffer", sys.stdin).read()
    return data if isinstance(data, bytes) else data.encode("utf-8", "surrogateescape")


def _print_lines(lines):
    sys.stdout.flush()
    sys.stdout.buffer.write(b"".join(line + b"\n" for line in lines))
    sys.stdout.buffer.flush()


USAGE = "usage: exhausted-outcome.sh [--step-ahead <red-test-id>] < leaf-output.txt"


def _lines():
    lines = _read_stdin().replace(b"\0", b"").split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def _refuse(why, line):
    sys.stderr.flush()
    sys.stderr.buffer.write(b"exhausted-outcome.sh: " + why.encode() + b": " + line + b"\n")
    sys.stderr.buffer.flush()
    return 2


def _resolved(path, root):
    """path resolved (symlinks included) relative to root, the working tree wrong-test-route.sh walks;
    None when it resolves outside root."""
    rel = os.path.relpath(os.path.realpath(path), root)
    return None if rel == ".." or rel.startswith(".." + os.sep) else rel


def step_ahead(red_test_id):
    root = os.path.realpath(".")
    red_file, sep, red_rest = red_test_id.partition("::")
    red = (_resolved(red_file, root) or red_file) + sep + red_rest if sep else red_test_id
    cases = []
    for line in _lines():
        marker = STEP_AHEAD_RE.match(line)
        if not marker:
            continue
        if b"::" not in marker.group(1):
            if os.fsdecode(marker.group(1)) == red:
                continue
            return _refuse("names no <file>::<case>", line)
        checked = STEP_AHEAD_ID_RE.fullmatch(marker.group(1))
        if not checked:
            return _refuse("is not a <path>::<name>[::<name>...][[param]] id", line)
        file = os.path.normpath(os.fsdecode(checked.group(1)))
        names = os.fsdecode(checked.group(2)).split("::")[1:]
        param = os.fsdecode(checked.group(3) or b"")
        resolved = _resolved(file, root)
        if red == ("::".join([resolved or file, *names]) + param if sep else names[-1] + param):
            continue
        if os.path.isabs(file) or file == ".." or file.startswith(".." + os.sep) or resolved is None:
            return _refuse("names a path outside the repository", line)
        if not os.path.isfile(file):
            return _refuse("names no existing file", line)
        if not file_defines(file, names[-1], names[:-1]):
            return _refuse("names a case its file does not define", line)
        case = os.fsencode("::".join([file, *names]) + param)
        if case not in cases:
            cases.append(case)
    if not cases:
        return 3
    _print_lines([b" ".join([b"prep", *cases])])
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "--step-ahead" and argv[1]:
        return step_ahead(argv[1])
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    lines = _lines()
    criteria, uidx = [], None
    for i, line in enumerate(lines):
        marker = MARKER_RE.match(line)
        if not marker:
            continue
        if marker.group(1) == b"SPLIT":
            criteria.append(marker.group(2))
        else:
            uidx, utail = i, marker.group(2)
    if criteria:
        _print_lines(criteria)
        return 0
    if uidx is not None:
        _print_lines([utail, *lines[uidx + 1:]])
        return 1
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
