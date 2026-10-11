"""replaces-case-survivors.sh's check, run in-process."""
import re
import sys

USAGE = "usage: replaces-case-survivors.sh <step text>"

STEP = re.compile(r"replaces\s+(.+?)\s+in\s+(\S+)")
NAME = re.compile(r"'([^']*)'")


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    names, path = STEP.search(argv[0]).groups()
    with open(path, encoding="utf-8") as f:
        suite = f.read()
    survivors = [n for n in NAME.findall(names) if f'"{n}"' in suite or f"'{n}'" in suite]
    for name in survivors:
        print(f"still present in {path}: {name}")
    return 1 if survivors else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
