"""unreplaced-cases.sh's answer: the bash cases a replaces-case step names that have no pytest replacement."""
import re
import sys

USAGE = "usage: unreplaced-cases.sh"


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    step, report = argv
    with open(report, encoding="utf-8") as handle:
        replaced = {m.group(1) for m in re.finditer(r"^REPLACES: (.*?) => ", handle.read(), re.M)}
    missing = [name for name in re.findall(r"'([^']+)'", step) if name not in replaced]
    for name in missing:
        print(name)
    return 1 if missing else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
