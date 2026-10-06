"""preserve-attempt.sh's computation, run in-process."""
import os
import shutil
import subprocess
import sys
import tempfile

USAGE = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]"


def main(argv):
    if len(argv) < 4 or not all(argv[:4]):
        print(USAGE, file=sys.stderr)
        return 2
    issue, step, phase, attempt = argv[:4]
    coords = f"issue {issue} step {step} {phase} attempt {attempt}"
    os.chdir(git("rev-parse", "--show-toplevel").stdout.rstrip("\n"))
    scratch = tempfile.mkdtemp()
    try:
        index = {**os.environ, "GIT_INDEX_FILE": os.path.join(scratch, "index")}
        git("add", "-A", env=index, capture=False)
        tree = git("write-tree", env=index).stdout.strip()
        result = git("commit-tree", tree, "-p", "HEAD", "-m", f"attempt: {coords}")
        if result.returncode != 0:
            return mapped(result.returncode)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    ref = f"refs/veri/attempts/{issue}/{step}/{phase}-{attempt}"
    if git("update-ref", ref, result.stdout.strip(), capture=False).returncode != 0:
        print(f"preserve-attempt.sh: could not preserve {coords} to {ref}", file=sys.stderr)
        return 1
    return 0


def git(*args, env=None, capture=True):
    return subprocess.run(["git", *args], env=env, text=True,
                          stdout=subprocess.PIPE if capture else None)


def mapped(code):
    return code if 0 <= code <= 3 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
