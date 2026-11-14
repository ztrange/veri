"""preflight.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import math
import os
import subprocess
import sys
import tempfile
import time

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


def run_script(name, *args, cwd=None, env=None):
    proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def label(name, *args):
    return " ".join([os.path.basename(name), *args])


def call(name, *args, cwd=None, env=None):
    code, out, err = run_script(name, *args, cwd=cwd, env=env)
    sys.stdout.write(label(name, *args) + " exit " + str(code) + "\n" + out)
    sys.stderr.write(err)
    return code, out, err


def detached(name, cmd, wt, env):
    detach = os.path.join(SCRIPTS, "detach-command.sh")
    call(detach, "start", name, cmd, cwd=wt, env=env)
    return call(detach, "wait", name, cwd=wt, env=env)[0]


def issue_body(n, wt):
    _, body, _ = call("gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    fd, body_file = tempfile.mkstemp(prefix="veri-preflight-body-")
    with os.fdopen(fd, "w") as f:
        f.write(body)
    return body_file


def stopped(step, what, code):
    sys.stdout.write("stopped at %d %s\n" % (step, what))
    return code


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, slug = argv
    if os.path.exists(os.path.join(".tdd", "wt", n, ".tdd", "issue-%s.md" % n)):
        sys.stderr.write("issue %s already holds a ledger: resume per RESUME.md\n" % n)
        return 2
    env = dict(os.environ, VERI_ISSUE=n)
    detect = os.path.join(SCRIPTS, "detect-test-command.sh")
    pending = os.path.join(".tdd", "wt", n, ".tdd", "issue-%s-preflight-wait" % n)
    if os.path.exists(pending):
        wt = os.path.abspath(os.path.join(".tdd", "wt", n))
        body_file = None
        fast_began = time.monotonic()
        code = call(os.path.join(SCRIPTS, "detach-command.sh"), "wait", "preflight-fast-" + n, cwd=wt, env=env)[0]
    else:
        for step, *cmd in ((1, "git", "rev-parse", "--is-inside-work-tree"), (1, "git", "status", "--porcelain"),
                           (2, "gh", "api", "user"), (2, "claude", "auth", "status"),
                           (2, os.path.join(SCRIPTS, "leaf-launchable.sh"))):
            code, out, _ = call(*cmd)
            if cmd[1:] == ["status", "--porcelain"] and code == 0 and out.strip():
                code = 1
            if cmd[1:] == ["auth", "status"] and '"loggedIn": false' in out:
                code = 1
            if code != 0:
                return stopped(step, label(*cmd), code)
        _, out, _ = call(os.path.join(SCRIPTS, "issue-worktree.sh"), n, slug)
        wt = out.strip()
        call(os.path.join(SCRIPTS, "stop-requested.sh"), "--clear", cwd=wt)
        marker = os.path.join(wt, ".tdd", "ci-conflict-rebased")
        if os.path.exists(marker):
            os.remove(marker)
        call(os.path.join(SCRIPTS, "unlabel-issue.sh"), n, cwd=wt)
        call(os.path.join(SCRIPTS, "worktree-setup.sh"), n, cwd=wt)
        body_file = issue_body(n, wt)
        call(os.path.join(SCRIPTS, "requirements-preflight.sh"), body_file, cwd=wt)
        _, fast, _ = call(detect, "--tier", "fast", "--issue", body_file, wt, cwd=wt)
        fast = fast.strip()
        fast_began = time.monotonic()
        code = detached("preflight-fast-" + n, fast, wt, env)
        if code == 3:
            open(os.path.join(wt, ".tdd", "issue-%s-preflight-wait" % n), "w").close()
    if code == 3:
        sys.stdout.write("waiting on preflight-fast-%s\n" % n)
        return 3
    if code != 0:
        return stopped(3, "detach-command.sh wait", code)
    baseline = math.ceil(time.monotonic() - fast_began)
    if body_file is None:
        body_file = issue_body(n, wt)
    _, full, _ = call(detect, "--tier", "all", "--issue", body_file, wt, cwd=wt)
    full = full.strip()
    call(os.path.join(SCRIPTS, "baseline-full-tier.sh"), n, full, cwd=wt)
    began = time.monotonic()
    detached("preflight-full-" + n, full, wt, env)
    call(os.path.join(SCRIPTS, "full-tier-time.sh"), "--record", str(int(time.monotonic() - began)), full, cwd=wt)
    full_secs = math.ceil(time.monotonic() - began)
    call("gh", "api", "repos/{owner}/{repo}", "-q", ".default_branch", cwd=wt)
    for args in (("0",), ("--issue", "0")):
        call(os.path.join(SCRIPTS, "refactor-budget.sh"), *args, cwd=wt)
    call(os.path.join(SCRIPTS, "step-budget.sh"), cwd=wt)
    call(os.path.join(SCRIPTS, "adjudicate.sh"), "--check-budget", cwd=wt)
    for leaf in ("develop-red", "revise-green", "verify-green"):
        call(os.path.join(SCRIPTS, "leaf-model.sh"), leaf, cwd=wt)
    call(os.path.join(SCRIPTS, "leaf-timeout.sh"), str(baseline), "--full", str(full_secs), cwd=wt)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
