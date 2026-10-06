"""preserve-attempt.sh's computation, run in-process."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

from ledger import CRITERION_RE, ledger_steps

USAGE = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]"


def main(argv):
    if len(argv) < 4 or not all(argv[:4]):
        print(USAGE, file=sys.stderr)
        return 2
    issue, step, phase, attempt = argv[:4]
    coords = f"issue {issue} step {step} {phase} attempt {attempt}"
    top = git("rev-parse", "--show-toplevel", quiet=True)
    if top.returncode != 0:
        print("preserve-attempt.sh: not in a git work tree", file=sys.stderr)
        return 2
    try:
        os.chdir(top.stdout.rstrip("\n"))
    except OSError:
        print("preserve-attempt.sh: cannot enter the repository's top level", file=sys.stderr)
        return 2
    scratch = tempfile.mkdtemp()
    try:
        index = {**os.environ, "GIT_INDEX_FILE": os.path.join(scratch, "index")}
        result = git("read-tree", "HEAD", env=index, capture=False)
        if result.returncode == 0:
            result = git("add", "-A", env=index, capture=False)
        if result.returncode == 0:
            result = git("write-tree", env=index)
        if result.returncode == 0:
            result = git("commit-tree", result.stdout.strip(), "-p", "HEAD", "-m", f"attempt: {coords}")
        if result.returncode != 0:
            return mapped(result.returncode)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    step_ref = sanitised(ledger_step_index(issue, os.fsencode(step).decode("utf-8", "surrogateescape")))
    ref = f"refs/veri/attempts/{issue}/{step_ref}/{phase}-{attempt}"
    if git("update-ref", ref, result.stdout.strip(), capture=False).returncode != 0:
        print(f"preserve-attempt.sh: could not preserve {coords} to {ref}", file=sys.stderr)
        return 1
    mark = argv[4] if len(argv) > 4 else ""
    if mark:
        try:
            copy_leaf_files(step_ref, phase, attempt, mark)
        except OSError as error:
            print(f"preserve-attempt.sh: {error}", file=sys.stderr)
            return 1
    return 0


def copy_leaf_files(step_ref, phase, attempt, mark):
    attempts = os.path.join(".tdd", "attempts")
    os.makedirs(attempts, exist_ok=True)
    for ext in ("log", "out"):
        source = os.path.join(".tdd", f"{phase}.{ext}")
        if os.path.isfile(source):
            shutil.copy(source, os.path.join(attempts, f"{step_ref}-{phase}-{attempt}-{mark}.{ext}"))


def ledger_step_index(issue, step):
    ledger = os.path.join(".tdd", f"issue-{issue}.md")
    if not os.path.isfile(ledger):
        return step
    try:
        with open(ledger, "rb") as f:
            text = f.read().replace(b"\0", b"").decode(errors="surrogateescape")
    except OSError as error:
        print(f"preserve-attempt.sh: {ledger}: {error.strerror}", file=sys.stderr)
        return step
    steps = [(index, step_text) for index, *_, step_text in ledger_steps(text)]
    if any(index == step for index, _ in steps):
        return step
    return next((index for index, step_text in steps if step in (step_text, unmarked(step_text))), step)


def unmarked(text):
    return re.sub(" " + CRITERION_RE + "$", "", text)


def sanitised(step_ref):
    return re.sub(r"[^0-9A-Za-z-]", "-", step_ref)


def git(*args, env=None, capture=True, quiet=False):
    return subprocess.run(["git", *args], env=env, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.DEVNULL if quiet else None)


def mapped(code):
    return code if 0 <= code <= 3 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
