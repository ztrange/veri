"""run-conductor.sh's launch of one conductor, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
# hazard: runs on the python3 it may refuse, so nothing here may need more than Python 3.9.
import contextlib
import glob
import importlib
import io
import os
import paths
import pid_file as pids
import requirements
import re
import calendar
import json
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

sys.dont_write_bytecode = True

from context_limits import context_limits
import event
from event_log import read_events
import github
import launch_floor
import run_end
import tunables
from git import symref_default
from session_env import strip_session_env

USAGE = "usage: run-conductor.sh <issue>"
HELD_REF_LOCK = ("cannot lock ref", "reference already exists")


def main(argv):
    if launch_floor.bash_refusal("run-conductor") or launch_floor.python_refusal("run-conductor"):
        return 2
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    raw_minimum = tunables.read("VERI_MIN_FREE_GB", "20")
    if not re.fullmatch(r"[0-9]+", raw_minimum, re.ASCII):
        sys.stderr.write("run-conductor: VERI_MIN_FREE_GB must be a whole number >= 0, got '%s'\n" % raw_minimum)
        return 2
    minimum = int(raw_minimum)
    for directory in (tempfile.gettempdir(), pinned_tmpdir(), os.getcwd()):
        free = free_gb(directory)
        if free < minimum:
            sys.stderr.write("run-conductor: '%s' has %d GB free, below VERI_MIN_FREE_GB=%d\n" % (directory, free, minimum))
            return 2
    here = paths.scripts_of(__file__)
    base = os.path.dirname(here)
    record = record_path(argv[0])
    readable = os.access(record, os.R_OK)
    resuming = readable and tunables.read("VERI_NEW_SKILL", None) != "1"
    if not resuming:
        try:
            subprocess.run([os.path.join(here, "update-veri.sh")])
        except OSError:
            pass
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
                if subprocess.run(["sleep", tunables.read("VERI_FETCH_RETRY_SLEEP") or "1"]).returncode != 0:
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
    resolved = git(base, "rev-parse", head_rev,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if resolved.returncode == 0:
        commit = resolved.stdout.strip()
        run_state = os.path.join(event.toplevel(), ".tdd")
        os.makedirs(run_state, exist_ok=True)
        seed_path = os.path.join(run_state, ".gitignore")
        if not os.path.exists(seed_path):
            with open(seed_path, "w") as seed:
                seed.write(".gitignore\nissue-*-skill-commit\nissue-*-conductor-model\n")
        if resuming:
            try:
                with open(record) as recorded_file:
                    recorded = recorded_file.read().rstrip("\n")
            except OSError:
                recorded = ""
            if git(base, "cat-file", "-e", recorded + "^{commit}",
                   stderr=subprocess.DEVNULL).returncode != 0:
                sys.stderr.write("run-conductor: recorded skill commit '%s' is not in '%s' — refusing to re-pin; "
                                 "set VERI_NEW_SKILL=1 to take the new skill\n" % (recorded, base))
                return 2
            commit = recorded
        else:
            with open(record, "w") as out:
                out.write(commit + "\n")
            if readable:
                worktree = run_worktree(argv[0])
                os.makedirs(worktree, exist_ok=True)
                if event.mark(worktree, event.context(tunables.with_values(VERI_ISSUE=argv[0])),
                              "skill-repin", ["commit=" + commit]) != 0:
                    return 2
        snapshot = tempfile.mkdtemp()
        try:
            status = extract(base, commit, snapshot)
            if status != 0:
                return status if status <= 3 else 2
            keep_pinned_scripts(snapshot, argv[0])
            return launch(snapshot, argv[0], commit, VERI_SKILL_COMMIT=commit, VERI_SKILL_CLONE=base, VERI_SKILL_REF=head_rev)
        finally:
            keep_pinned_scripts(snapshot, argv[0])
            shutil.rmtree(snapshot, ignore_errors=True)
    sys.stderr.write("run-conductor: no skill commit resolvable from '%s' — running unpinned\n" % base)
    return launch(base, argv[0], None, VERI_SKILL_UNPINNED="1")


def keep_pinned_scripts(snapshot, issue):
    kept = os.path.join(run_worktree(issue), ".tdd", "pinned-scripts")
    if is_registered_worktree(issue) and os.path.isdir(os.path.join(snapshot, "scripts")):
        shutil.rmtree(kept, ignore_errors=True)
        shutil.copytree(os.path.join(snapshot, "scripts"), kept)
        with open(os.path.join(kept, ".gitignore"), "w") as ignore:
            ignore.write("*\n")
        with open(os.path.join(kept, ".snapshot-dir"), "w") as where:
            where.write(snapshot)


def pinned_tmpdir():
    leg = importlib.import_module((__package__ + "." if __package__ else "") + "pytest_leg")
    return leg.PINNED_TMPDIR


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
    return text + ("\nSolve issue #%s by the procedure above.\n" % issue).encode()


def conductor_model():
    return tunables.read("VERI_MODEL_CONDUCTOR") or "opus"


def launch(base, issue, commit, **exports):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            body = github.gh_issue_view(issue, "body")
    except github.NoAnswer:
        sys.stderr.write("run-conductor.sh: issue body unavailable, Requirements row IDs unchecked\n")
    else:
        bad = requirements.malformed_row_id(body.split("\n"))
        if bad is not None:
            sys.stderr.write("run-conductor.sh: Requirement row ID is neither <prefix><digits> nor <prefix><next>: %s\n" % bad)
            return 2
    text = prompt(base, issue, commit)
    if text is None:
        return 2
    run_state = os.path.join(event.toplevel(), ".tdd")
    os.makedirs(run_state, exist_ok=True)
    sweep_dead_runs(run_state)
    run_tmp = tempfile.mkdtemp(prefix="veri-run-%s-" % issue)
    try:
        with open(os.path.join(run_state, "issue-%s-tmpdir-skill-commit" % issue), "w") as record:
            record.write("%s %d\n" % (run_tmp, os.getpid()))
        with open(os.path.join(run_state, "issue-%s-conductor-model" % issue), "w") as record:
            record.write(conductor_model() + "\n")
        return conduct(text, issue, dict(os.environ, **exports, TMPDIR=run_tmp))
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


def conduct(text, issue, env):
    strip_session_env(env)
    env.pop("VERI_NEW_SKILL", None)
    env.pop("FORCE_PROMPT_CACHING_5M", None)
    env["SHELL"] = env["CLAUDE_CODE_SHELL"] = shutil.which("bash")
    binary = os.environ.get("CLAUDE_BIN") or "claude"
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
        try:
            pid_file = os.path.join(run_worktree(issue), ".tdd", "conductor.pid")
            os.makedirs(os.path.dirname(pid_file), exist_ok=True)

            def record_pid():
                with open(pid_file, "w") as handle:
                    handle.write("%d\n%s\n" % (os.getpid(), pids._ps("lstart", os.getpid())))
            code = subprocess.run([binary, "-p", "--output-format", "stream-json",
                                   "--verbose"] + context_limits() + [
                                   "--permission-mode", "bypassPermissions", "--model",
                                   conductor_model()],
                                  input=text, env=env, preexec_fn=record_pid).returncode
        finally:
            try:
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
    if code == 0 and result is not None and not closed(issue) and not done_posted(issue):
        if event.mark(run_worktree(issue), event.context(tunables.with_values(VERI_ISSUE=issue)),
                      "bail", ["cause=needs-user"]) != 0:
            return 2
        paragraphs = [p for p in result.split("\n\n") if p.strip()]
        quoted = "\n".join("> " + line for line in (paragraphs[-1] if paragraphs else "").strip().splitlines())
        try:
            github.gh_issue_comment(issue, "needs-user: the conductor stopped without a verdict.\n\n" + quoted)
        except github.NoAnswer:
            sys.stderr.write("run-conductor: needs-user comment on issue #%s was refused by GitHub\n" % issue)
    return 141 if code == 0 and unread else code


def relay(stream, terminal, unread, results):
    for raw in stream:
        try:
            os.write(terminal, raw)
        except OSError:
            unread.append(True)
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        if isinstance(record, dict) and record.get("type") == "result" and isinstance(record.get("result"), str):
            results.append(record["result"])


def closed(issue):
    try:
        return bool(run_end.run_end(run_worktree(issue))[2])
    except (OSError, ValueError):
        return False


def done_posted(issue):
    since = last_resume(issue)
    number = 1
    while True:
        try:
            page = github.gh_json_page("", "repos/{owner}/{repo}/issues/%s/comments?per_page=100&page=%d" % (issue, number))
            thread = json.loads(page)
        except (github.NoAnswer, ValueError):
            return False
        bodies = thread if isinstance(thread, list) else thread.get("comments", [])
        if any(isinstance(c, dict) and str(c.get("body", "")).startswith("### ✅ Done")
               and posted_at(c) >= since for c in bodies):
            return True
        if len(bodies) < 100:
            return False
        number += 1


def last_resume(issue):
    try:
        events = read_events(os.path.join(run_worktree(issue), ".tdd", "events.jsonl"), skip_unreadable=True)
    except OSError:
        return 0
    return max([e.get("ts", 0) for e in events if e.get("event") == "resume" and isinstance(e.get("ts"), int)] or [0])


def posted_at(comment):
    try:
        return calendar.timegm(time.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ"))
    except (KeyError, TypeError, ValueError):
        return float("inf")


def run_worktree(issue):
    return os.path.join(event.toplevel(), ".tdd", "wt", issue)


def record_path(issue):
    return os.path.join(event.toplevel(), ".tdd", "issue-%s-skill-commit" % issue)


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
