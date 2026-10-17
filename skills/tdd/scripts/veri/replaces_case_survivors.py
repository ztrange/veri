"""replaces-case-survivors.sh's check, run in-process."""
import sys

from replaces_case import is_replaces_case_step, parse, unreadable

USAGE = "usage: replaces-case-survivors.sh <step text>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    if not is_replaces_case_step(argv[0]):
        return 3
    if unreadable(argv[0]):
        print("cannot read the case names of step: " + argv[0].replace("\n", " "), file=sys.stderr)
        return 2
    parsed = parse(argv[0])
    if parsed is None:
        return 3
    names, path = parsed
    try:
        with open(path, encoding="utf-8") as f:
            suite = "".join(
                line for line in f if not line.lstrip().startswith("#")
            )
    except FileNotFoundError:
        return 0
    survivors = [n for n in names if f'"{n}"' in suite or f"'{n}'" in suite]
    for name in survivors:
        print(f"still present in {path}: {name}")
    return 1 if survivors else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
