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


class Stop(Exception):
    def __init__(self, step, what, code):
        self.step, self.what, self.code = step, what, code


def checked(step, name, *args, ok=(0,), **kw):
    code, out, _ = call(name, *args, **kw)
    if code not in ok:
        raise Stop(step, label(name, *args), code)
    return out


DETACH = script("detach-command.sh")


def wait_on(name, wt, env):
    return call(DETACH, "wait", name, cwd=wt, env=env)[0]


def detached(name, cmd, wt, env):
    checked(3, DETACH, "start", name, cmd, cwd=wt, env=env)
    return wait_on(name, wt, env)


def issue_body(n, wt):
    body = checked(3, "gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    fd, body_file = tempfile.mkstemp(prefix="veri-preflight-body-")
    with os.fdopen(fd, "w") as f:
        f.write(body)
    return body_file


def pending_in(wt, n):
    return os.path.join(wt, ".tdd", "issue-%s-preflight-wait" % n)


def save_pending(wt, n, *fields):
    with open(pending_in(wt, n), "w") as f:
        f.write("\n".join(fields))


def load_pending(wt, n):
    path = pending_in(wt, n)
    return open(path).read().split("\n") if os.path.exists(path) else None


def stopped(step, what, code):
    sys.stdout.write("stopped at %d %s\n" % (step, what))
    return code


def check_environment():
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
    return None


def start_fast(n, slug, detect, env):
    wt = checked(3, script("issue-worktree.sh"), n, slug).strip()
    checked(3, script("stop-requested.sh"), "--clear", cwd=wt, ok=(0, 3))
    marker = os.path.join(wt, ".tdd", "ci-conflict-rebased")
    if os.path.exists(marker):
        os.remove(marker)
    checked(3, script("unlabel-issue.sh"), n, cwd=wt)
    checked(3, script("worktree-setup.sh"), n, cwd=wt, ok=(0, 3))
    body_file = issue_body(n, wt)
    checked(3, script("requirements-preflight.sh"), body_file, cwd=wt)
    fast = checked(3, detect, "--tier", "fast", "--issue", body_file, wt, cwd=wt).strip()
    fast_began = time.monotonic()
    code = detached("preflight-fast-" + n, fast, wt, env)
    if code == 3:
        save_pending(wt, n, "fast", fast)
    return wt, fast, body_file, fast_began, code


def start_full(n, wt, fast, body_file, fast_began, code, detect, env):
    if code == 3:
        sys.stdout.write("waiting on preflight-fast-%s\n" % n)
        return 3
    if code != 0:
        return stopped(3, "detach-command.sh wait", code)
    baseline = math.ceil(time.monotonic() - fast_began)
    if body_file is None:
        body_file = issue_body(n, wt)
    full = checked(3, detect, "--tier", "all", "--issue", body_file, wt, cwd=wt).strip()
    verdict = checked(3, script("baseline-full-tier.sh"), n, full, cwd=wt)
    alone = checked(3, detect, "--tier", "one test file", "--issue", body_file, wt, cwd=wt).strip()
    began = time.monotonic()
    reused = None
    code = None
    if verdict.split()[:1] == ["reuse"]:
        reused = int(verdict.split()[1])
    else:
        code = detached("preflight-full-" + n, full, wt, env)
    return baseline, full, alone, began, reused, code


def finish(n, wt, baseline, full, fast, alone, began, reused, code):
    if reused is not None:
        full_secs = reused
    elif code == 3:
        save_pending(wt, n, "full", str(baseline), full, fast, alone)
        sys.stdout.write("waiting on preflight-full-%s\n" % n)
        return 3
    elif code != 0:
        return stopped(3, "detach-command.sh wait", code)
    if reused is None:
        checked(3, script("full-tier-time.sh"), "--record", str(int(time.monotonic() - began)), full, cwd=wt)
        full_secs = math.ceil(time.monotonic() - began)
    branch = checked(4, "gh", "api", "repos/{owner}/{repo}", "-q", ".default_branch", cwd=wt)
    for args in (("0",), ("--issue", "0")):
        checked(5, script("refactor-budget.sh"), *args, cwd=wt, ok=(0, 3))
    if "plan" in tunables.read("VERI_SKIP_VERIFY").replace(",", " ").split():
        return stopped(5, "VERI_SKIP_VERIFY", 2)
    if tunables.read("VERI_STEP_GROWTH", "unset") == "":
        return stopped(5, "VERI_STEP_GROWTH", 2)
    if not tunables.read("VERI_MISSING_REROUTE_BUDGET", "0").isdigit():
        return stopped(5, "VERI_MISSING_REROUTE_BUDGET", 2)
    checked(5, script("step-budget.sh"), cwd=wt)
    checked(5, script("adjudicate.sh"), "--check-budget", cwd=wt)
    models = [checked(6, script("leaf-model.sh"), leaf, cwd=wt).strip()
              for leaf in ("develop-red", "revise-green", "verify-green")]
    timeout = checked(7, script("leaf-timeout.sh"), str(baseline), "--full", str(full_secs), cwd=wt)
    lines = ["worktree=" + wt, "fast_cmd=" + fast, "full_cmd=" + full, "alone_cmd=" + alone,
             "baseline=%d" % baseline, "full=%d" % full_secs, "full_tier_mode=" + ("reuse" if reused is not None else "run"),
             "default_branch=" + branch.strip(), "model_develop_red=" + models[0],
             "model_revise_green=" + models[1], "model_verify_green=" + models[2], "timeout=" + timeout.strip()]
    text = "\n".join(lines) + "\n"
    with open(os.path.join(wt, ".tdd", "issue-%s-preflight" % n), "w") as f:
        f.write(text)
    sys.stdout.write(text)
    return 0


def main(argv):
    try:
        return run(argv)
    except Stop as s:
        return stopped(s.step, s.what, s.code)


def run(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, slug = argv
    if os.path.exists(ledger_path(os.path.join(".tdd", "wt", n), n)):
        sys.stderr.write("issue %s already holds a ledger: resume per RESUME.md\n" % n)
        return 2
    env = tunables.with_values(VERI_ISSUE=n)
    detect = script("detect-test-command.sh")
    wt = os.path.abspath(os.path.join(".tdd", "wt", n))
    saved = load_pending(wt, n)
    if saved is not None and saved[0] == "full":
        baseline, full, fast, alone = int(saved[1]), saved[2], saved[3], saved[4]
        began = time.monotonic()
        code = wait_on("preflight-full-" + n, wt, env)
        return finish(n, wt, baseline, full, fast, alone, began, None, code)
    if saved is not None:
        fast = saved[1]
        body_file = None
        fast_began = time.monotonic()
        code = wait_on("preflight-fast-" + n, wt, env)
    else:
        stop = check_environment()
        if stop is not None:
            return stop
        wt, fast, body_file, fast_began, code = start_fast(n, slug, detect, env)
    started = start_full(n, wt, fast, body_file, fast_began, code, detect, env)
    if isinstance(started, int):
        return started
    baseline, full, alone, began, reused, code = started
    return finish(n, wt, baseline, full, fast, alone, began, reused, code)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
