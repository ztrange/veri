"""park-issue.sh's work, run in-process."""
import sys

import github


def main(argv):
    if len(argv) not in (3, 4):
        sys.stderr.write("park-issue.sh: too many arguments\n" if len(argv) > 4 else "")
        sys.stderr.write("usage: park-issue.sh <issue-number> <cause> <unblock> [<pr>]\n")
        return 2
    number, cause, unblock = argv[:3]
    for bad, name in ((not number.isdigit(), "issue number"), (not cause, "cause"), (not unblock, "unblock")):
        if bad:
            sys.stderr.write("park-issue.sh: bad %s\n" % name)
            return 2
    pr = "PR: %s\n" % argv[3] if len(argv) == 4 else ""
    try:
        github.gh_label_ensure("parked")
        github.gh_issue_add_label(number, "parked")
    except github.NoAnswer:
        sys.stderr.write("park-issue.sh: no answer from gh to the label call\n")
        return 2
    try:
        github.gh_issue_comment(number, github.PARKED_HEADING + "\nCause: %s\n%sUnblock: %s\n" % (cause, pr, unblock))
    except github.NoAnswer:
        sys.stderr.write("park-issue.sh: no answer from gh to the comment call\n")
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
