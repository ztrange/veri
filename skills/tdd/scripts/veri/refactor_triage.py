"""refactor-triage.sh's reading of a refactor leaf's report, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import functools
import re
import sys

import candidates
import entry

ACCEPTED = (*candidates.CLASSES, "in-step", "out-of-bounds")
CLASS_LIST = ", ".join(ACCEPTED[:-1]).encode() + b" or " + ACCEPTED[-1].encode()
NONE = re.compile(rb"^none\s*$")


_refuse = functools.partial(entry.refuse, prefix="refactor-triage: ")


USAGE = "usage: refactor-triage.sh < leaf-report.txt"


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    structural = []
    candidates_seen = False
    for line in sys.stdin.buffer.read().replace(b"\0", b"").split(b"\n"):
        found = candidates.line(line)
        if found is None:
            continue
        candidates_seen = True
        classed = False
        for cls in ACCEPTED:
            transform = candidates.candidate(line, cls)
            if transform is not None:
                if not transform:
                    return _refuse(cls.encode() + b" candidate line names no transform: " + line)
                if cls == "structural":
                    structural.append(transform)
                classed = True
        if not (classed or NONE.match(found)):
            return _refuse(b"candidate line has no class, or one that is not " + CLASS_LIST + b": " + line)
    if not candidates_seen:
        return _refuse(b"the report has no " + candidates.KEY.encode() + b" line")
    if not structural:
        return 3
    sys.stdout.buffer.write(b"".join(t + b"\n" for t in structural))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
