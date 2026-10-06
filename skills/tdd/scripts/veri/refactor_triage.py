"""refactor-triage.sh's reading of a refactor leaf's report, run in-process."""
import re
import sys

CANDIDATE = re.compile(rb"^CANDIDATES:\s*(.*)$")


def _candidate(cls):
    return re.compile(rb"^CANDIDATES:\s*" + cls + rb"\s*[|]\s*(.*)$")


STRUCTURAL = _candidate(rb"structural")
TEST_ONLY = _candidate(rb"test-only")
COSMETIC = _candidate(rb"cosmetic")
OUT_OF_SCOPE = _candidate(rb"out-of-scope")
NONE = re.compile(rb"^none\s*$")


def _refuse(text):
    sys.stderr.buffer.write(b"refactor-triage: " + text + b"\n")
    sys.stderr.buffer.flush()
    return 2


def main(argv):
    structural = []
    candidates_seen = False
    for line in sys.stdin.buffer.read().split(b"\n"):
        found = CANDIDATE.match(line)
        if not found:
            continue
        candidates_seen = True
        transform = STRUCTURAL.match(line)
        if transform:
            structural.append(transform.group(1))
        elif not (TEST_ONLY.match(line) or COSMETIC.match(line) or OUT_OF_SCOPE.match(line)
                     or NONE.match(found.group(1))):
            return _refuse(b"candidate line has no class, or one that is neither structural nor cosmetic: " + line)
    if not candidates_seen:
        return _refuse(b"the report has no CANDIDATES: line")
    if not structural:
        return 3
    sys.stdout.buffer.write(b"".join(t + b"\n" for t in structural))
    sys.stdout.buffer.flush()
    return 0
