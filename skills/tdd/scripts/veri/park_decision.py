"""park-decision.sh's work, run in-process: the owner's answer to a park, read from the issue's comments."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import github

USAGE = "usage: park-decision.sh <issue-number>\n"


def main(argv):
    number = argv[0]
    comments = [c for c in github.issue_comments(number) if github.trusted_comment(c)]
    parks = [i for i, c in enumerate(comments) if c["body"].startswith(github.PARKED_HEADING)]
    after = comments[parks[-1] + 1:]
    sys.stdout.write("\n".join(c["body"].rstrip("\n") + "\n" for c in after))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
