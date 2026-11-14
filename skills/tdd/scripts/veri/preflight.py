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


def label(name, *args):
    return " ".join([os.path.basename(name), *args])


def call(name, *args, cwd=None):
    code, out, err = run_script(name, *args, cwd=cwd)
    sys.stdout.write(label(name, *args) + " exit " + str(code) + "\n" + out)
    sys.stderr.write(err)
    return code, out, err


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, slug = argv
    for step, *cmd in ((1, "git", "rev-parse", "--is-inside-work-tree"), (1, "git", "status", "--porcelain"),
                       (2, "gh", "api", "user"), (2, "claude", "auth", "status"),
                       (2, os.path.join(SCRIPTS, "leaf-launchable.sh"))):
        code, out, _ = call(*cmd)
        if cmd[1:] == ["status", "--porcelain"] and code == 0 and out.strip():
            code = 1
        if code != 0:
            sys.stdout.write("stopped at %d %s\n" % (step, label(*cmd)))
            return code
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
