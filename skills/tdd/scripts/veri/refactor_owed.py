"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import re
import sys

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")


def candidate(cls):
    return re.compile(rf"^CANDIDATES:[ \t\n\r\f\v]*{cls}[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")


STRUCTURAL = candidate("structural")
TEST_ONLY = candidate("test-only")


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def append(file, step):
    structural, test_only = [], []
    for line in sys.stdin.read().split("\n"):
        match = STRUCTURAL.match(line)
        if match:
            structural.append(match.group(1))
        match = TEST_ONLY.match(line)
        if match:
            test_only.append("test-only | " + match.group(1))
    owed = structural + test_only
    if owed:
        with open(file, "a") as out:
            out.write(f"### {step}\n" + "".join(f"- {t}\n" for t in owed))
    return 0


def main(argv):
    verb, file, step = (list(argv) + ["", "", ""])[:3]
    if not verb or not file:
        return refuse()
    if verb == "append":
        return append(file, step)
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    return refuse()
