"""pr-ready.sh's logic, run in-process."""
import sys

try:
    from veri import github
except ImportError:
    import github


def main(argv):
    if len(argv) != 2:
        print("usage: pr-ready.sh <pr-number> <sha>", file=sys.stderr)
        return 2
    try:
        github.gh_pr_ready(argv[0], argv[1])
    except github.NoAnswer:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
