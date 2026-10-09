"""exhausted-outcome.sh's transform, run in-process.

Reads and writes bytes, reproducing the script's C locale behaviour whatever the
caller's locale, not the UTF-8 one: an invalid UTF-8 byte still matches, and only
ASCII whitespace is stripped after the colon, so a no-break space is kept.
"""
import re
import sys

MARKER_RE = re.compile(rb"^(SPLIT|NEEDS_USER):\s*(.*)$")


def _read_stdin():
    data = getattr(sys.stdin, "buffer", sys.stdin).read()
    return data if isinstance(data, bytes) else data.encode("utf-8", "surrogateescape")


def _print_lines(lines):
    sys.stdout.flush()
    sys.stdout.buffer.write(b"".join(line + b"\n" for line in lines))
    sys.stdout.buffer.flush()


def main(argv):
    lines = _read_stdin().replace(b"\0", b"").split(b"\n")
    if lines[-1] == b"":
        lines.pop()
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
