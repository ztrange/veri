"""refactor-triage.sh's reading of a refactor leaf's report, run in-process."""
import re
import sys

import candidates


def _encoded(pattern):
    return re.compile(pattern.pattern.encode())


CANDIDATE = _encoded(candidates.LINE)
PATTERNS = tuple((cls.encode(), _encoded(candidates.candidate(cls))) for cls in candidates.CLASSES)
CLASS_LIST = ", ".join(candidates.CLASSES[:-1]).encode() + b" or " + candidates.CLASSES[-1].encode()
NONE = re.compile(rb"^none\s*$")


def _refuse(text):
    sys.stderr.buffer.write(b"refactor-triage: " + text + b"\n")
    sys.stderr.buffer.flush()
    return 2


def main(argv):
    structural = []
    candidates_seen = False
    for line in sys.stdin.buffer.read().replace(b"\0", b"").split(b"\n"):
        found = CANDIDATE.match(line)
        if not found:
            continue
        candidates_seen = True
        classed = False
        for cls, pattern in PATTERNS:
            transform = pattern.match(line)
            if transform:
                if not transform.group(1):
                    return _refuse(cls + b" candidate line names no transform: " + line)
                if cls == b"structural":
                    structural.append(transform.group(1))
                classed = True
        if not (classed or NONE.match(found.group(1))):
            return _refuse(b"candidate line has no class, or one that is not " + CLASS_LIST + b": " + line)
    if not candidates_seen:
        return _refuse(b"the report has no " + candidates.KEY.encode() + b" line")
    if not structural:
        return 3
    sys.stdout.buffer.write(b"".join(t + b"\n" for t in structural))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
