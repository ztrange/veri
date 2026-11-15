"""preserve-attempt.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import shutil
import subprocess
import sys
import tempfile

import entry
import paths
import run_dir
from git import git
from ledger import CRITERION_RE, decode_ledger, ledger_steps, step_at

USAGE = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]"
IDENTITY = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@localhost",
            "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@localhost"}


def main(argv):
    if len(argv) < 4 or not all(argv[:4]):
        print(USAGE, file=sys.stderr)
        return 2
    if paths.inside_scripts(__file__):
        print("preserve-attempt.sh: type this from the run's worktree,"
              " not from the skill's own scripts directory", file=sys.stderr)
        return 2
    top = run_git("rev-parse", "--show-toplevel", quiet=True)
    if top.returncode != 0:
        print("preserve-attempt.sh: not in a git work tree", file=sys.stderr)
        return 2
    try:
        os.chdir(top.stdout.rstrip("\n"))
    except OSError:
        print("preserve-attempt.sh: cannot enter the repository's top level", file=sys.stderr)
        return 2
    return preserve(".", *argv[:4], argv[4] if len(argv) > 4 else "")


def preserve(repo, issue, step, phase, attempt, mark="", env=None):
    env = dict(os.environ if env is None else env)
    coords = f"issue {issue} step {step} {phase} attempt {attempt}"
    scratch = tempfile.mkdtemp()
    try:
        index = {**env, "GIT_INDEX_FILE": os.path.join(scratch, "index")}
        result = run_git("read-tree", "HEAD", env=index, capture=False, cwd=repo)
        if result.returncode == 0:
            result = run_git("add", "-A", env=index, capture=False, cwd=repo)
        if result.returncode == 0:
            result = run_git("write-tree", env=index, cwd=repo)
        if result.returncode == 0:
            result = run_git("commit-tree", result.stdout.strip(), "-p", "HEAD", "-m", f"attempt: {coords}",
                             env=IDENTITY | env, cwd=repo)
        if result.returncode != 0:
            return entry.to_contract(result.returncode)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    step_ref = sanitised(ledger_step_index(repo, issue, os.fsencode(step).decode("utf-8", "surrogateescape")))
    ref = f"refs/veri/attempts/{issue}/{step_ref}/{phase}-{attempt}"
    if run_git("update-ref", ref, result.stdout.strip(), env=env, capture=False, cwd=repo).returncode != 0:
        print(f"preserve-attempt.sh: could not preserve {coords} to {ref}", file=sys.stderr)
        return 1
    if mark:
        try:
            copy_leaf_files(repo, step_ref, phase, attempt, mark)
        except OSError as error:
            print(f"preserve-attempt.sh: {error}", file=sys.stderr)
            return 1
    return 0


def copy_leaf_files(repo, step_ref, phase, attempt, mark):
    attempts = run_dir.run_file(repo, "attempts")
    os.makedirs(attempts, exist_ok=True)
    for ext in ("log", "out"):
        source = run_dir.run_file(repo, f"{phase}.{ext}")
        if os.path.isfile(source):
            shutil.copy(source, os.path.join(attempts, f"{step_ref}-{phase}-{attempt}-{mark}.{ext}"))


def ledger_step_index(repo, issue, step):
    ledger = os.path.normpath(run_dir.ledger(repo, issue))
    if not os.path.isfile(ledger):
        return step
    try:
        with open(ledger, "rb") as f:
            text = decode_ledger(f.read())
    except OSError as error:
        print(f"preserve-attempt.sh: {ledger}: {error.strerror}", file=sys.stderr)
        return step
    found = step_at(ledger_steps(text), step, by_index=True, text_matches=names_text)
    return step if found is None else found.number


def names_text(reference, text):
    return reference in (text, unmarked(text))


def unmarked(text):
    return re.sub(" " + CRITERION_RE + "$", "", text)


def sanitised(step_ref):
    return re.sub(r"[^0-9A-Za-z-]", "-", step_ref)


def run_git(*args, env=None, capture=True, quiet=False, cwd=None):
    return git(*args, env=env, cwd=cwd, text=True,
               stdout=subprocess.PIPE if capture else None,
               stderr=subprocess.DEVNULL if quiet else None)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
