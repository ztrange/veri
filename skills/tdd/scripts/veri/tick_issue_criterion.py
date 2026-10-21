"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
import os
import sys
import tempfile

import event
import ledger
import tunables
from github import NoAnswer, gh_issue_edit, gh_issue_view

HEADING = "## Acceptance criteria"
USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"


def _unfenced(lines, start=0):
    fence = ""
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if fence:
            if s.startswith(fence) and not s.strip(fence[0]):
                fence = ""
        elif s[:3] in ("```", "~~~"):
            fence = s[0] * (len(s) - len(s.lstrip(s[0])))
        else:
            yield i, lines[i]


def find_section_start(lines):
    for i, line in _unfenced(lines):
        if line.strip() == HEADING:
            return i + 1
    return 0


def find_section_end(lines, start):
    for i, line in _unfenced(lines, start):
        if line.startswith(("# ", "## ")):
            return i
    return len(lines)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    matcher = argv[1] if len(argv) > 1 else ""
    try:
        body = gh_issue_view(n, "body").rstrip("\n")
    except NoAnswer:
        return 2
    lines = body.replace("\0", "").split("\n")
    start = find_section_start(lines)
    end = find_section_end(lines, start) if start else len(lines)
    ticked, section = ledger.ledger_tick("\n".join(lines[start:end]), matcher) if start else (False, "")
    if not ticked:
        print("tick-issue-criterion: no unchecked criterion matched '%s' on #%s" % (matcher, n),
              file=sys.stderr)
        event.mark(os.getcwd(), {**event.context(tunables.environment()), "issue": n}, "criterion-unticked", ["matcher=" + matcher])
        return 3
    text = "\n".join(lines[:start] + section.split("\n") + lines[end:])
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        gh_issue_edit(n, tmp)
    except NoAnswer:
        return 2
    finally:
        os.unlink(tmp)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
