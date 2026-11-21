"""rebase-onto-default.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import functools
import pathlib
import re
import subprocess
import sys

import entry
import event
import run_dir
import run_pins
import stack_branch
from git import git

USAGE = "usage: rebase-onto-default.sh [--graded-only] | --resolved <onto-sha>"
refuse = functools.partial(entry.refuse, prefix="rebase-onto-default: ")


def output(*args, **kwargs):
    return git(*args, text=True, stdout=subprocess.PIPE, **kwargs).stdout.rstrip("\n")


def git_file(name):
    return pathlib.Path(output("rev-parse", "--git-path", name)).resolve()


def kept_files():
    kept = git_file("kept-tdd-appends.diff")
    return sorted(kept.parent.glob(kept.name + "*"))


def saved_files(saved):
    return " ".join(str(p) for p in [saved, *kept_files()])


def rebase_in_progress():
    return any(pathlib.Path(path).is_dir() for path in output(
        "rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply").splitlines())


def unit_lines(text):
    return {line.split()[0]: line for line in text.splitlines()}


def union_graded(path):
    base, onto, branch = (unit_lines(output("show", f":{stage}:{path}")) for stage in (1, 2, 3))
    merged = onto | {unit: row for unit, row in branch.items() if row != base.get(unit)
                          and git("diff", "--quiet", "HEAD", "REBASE_HEAD", "--", unit).returncode != 0}
    pathlib.Path(path).write_text("".join(row + "\n" for row in merged.values()))
    git("add", path, text=True)


def record_branch_base(onto, done):
    """Re-record a run branch's base as <onto>, the record a resume reads its fast command at (#4374).

    Returns `done`, or the refusal when the write fails; a branch that is no run's records nothing."""
    issue = run_dir.branch_issue(output("symbolic-ref", "--quiet", "--short", "HEAD"))
    if issue:
        main = run_dir.main_tree_from_files()
        record = run_dir.issue_file(main, issue, run_pins.BRANCH_BASE)
        try:
            run_pins.write_branch_base(main, issue, onto)
        except OSError as error:
            return refuse(f"{'up to date with' if done == 3 else 'rebased onto'} {onto}, but could not re-record"
                          f" the branch base {record}: {error.strerror}")
    return done


def main(argv):
    if argv[:1] == ["--resolved"]:
        # A conflicted rebase resolved onto <onto-sha> by hand: re-record the base, rebase nothing.
        if len(argv) != 2:
            return refuse("--resolved takes one <onto-sha>", usage=USAGE)
        onto = argv[1]
        if not re.fullmatch(r"[0-9a-f]{7,40}", onto):
            return refuse(f"--resolved {onto} is not a hex commit name")
        if git("merge-base", "--is-ancestor", onto, "HEAD", text=True).returncode != 0:
            return refuse(f"HEAD does not contain {onto}; nothing to re-record")
        return record_branch_base(onto, 0)
    return event.stage("rebase", lambda: rebase(argv))


def rebase(argv):
    graded_only = "--graded-only" in argv
    try:
        default = stack_branch.run_base()[0] or ""
    except stack_branch.Refused as refused:
        return refuse(str(refused))
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
            return refuse(f"could not re-apply the set-aside appends; kept at"
                          f" {saved_files(saved)}")
        saved.unlink()
    if git("merge-base", "--is-ancestor", onto, "HEAD", text=True).returncode == 0:
        # Up to date still re-records: a rebase whose record write failed must not leave the old base behind.
        return record_branch_base(onto, 3)
    pre = output("rev-parse", "HEAD")
    callers = rebase_in_progress()
    changed = [line[3:] for line in output("status", "--porcelain", "--untracked-files=no").splitlines()]
    outside = [path for path in changed if not path.startswith(".tdd/")]
    if outside:
        return refuse("tracked changes outside .tdd would block the rebase: " + " ".join(outside))
    dirty = bool(changed)
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
                outcome = refuse("git rebase was refused without a conflict")
            else:
                while True:
                    conflicts = output("diff", "--name-only", "--diff-filter=U")
                    paths = conflicts.splitlines()
                    if not (graded_only and paths and all(pathlib.PurePath(c).name == "GRADED" for c in paths)):
                        break
                    for c in paths:
                        union_graded(c)
                    git("-c", "core.editor=true", "rebase", "--continue", text=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if rebase_in_progress():
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
        files = re.findall(r"^\+\+\+ b/(.+)$", appends, re.M)
        base = git_file("kept-tdd-appends.diff")
        kept = next(k for k in (base.with_name(f"{base.name}.{n}") for n in range(1, 10**6))
                    if not k.exists())
        saved.rename(kept)
        return refuse(f"could not re-apply the uncommitted appends to"
                      f" {' '.join(files)}; kept at"
                      f" {' '.join(str(p) for p in kept_files())}")
    if outcome:
        return outcome
    # A run's branch now sits on <onto>: re-record its branch base.
    if record_branch_base(onto, 0):
        return 2
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
