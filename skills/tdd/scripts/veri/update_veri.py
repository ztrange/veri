"""update-veri.sh's self-update, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

try:
    import tunables
except ImportError:
    from . import tunables

USAGE = "usage: update-veri.sh [--consent yes|no]"


def git(*args):
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def refuse(reason, code=1):
    print(f"update-veri.sh: {reason}", file=sys.stderr)
    return code


def main(argv):
    record = tunables.read("VERI_SELF_UPDATE_FILE") or os.path.expanduser("~/.veri-tools/self-update")
    if len(argv) == 2 and argv[0] == "--consent" and argv[1] in ("yes", "no"):
        os.makedirs(os.path.dirname(record), exist_ok=True)
        with open(record, "w") as f:
            f.write(argv[1] + "\n")
        return 0
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    if tunables.read("VERI_SELF_UPDATE") == "0":
        return refuse("VERI_SELF_UPDATE=0")
    if os.path.exists(record):
        answer = open(record).read().strip()
        if answer == "no":
            return refuse("self-update record says no")
        if answer != "yes":
            return refuse("self-update record holds neither yes nor no", 2)
    branch = git("symbolic-ref", "HEAD").stdout.strip().removeprefix("refs/heads/")
    default = git("symbolic-ref", "refs/remotes/origin/HEAD").stdout.strip().removeprefix("refs/remotes/origin/")
    if branch != default:
        return refuse(f"clone is on {branch}, not its upstream default branch {default}")
    if git("status", "--porcelain").stdout.strip():
        return refuse("working tree is dirty")
    if git("fetch").returncode != 0:
        return refuse("fetch of the upstream failed", 2)
    upstream = git("rev-parse", "--abbrev-ref", "origin/HEAD").stdout.strip()
    old = git("rev-parse", "HEAD").stdout.strip()
    new = git("rev-parse", upstream).stdout.strip()
    if old == new:
        return refuse("already current", 3)
    if git("merge-base", "--is-ancestor", "HEAD", upstream).returncode != 0:
        return refuse(f"{upstream} is not a fast-forward of HEAD")
    git("merge", "--ff-only", upstream)
    print(f"{old} -> {new}")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
