"""ready-check.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import json
import os
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse

import ci_on_pr
import ensure_run_state_ignored
import git
import launch_floor
import paths
import pid_file as pid_file_module
import tunables
from github import gh_probe as gh, push_dry_run
from case_reader import is_test_path
from session_env import strip_session_env
from wait_ci import trigger_lines

USAGE = "usage: ready-check.sh [--no-suites] [--no-permissions] [repo-root]"
WAIT_BOUND = 590  # detach-command.sh wait's own default
CALL_BOUND = WAIT_BOUND - 30  # one call's whole run, probe and tiers together, inside a 600 s tool call
call_deadline = None  # time.monotonic() at which this call's waiting must end; main sets it


def remaining(cap):
    """Whole seconds left before call_deadline, at most <cap>; <cap> when no deadline is set."""
    if call_deadline is None:
        return cap
    return max(0, min(cap, int(call_deadline - time.monotonic())))


def default_tip():
    name = git.default_branch(remote=False)
    return "refs/remotes/origin/" + name if name else "main"


def workflow_names(tip):
    """The paths under .github/workflows/ at <tip>."""
    return git.git("ls-tree", "--name-only", tip, ".github/workflows/", capture_output=True, text=True).stdout.split()


def triggers_on(event):
    tip = default_tip()
    for name in workflow_names(tip):
        text = git.git("show", tip + ":" + name, capture_output=True, text=True).stdout
        if any(event in line for line in trigger_lines(text)):
            return True
    return False


def script(name):
    return os.path.join(paths.resolved_scripts_of(__file__), name)


def resolved_tier(tier):
    """detect-test-command.sh --tier <tier>'s (exit code, command)."""
    found = subprocess.run([script("detect-test-command.sh"), "--tier", tier], capture_output=True, text=True)
    return found.returncode, found.stdout.strip()


def detect_tier(tier):
    """detect-test-command.sh --tier <tier>'s exit code."""
    return resolved_tier(tier)[0]


def tip_commit():
    """(the default branch's tip commit, None), or (None, why it does not resolve)."""
    ref = default_tip()
    found = git.git("rev-parse", "--verify", "--quiet", ref + "^{commit}", capture_output=True, text=True)
    sha = found.stdout.strip()
    if found.returncode != 0 or not sha:
        return None, f"the default branch's tip, {ref}, does not resolve to a commit"
    return sha, None


def record_path(wt, tier):
    """The record a tier run leaves in its worktree: its start time, the tip commit and the command, a line each."""
    return os.path.join(wt, ".tdd", f"ready-{tier}.record")


def read_record(wt, tier):
    """(start time, tip, command) from <wt>'s record, or None when there is none to read."""
    try:
        with open(record_path(wt, tier)) as record:
            began, tip, command = record.read().split("\n", 2)
        return float(began), tip, command.rstrip("\n")
    except (OSError, ValueError):
        return None


def listed(wt):
    """Whether `git worktree list` names <wt> as one of the repository's worktrees."""
    answer = git.git("worktree", "list", "--porcelain", capture_output=True, text=True).stdout
    paths = {os.path.realpath(line[len("worktree "):]) for line in answer.splitlines() if line.startswith("worktree ")}
    return os.path.realpath(wt) in paths


def run_state(wt, tier):
    """What is known of ready-<tier>'s detached run in <wt>: "ended" (it recorded an exit), "dead" (no exit, and its
    recorded pid answers no more, or now names a process started at another time), "running", or "unknown" (no
    exit and no readable pid file: it may be running). Only "ended" and "dead" let its worktree be removed."""
    base = os.path.join(wt, ".tdd", f"ready-{tier}")
    if os.path.exists(base + ".exit"):
        return "ended"
    try:
        with open(base + ".pid") as pid_file:
            lines = pid_file.read().split("\n")
        pid = int(lines[0])
    except (OSError, ValueError):
        return "unknown"
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "dead"
    except PermissionError:
        pass
    except OSError:
        return "unknown"
    started = lines[1].strip() if len(lines) > 1 else ""
    if not started:
        return "running"
    if pid_file_module.ps_field("lstart", pid) is False:
        return "unknown"
    return "running" if pid_file_module.same_start(started, pid) else "dead"


def removable(wt, tier):
    """Whether <wt> may be removed: no suite of ready-<tier> is, or may be, still running in it."""
    return run_state(wt, tier) in ("ended", "dead")


def placed(tier, wt, tip, command):
    """How <wt> holds ready-<tier>'s run of <command> at <tip>: "reuse" when git lists it and its record names this
    tip and command; "fresh" when nothing is there, or only a stale tier worktree of ours whose run is over, removed
    first; else why it cannot hold the run."""
    if not os.path.lexists(wt):
        return "fresh"
    ours = listed(wt) and read_record(wt, tier)
    if ours and ours[1:] == (tip, command):
        return "reuse"
    if ours and not removable(wt, tier):
        return f"no answer was obtained: an earlier run for another tip or command still runs, or may, in {wt}; wait for it to end"
    if ours and git.git("worktree", "remove", "--force", wt, capture_output=True, text=True).returncode == 0:
        return "fresh"
    return f"no answer was obtained: {wt} is in the way and is not a tier worktree this check made; move it aside"


NOT_STARTED = object()  # tier_run_row's answer when the call's deadline passed before the tier could start


def tier_run_row(tier, command, wt, deadline, state):
    """Run <command> once in <wt>, a detached worktree of the default branch's tip, through detach-command.sh; a run
    an earlier call started there for this tip and command is waited on, not started again. None while it is still
    running at wait's bound. <state>[wt] says how far this call got: added, started, or done."""
    name = "ready-" + tier
    detach = script("detach-command.sh")
    tip, why = tip_commit()
    if tip is None:
        return f"{tier} tier run", f"no answer was obtained: {why}"
    how = placed(tier, wt, tip, command)
    if how not in ("reuse", "fresh"):
        return f"{tier} tier run", how
    if how == "reuse":
        state[wt] = "started"
        known = run_state(wt, tier)
        if known == "unknown":
            return f"{tier} tier run", f"no answer was obtained: a run started in {wt} left no pid file and no exit, so it may still run; wait for it to end"
        if known == "dead":
            return f"{tier} tier run", f"no answer was obtained: the run in {wt} ended without recording an exit"
    if how == "fresh" and deadline - time.monotonic() <= 0:
        return NOT_STARTED
    if how == "fresh":
        added = git.git("worktree", "add", "--detach", wt, tip, capture_output=True, text=True)
        if added.returncode != 0:
            said = [line.strip() for line in (added.stderr or "").splitlines() if line.strip()]
            return f"{tier} tier run", "no answer was obtained: " + (
                said[-1] if said else f"git worktree add exited {added.returncode}")
        state[wt] = "added"
        os.makedirs(os.path.join(wt, ".tdd"), exist_ok=True)
        with open(record_path(wt, tier), "w") as record:
            record.write(f"{time.time()!r}\n{tip}\n{command}\n")
        subprocess.run([detach, "start", name, *shlex.split(command)], cwd=wt, capture_output=True, text=True)
    state[wt] = "started"
    bound = str(max(0, int(deadline - time.monotonic())))
    waited = subprocess.run([detach, "wait", name, bound], cwd=wt, capture_output=True, text=True)
    if waited.returncode == 3:
        return None
    state[wt] = "done"
    return finished_row(tier, wt, waited)


def finished_row(tier, wt, waited):
    """The row of ready-<tier>'s run in <wt>, which <waited> (detach-command.sh wait's answer) says has ended; a red
    run's whole output is kept beside <wt>, and a green run removes one kept before."""
    name = "ready-" + tier
    exit_file, output = (os.path.join(wt, ".tdd", name + suffix) for suffix in (".exit", ".out"))
    ended = os.path.getmtime(exit_file) if os.path.exists(exit_file) else time.time()
    row = f"{tier} tier run ({int(ended - read_record(wt, tier)[0])}s)"
    kept = os.path.join(os.path.dirname(wt), name + ".out")
    if waited.returncode == 0:
        with contextlib.suppress(FileNotFoundError):
            os.remove(kept)
        return row, None
    said = []
    if os.path.exists(output):
        shutil.copyfile(output, kept)
        with open(output, errors="replace") as out:
            said = [line.strip() for line in out if line.strip()]
    if waited.returncode == 2:
        return row, f"no answer was obtained (exit 2 from detach-command.sh wait {name})"
    return row, f"exit {waited.stdout.strip()}: {said[-1] if said else '(no output)'}"


def tier_run_rows(root):
    """(a row per tier RD2 resolves, None) — or, while a tier is still running at wait's bound, (the rows so far, the
    name it runs under). The tier worktrees this call added or used, and a .tdd/ made for those, are removed on every
    way out but that one, which leaves every tier's worktree in place for the call that waits again — save one whose
    detached run was started and not yet waited out, which an exception leaves in place, record and all."""
    rows, state, waiting, not_started = [], {}, None, []
    tdd = os.path.join(root, ".tdd")
    made_tdd = not os.path.exists(tdd)
    deadline = call_deadline if call_deadline is not None else time.monotonic() + CALL_BOUND
    try:
        for tier in ("fast", "all"):
            code, command = resolved_tier(tier)
            if code == 0:
                row = tier_run_row(tier, command, os.path.join(tdd, "ready-" + tier), deadline, state)
                if row is NOT_STARTED:
                    not_started.append("ready-" + tier)
                    continue
                if row is None:
                    waiting = "ready-" + tier
                    break
                rows.append(row)
        if not_started and waiting is None:
            waiting = f"{not_started[0]} (not started, the call's deadline passed: {', '.join(not_started)})"
    finally:
        if waiting is None:
            for wt in [wt for wt in state if removable(wt, os.path.basename(wt)[len("ready-"):])]:
                git.git("worktree", "remove", "--force", wt, capture_output=True, text=True)
            if made_tdd:
                with contextlib.suppress(OSError):
                    os.rmdir(tdd)
    return rows, waiting


def tier_row(tier):
    def check():
        code = detect_tier(tier)
        if code == 2:
            return f"{tier} tier", f"no answer was obtained (exit 2 from detect-test-command.sh --tier {tier})"
        return f"{tier} tier", None if code != 3 else f"add a `veri: {tier} tests:` line to CLAUDE.md"
    return check


def one_test_file_row():
    code = detect_tier("one test file")
    if code == 2:
        return "one test file", 'no answer was obtained (exit 2 from detect-test-command.sh --tier "one test file")'
    return "one test file", None if code == 0 else (
        'add a `veri: one test file: <command>` line to CLAUDE.md, the command taking the test file as "$1"')


def pull_request_row():
    holds = bool(ci_on_pr.declared()) or triggers_on("pull_request")
    return "pull_request", None if holds else "add a workflow under .github/workflows/ that triggers on pull_request, add a `veri: ci on pr: 0|1` line to CLAUDE.md, or set VERI_CI_ON_PR"


def push_row():
    return "push", None if triggers_on("push") else "add a workflow under .github/workflows/ that triggers on push to the default branch"


def test_file_row():
    holds = any(is_test_path(f) for f in git.git("ls-files", capture_output=True, text=True).stdout.splitlines())
    return "test file", None if holds else "track at least one test file"


def tdd_ignored_row():
    return ".tdd/", None if git.git("check-ignore", "-q", ".tdd/issue-0-spec.md", capture_output=True, text=True).returncode == 0 else "add `.tdd/` to .gitignore"


def gh_auth_row():
    return "gh auth", None if gh("auth", "status").returncode == 0 else "run `gh auth login`"


def push_access_row():
    pushed = gh("api", "repos/{owner}/{repo}")
    try:
        can_push = json.loads(pushed.stdout)["permissions"]["push"]
    except (ValueError, KeyError, TypeError):
        can_push = False
    return "push access", None if can_push else "ask for write access to the repository, or use an account that has it"


def listed_label_row(label):
    """The row for <label>: ok when `gh label list` names it; a failing call fails it like a missing label. The limit
    lifts gh's default of 30, past which a label that exists would read missing."""
    listed = gh("label", "list", "--limit", "1000", "--json", "name")
    try:
        names = [entry["name"] for entry in json.loads(listed.stdout)] if listed.returncode == 0 else []
    except (ValueError, KeyError, TypeError):
        names = []
    return f"label {label}", None if label in names else f"create the `{label}` label in the repository"


def label_row():
    label = tunables.get("VERI_LABEL")
    if not label:
        return "label", "VERI_LABEL is set but empty: name a label or leave VERI_LABEL unset"
    return listed_label_row(label)


# The run-state labels a run writes and never creates (#4081): a repository lacking one learns it here, not mid-run.
STATE_LABELS = ("pr-ready", "bailed", "parked", "stopped")


def state_label_row(label):
    return lambda: listed_label_row(label)


class Fix(str):
    """A failing row's fix (one command) with the reason the row fails, printed before it."""

    def __new__(cls, command, reason):
        fix = super().__new__(cls, command)
        fix.reason = reason
        return fix


class Neutral(str):
    """A row's verdict that is neither ok nor fail: printed as its own word, and counted as no fail."""


NOT_VERIFIABLE = Neutral("not verifiable")


def granted_scopes(answer):
    """The scopes the X-OAuth-Scopes header of `gh api -i user`'s <answer> lists; None with no such header (a
    fine-grained token)."""
    head = answer.split("\r\n\r\n", 1)[0].split("\n\n", 1)[0]
    for line in head.splitlines():
        name, _, value = line.partition(":")
        if name.strip().lower() == "x-oauth-scopes":
            return [scope.strip() for scope in value.split(",") if scope.strip()]
    return None


def origin_is_https():
    return git.git("remote", "get-url", "--push", "origin", capture_output=True, text=True).stdout.strip().startswith("https://")


def token_scopes_row():
    needed = ["repo", "workflow"] if origin_is_https() else ["repo"]
    user = gh("api", "-i", "user")
    status = (user.stdout or "").lstrip().split("\n", 1)[0].strip()
    if user.returncode != 0 and status.startswith("HTTP/"):
        return "token scopes", f"GitHub answered {status} to gh api -i user"
    if user.returncode != 0:
        return "token scopes", f"no answer was obtained (gh api -i user exited {user.returncode})"
    granted = granted_scopes(user.stdout)
    if granted is None:
        return "token scopes", NOT_VERIFIABLE
    missing = [scope for scope in needed if scope not in granted]
    return "token scopes", "gh auth refresh -s " + ",".join(missing) if missing else None


def selection_label_row(name):
    path = f"repos/{{owner}}/{{repo}}/labels/{urllib.parse.quote(name, safe='')}"
    answered = gh("api", path)
    if answered.returncode == 0:
        return f"label {name}", None
    if "HTTP 404" in (answered.stderr or ""):
        return f"label {name}", f"gh label create {shlex.quote(name)}"
    return f"label {name}", f"no answer was obtained (gh api {path} exited {answered.returncode})"


def priority_label_row():
    return selection_label_row(tunables.get("VERI_PRIORITY_LABEL"))


def bug_label_row():
    return selection_label_row("bug")


SKIPPED = Neutral("skipped")


def actions_read_row():
    if not workflow_names(default_tip()):
        return "actions read", SKIPPED
    readable = gh("api", "repos/{owner}/{repo}/actions/runs?per_page=1").returncode == 0
    return "actions read", None if readable else "grant the token read access to Actions (`actions: read`)"


def writable(path):
    """Whether the user can write <path>, or create it in the nearest directory that exists."""
    while not os.path.exists(path):
        path = os.path.dirname(path) or "."
    return os.access(path, os.W_OK)


def run_state_ignore_row():
    common = git.git("rev-parse", "--git-common-dir", capture_output=True, text=True).stdout.strip()
    for path in (os.path.abspath(".gitignore"), os.path.join(os.path.abspath(common), "info", "exclude")):
        with contextlib.redirect_stderr(io.StringIO()):
            present = ensure_run_state_ignored.has_rule(path)
        if present is None:
            shown = " ".join("-e " + shlex.quote(line) for line in ensure_run_state_ignored.RULE)
            return "run-state ignore", Fix(f"grep -nF {shown} {shlex.quote(path)}",
                                           f"{path} carries veri's run-state rule only in part, or out of order: complete "
                                           "those lines, in that order, or remove them")
        if not present and not writable(path):
            return "run-state ignore", f"chmod u+w {shlex.quote(path)}"
    return "run-state ignore", None


def ssh_chosen():
    """Whether the user already chose how git runs ssh: GIT_SSH_COMMAND or GIT_SSH set, or core.sshCommand configured."""
    if os.environ.get("GIT_SSH_COMMAND") or os.environ.get("GIT_SSH"):
        return True
    return bool(git.git("config", "--get", "core.sshCommand", capture_output=True, text=True).stdout.strip())


def push_dry_run_row():
    probe = "HEAD:refs/heads/veri-permission-probe-" + secrets.token_hex(4)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    if not ssh_chosen():
        env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
    pushed = push_dry_run(probe, env)
    if pushed.returncode == 0:
        return "push dry-run", None
    said = [line.strip() for line in pushed.stderr.splitlines() if line.strip()]
    return "push dry-run", said[-1] if said else f"git push --dry-run origin exited {pushed.returncode}"


PROBE_FILES = ("bash-probe.txt", "write-probe.txt", "shape-probe.txt")
PROBE_TIMEOUT = 300  # seconds; one haiku turn writing three files takes well under a minute
DENY_PLACES = ("/Library/Application Support/ClaudeCode/managed-settings.json, /etc/claude-code/managed-settings.json, "
               "and the user (~/.claude/settings.json) and project (.claude/settings.json) permissions.deny")


def bypass_permissions_row():
    """One haiku `claude -p` started as a leaf is, in a scratch directory under .tdd/, asked to write a nonce file
    with Bash and another with Write: ok iff both hold the nonce and it lists no permission denial. The scratch
    directory, and a .tdd/ made for it, are removed on every way out."""
    made_tdd = not os.path.exists(".tdd")
    os.makedirs(".tdd", exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="bypass-probe-", dir=".tdd")
    try:
        return probe_bypass(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        if made_tdd:
            with contextlib.suppress(OSError):
                os.rmdir(".tdd")


def leaf_env():
    """This process's environment with strip_session_env applied, as a leaf's `claude` is started."""
    env = dict(os.environ)
    strip_session_env(env)
    return env


def probe_bypass(scratch):
    nonce = secrets.token_hex(8)
    prompt = (f"Permission probe, nonce {nonce}. First use the Bash tool to run `printf %s {nonce} > {PROBE_FILES[0]}`. "
              f"Then use the Write tool to create {PROBE_FILES[1]} whose whole content is {nonce}. "
              "Then use the Bash tool to run this one command, exactly as written over two lines:\n"
              f"T=$'{nonce}'\nprintf '%s\\n' \"${{T/#/}}\" > shape-probe.txt\nDo nothing else.")
    limit = max(1, remaining(PROBE_TIMEOUT))
    try:
        ran = subprocess.run([tunables.claude_bin(), "-p", "--model", "haiku", "--permission-mode", "bypassPermissions",
                              "--output-format", "json", prompt], cwd=scratch, env=leaf_env(), capture_output=True,
                             text=True, timeout=limit)
    except subprocess.TimeoutExpired:
        return "bypassPermissions", f"no answer was obtained (claude -p gave none within {limit}s)"
    try:
        denials = json.loads(ran.stdout).get("permission_denials") or []
    except (ValueError, AttributeError):
        denials = []
    written = []
    for name in PROBE_FILES:
        path = os.path.join(scratch, name)
        if os.path.exists(path):
            with open(path) as probe:
                content = probe.read().strip().split("\n")[0].strip() if name == PROBE_FILES[2] else probe.read().strip()
                written.append(content == nonce)
        else:
            written.append(False)
    if all(written) and not denials:
        return "bypassPermissions", None
    tools = sorted({str(denial.get("tool_name")) for denial in denials if isinstance(denial, dict)})
    said = ", ".join(f"`{tool}`" for tool in tools) or "none listed"
    missing = [name for name, held in zip(PROBE_FILES, written) if not held]
    places = DENY_PLACES
    if PROBE_FILES[2] in missing:
        places += (", and permissions.ask and permissions.blockReadsOutsideWorkingDirectories, since Claude Code "
                   f"refused or asked on {PROBE_FILES[2]}'s command, which it could not statically analyze")
    return "bypassPermissions", (
        f"denied tools: {said}; nonce files missing or wrong: {', '.join(missing) or 'none'}; look in {places}")


SETTINGS_FILES = ("~/.claude/settings.json", ".claude/settings.json", ".claude/settings.local.json")


def merged_permissions():
    """(defaultModes, allow rules) across the user, project and local settings files that parse."""
    modes, allowed = [], set()
    for name in SETTINGS_FILES:
        try:
            with open(os.path.expanduser(name)) as handle:
                permissions = json.load(handle).get("permissions") or {}
            modes.append(permissions.get("defaultMode"))
            allowed.update(permissions.get("allow") or [])
        except (OSError, ValueError, AttributeError):
            continue
    return modes, allowed


def subagent_permissions_row():
    modes, allowed = merged_permissions()
    if "bypassPermissions" in modes:
        return "subagent permissions", None
    wanted = ["Bash(git *)"]
    command = resolved_tier("all")[1]
    if command:
        wanted.append(f"Bash({command})")
    wanted.append(f"Bash({paths.resolved_scripts_of(__file__)}/*)")
    missing = [rule for rule in wanted if rule not in allowed]
    if not missing:
        return "subagent permissions", None
    return "subagent permissions", "the dev session's subagents would prompt; add to permissions.allow: " + ", ".join(missing)


def bash_row():
    holds = launch_floor.bash_refusal("ready-check") == 0
    return "bash", None if holds else "install bash 5 or newer (`brew install bash`) and put it first on PATH"


def python_row():
    holds = launch_floor.python_refusal("ready-check") == 0
    return "Python", None if holds else f"install Python {launch_floor.python_floor()} or newer and put it first on PATH"


CHECKS = (tier_row("fast"), tier_row("all"), one_test_file_row, pull_request_row, push_row, test_file_row, tdd_ignored_row,
          gh_auth_row, push_access_row, label_row, *map(state_label_row, STATE_LABELS), token_scopes_row, priority_label_row, bug_label_row,
          actions_read_row, run_state_ignore_row, push_dry_run_row, bypass_permissions_row, subagent_permissions_row, bash_row, python_row)
# The permission rows (PRD 016.6a-c), which --no-permissions skips: RD7's rows are cheap and refuse a run, these only warn.
PERMISSION_CHECKS = (token_scopes_row, priority_label_row, bug_label_row, actions_read_row, run_state_ignore_row,
                     push_dry_run_row, bypass_permissions_row)
# The permission rows' check version, which preflight's .tdd/permissions-checked record carries: raise it whenever a
# permission row's probe changes, so every clone's record goes stale and the rows run again (PRD 016.9).
PERMISSIONS_CHECK_VERSION = 2


def permission_row_names():
    """The names PERMISSION_CHECKS' rows print under, in order."""
    return ["token scopes", "label " + tunables.get("VERI_PRIORITY_LABEL"), "label bug", "actions read",
            "run-state ignore", "push dry-run", "bypassPermissions"]


def rendered(name, verdict):
    if verdict is None:
        return f"ok    {name}"
    if isinstance(verdict, Neutral):
        return f"{verdict}  {name}"
    if isinstance(verdict, Fix):
        return f"fail  {name}: {verdict.reason}; run `{verdict}`"
    return f"fail  {name}: {verdict}"


def main(argv):
    """One call, its probe and tiers bounded together by CALL_BOUND counted from here."""
    global call_deadline
    call_deadline = time.monotonic() + CALL_BOUND
    try:
        return checked(argv)
    finally:
        call_deadline = None


def checked(argv):
    flags = []
    while argv and argv[0] in ("--no-suites", "--no-permissions") and argv[0] not in flags:
        flags.append(argv[0])
        argv = argv[1:]
    suites, permissions = "--no-suites" not in flags, "--no-permissions" not in flags
    if len(argv) > 1 or any(a.startswith("-") for a in argv):
        print(USAGE, file=sys.stderr)
        return 2
    root = None
    if argv:
        root = argv[0]
    else:
        listing = git.git("worktree", "list", "--porcelain", capture_output=True, text=True).stdout.split("\n", 1)[0]
        if listing.startswith("worktree "):
            root = listing[len("worktree "):]
    if root is not None:
        os.chdir(root)
    root = os.path.abspath(root) if root is not None else os.getcwd()
    inside = git.git("rev-parse", "--git-dir", capture_output=True, text=True)
    if inside.returncode != 0:
        print(f"ready-check.sh: not a git repository\n{USAGE}", file=sys.stderr)
        return 2
    results = [check() for check in CHECKS if permissions or check not in PERMISSION_CHECKS]
    tier_runs, waiting = tier_run_rows(root) if suites else ([], None)
    results += tier_runs
    failed = sum(1 for _, verdict in results if verdict and not isinstance(verdict, Neutral))
    rows = [rendered(name, verdict) for name, verdict in results]
    print(*rows, sep="\n")
    if waiting:
        print("waiting on " + waiting)
        return 3
    if failed:
        print(f"not ready — {failed} rows to fix")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
