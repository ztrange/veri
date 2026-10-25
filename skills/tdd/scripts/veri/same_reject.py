"""same-reject.sh's comparison, run in-process."""
import sys


def has_reason(path):
    try:
        with open(path) as handle:
            if any(line.startswith("REASON:") for line in handle):
                return True
    except OSError as error:
        print(f"same-reject.sh: {path}: {error.strerror}", file=sys.stderr)
        return False
    print(f"same-reject.sh: {path}: no REASON: line", file=sys.stderr)
    return False


def main(argv):
    if len(argv) != 2:
        print("usage: same-reject.sh <previous-reason-file> <current-reason-file>", file=sys.stderr)
        return 2
    found = [has_reason(path) for path in argv]
    return 0 if all(found) else 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
