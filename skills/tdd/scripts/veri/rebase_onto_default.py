"""rebase-onto-default.sh's logic, run in-process."""
import os
import pathlib
import re
import subprocess
import sys
import time

try:
    from git import git, symref_default
except ImportError:
    from .git import git, symref_default


def output(*args, **kwargs):
    return git(*args, text=True, stdout=subprocess.PIPE, **kwargs).stdout.rstrip("\n")


def git_file(name):
    return pathlib.Path(output("rev-parse", "--git-path", name)).resolve()


def default_branch():
    local = git("rev-parse", "-q", "--verify", "--abbrev-ref", "refs/remotes/origin/HEAD",
                text=True, stdout=subprocess.PIPE)
    if local.returncode == 0:
        return local.stdout.rstrip("\n").removeprefix("origin/")
    answer = git("ls-remote", "--symref", "origin", "HEAD", text=True,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    return symref_default(answer) or ""


def rebase_in_progress():
    return any(git_file(name).is_dir() for name in ("rebase-merge", "rebase-apply"))


def refuse(reason):
    sys.stderr.write(f"rebase-onto-default: {reason}\n")
    return 2


def main(argv):
    try:
        default = default_branch()
    except FileNotFoundError:
        default = ""
    if not default:
        return refuse("refs/remotes/origin/HEAD is not set — no default branch to rebase onto")
    if git("fetch", "-q", "origin", text=True,
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return refuse("git fetch of origin failed")
    remote = git("ls-remote", "origin", f"refs/heads/{default}", text=True,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if remote.returncode != 0:
        return refuse(f"git ls-remote of refs/heads/{default} on origin failed")
    onto = output("rev-parse", f"origin/{default}")
    if onto != re.match(r"\S*", remote.stdout).group():
        return refuse(f"origin/{default} is stale — it is not the sha origin reports")
    saved =git_file("set-aside-tdd-appends.diff")
    if saved.is_file():
        if git("apply", text=True, input=saved.read_text(), stderr=subprocess.DEVNULL).returncode != 0:
            return refuse(f"could not re-apply the set-aside appends; kept at {saved}")
        saved.unlink()
    if git("merge-base", "--is-ancestor", onto, "HEAD", text=True).returncode == 0:
        return 3
    pre = output("rev-parse", "HEAD")
    callers = any(pathlib.Path(path).is_dir() for path in output(
        "rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply").splitlines())
    dirty = output("status", "--porcelain", "--untracked-files=no", "--", ".tdd")
    appends = output("diff", "HEAD", "--", ".tdd") if dirty else ""
    if appends:
        saved.write_text(appends + "\n")
        git("checkout", "HEAD", "--", ".tdd", text=True)
    outcome = 0
    try:
        rebased = git("rebase", "-q", onto, text=True, stdout=subprocess.DEVNULL).returncode == 0
        if not rebased:
            if callers:
                outcome = refuse("a rebase was already in progress; git rebase refused to start")
            elif not rebase_in_progress():
                outcome = 2
            else:
                conflicts = output("diff", "--name-only", "--diff-filter=U")
                git("rebase", "--abort", text=True)
                sys.stdout.write(f"{conflicts}\n")
                outcome = 1
    finally:
        if appends:
            reapplied = git("apply", text=True, input=appends + "\n",
                            stderr=subprocess.DEVNULL).returncode == 0
    if appends and reapplied:
        saved.unlink()
    if appends and not reapplied:
        kept = git_file("kept-tdd-appends.diff")
        earlier = sorted(kept.parent.glob(kept.name + "*"))
        if kept.exists():
            kept = kept.with_name(f"{kept.name}.{int(time.time())}.{os.getpid()}")
        kept.write_text(appends + "\n")
        files = re.findall(r"^\+\+\+ b/(.+)$", appends, re.M)
        return refuse(f"could not re-apply the uncommitted appends to"
                      f" {' '.join(files)}; kept at"
                      f" {' '.join(str(p) for p in [*earlier, kept])}")
    if outcome:
        return outcome
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
