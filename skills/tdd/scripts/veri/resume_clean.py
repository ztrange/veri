"""resume-clean.sh's computations, run in-process."""
import subprocess
import sys

PATHSPEC = ["--", ".", ":!.tdd"]


def git(*args):
    return subprocess.run(["git", *args], check=True, stdout=subprocess.PIPE, text=True).stdout


def main(argv):
    appends = subprocess.run(["git", "diff", "--binary", "HEAD", "--", ".tdd"],
                             check=True, stdout=subprocess.PIPE).stdout
    stray = git("status", "--porcelain", "-uall", *PATHSPEC)
    git("reset", "--hard", "HEAD")
    git("clean", "-fd", "-e", ".tdd")
    if appends:
        subprocess.run(["git", "apply", "-"], input=appends, check=True)
    sys.stdout.write(stray)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
