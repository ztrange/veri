"""preflight.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: preflight.sh <n> <slug>"


STEPS = [
    (1, "git repo and clean tree"),
    (2, "gh and claude authenticated"),
    (3, "suite green at baseline"),
    (4, "default branch"),
    (5, "tunables parse"),
    (6, "leaf models parse"),
    (7, "size the hard timeout"),
]

SCRIPTS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def run_script(name, *args, cwd=None):
    proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout, proc.stderr


def call(name, *args, cwd=None):
    code, out, err = run_script(name, *args, cwd=cwd)
    sys.stdout.write(" ".join([os.path.basename(name), *args]) + " exit " + str(code) + "\n" + out)
    sys.stderr.write(err)
    return code, out, err


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, slug = argv
    for cmd in (("git", "rev-parse", "--is-inside-work-tree"), ("git", "status", "--porcelain"),
                ("gh", "api", "user"), ("claude", "auth", "status"),
                (os.path.join(SCRIPTS, "leaf-launchable.sh"),)):
        call(*cmd)
    _, out, _ = call(os.path.join(SCRIPTS, "issue-worktree.sh"), n, slug)
    wt = out.strip()
    call(os.path.join(SCRIPTS, "stop-requested.sh"), "--clear", cwd=wt)
    marker = os.path.join(wt, ".tdd", "ci-conflict-rebased")
    if os.path.exists(marker):
        os.remove(marker)
    call(os.path.join(SCRIPTS, "unlabel-issue.sh"), n, cwd=wt)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
