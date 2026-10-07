"""cover-outcome.sh's answer, read off a cover leaf's report on stdin."""
import sys


def main(argv):
    fields = {}
    for line in sys.stdin.read().split("\n"):
        for key in ("COVERED", "CAUGHT_BY", "PROOF"):
            if line.startswith(key + ": "):
                fields[key] = line[len(key) + 2:]
                break
    covered = fields.get("COVERED", "")
    if covered == "yes":
        print(fields.get("CAUGHT_BY", ""))
        return 0
    if covered == "no":
        return 1
    if covered in ("unreachable", "type-only"):
        print("%s: %s" % (covered, fields.get("PROOF", "")))
        return 3
    print("cover-outcome: no COVERED: line found", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
