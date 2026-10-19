"""stop-reason.sh's report, run in-process."""
import os
import sys


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: stop-reason.sh <issue>\n")
        return 2
    if not os.path.isdir(os.path.join(".tdd", "wt", argv[0])):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
