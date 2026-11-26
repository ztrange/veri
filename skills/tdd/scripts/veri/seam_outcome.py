"""seam-outcome.sh's answer, read off a develop-seam leaf's report on stdin."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from entry import no_arguments, write
from report import report_read

USAGE = "usage: seam-outcome.sh (the develop-seam leaf's report on stdin)"


def main(argv):
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    report = sys.stdin.buffer.read().decode("utf-8", "surrogateescape")
    fields = report_read(report, ("SEAM", "REACHES", "PROOF"))
    reaches = fields.get("REACHES", "")
    if reaches == "yes":
        seam = fields.get("SEAM", "")
        if seam in ("", "NONE"):
            write(sys.stderr, "seam-outcome: REACHES: yes without a SEAM: line", before=False, after=False)
            return 2
        write(sys.stdout, seam, before=False, after=False)
        return 0
    if reaches == "no":
        write(sys.stdout, fields.get("PROOF", ""), before=False, after=False)
        return 1
    write(sys.stderr, "seam-outcome: no REACHES: yes|no line found", before=False, after=False)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
