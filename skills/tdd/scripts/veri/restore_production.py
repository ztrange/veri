"""restore-production.sh's restore, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import git

USAGE = "usage: restore-production.sh <test-path>..."


def refuse(message):
    print(f"restore-production.sh: {message}", file=sys.stderr)
    return 2


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
    keep_tests = [":(exclude,glob)**/tests/**"]
    for args in (["checkout", "HEAD", "--", ".", *keep], ["clean", "-fq", "--", ".", *keep, *keep_tests]):
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
