"""rebase-onto-default.sh's logic, run in-process."""
import re
import subprocess
import sys


def git(*args, **kwargs):
    return subprocess.run(["git", *args], text=True, **kwargs)


def output(*args, **kwargs):
    return git(*args, stdout=subprocess.PIPE, **kwargs).stdout.rstrip("\n")


def default_branch():
    local = git("rev-parse", "-q", "--verify", "--abbrev-ref", "refs/remotes/origin/HEAD",
                stdout=subprocess.PIPE)
    if local.returncode == 0:
        return local.stdout.rstrip("\n").removeprefix("origin/")
    answer = git("ls-remote", "--symref", "origin", "HEAD",
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    return "\n".join(re.findall(r"^ref: refs/heads/(\S*)[^\S\n]*HEAD$", answer, re.MULTILINE))


def main(argv):
    try:
        default = default_branch()
    except FileNotFoundError:
        default = ""
    if not default:
        sys.stderr.write("rebase-onto-default: refs/remotes/origin/HEAD is not set"
                         " — no default branch to rebase onto\n")
        return 2
    if git("fetch", "-q", "origin").returncode != 0:
        return 2
    git("ls-remote", "origin", f"refs/heads/{default}")
    onto = output("rev-parse", f"origin/{default}")
    if git("merge-base", "--is-ancestor", onto, "HEAD").returncode == 0:
        return 3
    pre = output("rev-parse", "HEAD")
    git("rebase", "-q", onto)
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0
