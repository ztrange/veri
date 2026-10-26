"""same-reject.sh's comparison, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys


def reason_of(path):
    try:
        with open(path) as handle:
            for line in handle:
                if line.startswith("REASON:"):
                    return " ".join(line.split())
    except OSError as error:
        print(f"same-reject.sh: {path}: {error.strerror}", file=sys.stderr)
        return None
    print(f"same-reject.sh: {path}: no REASON: line", file=sys.stderr)
    return None


def main(argv):
    if len(argv) != 2:
        print("usage: same-reject.sh <previous-reason-file> <current-reason-file>", file=sys.stderr)
        return 2
    found = [reason_of(path) for path in argv]
    if None in found:
        return 2
    return 0 if found[0] == found[1] else 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
