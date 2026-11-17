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

import ensure_run_state_ignored
import git
import launch_floor
import paths
import tunables
from github import gh_probe as gh, push_dry_run
from case_reader import is_test_path
from wait_ci import trigger_lines

USAGE = "usage: ready-check.sh [repo-root]"
WAIT_BOUND = 590  # detach-command.sh wait's own default: one call's whole wait on the tiers, both together


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


def tier_run_row(tier, command, wt, deadline):
    """Run <command> once in <wt>, a detached worktree of the default branch's tip, through detach-command.sh; a run
    an earlier call started there (its start time recorded in <wt>) is waited on, not started again. None while it
    is still running at wait's bound."""
    name = "ready-" + tier
    detach = script("detach-command.sh")
    started = os.path.join(wt, ".tdd", name + ".began")
    if not os.path.exists(started):
        git.git("worktree", "add", "--detach", wt, default_tip(), capture_output=True, text=True)
        os.makedirs(os.path.join(wt, ".tdd"), exist_ok=True)
        with open(started, "w") as began:
            began.write(repr(time.time()))
        subprocess.run([detach, "start", name, *shlex.split(command)], cwd=wt, capture_output=True, text=True)
    bound = str(max(0, int(deadline - time.monotonic())))
    waited = subprocess.run([detach, "wait", name, bound], cwd=wt, capture_output=True, text=True)
    if waited.returncode == 3:
        return None
    return finished_row(tier, wt, waited)


def finished_row(tier, wt, waited):
    """The row of ready-<tier>'s run in <wt>, which <waited> (detach-command.sh wait's answer) says has ended; a red
    run's whole output is kept beside <wt>, and a green run removes one kept before."""
    name = "ready-" + tier
    exit_file, output = (os.path.join(wt, ".tdd", name + suffix) for suffix in (".exit", ".out"))
    ended = os.path.getmtime(exit_file) if os.path.exists(exit_file) else time.time()
    with open(os.path.join(wt, ".tdd", name + ".began")) as began:
        row = f"{tier} tier run ({int(ended - float(began.read()))}s)"
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
    name it runs under). The worktrees made for them, and a .tdd/ made for those, are removed on every way out but
    that one, which leaves every tier's worktree in place for the call that waits again."""
    rows, made, waiting = [], [], None
    tdd = os.path.join(root, ".tdd")
    made_tdd = not os.path.exists(tdd)
    deadline = time.monotonic() + WAIT_BOUND
    try:
        for tier in ("fast", "all"):
            code, command = resolved_tier(tier)
            if code == 0:
                made.append(os.path.join(tdd, "ready-" + tier))
                row = tier_run_row(tier, command, made[-1], deadline)
                if row is None:
                    waiting = "ready-" + tier
                    break
                rows.append(row)
    finally:
        if waiting is None:
            for wt in made:
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
    holds = bool(tunables.read("VERI_CI_ON_PR")) or triggers_on("pull_request")
    return "pull_request", None if holds else "add a workflow under .github/workflows/ that triggers on pull_request, or set VERI_CI_ON_PR"


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


def label_row():
    label = tunables.get("VERI_LABEL")
    if not label:
        return "label", "VERI_LABEL is set but empty: name a label or leave VERI_LABEL unset"
    listed = gh("label", "list", "--json", "name")
    try:
        names = [entry["name"] for entry in json.loads(listed.stdout)] if listed.returncode == 0 else []
    except (ValueError, KeyError, TypeError):
        names = []
    return f"label {label}", None if label in names else f"create the `{label}` label in the repository"


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
                                           "those three lines, in that order, or remove them")
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


PROBE_FILES = ("bash-probe.txt", "write-probe.txt")


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


def probe_bypass(scratch):
    nonce = secrets.token_hex(8)
    prompt = (f"Permission probe, nonce {nonce}. First use the Bash tool to run `printf %s {nonce} > {PROBE_FILES[0]}`. "
              f"Then use the Write tool to create {PROBE_FILES[1]} whose whole content is {nonce}. Do nothing else.")
    ran = subprocess.run([tunables.claude_bin(), "-p", "--model", "haiku", "--permission-mode", "bypassPermissions",
                          "--output-format", "json", prompt], cwd=scratch, capture_output=True, text=True)
    try:
        denials = json.loads(ran.stdout).get("permission_denials") or []
    except (ValueError, AttributeError):
        denials = []
    written = []
    for name in PROBE_FILES:
        path = os.path.join(scratch, name)
        if os.path.exists(path):
            with open(path) as probe:
                written.append(probe.read().strip() == nonce)
        else:
            written.append(False)
    return "bypassPermissions", None if all(written) and not denials else "fail"


def bash_row():
    holds = launch_floor.bash_refusal("ready-check") == 0
    return "bash", None if holds else "install bash 5 or newer (`brew install bash`) and put it first on PATH"


def python_row():
    holds = launch_floor.python_refusal("ready-check") == 0
    return "Python", None if holds else f"install Python {launch_floor.python_floor()} or newer and put it first on PATH"


CHECKS = (tier_row("fast"), tier_row("all"), one_test_file_row, pull_request_row, push_row, test_file_row, tdd_ignored_row,
          gh_auth_row, push_access_row, label_row, token_scopes_row, priority_label_row, bug_label_row,
          actions_read_row, run_state_ignore_row, push_dry_run_row, bypass_permissions_row, bash_row, python_row)


def rendered(name, verdict):
    if verdict is None:
        return f"ok    {name}"
    if isinstance(verdict, Neutral):
        return f"{verdict}  {name}"
    if isinstance(verdict, Fix):
        return f"fail  {name}: {verdict.reason}; run `{verdict}`"
    return f"fail  {name}: {verdict}"


def main(argv):
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
    results = [check() for check in CHECKS]
    tier_runs, waiting = tier_run_rows(root)
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
