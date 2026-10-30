"""update-veri.sh's self-update, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: update-veri.sh [--consent yes|no]"


def git(*args):
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def main(argv):
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    record = os.environ.get("VERI_SELF_UPDATE_FILE") or os.path.expanduser("~/.veri-tools/self-update")
    if os.path.exists(record) and open(record).read().strip() == "no":
        print("update-veri.sh: self-update record says no", file=sys.stderr)
        return 1
    upstream = git("rev-parse", "--abbrev-ref", "origin/HEAD").stdout.strip()
    old = git("rev-parse", "HEAD").stdout.strip()
    new = git("rev-parse", upstream).stdout.strip()
    git("merge", "--ff-only", upstream)
    print(f"{old} -> {new}")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
