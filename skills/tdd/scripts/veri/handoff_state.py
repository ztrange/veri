"""handoff-state.sh's computation, run in-process."""
import sys

from git import git


def out(*args):
    return git(*args, capture_output=True, text=True).stdout.strip()


def main(argv):
    sha = out("rev-parse", "main")
    tag = out("tag", "--sort=-v:refname").splitlines()[0]
    print("main %s %s" % (sha, tag))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
