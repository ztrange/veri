"""rebase-onto-default.sh's logic, run in-process."""
import pathlib
import re
import subprocess
import sys

try:
    from git import git, symref_default
except ImportError:
    from .git import git, symref_default


def output(*args, **kwargs):
    return git(*args, text=True, stdout=subprocess.PIPE, **kwargs).stdout.rstrip("\n")


def default_branch():
    local = git("rev-parse", "-q", "--verify", "--abbrev-ref", "refs/remotes/origin/HEAD",
                text=True, stdout=subprocess.PIPE)
    if local.returncode == 0:
        return local.stdout.rstrip("\n").removeprefix("origin/")
    answer = git("ls-remote", "--symref", "origin", "HEAD", text=True,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    return symref_default(answer) or ""


def rebase_in_progress():
    return any(pathlib.Path(output("rev-parse", "--git-path", name)).is_dir()
               for name in ("rebase-merge", "rebase-apply"))


def main(argv):
    try:
        default = default_branch()
    except FileNotFoundError:
        default = ""
    if not default:
        sys.stderr.write("rebase-onto-default: refs/remotes/origin/HEAD is not set"
                         " — no default branch to rebase onto\n")
        return 2
    if git("fetch", "-q", "origin", text=True,
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return 2
    remote = git("ls-remote", "origin", f"refs/heads/{default}", text=True,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if remote.returncode != 0:
        return 2
    onto = output("rev-parse", f"origin/{default}")
    if onto != re.match(r"\S*", remote.stdout).group():
        return 2
    if git("merge-base", "--is-ancestor", onto, "HEAD", text=True).returncode == 0:
        return 3
    pre = output("rev-parse", "HEAD")
    callers = any(pathlib.Path(path).is_dir() for path in output(
        "rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply").splitlines())
    if git("rebase", "-q", onto, text=True, stdout=subprocess.DEVNULL).returncode != 0:
        if callers or not rebase_in_progress():
            return 2
        conflicts = output("diff", "--name-only", "--diff-filter=U")
        git("rebase", "--abort", text=True)
        sys.stdout.write(f"{conflicts}\n")
        return 1
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
