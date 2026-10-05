"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import re
import sys

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")

TEST_ONLY = re.compile(r"^CANDIDATES:[ \t\n\r\f\v]*test-only[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def append(file, step):
    owed = []
    for line in sys.stdin.read().split("\n"):
        match = TEST_ONLY.match(line)
        if match:
            owed.append("test-only | " + match.group(1))
    if owed:
        with open(file, "a") as out:
            out.write(f"### {step}\n" + "".join(f"- {t}\n" for t in owed))
    return 0


def main(argv):
    verb = argv[0] if argv else ""
    file = argv[1] if len(argv) > 1 else ""
    if not verb or not file:
        return refuse()
    if verb == "append":
        return append(file, argv[2])
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    return refuse()
