"""stack-green.sh's logic, run in-process: the newest commit of the stack branch that ends an issue and that CI passed,
where a slice of the stack may be cut (PRD 034.2b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import entry
import github
import stack_branch

USAGE = "usage: stack-green.sh"
ENDS_READ = 20  # the newest issue ends whose check runs are read, one read each; an older one is never cut at
_TRAILING = re.compile(r"((?:\s*\([^()]*\))+)\s*$")


def named(subject):
    """The issue numbers a commit subject names, as a set: every `#<n>` inside the parenthesised group or groups it
    ends with (`(#1)`, `(#1, #3)`, `(#1) (#2)`, `(#1 and #3)`); a `#<n>` elsewhere in it, or a subject ending in
    anything else (a revert's closing quote), names none."""
    found = _TRAILING.search(subject)
    return set(re.findall(r"#(\d+)", found.group(1))) if found else set()


def issue_ends(subjects):
    """Per subject, oldest first, whether its commit is an issue end: no issue number named at or before it is named
    after it, a subject naming none counting as naming the issues of the nearest earlier subject that names one (none
    when no earlier one does). Linear in the number of subjects."""
    issues, owner = [], set()
    for subject in subjects:
        owner = named(subject) or owner
        issues.append(owner)
    last = {}
    for at, names in enumerate(issues):
        for issue in names:
            last[issue] = at
    ends, reach = [], -1
    for at, names in enumerate(issues):
        reach = max([reach] + [last[issue] for issue in names])
        ends.append(reach <= at)
    return ends


def tested(runs):
    """Whether a commit whose check runs are <runs> [(status, conclusion)] is tested: all completed, each concluding
    success, neutral or skipped, at least one success."""
    return (all(status == "completed" and conclusion in ("success", "neutral", "skipped") for status, conclusion in runs)
            and ("completed", "success") in runs)


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    try:
        span = stack_branch.ahead(".")
    except stack_branch.Refused as refused:
        return entry.refuse(str(refused), prefix="stack-green: ")
    if span is None:
        return entry.refuse("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)",
                            prefix="stack-green: ")
    stack, default, commits = span
    ends = issue_ends([subject for _, subject in commits])
    candidates = [sha for (sha, _), end in reversed(list(zip(commits, ends, strict=True))) if end]
    for sha in candidates[:ENDS_READ]:
        try:
            runs = github.check_runs(sha)
        except (github.NoAnswer, ValueError) as no:
            detail = no.detail or no.answer if isinstance(no, github.NoAnswer) else str(no)
            return entry.refuse(" ".join(str(detail).split()), prefix="stack-green: ")
        if tested(runs):
            sys.stdout.write(sha + "\n")
            return 0
    if len(candidates) > ENDS_READ:
        said = "none of the newest %d of %d issue ends on origin/%s is tested; the %d older ones were not read" % (
            ENDS_READ, len(candidates), stack, len(candidates) - ENDS_READ)
    else:
        said = "no issue end among the %d commits of origin/%s..origin/%s is tested (%d read)" % (
            len(commits), default, stack, len(candidates))
    print("stack-green: " + said, file=sys.stderr)
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
