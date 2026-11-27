"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import tempfile

import event
import issue_body
import ledger
import tunables
from github import NoAnswer, gh_issue_edit, gh_issue_view

USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"


def _tick_wrapped(text, matcher):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        match = ledger.STEP_RE.fullmatch(line)
        if not match or match.group(2) != " ":
            continue
        j = i + 1
        while j < len(lines) and not ledger.STEP_RE.fullmatch(lines[j]):
            j += 1
        if any(matcher in held for held in lines[i:j]):
            lines[i] = f"{match.group(1)}[x]{match.group(3) or ''}"
            return True, "\n".join(lines)
    return False, text


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    return tick(argv[0], argv[1] if len(argv) > 1 else "")


def tick(n, matcher):
    """Tick the first unchecked criterion of issue <n> holding <matcher>: 0 ticked, 3 none matched, 2 no answer."""
    try:
        body = gh_issue_view(n, "body").rstrip("\n")
    except NoAnswer:
        return 2
    text = body.replace("\0", "")
    lines = text.split("\n")
    found = issue_body.spans(text, issue_body.CRITERIA)
    start, end = found[-1] if found else (0, len(lines))
    ticked, section = _tick_wrapped("\n".join(lines[start:end]), matcher) if found else (False, "")
    if not ticked:
        print("tick-issue-criterion: no unchecked criterion matched '%s' on #%s" % (matcher, n),
              file=sys.stderr)
        event.mark(os.getcwd(), {**event.context(tunables.environment()), "issue": n}, "criterion-unticked",
                   ["matcher=" + matcher])
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
