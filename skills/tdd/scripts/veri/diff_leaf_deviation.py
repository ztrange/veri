"""diff-leaf-deviation.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import event
import git

USAGE = "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>"


def main(argv):
    try:
        return _main(argv)
    except git.GitFailed as failed:
        print("diff-leaf-deviation.sh: git " + " ".join(failed.args_) + " failed: " + failed.stderr.strip(),
              file=sys.stderr)
        return 2


def _main(argv):
    if len(argv) == 3:
        leaf, base, ledger = argv
        count = int(git.out("rev-list", "--count", base + "..HEAD"))
        touched = git.out("diff", "--name-only", base + "..HEAD", "--", ledger)
        if count < 2 and not touched:
            return 3
        head = git.out("rev-parse", "HEAD")
        return event.append(".", {}, "diff-leaf-deviation",
                            ["leaf=" + leaf, "base=" + base, "head=" + head, "commits=" + str(count)])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
