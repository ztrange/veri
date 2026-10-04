"""exhausted-outcome.sh's transform, run in-process."""
import re
import sys

SPLIT_RE = re.compile("^SPLIT: (.*)$")
NEEDS_USER_RE = re.compile("^NEEDS_USER: (.*)$")


def main(argv):
    criteria, utail = [], None
    for line in sys.stdin.read().split("\n"):
        split = SPLIT_RE.match(line)
        needs_user = NEEDS_USER_RE.match(line)
        if split:
            criteria.append(split.group(1))
        elif needs_user:
            utail = needs_user.group(1)
    if criteria:
        sys.stdout.write("".join(f"{c}\n" for c in criteria))
        return 0
    if utail is not None:
        sys.stdout.write(f"{utail}\n")
        return 1
    return 3
