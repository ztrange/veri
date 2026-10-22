"""resume-clean.sh's computations, run in-process."""
import subprocess
import sys

PATHSPEC = ["--", ".", ":!.tdd"]


def git(*args):
    return subprocess.run(["git", *args], check=True, stdout=subprocess.PIPE, text=True).stdout


def main(argv):
    stray = git("status", "--porcelain", "-uall", *PATHSPEC)
    git("reset", "--hard", "HEAD")
    git("clean", "-fd", "-e", ".tdd")
    sys.stdout.write(stray)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
