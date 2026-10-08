"""run-conductor.sh's launch of one conductor, run in-process."""
import os
import shutil
import subprocess
import sys
import tempfile

import launch_floor
from git import symref_default
from session_env import strip_session_env

USAGE = "usage: run-conductor.sh <issue>"


def main(argv):
    if launch_floor.bash_refusal("run-conductor") or launch_floor.python_refusal("run-conductor"):
        return 2
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.dirname(here)
    head_rev = "HEAD"
    if git(base, "remote", "get-url", "origin",
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        fetches = 0
        while True:
            fetch = git(base, "fetch", "-q", "origin",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            fetches += 1
            if fetch.returncode == 0:
                break
            sys.stderr.write(fetch.stderr.rstrip("\n") + "\n")
            if "cannot lock ref" in fetch.stderr and fetches < 60:
                if subprocess.run(["sleep", os.environ.get("VERI_FETCH_RETRY_SLEEP") or "1"]).returncode != 0:
                    return 1
                continue
            sys.stderr.write("run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base)
            return 2
        head_rev = "refs/remotes/origin/HEAD"
        if not verifies(base, head_rev):
            answer = git(base, "ls-remote", "--symref", "origin", "HEAD",
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if answer.returncode != 0:
                return 2
            default = symref_default(answer.stdout)
            if not default:
                return refuse_unpinned(base, "origin names no default branch")
            head_rev = "refs/remotes/origin/" + default
            if not verifies(base, head_rev):
                return refuse_unpinned(base, "origin's default branch '%s' has no %s" % (default, head_rev))
    resolved = git(base, "rev-parse", head_rev,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if resolved.returncode == 0:
        commit = resolved.stdout.strip()
        os.makedirs(".tdd", exist_ok=True)
        if not os.path.exists(".tdd/.gitignore"):
            with open(".tdd/.gitignore", "w") as seed:
                seed.write(".gitignore\nissue-*-skill-commit\n")
        record = ".tdd/issue-%s-skill-commit" % argv[0]
        readable = os.access(record, os.R_OK)
        if readable and os.environ.get("VERI_NEW_SKILL") != "1":
            try:
                with open(record) as recorded_file:
                    recorded = recorded_file.read().rstrip("\n")
            except OSError:
                recorded = ""
            if git(base, "cat-file", "-e", recorded + "^{commit}",
                   stderr=subprocess.DEVNULL).returncode != 0:
                sys.stderr.write("run-conductor: recorded skill commit '%s' is not in '%s' — refusing to re-pin; "
                                 "set VERI_NEW_SKILL=1 to take the new skill\n" % (recorded, base))
                return 2
            commit = recorded
        else:
            with open(record, "w") as out:
                out.write(commit + "\n")
            if readable:
                worktree = ".tdd/wt/" + argv[0]
                os.makedirs(worktree, exist_ok=True)
                if subprocess.run([os.path.join(here, "event.sh"), "skill-repin", "commit=" + commit],
                                  cwd=worktree,
                                  env=dict(os.environ, VERI_ISSUE=argv[0])).returncode != 0:
                    return 2
        snapshot = tempfile.mkdtemp()
        try:
            status = extract(base, commit, snapshot)
            if status != 0:
                return status if status <= 3 else 2
            return launch(snapshot, argv[0], commit, VERI_SKILL_COMMIT=commit, VERI_SKILL_CLONE=base, VERI_SKILL_REF=head_rev)
        finally:
            shutil.rmtree(snapshot, ignore_errors=True)
    sys.stderr.write("run-conductor: no skill commit resolvable from '%s' — running unpinned\n" % base)
    return launch(base, argv[0], None, VERI_SKILL_UNPINNED="1")


def prompt(base, issue, commit):
    skill_file = os.path.join(base, "SKILL.md")
    try:
        with open(skill_file, "rb") as skill:
            text = skill.read().rstrip(b"\n")
    except OSError:
        sys.stderr.write("run-conductor: cannot read '%s'\n" % skill_file)
        return None
    text += ("\n\nBase directory for this skill: %s\n" % base).encode()
    if commit is not None:
        text += ("\nPinned skill commit (name it in the plan comment): %s\n" % commit).encode()
    return text + ("\nSolve issue #%s by the procedure above.\n" % issue).encode()


def launch(base, issue, commit, **exports):
    text = prompt(base, issue, commit)
    if text is None:
        return 2
    env = dict(os.environ, **exports)
    strip_session_env(env)
    return subprocess.run([os.environ.get("CLAUDE_BIN") or "claude", "-p", "--output-format", "stream-json",
                           "--verbose", "--permission-mode", "bypassPermissions"],
                          input=text, env=env).returncode


def extract(base, commit, snapshot):
    read_end, write_end = os.pipe()
    try:
        archive = subprocess.Popen(git_argv(base, "archive", commit, "."), stdout=write_end)
        tar = subprocess.Popen(["tar", "-x", "-C", snapshot], stdin=read_end)
    finally:
        os.close(read_end)
        os.close(write_end)
    tar_code, archive_code = tar.wait(), archive.wait()
    return tar_code or archive_code


def verifies(base, ref):
    return git(base, "rev-parse", "-q", "--verify", ref, stdout=subprocess.DEVNULL).returncode == 0


def git(base, *args, **kwargs):
    return subprocess.run(git_argv(base, *args), **kwargs)


def git_argv(base, *args):
    return ["git", "-C", base] + list(args)


def refuse_unpinned(base, why):
    sys.stderr.write("run-conductor: refs/remotes/origin/HEAD is not set in '%s' and %s — refusing to run unpinned\n" % (base, why))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
