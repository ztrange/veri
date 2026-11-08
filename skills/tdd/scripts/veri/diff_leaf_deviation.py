"""diff-leaf-deviation.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

import event

USAGE = "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>"


def main(argv):
    if len(argv) == 3:
        leaf, base, ledger = argv
        count = int(subprocess.run(["git", "rev-list", "--count", base + "..HEAD"],
                                   capture_output=True, text=True, check=True).stdout)
        touched = subprocess.run(["git", "diff", "--name-only", base + "..HEAD", "--", ledger],
                                 capture_output=True, text=True, check=True).stdout.strip()
        if count < 2 and not touched:
            return 3
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        return event.append(".", {}, "diff-leaf-deviation",
                            ["leaf=" + leaf, "base=" + base, "head=" + head, "commits=" + str(count)])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
