"""park-issue.sh's work, run in-process."""
import sys

import github


def main(argv):
    if len(argv) not in (3, 4):
        sys.stderr.write("usage: park-issue.sh <issue-number> <cause> <unblock> [<pr>]\n")
        return 2
    number, cause, unblock = argv[:3]
    pr = "PR: %s\n" % argv[3] if len(argv) == 4 else ""
    github.gh_label_ensure("parked")
    github.gh_issue_add_label(number, "parked")
    github.gh_issue_comment(number, "### ⏸ Parked\nCause: %s\n%sUnblock: %s\n" % (cause, pr, unblock))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
