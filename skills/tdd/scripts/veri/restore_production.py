"""restore-production.sh's restore, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import git
import tests_frozen

USAGE = "usage: restore-production.sh <test-path>..."


def refuse(message):
    print(f"restore-production.sh: {message}", file=sys.stderr)
    return 2


def spared_tests():
    """Every changed or untracked path veri classifies as a test, and the wholly untracked directory holding it.

    git clean removes a wholly untracked directory as one unit, so excluding a file inside it is not enough.
    """
    listed = git.git("ls-files", "-z", capture_output=True, text=True)
    if listed.returncode:
        return []
    names = tests_frozen._differing_tests()
    tracked = listed.stdout.split("\0")
    tracked_dirs = {parent for name in tracked for parent in _parents(name)}
    spared = set(names)
    for name in names:
        fresh = [parent for parent in _parents(name) if parent not in tracked_dirs]
        if fresh:
            spared.add(fresh[-1])
    return sorted(spared)


def _parents(name):
    parents = []
    while os.path.dirname(name):
        name = os.path.dirname(name)
        parents.append(name)
    return parents


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    for path in argv:
        if "::" in path:
            return refuse(f"{path}: a pytest node id, not a path")
        if path.startswith(":"):
            return refuse(f"{path}: a pathspec magic prefix, not a path")
    if git.git("rev-parse", "--show-prefix", capture_output=True, text=True).stdout.strip():
        return refuse("run it from the worktree root")
    keep = [f":(exclude,literal){path}" for path in argv]
    keep += [":(exclude,glob).tdd/issue-*.md", ":(exclude,glob)**/GRADED"]
    keep += [f":(exclude,literal){path}" for path in spared_tests()]
    for args in (["checkout", "HEAD", "--", ".", *keep], ["clean", "-fq", "--", ".", *keep]):
        done = git.git(*args, capture_output=True, text=True)
        if done.returncode:
            message = done.stderr.strip()
            if args[0] == "clean":
                message += "\nrestore-production.sh: partial restore: production reverted, untracked files not removed"
            return refuse(message)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
