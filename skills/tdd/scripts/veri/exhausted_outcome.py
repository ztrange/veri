"""exhausted-outcome.sh's transform, run in-process."""
import re
import sys

SPLIT_RE = re.compile(r"^SPLIT:\s*(.*)$")
NEEDS_USER_RE = re.compile(r"^NEEDS_USER:\s*(.*)$")


def _print_lines(lines):
    sys.stdout.write("".join(f"{line}\n" for line in lines))


def main(argv):
    lines = sys.stdin.read().replace("\0", "").split("\n")
    if lines[-1] == "":
        lines.pop()
    criteria, uidx = [], None
    for i, line in enumerate(lines):
        split = SPLIT_RE.match(line)
        needs_user = NEEDS_USER_RE.match(line)
        if split:
            criteria.append(split.group(1))
        elif needs_user:
            uidx, utail = i, needs_user.group(1)
    if criteria:
        _print_lines(criteria)
        return 0
    if uidx is not None:
        _print_lines([utail, *lines[uidx + 1:]])
        return 1
    return 3
