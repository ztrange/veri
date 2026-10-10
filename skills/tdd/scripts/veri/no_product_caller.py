"""no-product-caller.sh's caller scan, run in-process."""
import os
import sys

USAGE = "usage: no-product-caller.sh <name>.sh"
PRODUCT_FILES = [
    "skills/tdd/SKILL.md",
    "skills/tdd-fix/SKILL.md",
    "skills/tdd-candidates/SKILL.md",
    "Makefile",
]
PRODUCT_DIRS = ["docs/hooks", "skills/tdd/scripts/veri"]


def product_paths():
    paths = [path for path in PRODUCT_FILES if os.path.isfile(path)]
    for top in PRODUCT_DIRS:
        for root, dirs, files in os.walk(top):
            dirs[:] = sorted(d for d in dirs if d != "tests")
            paths.extend(os.path.join(root, name) for name in sorted(files))
    return paths


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    name = argv[0]
    own = os.path.join("skills/tdd/scripts/veri", name[:-3].replace("-", "_") + ".py")
    callers = []
    for path in product_paths():
        if name.endswith(".sh") and path == own:
            continue
        with open(path, encoding="utf-8", errors="replace") as product:
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
