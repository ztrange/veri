"""graded-only-conflict.sh's computations, run in-process: does HEAD conflict with the default branch only in GRADED files?"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

try:
    from git import git
except ImportError:
    from .git import git


def is_graded(path):
    return os.path.basename(path) == "GRADED"


def conflicting_paths(onto):
    """The paths a merge of HEAD and onto conflicts in, or None when git gave no answer."""
    merged = git("merge-tree", "--write-tree", "--name-only", "HEAD", onto, text=True, stdout=subprocess.PIPE,
                 stderr=subprocess.DEVNULL)
    if merged.returncode not in (0, 1):
        return None
    if merged.returncode == 0:
        return []
    paths = []
    for line in merged.stdout.split("\n")[1:]:
        if not line:
            break
        paths.append(line)
    return paths


def main(argv):
    if argv:
        sys.stderr.write("usage: graded-only-conflict.sh\n")
        return 2
    upstream = git("rev-parse", "-q", "--verify", "refs/remotes/origin/HEAD", text=True, stdout=subprocess.PIPE)
    paths = conflicting_paths(upstream.stdout.strip() or "HEAD") if upstream.returncode == 0 else None
    if paths is None:
        sys.stderr.write("graded-only-conflict.sh: no answer from git about origin's default branch\n")
        return 2
    return 0 if paths and all(is_graded(path) for path in paths) else 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
