"""no-product-caller.sh's caller scan, run in-process."""
import sys

USAGE = "usage: no-product-caller.sh <name>.sh"
PRODUCT_FILES = ["skills/tdd/SKILL.md"]


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    name = argv[0]
    callers = []
    for path in PRODUCT_FILES:
        with open(path, encoding="utf-8") as product:
            for number, line in enumerate(product, 1):
                if name in line:
                    callers.append(f"{path}:{number}")
    if not callers:
        return 0
    print("\n".join(callers))
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
