"""cover-outcome.sh's answer, read off a cover leaf's report on stdin."""
import sys

from report import report_read


def main(argv):
    fields = report_read(sys.stdin.read(), ("COVERED", "CAUGHT_BY", "PROOF"))
    covered = fields.get("COVERED", "")
    if covered == "yes":
        print(fields.get("CAUGHT_BY", ""))
        return 0
    if covered == "no":
        return 1
    if covered in ("unreachable", "type-only"):
        proof = fields.get("PROOF", "")
        if proof in ("", "NONE"):
            print("cover-outcome: COVERED: %s without a PROOF: line" % covered, file=sys.stderr)
            return 2
        print("%s: %s" % (covered, proof))
        return 3
    print("cover-outcome: no COVERED: line found", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
