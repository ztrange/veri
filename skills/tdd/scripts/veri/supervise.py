"""supervise.sh's watchdog, run in-process."""
import errno
import json
import os
import re
import signal
import subprocess
import sys
import time
from typing import NamedTuple

import entry
import event
import harvest_usage
import preserve_attempt
import tunables
from extract_result import extract
from leaf_log import result_records
from leaf_model import leaf_model
from leaf_role import leaf_role
from ledger import carries_mark, trailing_markers
from pid_file import number_in

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USAGE = "usage: supervise.sh <name> <cmd> [args...]"


class Watch(NamedTuple):
    watched: bool
    timeout: str
    heartbeat: str
    poll: str
    kill_poll: float


def refuse(*lines):
    for line in lines:
        print(line, file=sys.stderr)
    return 2


def not_a_number(var, value):
    if not re.fullmatch(r"[0-9]+", value):
        return refuse(f"supervise: {var} is not a number: '{value}'")
    return None


def numeric_env(var, default):
    value = tunables.read(var, unless_empty=default)
    return value, not_a_number(var, value)


def write_line(path, value):
    with open(path, "w") as f:
        f.write(f"{value}\n")


def discard(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def tolerated(name, action, path, op, *args):
    try:
        op(*args)
    except OSError as error:
        print(f"supervise[{name}]: could not {action} {path}: {error.strerror}", file=sys.stderr)


def truncate(path):
    open(path, "wb").close()


TRAPPED = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


def leaf_dispositions(ignored):
    def preexec():
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
        for sig in TRAPPED:
            if sig not in ignored:
                signal.signal(sig, signal.SIG_DFL)
    return preexec


def awake_seconds():
    command = tunables.read("VERI_AWAKE_CLOCK")
    if command:
        words = command.split()
        try:
            done = captured(*words)
        except OSError as error:
            if error.errno != errno.ENOEXEC:
                raise
            done = captured("/bin/sh", *words)
        return int(done.stdout.rstrip("\n"))
    clock = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)
    return int(time.clock_gettime(clock))


def captured(*args):
    return subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)


def answered(*args):
    done = captured(*args)
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


def now():
    return captured("date", "+%s").stdout.rstrip("\n")


def mtime_of(path):
    m = answered("stat", "-c", "%Y", path)
    if m is None:
        m = answered("stat", "-f", "%m", path)
    if not re.fullmatch(r"[0-9]+", m or ""):
        m = now()
    return m


def signal_tree(pid, sig):
    try:
        os.killpg(pid, sig)
    except OSError:
        try:
            os.kill(pid, sig)
        except OSError:
            pass


def group_alive(pgid):
    return bool(answered("pgrep", "-g", str(pgid)))


def kill_tree(leaf, kill_poll):
    signal_tree(leaf.pid, signal.SIGTERM)
    for _ in range(5):
        if leaf.poll() is not None and not group_alive(leaf.pid):
            return
        time.sleep(kill_poll)
    signal_tree(leaf.pid, signal.SIGKILL)


def pause(poll):
    try:
        secs = float(poll)
    except ValueError:
        print(f"sleep: invalid time interval '{poll}'", file=sys.stderr)
        return
    time.sleep(secs)


def read_log(name, log):
    try:
        with open(log, "rb") as f:
            return f.read()
    except OSError as error:
        print(f"supervise[{name}]: {error}", file=sys.stderr)
        return None


def recover_finished_leaf(name, log, reason):
    data = read_log(name, log)
    if data is None:
        return None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    records = result_records(text.splitlines())
    if not records:
        return None
    outcome = "failure" if records[-1].get("is_error") else "success"
    print(f"supervise[{name}]: killed after the leaf had already written its result ({reason})"
          f" — reporting the leaf's own {outcome}", file=sys.stderr)
    try:
        result = extract(text)
    except Exception:
        return outcome
    with open(log, "ab") as f:
        f.write(b"\n" + result.encode("utf-8"))
    return outcome


def mark(role, env, *fields):
    if not role:
        return
    event.mark("", event.context(dict(env, **dict(pair.split("=", 1) for pair in role.split()))), fields[0], fields[1:])


def refuse_empty_step(role, env, name, reason):
    write_line(f".tdd/{name}.exit", 2)
    mark(role or "actor=supervisor", env, "launch-refused", f"name={name}", f"reason={reason}")
    return refuse(f"supervise: refusing to launch {name}: {reason}")


def preserve_killed_attempt(name, attempt, env):
    issue, step = tunables.read("VERI_ISSUE"), tunables.read("VERI_STEP")
    if not issue or not step:
        return
    if captured("git", "rev-parse", "--verify", "-q", "HEAD").returncode != 0:
        return
    sys.stderr.flush()
    if preserve_attempt.preserve(".", issue, step, name, str(attempt), "stuck", env=env) != 0:
        print(f"supervise[{name}]: could not preserve the stuck attempt"
              f" (issue {issue} step {step} {name} attempt {attempt})", file=sys.stderr)


def still_alive_owner(ownerfile):
    try:
        with open(ownerfile) as f:
            line = f.readline()
    except OSError:
        return None
    fields = line.split(None, 1)
    owner_pid = fields[0] if fields else ""
    owner_name = fields[1].strip() if len(fields) > 1 else ""
    if os.path.exists(f".tdd/{owner_name}.exit") or not re.fullmatch(r"0*[1-9][0-9]*", owner_pid):
        return None
    try:
        os.kill(int(owner_pid), 0)
    except OSError:
        return None
    return owner_pid, owner_name


def attempt_once(started, name, cmd, log, rcfile, leaf_env, preexec, watch):
    watched, timeout, heartbeat, poll, kill_poll = watch
    tolerated(name, "remove", rcfile, discard, rcfile)
    tolerated(name, "truncate", log, truncate, log)
    t0 = now()
    a0 = awake_seconds()
    prev_t, prev_a = int(t0), a0
    leaf = subprocess.Popen(["/bin/sh", "-c", 'log=$1 rc=$2; shift 2; "$@" >"$log" 2>&1; echo $? >"$rc"',
                             "sh", log, rcfile, *cmd], process_group=0, env=leaf_env,
                            restore_signals=False, preexec_fn=preexec)
    started.append(leaf)
    status = reason = ""
    rc = "0"
    seen_at = int(t0)
    if watched:
        last_m = mtime_of(log)
    while True:
        if os.path.isfile(rcfile):
            with open(rcfile) as f:
                rc = f.read().rstrip("\n")
            status = "success" if rc == "0" else "failure"
            break
        t = int(now())
        a = awake_seconds()
        seen_at += (t - prev_t) - (a - prev_a)
        prev_t, prev_a = t, a
        if a - a0 >= int(timeout, 10):
            reason = f"hard timeout {timeout}s exceeded"
        elif watched:
            m = mtime_of(log)
            if m != last_m:
                last_m, seen_at = m, t
            silence = t - seen_at
            if silence > int(heartbeat, 10):
                reason = f"no heartbeat for {silence}s (window {heartbeat}s)"
        if reason:
            status = "killed-stuck"
            kill_tree(leaf, kill_poll)
            break
        pause(poll)
    leaf.wait()
    if status == "killed-stuck":
        outcome = recover_finished_leaf(name, log, reason)
        if outcome is not None:
            status, reason = outcome, ""
    return status, reason, rc, a0


def trap(started, exitfile, kill_poll, ignored):
    def on_signal(*_):
        if started:
            kill_tree(started[-1], kill_poll)
        write_line(exitfile, 2)
        os._exit(2)

    for sig in TRAPPED:
        if sig not in ignored:
            signal.signal(sig, on_signal)


def red_awaits_pass(step):
    last = None
    try:
        with open(".tdd/events.jsonl") as f:
            for text in f:
                try:
                    rec = json.loads(text)
                except ValueError:
                    continue
                if not isinstance(rec, dict) or str(rec.get("step")) != step or rec.get("phase") not in ("red", "pin"):
                    continue
                if rec.get("event") == "launch" and rec.get("phase") == "red":
                    last = False
                elif rec.get("event") == "verdict" and last is not None:
                    last = rec.get("verdict") == "PASS"
    except OSError:
        return False
    return last is False


def ci_repair_step(issue, step):
    try:
        with open(f".tdd/issue-{issue}.md") as f:
            boxes = [t for t in f if re.match(r"\s*- \[.\]", t)]
        if not step.isdigit():
            return carries_mark(trailing_markers(step), "ci-repair") and any(re.sub(r"\s*- \[.\] ", "", t, count=1).startswith(step) for t in boxes)
        return carries_mark(trailing_markers(boxes[int(step) - 1]), "ci-repair")
    except (OSError, ValueError, IndexError):
        return False


def main(argv):
    ignored = {sig for sig in TRAPPED if signal.getsignal(sig) is signal.SIG_IGN}
    if signal.SIGINT not in ignored:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    if not argv or not argv[0]:
        return refuse(USAGE)
    if len(argv) < 2:
        return refuse("supervise: missing <cmd>", USAGE)
    timeout = tunables.read("VERI_TIMEOUT")
    if timeout and (refused := not_a_number("VERI_TIMEOUT", timeout)):
        return refused
    issue = tunables.read("VERI_ISSUE")
    if not timeout and issue:
        settled = f".tdd/issue-{issue}-timeout"
        top = answered("git", "rev-parse", "--show-toplevel")
        if top is not None:
            settled = f"{top}/{settled}"
        if os.path.isfile(settled):
            with open(settled) as f:
                timeout = f.read().rstrip("\n")
            if timeout and (refused := not_a_number(settled, timeout)):
                return refused
            if not timeout or int(timeout, 10) < 1:
                return refuse(f"supervise: {settled} must hold a whole number of seconds >= 1: '{timeout}'")
    timeout = timeout or "900"
    kill_poll, bad = tunables.resolve("VERI_KILL_POLL")
    if bad:
        return refuse(f"supervise: VERI_KILL_POLL must be {bad[1]}: {bad[0]}")
    heartbeat, refused = numeric_env("VERI_HEARTBEAT", "180")
    if refused:
        return refused
    retries, refused = numeric_env("VERI_STUCK_RETRIES", "1")
    if refused:
        return refused
    poll = tunables.read("VERI_POLL", unless_empty="1")
    name = argv[0]
    if top := event.toplevel():
        os.chdir(top)
    tolerated(name, "create", ".tdd", lambda: os.makedirs(".tdd", exist_ok=True))
    log, rcfile, exitfile = f".tdd/{name}.log", f".tdd/{name}.rc", f".tdd/{name}.exit"
    role = model = ""
    watched = not name.startswith("verdict-")
    if watched:
        found = leaf_role(name)
        if found is not None:
            role = " ".join(f"{k}={v}" for k, v in found.items())
        model = leaf_model(name)
    skill_commit = answered("git", "-C", HERE, "rev-parse", "HEAD") or tunables.read("VERI_SKILL_COMMIT") or "unknown"
    leaf_env = {**os.environ}
    leaf_env.update(VERI_LEAF_MODEL=model, VERI_SKILL_COMMIT=skill_commit)
    step = tunables.read("VERI_STEP")
    if "VERI_STEP" in tunables.environment() and not step:
        return refuse_empty_step(role, leaf_env, name, "VERI_STEP is set but empty")
    if "--step" in argv and argv[argv.index("--step") + 1:][:1] == [""]:
        return refuse_empty_step(role, leaf_env, name, "--step is empty")
    if name.startswith("develop-green") and step and red_awaits_pass(step) and not ci_repair_step(issue, step):
        write_line(exitfile, 2)
        return refuse(f"supervise: refusing to launch {name}: step {step} has no verify-red PASS after its latest red leaf")
    ownerfile = ".tdd/leaf.owner"
    owner = still_alive_owner(ownerfile)
    if owner is not None:
        owner_pid, owner_name = owner
        if owner_name != name:
            write_line(exitfile, 2)
        return refuse(f"supervise: refusing to launch {name}: leaf {owner_name or '?'} (pid {owner_pid})"
                      " is still alive in this worktree")
    if watched and not name.startswith("conductor-"):
        tolerated(name, "write", ownerfile, write_line, ownerfile, f"{os.getpid()} {name}")
    mark(role, leaf_env, "launch", f"name={name}", f"cmd={' '.join(argv[1:])}", f"model={model}")
    pidfile = f".tdd/{name}.pid"
    tolerated(name, "write", pidfile, write_line, pidfile, os.getpid())
    discard(exitfile)
    started = []
    preexec = leaf_dispositions(ignored)
    trap(started, exitfile, kill_poll, ignored)
    watch = Watch(watched, timeout, heartbeat, poll, kill_poll)
    tries = 0
    while True:
        status, reason, rc, a0 = attempt_once(started, name, argv[1:], log, rcfile, leaf_env, preexec, watch)
        if status != "killed-stuck":
            break
        preserve_killed_attempt(name, tries + 1, leaf_env)
        if tries >= int(retries, 10):
            break
        tries += 1
        mark(role, leaf_env, "retry", f"cause={reason}")
        print(f"supervise[{name}]: retry {tries}/{retries} after killed-stuck", file=sys.stderr)
    ec = {"success": 0, "failure": 1, "killed-stuck": 2}[status]
    if rc == "2":
        ec = 2
    secs = awake_seconds() - a0
    if watched:
        sys.stderr.flush()
        harvest_usage.harvest(name, leaf_env)
    print(f"supervise[{name}]: {status}" + (f" — {reason}" if reason else ""), file=sys.stderr)
    sys.stderr.flush()
    mark(role, leaf_env, "exit", f"status={ec}", *([f"cause={reason}"] if reason else []), f"secs={secs}")
    data = read_log(name, log) or b""
    try:
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    except BrokenPipeError:
        entry.silence_stdout()
    if number_in(exitfile) is None:
        write_line(exitfile, ec)
    return ec


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
