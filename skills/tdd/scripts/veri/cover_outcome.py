"""cover-outcome.sh's answer, read off a cover leaf's report on stdin."""
import sys

from report import report_read


def write(stream, text):
    stream.buffer.write((text + "\n").encode("utf-8", "surrogateescape"))


def main(argv):
    report = sys.stdin.buffer.read().decode("utf-8", "surrogateescape")
    fields = report_read(report, ("COVERED", "CAUGHT_BY", "PROOF"))
    covered = fields.get("COVERED", "")
    if covered == "yes":
        write(sys.stdout, fields.get("CAUGHT_BY", ""))
        return 0
    if covered == "no":
        return 1
    if covered in ("unreachable", "type-only"):
        proof = fields.get("PROOF", "")
        if proof in ("", "NONE"):
            write(sys.stderr, "cover-outcome: COVERED: %s without a PROOF: line" % covered)
            return 2
        write(sys.stdout, "%s: %s" % (covered, proof))
        return 3
    write(sys.stderr, "cover-outcome: no COVERED: line found")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
