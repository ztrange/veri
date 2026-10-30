"""rebase-onto-default.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
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


def git_file(name):
    return pathlib.Path(output("rev-parse", "--git-path", name)).resolve()


def kept_files():
    kept = git_file("kept-tdd-appends.diff")
    return sorted(kept.parent.glob(kept.name + "*"))


def saved_files(saved):
    return " ".join(str(p) for p in [saved, *kept_files()])


def default_branch():
    local = git("rev-parse", "-q", "--verify", "--abbrev-ref", "refs/remotes/origin/HEAD",
                text=True, stdout=subprocess.PIPE)
    if local.returncode == 0:
        return local.stdout.rstrip("\n").removeprefix("origin/")
    answer = git("ls-remote", "--symref", "origin", "HEAD", text=True,
                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    return symref_default(answer) or ""


def rebase_in_progress():
    return any(pathlib.Path(path).is_dir() for path in output(
        "rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply").splitlines())


def stage(number, path):
    shown = git("show", f":{number}:{path}", text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return shown.stdout.splitlines() if shown.returncode == 0 else []


def unit_of(line):
    return line.partition(" ")[0]


def union_by_unit(base, ours, theirs):
    """One line per unit: the replayed commit's for each unit it signs, the rebase target's for every other."""
    signed = {unit_of(line): line for line in theirs if line not in base}
    dropped = {unit_of(line) for line in base} - {unit_of(line) for line in theirs}
    kept = [signed.pop(unit_of(line), line) for line in ours if unit_of(line) not in dropped or unit_of(line) in signed]
    return kept + list(signed.values())


def unioned_graded_conflicts():
    """Finish a rebase stopped only on GRADED files; False leaves it stopped on another path."""
    while rebase_in_progress():
        conflicts = output("diff", "--name-only", "--diff-filter=U").splitlines()
        if not conflicts or not all(pathlib.PurePath(path).name == "GRADED" for path in conflicts):
            return False
        top = pathlib.Path(output("rev-parse", "--show-toplevel"))
        for path in conflicts:
            lines = union_by_unit(stage(1, path), stage(2, path), stage(3, path))
            (top / path).write_text("".join(line + "\n" for line in lines))
            git("add", "--", path, text=True)
        git("-c", "core.editor=true", "rebase", "--continue", text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


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
            return refuse(f"could not re-apply the set-aside appends; kept at"
                          f" {saved_files(saved)}")
        saved.unlink()
    if git("merge-base", "--is-ancestor", onto, "HEAD", text=True).returncode == 0:
        return 3
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
            elif not unioned_graded_conflicts():
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
    sys.stdout.write(f"{pre}\n{onto}\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
