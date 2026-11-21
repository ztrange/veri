"""same-reject.sh's comparison, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from report import report_values


def reason_of(path):
    try:
        with open(path) as handle:
            text = handle.read()
    except OSError as error:
        print(f"same-reject.sh: {path}: {error.strerror}", file=sys.stderr)
        return None
    reason = report_values(text, "REASON", occurrence="first", space="kept")
    if reason is not None:
        return " ".join(("REASON:" + reason).split())
    if text.split():
        return " ".join(text.split())
    print(f"same-reject.sh: {path}: no reason", file=sys.stderr)
    return None


USAGE = "usage: same-reject.sh <previous-reason-file> <current-reason-file>"


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
