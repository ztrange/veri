"""restore-production.sh's restore, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import git

USAGE = "usage: restore-production.sh <test-path>..."


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    for path in argv:
        if "::" in path:
            print(f"restore-production.sh: {path}: a pytest node id, not a path", file=sys.stderr)
            return 2
    keep = [f":(exclude,literal){path}" for path in argv]
    keep += [":(exclude,glob).tdd/issue-*.md", ":(exclude,glob)**/GRADED"]
    for args in (["checkout", "HEAD", "--", ".", *keep], ["clean", "-fq", "--", ".", *keep]):
        done = git.git(*args, capture_output=True, text=True)
        if done.returncode:
            print(f"restore-production.sh: {done.stderr.strip()}", file=sys.stderr)
            if args[0] == "clean":
                print("restore-production.sh: partial restore: production reverted, untracked files not removed",
                      file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
