"""parse-verdict.sh's transform, run in-process."""
import re
import sys

SPACE = " \t\n\v\f\r"
VERDICT_RE = re.compile(f"^verdict:[{SPACE}]*(.*)$", re.IGNORECASE)


def verdict_word(lines):
    tail = None
    for line in lines:
        match = VERDICT_RE.match(line)
        if match:
            tail = match.group(1)
    return re.split(f"[{SPACE}]", tail, maxsplit=1)[0]


def main(argv):
    word = verdict_word(sys.stdin.read().split("\n"))
    print(f"parse-verdict: unrecognised verdict word '{word}'", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
