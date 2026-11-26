"""run-conductor.sh's launch of one conductor, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import calendar
import collections
import contextlib
import glob
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

import entry
import leg_tmpdir
import paths
import pid_file as pids
import pinned_scripts
import requirements
import run_dir
import run_pins
import run_records

# Only the entry-point run switches bytecode off; an importer keeps its own setting.
sys.dont_write_bytecode = sys.dont_write_bytecode or __name__ == "__main__"

import event
import event_log
import github
import launch_floor
import leaf_timeout
import run_end
import tunables
from context_limits import context_limits
from git import symref_default
from leaf_log import result_text
from session_env import strip_session_env

USAGE = "usage: run-conductor.sh <issue>"
HELD_REF_LOCK = ("cannot lock ref", "reference already exists")


class Claim:
    """conductor.pid taken for this process on entry, with the directories made to hold it; on exit the file, then
    those directories deepest first, are removed only while the file still holds this claim's own bytes."""

    def __init__(self, path):
        self.path, self.made, self.held = path, [], None

    def __enter__(self):
        directory = os.path.dirname(os.path.abspath(self.path))
        while not os.path.isdir(directory):
            self.made.insert(0, directory)
            directory = os.path.dirname(directory)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.held = pids.record(self.path, os.getpid()).encode()
        return self

    def keep_directories(self):
        """The launch is under way: the run's directories outlive the claim, so its exit removes none of them."""
        self.made = []

    def hand_off(self):
        """The launched conductor recorded its own pid: the file is no longer this claim's to remove."""
        self.held = None

    def __exit__(self, *_):
        try:
            with open(self.path, "rb") as handle:
                mine = self.held is not None and handle.read() == self.held
        except FileNotFoundError:
            mine = False
        if mine:
            os.remove(self.path)
            for directory in reversed(self.made):
                with contextlib.suppress(OSError):
                    os.rmdir(directory)


def main(argv):
    tunables.pop("VERI_EVENT_STRICT")  # a run never checks its events (PRD 014 JR3): telemetry never bails it
    for name in ("REVISE_BUDGET", "VERI_REBASED_TIP_SUITE", "VERI_BRANCH_SUITE", "VERI_BASELINE_FULL_TIER",
                 "VERI_FULL_TIER_MAX_AGE_DAYS", "VERI_CI_FLAKE_RERUNS",
                 "VERI_TEST_QUALITY_FIXES", "VERI_BRANCH_REPAIRS"):
        _, bad = tunables.resolve(name)
        if bad:
            sys.stderr.write("run-conductor: %s must be %s, got '%s'\n" % (name, bad[1], bad[0]))
            return 2
    if launch_floor.bash_refusal("run-conductor") or launch_floor.python_refusal("run-conductor"):
        return 2
    if not argv or entry.whole_number(argv[0]) is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    live = pids.recorded_started(run_worktree(argv[0]))
    if live:
        sys.stderr.write("run-conductor: a conductor for issue %s is already live (pid %s)\n" % (argv[0], live))
        return 2
    with Claim(pid_file_path(argv[0])) as claim:
        return preflight_and_launch(argv, claim)


def pid_file_path(issue):
    return run_dir.run_file(run_worktree(issue), "conductor.pid")


def preflight_and_launch(argv, claim=None):
    raw_minimum = tunables.get("VERI_MIN_FREE_GB")
    minimum = entry.whole_number(raw_minimum, 0)
    if minimum is None:
        sys.stderr.write("run-conductor: VERI_MIN_FREE_GB must be a whole number >= 0, got '%s'\n" % raw_minimum)
        return 2
    for directory in (tempfile.gettempdir(), pinned_tmpdir(), os.getcwd()):
        free = free_gb(directory)
        if free < minimum:
            sys.stderr.write("run-conductor: '%s' has %d GB free, below VERI_MIN_FREE_GB=%d\n" % (directory, free, minimum))
            return 2
    here = paths.scripts_of(__file__)
    base = os.path.dirname(here)
    record = record_path(argv[0])
    released = run_dir.issue_file(event.toplevel(), argv[0], "-released")
    mode = pin_mode(record, released)
    resuming = mode == "resume"
    if not resuming:
        for word in tunables.get("VERI_SKIP_VERIFY").split(","):
            if word and word not in ("refactor", "pin", "green", "red", "diff", "branch"):
                sys.stderr.write("run-conductor: VERI_SKIP_VERIFY names '%s', which cannot be skipped (only refactor, pin, green, red, diff and branch can)\n" % word)
                return 2
    carried = None
    if mode == "first" and not os.path.lexists(record):
        carried = carried_pin(argv[0])
    if carried:
        mode, resuming = "resume", True
    if not resuming:
        update_veri(here)
    head_rev = "HEAD"
    if git(base, "remote", "get-url", "origin",
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        fetches = 0
        while True:
            fetch = git(base, "fetch", "-q", "origin",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            fetches += 1
            if fetch.returncode == 0:
                break
            sys.stderr.write(fetch.stderr.rstrip("\n") + "\n")
            held = any(wording in fetch.stderr for wording in HELD_REF_LOCK)
            if held and fetches < 60:
                if subprocess.run(["sleep", tunables.get("VERI_FETCH_RETRY_SLEEP", unless_empty=True)]).returncode != 0:
                    return 1
                continue
            if held:
                sys.stderr.write("run-conductor: another process holds the ref lock\n")
            sys.stderr.write("run-conductor: fetch of origin failed in '%s' — refusing to run a skill that may be stale\n" % base)
            return 2
        head_rev = "refs/remotes/origin/HEAD"
        if not verifies(base, head_rev):
            answer = git(base, "ls-remote", "--symref", "origin", "HEAD",
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if answer.returncode != 0:
                return 2
            default = symref_default(answer.stdout)
            if not default:
                return refuse_unpinned(base, "origin names no default branch")
            head_rev = "refs/remotes/origin/" + default
            if not verifies(base, head_rev):
                return refuse_unpinned(base, "origin's default branch '%s' has no %s" % (default, head_rev))
    if carried:
        mode = adopt_carried_pin(base, head_rev, carried, record)
        if mode == "resume":
            # The timeout travels with the pin it was settled under: a rejected carry is a fresh launch in every respect.
            restore_carried_timeout(argv[0])
        if mode == "first":
            # A rejected carried pin leaves a fresh launch, which updates veri's clone first; that runs here instead.
            update_veri(here)
    snap = skill_snapshot(base, head_rev, record, mode)
    if snap.kind != "unpinned":
        commit = snap.commit
        run_state = os.path.join(event.toplevel(), ".tdd")
        os.makedirs(run_state, exist_ok=True)
        seed_path = os.path.join(run_state, ".gitignore")
        if not os.path.exists(seed_path):
            with open(seed_path, "w") as seed:
                seed.write(run_pins.gitignore_seed())
        if snap.kind == "refused":
            sys.stderr.write(snap.message)
            return snap.code
        if snap.kind != "kept":
            with open(record, "w") as out:
                out.write(commit + "\n")
            if os.path.exists(released):
                os.remove(released)
            run_pins.write_skip_verify(event.toplevel(), argv[0], tunables.get("VERI_SKIP_VERIFY"))
            run_pins.write_baseline_full_tier(event.toplevel(), argv[0], tunables.get("VERI_BASELINE_FULL_TIER"))
            if snap.kind == "repin":
                worktree = run_worktree(argv[0])
                os.makedirs(worktree, exist_ok=True)
                if event.mark(worktree, event.context(tunables.with_values(VERI_ISSUE=argv[0])),
                              "skill-repin", ["commit=" + commit]) != 0:
                    return 2
        snapshot = pinned_scripts.make_snapshot()
        try:
            status = extract(base, commit, snapshot)
            if status != 0:
                return status if status <= 3 else 2
            pinned_scripts.write_snapshot_marker(snapshot, run_worktree(argv[0]))
            pinned_scripts.make_read_only(snapshot)
            extracted = pinned_scripts.snapshot_digest(snapshot)
            run_pins.write_snapshot_digest(event.toplevel(), argv[0], pinned_scripts.digest_text(extracted))
            keep_pinned_scripts(snapshot, argv[0])
            code = launch(snapshot, argv[0], commit, claim=claim, VERI_SKILL_COMMIT=commit, VERI_SKILL_CLONE=base, VERI_SKILL_REF=head_rev)
            changed = snapshot_change(snapshot, argv[0], extracted)
            if changed is None:
                return code
            sys.stderr.write("run-conductor: the skill snapshot changed during the run\n")
            worktree = run_worktree(argv[0])
            os.makedirs(worktree, exist_ok=True)
            event.mark(worktree, event.context(tunables.with_values(VERI_ISSUE=argv[0])),
                       "snapshot-changed", ["path=" + changed])
            return 2
        finally:
            try:
                keep_pinned_scripts(snapshot, argv[0])
            finally:
                pinned_scripts.remove_tree(snapshot)
    sys.stderr.write("run-conductor: no skill commit resolvable from '%s' — running unpinned\n" % base)
    return launch(base, argv[0], None, claim=claim, VERI_SKILL_UNPINNED="1")


Snapshot = collections.namedtuple("Snapshot", "kind commit why message code")


def update_veri(here):
    """Fast-forward veri's own clone (update-veri.sh) before a fresh pin; a script that cannot start is skipped."""
    try:
        subprocess.run([os.path.join(here, "update-veri.sh")])
    except OSError:
        pass


def restore_carried_timeout(issue):
    """Write the run's timeout pin (in its worktree, where leaf_timeout.settled reads it) from the one origin's
    refs/veri/runs/<issue> carries, when the run has none of its own; a carried value settled() would refuse is named in
    one stderr line and ignored, so the run settles its timeout as a fresh one does."""
    pin = leaf_timeout.pin_path(run_worktree(issue), issue)
    if os.path.lexists(pin):
        return
    carried = run_records.read(issue, "issue-%s-timeout" % issue, event.toplevel() or ".")
    if carried is None:
        return
    if not leaf_timeout.valid_pin(carried):
        sys.stderr.write("run-conductor: the carried issue-%s-timeout holds '%s', not a whole number of seconds >= 1"
                         " — ignored\n" % (issue, " ".join(carried.split())))
        return
    os.makedirs(os.path.dirname(pin), exist_ok=True)
    with open(pin, "w") as out:
        out.write(carried.rstrip("\n") + "\n")


def carried_pin(issue):
    """The skill commit origin's refs/veri/runs/<issue> carries, when it carries a commit name; None otherwise."""
    carried = (run_records.read(issue, "issue-%s-skill-commit" % issue, event.toplevel() or ".") or "").strip()
    return carried if re.fullmatch(r"[0-9a-f]{7,40}", carried) else None


def adopt_carried_pin(base, head_rev, carried, record):
    """The launch's mode once the <carried> pin is judged: "resume", its <record> written, when it is an ancestor of
    <head_rev> (the skill clone's origin default) in <base>; else "first", with one stderr line naming it. refs/veri/*
    lies outside the default branch's protection, so a pin anyone pushed there is honoured only when reviewed code
    already holds it."""
    if git(base, "merge-base", "--is-ancestor", carried, head_rev,
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        sys.stderr.write("run-conductor: the carried skill pin %s is not an ancestor of %s in '%s' — ignored,"
                         " pinning fresh\n" % (carried, head_rev, base))
        return "first"
    os.makedirs(os.path.dirname(record), exist_ok=True)
    with open(record, "w") as out:
        out.write(carried + "\n")
    return "resume"


def pin_mode(record, released):
    """Whether a launch resumes its pinned skill or takes the current one, from the run's files and env.

    | record readable | VERI_NEW_SKILL=1 | released marker | mode       |
    |-----------------|------------------|-----------------|------------|
    | no              | any              | any             | "first"    |
    | yes             | yes              | any             | "env"      |
    | yes             | no               | exists          | "released" |
    | yes             | no               | absent          | "resume"   |
    """
    if not os.access(record, os.R_OK):
        return "first"
    if tunables.get("VERI_NEW_SKILL") == "1":
        return "env"
    return "released" if os.path.exists(released) else "resume"


def skill_snapshot(base, head_rev, record, mode):
    """Which skill snapshot this run executes, decided from `mode` (see pin_mode) and git; no side effect.

    Answers Snapshot(kind, commit, why, message, code), after `git rev-parse head_rev` in `base`:

    | rev-parse | mode            | recorded commit in `base` | kind       | commit        | why        | effects the caller performs |
    |-----------|-----------------|---------------------------|------------|---------------|------------|-----------------------------|
    | fails     | any             | not looked up             | "unpinned" | None          | ""         | message, launch unpinned    |
    | ok        | "resume"        | resolves (cat-file -e)    | "kept"     | the recorded  | ""         | seed .tdd/.gitignore        |
    | ok        | "resume"        | does not resolve          | "refused"  | None          | ""         | seed; message on stderr, code 2 |
    | ok        | "first"         | not looked up             | "first"    | resolved head | "first"    | seed, write pin, consume marker, other pins |
    | ok        | "env"/"released"| not looked up             | "repin"    | resolved head | the mode   | as "first", then the skill-repin event |

    An unreadable recorded file reads as "" (which does not resolve). `message` is the exact stderr text.
    """
    resolved = git(base, "rev-parse", head_rev,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if resolved.returncode != 0:
        return Snapshot("unpinned", None, "", "", 0)
    commit = resolved.stdout.strip()
    if mode != "resume":
        return Snapshot("first" if mode == "first" else "repin", commit, mode, "", 0)
    try:
        with open(record) as recorded_file:
            recorded = recorded_file.read().rstrip("\n")
    except OSError:
        recorded = ""
    if git(base, "cat-file", "-e", recorded + "^{commit}",
           stderr=subprocess.DEVNULL).returncode != 0:
        return Snapshot("refused", None, "", "run-conductor: recorded skill commit '%s' is not in '%s' — refusing to re-pin; "
                        "set VERI_NEW_SKILL=1 to take the new skill\n" % (recorded, base), 2)
    return Snapshot("kept", recorded, "", "", 0)


def snapshot_change(snapshot, issue, extracted):
    """What changed since extraction, against the digest <extracted> held in memory since then (never re-read from
    disk, where a leaf can write): the first entry of <snapshot> that differs, relative to it, `.` when the snapshot
    cannot be read (fail closed); else the digest file's path when that file no longer holds <extracted> (a leaf
    tampered with what supervise.sh trusts); None when nothing changed."""
    try:
        changed = pinned_scripts.first_change(extracted, snapshot)
    except OSError:
        changed = snapshot
    if changed is not None:
        return os.path.relpath(changed, snapshot)
    try:
        recorded = run_pins.snapshot_digest(issue, event.toplevel())
    except (OSError, ValueError):
        recorded = None
    if recorded != pinned_scripts.digest_text(extracted):
        return os.path.abspath(run_dir.issue_file(event.toplevel(), issue, run_pins.SNAPSHOT_DIGEST))
    return None


def keep_pinned_scripts(snapshot, issue):
    kept = run_dir.run_file(run_worktree(issue), "pinned-scripts")
    if is_registered_worktree(issue) and os.path.isdir(os.path.join(snapshot, "scripts")):
        if os.path.lexists(kept):
            pinned_scripts.remove_tree(kept)
        pinned_scripts.copy_writable(os.path.join(snapshot, "scripts"), kept)
        with open(os.path.join(kept, ".gitignore"), "w") as ignore:
            ignore.write("*\n")
        with open(os.path.join(kept, ".snapshot-dir"), "w") as where:
            where.write(snapshot)


def pinned_tmpdir():
    return leg_tmpdir.PINNED_TMPDIR


def free_gb(path):
    return shutil.disk_usage(path).free // 2 ** 30


def prompt(base, issue, commit):
    skill_file = os.path.join(base, "SKILL.md")
    try:
        with open(skill_file, "rb") as skill:
            text = skill.read().rstrip(b"\n")
    except OSError:
        sys.stderr.write("run-conductor: cannot read '%s'\n" % skill_file)
        return None
    text += ("\n\nBase directory for this skill: %s\n" % base).encode()
    if commit is not None:
        text += ("\nPinned skill commit (name it in the plan comment): %s\n" % commit).encode()
    budget = tunables.read("REVISE_BUDGET")
    if budget:
        text += ("\nREVISE_BUDGET=%s\n" % budget).encode()
    return text + ("\nSolve issue #%s by the procedure above.\n" % issue).encode()


def conductor_model():
    return tunables.get("VERI_MODEL_CONDUCTOR", unless_empty=True)


def launch(base, issue, commit, claim=None, **exports):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            body = github.gh_issue_view(issue, "body")
    except github.NoAnswer:
        sys.stderr.write("run-conductor.sh: issue body unavailable, Requirements row IDs unchecked\n")
    else:
        bad = requirements.malformed_row_id(body.split("\n"))
        if bad is not None:
            sys.stderr.write("run-conductor.sh: Requirement row ID is none of <prefix><digits>, <prefix><next> or <prefix><digits><letters><reword>: %s\n" % bad)
            return 2
    text = prompt(base, issue, commit)
    if text is None:
        return 2
    run_state = os.path.join(event.toplevel(), ".tdd")
    os.makedirs(run_state, exist_ok=True)
    sweep_dead_runs(run_state)
    run_tmp = tempfile.mkdtemp(prefix="veri-run-%s-" % issue)
    try:
        with open(run_dir.issue_file(event.toplevel(), issue, "-tmpdir-skill-commit"), "w") as record:
            record.write("%s %d\n" % (run_tmp, os.getpid()))
        run_pins.write_conductor_model(event.toplevel(), issue, conductor_model())
        run_pins.write_launch_env(event.toplevel(), issue, tunables.environment())
        exports["VERI_STATE_LABEL_ISSUE"] = issue
        return conduct(text, issue, dict(os.environ, **exports, TMPDIR=run_tmp), claim)
    finally:
        shutil.rmtree(run_tmp, ignore_errors=True)


def sweep_dead_runs(run_state):
    for name in glob.glob(os.path.join(run_state, "issue-*-tmpdir-skill-commit")):
        try:
            with open(name) as record:
                directory, pid = record.read().split()
            pid = int(pid)
        except (OSError, ValueError):
            sys.stderr.write("run-conductor: cannot read '%s'; leaving its directory alone\n" % name)
            continue
        try:
            os.kill(pid, 0)
        except PermissionError:
            continue
        except ProcessLookupError:
            parent, leaf = os.path.split(os.path.realpath(directory))
            if parent == os.path.realpath(tempfile.gettempdir()) and leaf.startswith("veri-run-"):
                shutil.rmtree(directory, ignore_errors=True)


def conduct(text, issue, env, claim=None):
    strip_session_env(env)
    env.pop("VERI_NEW_SKILL", None)
    env.pop("FORCE_PROMPT_CACHING_5M", None)
    env.pop("VERI_EVENT_STRICT", None)
    env["SHELL"] = env["CLAUDE_CODE_SHELL"] = shutil.which("bash")
    binary = tunables.claude_bin()
    event.state_labels(b"start", env.get("VERI_STATE_LABEL_ISSUE"))
    unread = []
    result = None
    terminated = []
    previous = {sig: signal.signal(sig, handler) for sig, handler in (
        (signal.SIGPIPE, lambda *_: unread.append(True)),
        (signal.SIGTERM, lambda *_: terminated.append(True)),
        (signal.SIGINT, lambda *_: None),
        (signal.SIGHUP, lambda *_: None))}
    try:
        read_end, write_end = os.pipe()
        seen = []
        sys.stdout.flush()
        terminal = os.dup(1)
        reader = threading.Thread(target=relay, args=(os.fdopen(read_end, "rb"), terminal, unread, seen), daemon=True)
        reader.start()
        os.dup2(write_end, 1)
        recorded_read, recorded_write = os.pipe()
        try:
            pid_file = pid_file_path(issue)
            os.makedirs(os.path.dirname(pid_file), exist_ok=True)
            if claim is not None:
                claim.keep_directories()

            def record_pid():
                recorded = pids.record(pid_file, os.getpid())
                os.write(recorded_write, recorded.encode())
                event.mark(run_worktree(issue), event.context(tunables.with_values(VERI_ISSUE=issue)),
                           "conductor-start", ["pid=%d" % os.getpid(), "started=%s" % recorded.split("\n")[1]])
            code = subprocess.run([binary, "-p", "--output-format", "stream-json",
                                   "--verbose"] + context_limits() + [
                                   "--permission-mode", "bypassPermissions", "--model",
                                   conductor_model()],
                                  input=text, env=env, preexec_fn=record_pid).returncode
        finally:
            os.close(recorded_write)
            with os.fdopen(recorded_read, "rb") as recorded:
                ours = recorded.read()
            if ours and claim is not None:
                claim.hand_off()
            try:
                with open(pid_file, "rb") as handle:
                    if handle.read() == ours:
                        os.remove(pid_file)
            except FileNotFoundError:
                pass
            os.dup2(terminal, 1)
            os.close(write_end)
            reader.join()
            os.close(terminal)
        result = seen[-1] if seen else None
    except FileNotFoundError:
        sys.stderr.write("run-conductor: %s: command not found\n" % binary)
        code = 127
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    if terminated:
        return 128 + signal.SIGTERM
    if not past_preflight(issue):
        try:
            os.remove(record_path(issue))
        except FileNotFoundError:
            pass
    if code < 0:
        return 128 - code
    posted = done_posted(issue) if code == 0 and result is not None and not closed(issue) else True
    if posted is None:
        sys.stderr.write("run-conductor: no answer reading the comments of issue #%s; no needs-user bail written\n" % issue)
        return 2
    if not posted:
        if event.mark(run_worktree(issue), event.context(tunables.with_values(VERI_ISSUE=issue)),
                      "bail", ["cause=needs-user"]) != 0:
            return 2
        event.state_labels(b"bail", issue)
        paragraphs = [p for p in result.split("\n\n") if p.strip()]
        quoted = "\n".join("> " + line for line in (paragraphs[-1] if paragraphs else "").strip().splitlines())
        try:
            github.gh_issue_comment(issue, github.published("needs-user: the conductor stopped without a verdict.\n\n" + quoted))
        except github.NoAnswer:
            sys.stderr.write("run-conductor: needs-user comment on issue #%s was refused by GitHub\n" % issue)
    return 141 if code == 0 and unread else code


def relay(stream, terminal, unread, results):
    for raw in stream:
        try:
            os.write(terminal, raw)
        except OSError:
            unread.append(True)
        text = result_text(raw)
        if text is not None:
            results.append(text)


def closed(issue):
    try:
        return bool(run_end.run_end(run_worktree(issue))[2])
    except (OSError, ValueError):
        return False


def done_posted(issue):
    """Whether a trusted (github.trusted_comment) `### ✅ Done` comment was posted since the last resume; None when
    GitHub gave no answer. An untrusted one counts as absent: a stranger's comment cannot silence the bail."""
    since = last_resume(issue)
    number = 1
    while True:
        try:
            thread = json.loads(github.gh_json_page(
                "", "repos/{owner}/{repo}/issues/%s/comments?per_page=100&page=%d" % (issue, number)))
        except (github.NoAnswer, ValueError):
            return None
        bodies = thread.get("comments", []) if isinstance(thread, dict) else thread
        if not isinstance(bodies, list):
            return None
        if any(github.trusted_comment(c) and str(c.get("body", "")).startswith("### ✅ Done")
               and posted_at(c) >= since for c in bodies):
            return True
        if len(bodies) < 100:
            return False
        number += 1


def last_resume(issue):
    try:
        events = event_log.events(run_worktree(issue), "resume", skip_unreadable=True)
    except OSError:
        return 0
    return max([e.get("ts", 0) for e in events if e.get("event") == "resume" and isinstance(e.get("ts"), int)] or [0])


def posted_at(comment):
    try:
        return calendar.timegm(time.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ"))
    except (KeyError, TypeError, ValueError):
        return float("inf")


def run_worktree(issue):
    return run_dir.worktree(event.toplevel(), issue)


def record_path(issue):
    return run_dir.issue_file(event.toplevel(), issue, "-skill-commit")


def is_registered_worktree(issue):
    run_wt = run_worktree(issue)
    top = git(run_wt, "rev-parse", "--show-toplevel",
              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return top.returncode == 0 and top.stdout.rstrip("\n") == os.path.realpath(run_wt)


def past_preflight(issue):
    if is_registered_worktree(issue):
        return True
    branches = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/heads/tdd/%s-*" % issue],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return bool(branches.stdout.rstrip("\n"))


def extract(base, commit, snapshot):
    read_end, write_end = os.pipe()
    try:
        archive = subprocess.Popen(git_argv(base, "archive", commit, "."), stdout=write_end)
        tar = subprocess.Popen(["tar", "-x", "-C", snapshot], stdin=read_end)
    finally:
        os.close(read_end)
        os.close(write_end)
    tar_code, archive_code = tar.wait(), archive.wait()
    return tar_code or archive_code


def verifies(base, ref):
    return git(base, "rev-parse", "-q", "--verify", ref, stdout=subprocess.DEVNULL).returncode == 0


def git(base, *args, **kwargs):
    return subprocess.run(git_argv(base, *args), **kwargs)


def git_argv(base, *args):
    return ["git", "-C", base] + list(args)


def refuse_unpinned(base, why):
    sys.stderr.write("run-conductor: refs/remotes/origin/HEAD is not set in '%s' and %s — refusing to run unpinned\n" % (base, why))
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
