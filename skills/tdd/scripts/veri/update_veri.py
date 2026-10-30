"""update-veri.sh's self-update, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: update-veri.sh [--consent yes|no]"


def git(*args):
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def refuse(reason):
    print(f"update-veri.sh: {reason}", file=sys.stderr)
    return 1


def main(argv):
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    if os.environ.get("VERI_SELF_UPDATE") == "0":
        return refuse("update-veri.sh: VERI_SELF_UPDATE=0")
    record = os.environ.get("VERI_SELF_UPDATE_FILE") or os.path.expanduser("~/.veri-tools/self-update")
    if os.path.exists(record) and open(record).read().strip() == "no":
        return refuse("update-veri.sh: self-update record says no")
    branch = git("symbolic-ref", "HEAD").stdout.strip().removeprefix("refs/heads/")
    default = git("symbolic-ref", "refs/remotes/origin/HEAD").stdout.strip().removeprefix("refs/remotes/origin/")
    if branch != default:
        return refuse(f"update-veri.sh: clone is on {branch}, not its upstream default branch {default}")
    if git("status", "--porcelain").stdout.strip():
        return refuse("update-veri.sh: working tree is dirty")
    upstream = git("rev-parse", "--abbrev-ref", "origin/HEAD").stdout.strip()
    old = git("rev-parse", "HEAD").stdout.strip()
    new = git("rev-parse", upstream).stdout.strip()
    git("merge", "--ff-only", upstream)
    print(f"{old} -> {new}")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
