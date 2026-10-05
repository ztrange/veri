"""rebase-onto-default.sh's logic, run in-process."""
import subprocess
import sys


def git(*args, **kwargs):
    return subprocess.run(["git", *args], text=True, **kwargs)


def output(*args, **kwargs):
    return git(*args, stdout=subprocess.PIPE, **kwargs).stdout.rstrip("\n")


def main(argv):
    default = output("rev-parse", "-q", "--verify", "--abbrev-ref",
                     "refs/remotes/origin/HEAD").removeprefix("origin/")
    if git("fetch", "-q", "origin").returncode != 0:
        return 2
    onto = output("rev-parse", f"origin/{default}")
    if git("merge-base", "--is-ancestor", onto, "HEAD").returncode == 0:
        return 3
    pre = output("rev-parse", "HEAD")
    git("rebase", "-q", onto)
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0
