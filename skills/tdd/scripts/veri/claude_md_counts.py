"""claude_md_counts.sh's computation: the lines of a CLAUDE.md that state a count of the tree."""
import re
import sys

_NUMBER = (
    r"(?:\d+|(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen"
    r"|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)(?:-\w+)?)"
)
_COUNT = re.compile(rf"\b{_NUMBER}\s+(?:\S+\s+){{0,2}}(?:files|suites|scripts)\b", re.IGNORECASE)
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def offences(path):
    with open(path) as f:
        return [
            f"{path}:{number}: states a count of the tree: {line.strip()}"
            for number, line in enumerate(f, 1)
            if _COUNT.search(line) and not _DATE.search(line)
        ]


def main(argv):
    found = offences(argv[0])
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
