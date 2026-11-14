"""preflight.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import math
import os
import subprocess
import sys
import tempfile
import time

import tunables
from ledger import ledger_path

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

SCRIPTS = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def script(name):
    return os.path.join(SCRIPTS, name)


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


DETACH = script("detach-command.sh")


def wait_on(name, wt, env):
    return call(DETACH, "wait", name, cwd=wt, env=env)[0]


def detached(name, cmd, wt, env):
    call(DETACH, "start", name, cmd, cwd=wt, env=env)
    return wait_on(name, wt, env)


def issue_body(n, wt):
    _, body, _ = call("gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    fd, body_file = tempfile.mkstemp(prefix="veri-preflight-body-")
    with os.fdopen(fd, "w") as f:
        f.write(body)
    return body_file


def pending_in(wt, n):
    return os.path.join(wt, ".tdd", "issue-%s-preflight-wait" % n)


def save_pending(wt, n, text):
    with open(pending_in(wt, n), "w") as f:
        f.write(text)


def stopped(step, what, code):
    sys.stdout.write("stopped at %d %s\n" % (step, what))
    return code


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, slug = argv
    if os.path.exists(ledger_path(os.path.join(".tdd", "wt", n), n)):
        sys.stderr.write("issue %s already holds a ledger: resume per RESUME.md\n" % n)
        return 2
    env = tunables.with_values(VERI_ISSUE=n)
    detect = script("detect-test-command.sh")
    resumed_wt = os.path.abspath(os.path.join(".tdd", "wt", n))
    pending = pending_in(resumed_wt, n)
    reused = None
    body_file = None
    saved = open(pending).read().split("\n") if os.path.exists(pending) else [""]
    if saved[0] == "full":
        wt = resumed_wt
        baseline, full, fast, alone = int(saved[1]), saved[2], saved[3], saved[4]
        began = time.monotonic()
        code = wait_on("preflight-full-" + n, wt, env)
    elif os.path.exists(pending):
        wt = resumed_wt
        fast = saved[1]
        fast_began = time.monotonic()
        code = wait_on("preflight-fast-" + n, wt, env)
    else:
        for step, *cmd in ((1, "git", "rev-parse", "--is-inside-work-tree"), (1, "git", "status", "--porcelain"),
                           (2, "gh", "api", "user"), (2, "claude", "auth", "status"),
                           (2, script("leaf-launchable.sh"))):
            code, out, _ = call(*cmd)
            if cmd[1:] == ["status", "--porcelain"] and code == 0 and out.strip():
                code = 1
            if cmd[1:] == ["auth", "status"] and '"loggedIn": false' in out:
                code = 1
            if code != 0:
                return stopped(step, label(*cmd), code)
        _, out, _ = call(script("issue-worktree.sh"), n, slug)
        wt = out.strip()
        call(script("stop-requested.sh"), "--clear", cwd=wt)
        marker = os.path.join(wt, ".tdd", "ci-conflict-rebased")
        if os.path.exists(marker):
            os.remove(marker)
        call(script("unlabel-issue.sh"), n, cwd=wt)
        call(script("worktree-setup.sh"), n, cwd=wt)
        body_file = issue_body(n, wt)
        call(script("requirements-preflight.sh"), body_file, cwd=wt)
        _, fast, _ = call(detect, "--tier", "fast", "--issue", body_file, wt, cwd=wt)
        fast = fast.strip()
        fast_began = time.monotonic()
        code = detached("preflight-fast-" + n, fast, wt, env)
        if code == 3:
            save_pending(wt, n, "fast\n" + fast)
    if saved[0] != "full":
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
        _, verdict, _ = call(script("baseline-full-tier.sh"), n, full, cwd=wt)
        alone = call(detect, "--tier", "one test file", "--issue", body_file, wt, cwd=wt)[1].strip()
        began = time.monotonic()
        if verdict.split()[:1] == ["reuse"]:
            reused = int(verdict.split()[1])
        else:
            code = detached("preflight-full-" + n, full, wt, env)
    if reused is not None:
        full_secs = reused
    elif code == 3:
        save_pending(wt, n, "full\n%d\n%s\n%s\n%s" % (baseline, full, fast, alone))
        sys.stdout.write("waiting on preflight-full-%s\n" % n)
        return 3
    if reused is None:
        call(script("full-tier-time.sh"), "--record", str(int(time.monotonic() - began)), full, cwd=wt)
        full_secs = math.ceil(time.monotonic() - began)
    _, branch, _ = call("gh", "api", "repos/{owner}/{repo}", "-q", ".default_branch", cwd=wt)
    for args in (("0",), ("--issue", "0")):
        call(script("refactor-budget.sh"), *args, cwd=wt)
    if "plan" in tunables.read("VERI_SKIP_VERIFY").replace(",", " ").split():
        return stopped(5, "VERI_SKIP_VERIFY", 2)
    if tunables.read("VERI_STEP_GROWTH", "unset") == "":
        return stopped(5, "VERI_STEP_GROWTH", 2)
    if not tunables.read("VERI_MISSING_REROUTE_BUDGET", "0").isdigit():
        return stopped(5, "VERI_MISSING_REROUTE_BUDGET", 2)
    call(script("step-budget.sh"), cwd=wt)
    call(script("adjudicate.sh"), "--check-budget", cwd=wt)
    models = [call(script("leaf-model.sh"), leaf, cwd=wt)[1].strip()
              for leaf in ("develop-red", "revise-green", "verify-green")]
    _, timeout, _ = call(script("leaf-timeout.sh"), str(baseline), "--full", str(full_secs), cwd=wt)
    lines = ["worktree=" + wt, "fast_cmd=" + fast, "full_cmd=" + full, "alone_cmd=" + alone,
             "baseline=%d" % baseline, "full=%d" % full_secs, "full_tier_mode=" + ("reuse" if reused is not None else "run"),
             "default_branch=" + branch.strip(), "model_develop_red=" + models[0],
             "model_revise_green=" + models[1], "model_verify_green=" + models[2], "timeout=" + timeout.strip()]
    text = "\n".join(lines) + "\n"
    with open(os.path.join(wt, ".tdd", "issue-%s-preflight" % n), "w") as f:
        f.write(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
