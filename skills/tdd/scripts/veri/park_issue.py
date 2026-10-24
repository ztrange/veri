"""park-issue.sh's work, run in-process."""
import sys

import github


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: park-issue.sh <issue-number> <cause> <unblock> [<pr>]\n")
        return 2
    number, cause, unblock = argv
    github.gh_issue_add_label(number, "parked")
    github.gh_issue_comment(number, "### ⏸ Parked\nCause: %s\nUnblock: %s\n" % (cause, unblock))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
