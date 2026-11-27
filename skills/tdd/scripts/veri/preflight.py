"""preflight.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import datetime
import hashlib
import json
import math
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

import event
import fused
import ready_check
import run_dir
import run_pins
import run_records
import stack_branch
import tunables

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
    checked(3, DETACH, "start", name, *shlex.split(cmd), cwd=wt, env=env)
    return wait_on(name, wt, env)


def issue_body(n, wt):
    body = checked(3, "gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    fd, body_file = tempfile.mkstemp(prefix="veri-preflight-body-")
    with os.fdopen(fd, "w") as f:
        f.write(body)
    return body_file


def pending_in(wt, n):
    return run_dir.issue_file(wt, n, "-preflight-wait")


def save_pending(wt, n, *fields):
    """Record the wait preflight exits 3 on: its <fields>, the conductor it ran under (FC7), and what step 3 settled
    before it (CARRIED), so a second call neither repeats nor loses it (RP8)."""
    with open(pending_in(wt, n), "w") as f:
        json.dump({"conductor": fused.conductor(wt), "fields": list(fields), "carried": CARRIED}, f)


def load_pending(wt, n):
    """The fields of the wait a first call recorded, CARRIED restored from it; None when there is no usable record. A
    record another conductor wrote is removed: its wait would hand back a dead run's code (FC7)."""
    try:
        with open(pending_in(wt, n)) as f:
            record = json.load(f)
        fields, carried = record["fields"], record["carried"]
        theirs = record.get("conductor")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    if theirs != fused.conductor(wt):
        os.remove(pending_in(wt, n))
        return None
    CARRIED.update(carried)
    return fields


def carried_lines():
    """The `stray=` and `rebased_from=` lines a handed-back worktree carries (RP6, RP7)."""
    return (["stray=" + path for path in CARRIED.get("stray", [])]
            + (["rebased_from=" + CARRIED["rebased_from"]] if CARRIED.get("rebased_from") else []))


def stopped(step, what, code):
    sys.stdout.write("".join(line + "\n" for line in carried_lines()) + "stopped at %d %s\n" % (step, what))
    return code


def check_environment(answered=None):
    """Steps 1 and 2's checks before ready-check.sh; the gh call's stdout lands in <answered>["user"], "" when it
    failed."""
    for step, *cmd in ((1, "git", "rev-parse", "--is-inside-work-tree"), (1, "git", "status", "--porcelain"),
                       (2, "gh", "api", "user"), (2, "claude", "auth", "status"),
                       (2, script("leaf-launchable.sh"))):
        code, out, _ = call(*cmd)
        if answered is not None and cmd[0] == "gh":
            answered["user"] = out if code == 0 else ""
        if cmd[1:] == ["status", "--porcelain"] and code == 0 and out.strip():
            code = 1
        if cmd[1:] == ["auth", "status"] and '"loggedIn": false' in out:
            code = 1
        if code != 0:
            return stopped(step, label(*cmd), code)
    return None


def refusing_rows():
    """The names of the readiness rows whose failure stops a run (RD2, RD3, RD7); every other failing row warns."""
    label = tunables.get("VERI_LABEL")
    return ("fast tier", "all tier", "pull_request", "gh auth", "push access", "label " + label if label else "label")


RECORD_KEYS = ("login", "origin", "version", "date")


def main_working_tree():
    """The main working tree's path, from `git worktree list`'s first entry; None when git gives none."""
    code, out, _ = run_script("git", "worktree", "list", "--porcelain")
    first = out.split("\n", 1)[0] if code == 0 else ""
    return first[len("worktree "):] or None if first.startswith("worktree ") else None


def permission_facts(user_answer):
    """The facts the permission record is keyed on: the gh login (from step 2's `gh api user` answer), a sha256 of
    origin's URL (never the URL, which may carry a credential) and the check's version, as {key: text}; None when any
    cannot be read, so nothing is skipped or written."""
    try:
        login = json.loads(user_answer)["login"]
    except (ValueError, KeyError, TypeError):
        return None
    code, url, _ = run_script("git", "remote", "get-url", "origin")
    url = url.strip() if code == 0 else ""
    if not isinstance(login, str) or not login.strip() or not url or "\n" in login + url:
        return None
    return {"login": login.strip(), "origin": hashlib.sha256(url.encode()).hexdigest(),
            "version": str(ready_check.PERMISSIONS_CHECK_VERSION)}


def permissions_record(main):
    return os.path.join(main, ".tdd", "permissions-checked")


def today():
    """The local date, read once per check: the one clock the permission record is written and judged by."""
    return datetime.date.today()


def recorded_date(path, facts, on):
    """The date <path>'s record holds when it names exactly <facts>; None for one that is missing, unreadable,
    malformed, dated after <on> or written for another login, URL or version: each runs the permission rows."""
    try:
        with open(path) as f:
            lines = f.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return None
    if lines[-1:] == [""]:
        lines.pop()
    held = [line.partition("=") for line in lines]
    if [key for key, eq, _ in held if eq] != list(RECORD_KEYS) or len(held) != len(RECORD_KEYS):
        return None
    record = {key: value for key, _, value in held}
    try:
        date = datetime.date.fromisoformat(record["date"])
    except ValueError:
        return None
    if date > on or any(record[key] != value for key, value in facts.items()):
        return None
    return record["date"]


def write_record(path, facts, on):
    """Write <facts> and the date <on> to <path>, whole or not at all. A write that fails costs only the record: one
    stderr line naming it (relative to the main working tree) and why, the temporary file this call made removed, and
    preflight goes on, the rows simply running again next time."""
    text = "".join(f"{key}={value}\n" for key, value in {**facts, "date": on.isoformat()}.items())
    partial = None
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd, partial = tempfile.mkstemp(prefix=".permissions-checked-", dir=os.path.dirname(path))
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(partial, path)
    except OSError as e:
        if partial is not None:
            with contextlib.suppress(OSError):
                os.remove(partial)
        shown = os.path.join(".tdd", os.path.basename(path))
        sys.stderr.write("preflight.sh: %s not written (%s); the permission rows run again next time\n"
                         % (shown, e.strerror or type(e).__name__))


def permission_rows_passed(out):
    """Whether ready-check.sh's <out> prints every permission row, none of them `fail`: a failing row ends in its
    fix (`fail  <name>: <fix>`), so only a row that holds ends in its name."""
    lines = out.splitlines()
    return all(any(line.endswith("  " + name) for line in lines)
               for name in ready_check.permission_row_names())


def check_readiness(user_answer=""):
    """Step 2's last check: ready-check.sh --no-suites, stopping the run on a failing refusing row. Its permission
    rows are skipped (--no-permissions) while the main working tree's .tdd/permissions-checked names the current gh
    login, origin URL and check version, and VERI_RECHECK_PERMISSIONS is not 1."""
    recheck = tunables.get("VERI_RECHECK_PERMISSIONS")
    if not tunables.parses("VERI_RECHECK_PERMISSIONS", recheck):
        sys.stdout.write("VERI_RECHECK_PERMISSIONS=%s: not 0 or 1\n" % recheck)
        return stopped(2, "VERI_RECHECK_PERMISSIONS", 2)
    main = main_working_tree()
    facts = permission_facts(user_answer) if main else None
    record = permissions_record(main) if facts else None
    on = today()
    checked_on = recorded_date(record, facts, on) if record and recheck == "0" else None
    if checked_on:
        sys.stdout.write("permission rows skipped: checked %s\n" % checked_on)
        code, out, _ = call(script("ready-check.sh"), "--no-suites", "--no-permissions")
    else:
        code, out, _ = call(script("ready-check.sh"), "--no-suites")
        if record and code in (0, 1) and permission_rows_passed(out):
            write_record(record, facts, on)
    refused = [line for line in out.splitlines()
               if any(line.startswith(f"fail  {name}: ") for name in refusing_rows())]
    if code == 1 and refused:
        return stopped(2, "ready-check.sh --no-suites", 1)
    if code not in (0, 1):
        return stopped(2, "ready-check.sh --no-suites", 2)
    return None


# The calls PREFLIGHT.md step 3 names for a worktree issue-worktree.sh handed back, in the order this script makes them
# (RP4, RP5); unit/test_preflight_steps.py fails when one of them is missing here (RP15).
HANDED_BACK = ("resume-clean.sh", "rebase-onto-default.sh", "event.sh resume-rebase",
               "tests-frozen.sh rerecord-rebased", "push-branch.sh --force-with-lease")

# What step 3 settles for the rest of the run (RP6, RP7): "run", resume or fresh; and for a handed-back worktree the
# paths resume-clean.sh printed under "stray", and under "rebased_from" the pre-rebase sha when the rebase moved the
# branch. Filled by one run of main().
CARRIED = {}


def handed_back(n, wt, ledger):
    """PREFLIGHT.md step 3's block for a worktree issue-worktree.sh handed back: discard a killed leaf's leftovers,
    rebase onto the default branch and, when that moved the branch, mark it and re-record the frozen tests (RP4)."""
    stray = checked(3, script("resume-clean.sh"), cwd=wt)
    CARRIED["stray"] = [line[3:] for line in stray.splitlines() if line.strip()]
    code, out, _ = call(script("rebase-onto-default.sh"), cwd=wt)
    if code not in (0, 1, 3):
        raise Stop(3, "rebase-onto-default.sh", code)
    if code != 0:
        return
    pre = out.split("\n", 1)[0].strip()
    CARRIED["rebased_from"] = pre
    head = checked(3, "git", "rev-parse", "HEAD", cwd=wt).strip()
    checked(3, script("event.sh"), "resume-rebase", "from=" + pre, "rebased=" + head, cwd=wt,
            env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))
    checked(3, script("tests-frozen.sh"), "rerecord-rebased", ledger, pre, cwd=wt, ok=(0, 3))


def leased_push(wt, pre):
    """Publish a resume rebase that moved the branch, once the fast tier is green: the lease pinned to the pre-rebase
    sha, never a bare force, and only from a clean tree (RP5, RP10)."""
    if checked(3, "git", "status", "--porcelain", cwd=wt).strip():
        raise Stop(3, "tree-check", 1)
    branch = checked(3, "git", "rev-parse", "--abbrev-ref", "HEAD", cwd=wt).strip()
    checked(3, script("push-branch.sh"), "--force-with-lease=%s:%s" % (branch, pre), cwd=wt)


def recorded_base(n, wt, main):
    """The branch base a fresh launch recorded under <main>, else, with no local record, the copy origin's
    refs/veri/runs/<n> carries, written back to the record; a base missing, unreadable, not a hex commit name or not an
    ancestor of HEAD in <wt> (a git that cannot tell included) stops step 3 with exit 2 naming the record."""
    path = run_dir.issue_file(main, n, run_pins.BRANCH_BASE)
    carried = False
    try:
        base = run_pins.branch_base(n, main)
    except FileNotFoundError:
        base, carried = (run_records.read(n, os.path.basename(path), wt) or "").strip(), True
    except OSError:
        base = None
    if (base is None or not re.fullmatch(r"[0-9a-f]{7,40}", base)
            or call("git", "merge-base", "--is-ancestor", base, "HEAD", cwd=wt)[0] != 0):
        raise Stop(3, "branch-base record " + path, 2)
    if carried:
        run_pins.write_branch_base(main, n, base)
    return base


def fresh_base(wt):
    """The merge base of HEAD and the branch the run was cut from: origin/<stack> when its cut recorded a stack, as
    rebase-onto-default.sh re-records it, else origin/HEAD. Exit 2 when it cannot be told, never an empty record
    (#4374)."""
    try:
        # run_base checks the cut's record against the named stack; with no record it would ask git for the default.
        ref = "origin/" + stack_branch.run_base(wt)[0] if stack_branch.recorded_base(wt) else "origin/HEAD"
    except stack_branch.Refused as refused:
        raise Stop(3, "branch base: " + str(refused), 2) from refused
    # git merge-base exits 1 when there is no common ancestor, so a 0 always printed one.
    code, out, _ = call("git", "merge-base", "HEAD", ref, cwd=wt)
    if code != 0:
        raise Stop(3, "git merge-base HEAD %s exit %d" % (ref, code), 2)
    return out.strip()


def set_up(n, slug, detect):
    """The run's worktree, made ready for its baseline suite: (worktree, fast tier command, issue body file)."""
    wt = checked(3, script("issue-worktree.sh"), n, slug).strip()
    checked(3, script("stop-requested.sh"), "--clear", cwd=wt, ok=(0, 3))
    marker = run_dir.run_file(wt, "ci-conflict-rebased")
    if os.path.exists(marker):
        os.remove(marker)
    ledger = os.path.relpath(run_dir.ledger(".", n))
    resume = os.path.exists(os.path.join(wt, ledger))
    CARRIED["run"] = "resume" if resume else "fresh"
    if not resume:
        checked(3, script("unlabel-issue.sh"), n, cwd=wt)
    checked(3, script("worktree-setup.sh"), n, cwd=wt, ok=(0, 3))
    if os.path.exists(run_dir.run_file(wt, "handed-back")):
        handed_back(n, wt, ledger)
    body_file = issue_body(n, wt)
    checked(3, script("requirements-preflight.sh"), body_file, *([ledger] if resume else []), cwd=wt)
    # The fast command every leaf and verifier is handed is read at the branch base, the merge base of HEAD and
    # origin/HEAD (origin/<stack> on a stacked run) a verifier reads its run lines at, so a CLAUDE.md a leaf committed
    # on a resumed branch never sets it; with no base, detect-test-command.sh refuses (exit 2), never reading the
    # working tree (#4263). A fresh run records it in the main working tree once the branch is cut, and a resume reads
    # it back from there, never recomputing it from refs a leaf can rewrite (#4374).
    main = run_dir.main_tree_from_files(wt)
    if resume:
        base = recorded_base(n, wt, main)
    else:
        base = fresh_base(wt)
        run_pins.write_branch_base(main, n, base)
    fast = checked(3, detect, "--tier", "fast", "--issue", body_file, "--at", base, wt, cwd=wt).strip()
    return wt, fast, body_file


def recorded_green(n, wt, fast, body_file, detect):
    """Whether this machine records a green baseline of the tree under test with these commands."""
    tree = call("git", "rev-parse", "HEAD^{tree}", cwd=wt)[1].strip()
    full = checked(3, detect, "--tier", "all", "--issue", body_file, wt, cwd=wt).strip()
    out = call(script("baseline-full-tier.sh"), "--green", n, tree, fast, full, cwd=wt)[1]
    return out.strip() == "skip"


def ci_green(wt):
    """Whether CI's `CI` workflow concluded `success` on a `push` of the commit under test. A `pull_request` run
    reports the PR head's sha but tests the merge commit with its base, so it never vouches for this tree."""
    sha = call("git", "rev-parse", "HEAD", cwd=wt)[1].strip()
    code, out, _ = call("gh", "run", "list", "--workflow", "CI", "--event", "push", "--commit", sha, "--limit", "1",
                        "--json", "headSha,status,conclusion,event", cwd=wt)
    if code != 0:
        return False
    try:
        latest = json.loads(out)[0]
        return ((latest["headSha"], latest["status"], latest["conclusion"], latest["event"])
                == (sha, "completed", "success", "push"))
    except (ValueError, LookupError, TypeError):
        return False


def start_fast(n, wt, fast, env):
    fast_began = time.monotonic()
    code = detached("preflight-fast-" + n, fast, wt, env)
    if code == 3:
        save_pending(wt, n, "fast", fast)
    return fast_began, code


def start_full(n, wt, fast, body_file, fast_began, code, detect, env):
    if code == 3:
        sys.stdout.write("waiting on preflight-fast-%s\n" % n)
        return 3
    if code != 0:
        return stopped(3, "detach-command.sh wait", code)
    baseline = 0 if fast_began is None else math.ceil(time.monotonic() - fast_began)
    if CARRIED.get("rebased_from"):
        leased_push(wt, CARRIED["rebased_from"])
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


def full_result(n, wt, baseline, full, fast, alone, began, reused, code):
    """(0, the full tier's seconds) once it passed or its time was reused; else (the exit code preflight stops with,
    None)."""
    if reused is not None:
        return 0, reused
    if code == 3:
        save_pending(wt, n, "full", str(baseline), full, fast, alone)
        sys.stdout.write("waiting on preflight-full-%s\n" % n)
        return 3, None
    if code != 0:
        return stopped(3, "detach-command.sh wait", code), None
    checked(3, script("full-tier-time.sh"), "--record", str(int(time.monotonic() - began)), full, cwd=wt)
    return 0, math.ceil(time.monotonic() - began)


def checked_models(wt):
    """Steps 5 and 6: the tunables and budgets checked, then the leaf models; the exit code preflight stops with, else
    the models of develop-red, revise-green and verify-green."""
    for args in (("0",), ("--issue", "0")):
        checked(5, script("refactor-budget.sh"), *args, cwd=wt, ok=(0, 3))
    if "plan" in tunables.read("VERI_SKIP_VERIFY").replace(",", " ").split():
        return stopped(5, "VERI_SKIP_VERIFY", 2)
    effort = tunables.get("VERI_EFFORT_VERIFIER")
    if effort and not tunables.parses("VERI_EFFORT_VERIFIER", effort):
        return stopped(5, "VERI_EFFORT_VERIFIER", 2)
    if tunables.is_set("VERI_STEP_GROWTH"):
        sys.stdout.write("VERI_STEP_GROWTH=%s: VERI_STEP_GROWTH is retired; unset it and use VERI_STEP_GROWTH_PERCENT\n"
                         % tunables.environment()["VERI_STEP_GROWTH"])
        return stopped(5, "VERI_STEP_GROWTH", 2)
    percent = tunables.get("VERI_STEP_GROWTH_PERCENT")
    if not tunables.parses("VERI_STEP_GROWTH_PERCENT", percent):
        sys.stdout.write("VERI_STEP_GROWTH_PERCENT=%s: not a whole number >= 0\n" % percent)
        return stopped(5, "VERI_STEP_GROWTH_PERCENT", 2)
    for name in ("VERI_MISSING_REROUTE_BUDGET", "VERI_QUALITY_REPAIRS"):
        if not tunables.get(name).isdigit():
            return stopped(5, name, 2)
    checked(5, script("step-budget.sh"), cwd=wt)
    checked(5, script("adjudicate.sh"), "--check-budget", cwd=wt)
    return [checked(6, script("leaf-model.sh"), leaf, cwd=wt).strip()
            for leaf in ("develop-red", "revise-green", "verify-green")]


def finish(n, wt, baseline, full, fast, alone, reused, full_secs):
    branch = checked(4, "gh", "api", "repos/{owner}/{repo}", "-q", ".default_branch", cwd=wt)
    models = checked_models(wt)
    if isinstance(models, int):
        return models
    timeout = checked(7, script("leaf-timeout.sh"), str(baseline), "--full", str(full_secs), cwd=wt)
    lines = ["worktree=" + wt, "fast_cmd=" + fast, "full_cmd=" + full, "alone_cmd=" + alone,
             "baseline=%d" % baseline, "full=%d" % full_secs,
             "full_tier_mode=" + ("reuse" if reused is not None else "run"),
             "default_branch=" + branch.strip(), "model_develop_red=" + models[0],
             "model_revise_green=" + models[1], "model_verify_green=" + models[2], "timeout=" + timeout.strip(),
             "run=" + CARRIED["run"], *carried_lines()]
    text = "\n".join(lines) + "\n"
    with open(run_dir.issue_file(wt, n, "-preflight"), "w") as f:
        f.write(text)
    sys.stdout.write(text)
    return 0


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    CARRIED.clear()
    wt = os.path.abspath(run_dir.worktree("", n))
    if not os.path.isdir(os.path.join(wt, ".tdd")):
        # Unmarked: the stage's lines would create the worktree's directory, which a stop before step 3 must not leave.
        # A conductor's launch has made it (its pid file) before preflight runs, so every launched preflight is marked.
        return stopping(run, argv, wt)
    return event.stage("preflight", lambda: stopping(run, argv, wt), wt,
                       event.context(tunables.with_values(VERI_ISSUE=n)))


def stopping(step, *args):
    """`step(*args)`, a `Stop` it raises turned into its exit code."""
    try:
        return step(*args)
    except Stop as s:
        return stopped(s.step, s.what, s.code)


def fresh_setup(n, slug, detect):
    """A launch with no waiting preflight to resume: the environment and readiness checks, then the worktree's set-up;
    the exit code preflight stops with, else (worktree, fast tier command, issue body file)."""
    answered = {}
    stop = check_environment(answered)
    if stop is not None:
        return stop
    stop = check_readiness(answered.get("user", ""))
    if stop is not None:
        return stop
    return set_up(n, slug, detect)


def run(argv, wt):
    n, slug = argv
    env = tunables.with_values(VERI_ISSUE=n)
    detect = script("detect-test-command.sh")
    saved = load_pending(wt, n)
    fast = body_file = None
    if saved is None:
        ready = fresh_setup(n, slug, detect)
        if isinstance(ready, int):
            return ready
        wt, fast, body_file = ready
    got = {}
    code = event.stage("baseline", lambda: stopping(baseline_suite, n, wt, saved, fast, body_file, detect, env, got),
                       wt, event.context(env))
    if code != 0:
        return code
    return stopping(finish, n, wt, got["baseline"], got["full"], got["fast"], got["alone"], got["reused"],
                    got["full_secs"])


def baseline_suite(n, wt, saved, fast, body_file, detect, env, got):
    """Stage `baseline`: the fast tier, then the full tier (or its reused time), from wherever a waiting preflight left
    them; 0 with `got` filled once both passed, else the exit code preflight stops with (3: still waiting)."""
    if saved is not None:
        tiers = resumed_tiers(n, wt, saved, detect, env)
    else:
        tiers = fresh_tiers(n, wt, fast, body_file, detect, env)
    if isinstance(tiers, int):
        return tiers
    baseline, full, fast, alone, began, reused, code = tiers
    code, full_secs = full_result(n, wt, baseline, full, fast, alone, began, reused, code)
    got.update(baseline=baseline, full=full, fast=fast, alone=alone, reused=reused, full_secs=full_secs)
    # Only a baseline whose fast tier ran green, in this call or one a wait carried over, is recorded: one skipped on
    # CI's word or the record's never is, even once its full tier is waited on to green.
    if code == 0 and CARRIED.get("fast_ran"):
        tree = call("git", "rev-parse", "HEAD^{tree}", cwd=wt)[1].strip()
        call(script("baseline-full-tier.sh"), "--record-green", n, tree, fast, full, cwd=wt)
    return code


def resumed_tiers(n, wt, saved, detect, env):
    """The tiers a waiting preflight saved: its full tier waited on, or its fast tier waited on and the full tier
    started after it; (baseline, full, fast, alone, began, reused, code), else the exit code preflight stops with."""
    if saved[0] == "full":
        baseline, full, fast, alone = int(saved[1]), saved[2], saved[3], saved[4]
        began = time.monotonic()
        return baseline, full, fast, alone, began, None, wait_on("preflight-full-" + n, wt, env)
    fast = saved[1]
    fast_began = time.monotonic()
    code = wait_on("preflight-fast-" + n, wt, env)
    CARRIED["fast_ran"] = code == 0
    return full_after(n, wt, fast, None, fast_began, code, detect, env)


def fresh_tiers(n, wt, fast, body_file, detect, env):
    """A fresh launch's tiers: the fast tier skipped on a recorded green or CI's word, else started, then the full tier
    started after it; (baseline, full, fast, alone, began, reused, code), else the exit code preflight stops with."""
    if recorded_green(n, wt, fast, body_file, detect) or ci_green(wt):
        fast_began, code = None, 0
    else:
        fast_began, code = start_fast(n, wt, fast, env)
        CARRIED["fast_ran"] = code == 0
    return full_after(n, wt, fast, body_file, fast_began, code, detect, env)


def full_after(n, wt, fast, body_file, fast_began, code, detect, env):
    """`start_full` after the fast tier, its result carrying `fast`."""
    started = start_full(n, wt, fast, body_file, fast_began, code, detect, env)
    if isinstance(started, int):
        return started
    baseline, full, alone, began, reused, code = started
    return baseline, full, fast, alone, began, reused, code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
