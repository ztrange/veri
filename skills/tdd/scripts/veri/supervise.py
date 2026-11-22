"""supervise.sh's watchdog, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import errno
import json
import os
import paths
import re
import signal
import subprocess
import sys
import time
from typing import NamedTuple

import entry
import event
import event_log
import full_run_lock
import harvest_usage
import leaf_timeout
import mutation_record
import pinned_scripts
import preserve_attempt
import run_dir
import run_pins
import tunables
from case_reader import is_test_path
from extract_result import extract
from frozen_record import work_tree_hash, pass_marker_current
from leaf_log import result_records
from leaf_model import leaf_model
from leaf_role import leaf_role
from ledger import carries_mark, ledger_steps, step_at, trailing_markers
from pid_file import number_in, ps_field, record, same_start

HERE = paths.scripts_of(__file__)

# A refused launch exits 2, writes one `launch-refused` event (name=, reason=) naming the leaf and
# starts no leaf. Causes: a run-leaf.sh launch whose prompt file is missing or empty, a run-leaf.sh
# launch with no prompt argument, VERI_STEP set but empty, an empty --step value, and a pending
# .tdd/stop of at-leaf or now.
USAGE = "usage: supervise.sh <name> <cmd> [args...]"


class Watch(NamedTuple):
    watched: bool
    timeout: str
    heartbeat: str
    poll: str
    kill_poll: float
    tool_idle: str = "600"


class LeafHolder:
    """What the trap reads to answer a signal: the leaf last started, whether one is being started now, and the
    signal that arrived while it was, raised once the leaf exists so the trap can kill it."""

    def __init__(self):
        self.leaf = None
        self.launching = False
        self.held = None


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


def clock_command(command):
    """A test seam's clock: <command> split on spaces, through /bin/sh when it is not executable; its stdout."""
    words = command.split()
    try:
        done = captured(*words)
    except OSError as error:
        if error.errno != errno.ENOEXEC:
            raise
        done = captured("/bin/sh", *words)
    return done.stdout.rstrip("\n")


def awake_seconds():
    command = tunables.read("VERI_AWAKE_CLOCK")
    if command:
        return int(clock_command(command))
    clock = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)
    return int(time.clock_gettime(clock))


def captured(*args):
    return subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)


def answered(*args):
    done = captured(*args)
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


def now():
    command = tunables.read("VERI_WALL_CLOCK")
    if command:
        return clock_command(command)
    return str(int(time.time()))


def mtime_of(path):
    try:
        return str(int(os.stat(path).st_mtime))
    except OSError:
        return now()


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


def cpu_seconds(field):
    days, _, clock = field.rpartition("-")
    return int(days or "0", 10) * 86400 + sum(float(part) * 60 ** i for i, part in enumerate(reversed(clock.split(":"))))


def tree_cpu_seconds(pid):
    done = captured("ps", "-A", "-o", "pid=,ppid=,time=,comm=")
    rows = [fields for fields in (line.split(None, 3) for line in done.stdout.splitlines()) if len(fields) == 4]
    tree, total = {str(pid)}, 0.0
    for child, parent, cpu, comm in rows:
        if parent in tree:
            tree.add(child)
            if os.path.basename(comm) != "claude":
                total += cpu_seconds(cpu)
    return total if len(tree) > 1 else None


def log_growth(log, offset):
    try:
        with open(log, "rb") as f:
            if os.fstat(f.fileno()).st_size < offset:
                offset = 0
            f.seek(offset)
            data = f.read()
    except OSError:
        return [], offset
    end = data.rfind(b"\n") + 1
    return data[:end].splitlines(), offset + end


def heartbeat_line(line):
    try:
        record = json.loads(line)
    except ValueError:
        return False
    return isinstance(record, dict) and record.get("type") == "tool_progress" and record.get("heartbeat") is True


TOOL_COMMAND_LIMIT = 120


def command_head(command):
    """A command's first line, cut to TOOL_COMMAND_LIMIT characters with a trailing `…` when longer."""
    first = (command.splitlines() or [""])[0]
    return first if len(first) <= TOOL_COMMAND_LIMIT else first[:TOOL_COMMAND_LIMIT] + "…"


def in_flight_tool(text):
    """The last `tool_use` in a stream log with no `tool_result` after it, as `<name>: <command_head> (<secs>s)`, else None."""
    call, answered, secs = None, set(), {}
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if not isinstance(record, dict):
            continue
        if record.get("type") == "tool_progress":
            secs[record.get("parent_tool_use_id")] = record.get("elapsed_time_seconds", 0)
            continue
        message = record.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                call = block
            elif isinstance(block, dict) and block.get("type") == "tool_result":
                answered.add(block.get("tool_use_id"))
    if call is None or call.get("id") in answered:
        return None
    tool_input = call.get("input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    label = f"{call.get('name')}: {command_head(command)}" if isinstance(command, str) else f"{call.get('name')}"
    return f"{label} ({secs.get(call.get('id'), 0)}s)"


def log_in_flight_tool(log):
    """`in_flight_tool` over the log at `log`, None when it cannot be read (read_log already reports that)."""
    try:
        with open(log, "rb") as f:
            return in_flight_tool(f.read().decode("utf-8", errors="replace"))
    except OSError:
        return None


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


def launch_fields(name, cmd, model):
    """The `launch` event's fields: the leaf's name, its command line after the binary and its model, and for a
    verifier leaf the VERI_EFFORT_VERIFIER it was launched at, when that is set (absent otherwise)."""
    fields = [f"name={name}", f"cmd={' '.join(cmd)}", f"model={model}"]
    effort = tunables.get("VERI_EFFORT_VERIFIER")
    if effort and name.startswith("verify-"):
        fields.append(f"effort={effort}")
    return fields


def mark(role, env, *fields):
    if not role:
        return
    event.mark("", event.context(dict(env, **dict(pair.split("=", 1) for pair in role.split()))), fields[0], fields[1:])


def mutation_records():
    return mutation_record.snapshot()


def restore_mutation_records(before, role, env, name):
    after = mutation_records()
    step = re.sub(r"`[^`]*`|\"[^\"]*\"|(?<!\w)'[^']*'(?!\w)", "", tunables.read("VERI_STEP") or "")
    named = re.findall(r"mutation-record:\s*([^\s,;:)]*[^\s,.;:)])", step)
    for path in sorted(set(before) | set(after)):
        if before.get(path) == after.get(path) or path in named:
            continue
        if path in before:
            with open(path, "wb") as f:
                f.write(before[path])
        else:
            os.remove(path)
        mark(role, env, "mutation-record-restored", f"name={name}", f"file={path}")


def production_files():
    ran = subprocess.run(["git", "ls-files", "-m", "-z"], capture_output=True)
    out = {}
    for raw in (ran.stdout or b"").split(b"\0") if ran.returncode == 0 else []:
        path = os.fsdecode(raw)
        if raw and not is_test_path(path) and os.path.isfile(path):
            with open(path, "rb") as f:
                out[path] = f.read()
    return out


def restore_production_files(before, role, env, name):
    for path, content in sorted(before.items()):
        if os.path.isfile(path):
            with open(path, "rb") as f:
                if f.read() == content:
                    continue
        with open(path, "wb") as f:
            f.write(content)
        mark(role, env, "production-file-restored", f"name={name}", f"file={path}")


class Refusal:
    """A launch the gates refused: its stderr lines, and the side effects `perform` makes before printing them.

    `exit_file` is the `.exit` path that gets `2`, or None; `journal` the `(role, env, fields)` of the one event
    `mark` writes, or None. Every refusal exits 2.
    """
    __slots__ = ("lines", "exit_file", "journal")
    code = 2

    def __init__(self, *lines, exit_file=None, journal=None):
        self.lines, self.exit_file, self.journal = lines, exit_file, journal

    def __repr__(self):
        return f"Refusal{self.lines!r} exit_file={self.exit_file!r} journal={self.journal and self.journal[2]!r}"

    def perform(self):
        """Write the `.exit` file, then the event, then the lines to stderr; return the exit code."""
        if self.exit_file is not None:
            write_line(self.exit_file, 2)
        if self.journal is not None:
            role, env, fields = self.journal
            mark(role, env, *fields)
        entry.refuse(*self.lines)
        return self.code


def launch_refused(role, env, name, reason):
    """The refusal that writes `.exit` and a `launch-refused` event (name=, reason=)."""
    return Refusal(f"supervise: refusing to launch {name}: {reason}", exit_file=run_dir.run_file("", f"{name}.exit"),
                   journal=(role or "actor=supervisor", env, ("launch-refused", f"name={name}", f"reason={reason}")))


class Launch(NamedTuple):
    """What the attempt loop reads once every gate has let a leaf launch."""
    name: str
    cmd: list
    role: str
    model: str
    leaf_env: dict
    log: str
    rcfile: str
    exitfile: str
    ownerfile: str
    retries: str
    watch: Watch


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
            line, started = f.readline(), f.readline().strip()
    except OSError:
        return None
    fields = line.split(None, 1)
    owner_pid = fields[0] if fields else ""
    owner_name = fields[1].strip() if len(fields) > 1 else ""
    if os.path.exists(run_dir.run_file("", f"{owner_name}.exit")) or not re.fullmatch(r"0*[1-9][0-9]*", owner_pid):
        return None
    try:
        os.kill(int(owner_pid), 0)
    except OSError:
        return None
    if started and (live := ps_field("lstart", owner_pid)) and live != started:
        return None
    return owner_pid, owner_name


def lock_waiting(marker):
    """Whether the lock-wait marker at <marker> says a pytest leg is waiting for the full-run lock (#3989).

    An empty marker (an older leg's) does; one naming a pid of at least 1 does only while that pid answers `kill 0`
    under the start time on its line 2, as `pid_file.same_start` compares it, both lines taken from the one read, so a marker
    removed after it is judged by what was read and never raises (#4415). A missing, unreadable or malformed one,
    pid 0, or one whose waiter's start time was not recorded or cannot be read now, does not, so a leaf's timers run."""
    try:
        with open(marker, "rb") as f:
            text = f.read()
    except OSError:
        return False
    if not text.strip():
        return True
    lines = text.split(b"\n")
    first = lines[0].strip(b" \t")
    pid = int(first) if re.fullmatch(rb"[0-9]+", first) else 0
    if pid < 1:
        return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        pass
    except (OSError, OverflowError):
        return False
    started = (lines[1:2] or [b""])[0].decode(errors="replace").strip()
    return bool(started) and same_start(started, pid)


def attempt_once(holder, name, cmd, log, rcfile, leaf_env, preexec, watch):
    watched, timeout, heartbeat, poll, kill_poll, _ = watch
    tolerated(name, "remove", rcfile, discard, rcfile)
    tolerated(name, "truncate", log, truncate, log)
    tolerated(name, "remove", leaf_env["PYTEST_LEG_LOCK_WAIT_MARKER"], discard, leaf_env["PYTEST_LEG_LOCK_WAIT_MARKER"])
    t0 = now()
    a0 = awake_seconds()
    prev_t, prev_a = int(t0), a0
    holder.launching, holder.held = True, None
    try:
        leaf = subprocess.Popen(["/bin/sh", "-c", 'log=$1 rc=$2; shift 2; "$@" >"$log" 2>&1; echo $? >"$rc.tmp" && mv "$rc.tmp" "$rc"',
                                 "sh", log, rcfile, *cmd], process_group=0, env=leaf_env,
                                restore_signals=False, preexec_fn=preexec)
    except BaseException:
        holder.launching, holder.held = False, None
        raise
    holder.leaf = leaf
    holder.launching = False
    held, holder.held = holder.held, None
    if held is not None:
        signal.raise_signal(held)
    waitfile = leaf_env["PYTEST_LEG_LOCK_WAIT_MARKER"]
    status = reason = ""
    rc = "0"
    seen_at = int(t0)
    tool_idle = int(watch.tool_idle, 10)
    idle_since, last_cpu, log_offset = a0, None, 0
    if watched:
        last_m = mtime_of(log)
    while True:
        if os.path.isfile(rcfile):
            with open(rcfile) as f:
                rc = f.read().rstrip("\n")
            status = "success" if rc == "0" else "failure"
            break
        if leaf.poll() is not None and not os.path.isfile(rcfile):
            status = reason = "killed-external"
            break
        t = int(now())
        a = awake_seconds()
        seen_at += (t - prev_t) - (a - prev_a)
        if lock_waiting(waitfile):
            a0 += a - prev_a
            idle_since += a - prev_a
            seen_at += a - prev_a
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
            cpu = tree_cpu_seconds(leaf.pid)
            lines, log_offset = log_growth(log, log_offset)
            streamed = any(line.strip() and not heartbeat_line(line) for line in lines)
            if cpu is None or cpu != last_cpu or streamed:
                idle_since, last_cpu = a, cpu
            elif a - idle_since >= tool_idle:
                reason = f"no descendant CPU for {a - idle_since}s (VERI_TOOL_IDLE window {tool_idle}s)"
        if reason:
            status = "killed-stuck"
            kill_tree(leaf, kill_poll)
            tool = log_in_flight_tool(log)
            if tool:
                reason += f"; in-flight tool call {tool}"
            break
        pause(poll)
    leaf.wait()
    tolerated(name, "remove", waitfile, discard, waitfile)
    if status == "killed-stuck":
        outcome = recover_finished_leaf(name, log, reason)
        if outcome is not None:
            status, reason = outcome, ""
    return status, reason, rc, a0


def trap(holder, exitfile, kill_poll, ignored):
    def on_signal(signum, _frame):
        if holder.launching:
            holder.held = signum
            return
        if holder.leaf is not None:
            kill_tree(holder.leaf, kill_poll)
        write_line(exitfile, 2)
        os._exit(2)

    for sig in TRAPPED:
        if sig not in ignored:
            signal.signal(sig, on_signal)


def red_awaits_pass(step):
    last = None
    try:
        for rec in event_log.events(".", "launch", "verdict", skip_unreadable=True):
            if str(rec.get("step")) != step or rec.get("phase") not in ("red", "pin"):
                continue
            if rec.get("event") == "launch" and rec.get("phase") == "red":
                last = False
            elif rec.get("event") == "verdict" and last is not None:
                last = rec.get("verdict") == "PASS"
    except OSError:
        return False
    return last is False


def ledger_step(issue, step, **rule):
    """The Step the reference `step` names in the run's ledger, or None; `rule` is ledger.step_at's.

    OSError, and ValueError for a digit that int() cannot read ("²"), reach the caller.
    """
    with open(run_dir.ledger(".", issue)) as f:
        steps = ledger_steps(f.read())
    return step_at(steps, step, **rule)


def starts_with(reference, text):
    return text.startswith(reference)


def ci_repair_step(issue, step):
    try:
        found = ledger_step(issue, step, text_matches=starts_with)
    except (OSError, ValueError):
        return False
    if not step.isdigit():
        return carries_mark(trailing_markers(step), "ci-repair") and found is not None
    return found is not None and carries_mark(trailing_markers(found.text), "ci-repair")


def step_text(issue, step):
    try:
        found = ledger_step(issue, step)
    except (OSError, ValueError):
        return None
    return None if found is None else found.text


def whole_number_refusal(var, value):
    """The refusal of a `value` that is no whole number (ASCII digits only), or None."""
    if entry.whole_number(value, 0) is None:
        return Refusal(f"supervise: {var} is not a number: '{value}'")
    return None


def not_a_number(var, value):
    """`whole_number_refusal` performed: its line printed and 2, or None."""
    refused = whole_number_refusal(var, value)
    return None if refused is None else refused.perform()


def snapshot_change(issue):
    """Why a leaf of run <issue> may not launch from the skill snapshot supervise runs from, or None: the first
    entry that differs from the digest recorded at extraction (the marker included), a missing digest, or what
    could not be read. Whether supervise runs from a snapshot is the name of the directory it runs from
    (`veri-snapshot-*`, which run-conductor.sh makes), a fact no leaf removes by deleting a file; a skill run from
    any other directory, or an unpinned run (VERI_SKILL_UNPINNED=1), is not checked."""
    snapshot = os.path.dirname(HERE)
    if not issue or tunables.read("VERI_SKILL_UNPINNED") == "1" \
            or not os.path.basename(snapshot).startswith(pinned_scripts.SNAPSHOT_PREFIX):
        return None
    try:
        main = run_dir.main_tree_from_files()
        recorded = run_pins.snapshot_digest(issue, main)
        if recorded is None:
            return f"the skill snapshot {snapshot} has no recorded digest " \
                   f"{run_dir.issue_file(main, issue, run_pins.SNAPSHOT_DIGEST)}"
        changed = pinned_scripts.first_change(pinned_scripts.parse_digest(recorded), snapshot)
    except (OSError, ValueError, RecursionError) as error:
        return f"the skill snapshot {snapshot} could not be checked: {error}"
    return changed and f"the skill snapshot {changed} changed since extraction"


def launch_plan(argv):
    """May this leaf launch, and with what settings: a `Launch`, or the first gate's `Refusal`.

    The gates, in the order they are tried (an input tripping two reports the first). Every refusal exits 2;
    "journal" is one `launch-refused` event (name=, reason=), written after `.exit` and before stderr:

    | # | gate                                                     | stderr (after `supervise: `)              | `.exit` | journal |
    |---|----------------------------------------------------------|-------------------------------------------|---------|---------|
    | 1 | no argument, or an empty name                            | the usage line alone (no prefix)          | no      | no      |
    | 2 | a name and no command                                    | `missing <cmd>`, then the usage line      | no      | no      |
    | 3 | VERI_TIMEOUT set, not a whole number                     | `VERI_TIMEOUT is not a number: '<v>'`     | no      | no      |
    | 4 | no VERI_TIMEOUT, VERI_ISSUE set: the run's timeout pin   | `<pin> is not a number: '<v>'`            | no      | no      |
    |   | (`git rev-parse --show-toplevel` finds it) not a number  |                                           |         |         |
    | 5 | that pin empty or below 1                                | `<pin> must hold a whole number of …`     | no      | no      |
    | 6 | VERI_KILL_POLL invalid                                   | `VERI_KILL_POLL must be <rule>: <v>`      | no      | no      |
    | 7 | VERI_HEARTBEAT, 8 VERI_TOOL_IDLE, 9 VERI_STUCK_RETRIES   | `<VAR> is not a number: '<v>'`            | no      | no      |
    |   | not a whole number (each in that order)                  |                                           |         |         |
    |   | -- then: chdir to the work tree, create .tdd, read the leaf's role and model, `git -C <skill> rev-parse HEAD` |
    | 10| VERI_STEP set but empty                                  | `refusing to launch <n>: VERI_STEP is …`  | yes     | yes     |
    | 11| `--step` with an empty value                             | `refusing to launch <n>: --step is empty` | yes     | yes     |
    | 12| run-leaf.sh with no prompt argument                      | `… run-leaf.sh was given no prompt …`     | yes     | yes     |
    | 13| run-leaf.sh, prompt file missing                         | `… the prompt file <f> does not exist`    | yes     | yes     |
    | 14| run-leaf.sh, prompt file empty                           | `… the prompt file <f> is empty`          | yes     | yes     |
    | 15| `.tdd/stop` holds at-leaf or now                         | `… a stop (<mode>) is pending`            | yes     | yes     |
    | 16| develop-green, the step's latest red has no verify-red   | `… step <s> has no verify-red PASS …`     | yes     | no      |
    |   | PASS, and the step is no `⟦ci-repair⟧` step              |                                           |         |         |
    | 17| verify-red/verify-green, work-tree hash not computable   | `… the work-tree hash could not be …`     | yes     | no      |
    | 18| verify-red/verify-green, no current check-earlier marker | `… step <s> has no current check-earlier …` | yes   | no      |
    | 19| `.tdd/leaf.owner` names a live other leaf                | `… leaf <o> (pid <p>) is still alive …`   | yes     | no      |
    |   | … names a live leaf of this same name                    | the same                                  | no      | no      |
    | 20| run from a `veri-snapshot-*` directory whose entry (the  | `… the skill snapshot <file> changed …`   | yes     | yes     |
    |   | marker included) differs from the run's recorded digest, | `… the skill snapshot <s> has no …`       | yes     | yes     |
    |   | no digest recorded, or unreadable (`snapshot_change`)    | `… the skill snapshot <s> could not …`    | yes     | yes     |

    Gates 1-9 change nothing on disk; from gate 10 on the working directory is the work tree.
    """
    if not argv or not argv[0]:
        return Refusal(USAGE)
    if len(argv) < 2:
        return Refusal("supervise: missing <cmd>", USAGE)
    timeout = tunables.read("VERI_TIMEOUT")
    if timeout and (refused := whole_number_refusal("VERI_TIMEOUT", timeout)):
        return refused
    issue = tunables.read("VERI_ISSUE")
    if not timeout and issue:
        top = answered("git", "rev-parse", "--show-toplevel")
        try:
            timeout = leaf_timeout.settled("" if top is None else top, issue) or timeout
        except leaf_timeout.Malformed as bad:
            if bad.not_a_number:
                return Refusal(f"supervise: {bad.path} is not a number: '{bad.text}'")
            return Refusal(f"supervise: {bad.path} must hold a whole number of seconds >= 1: '{bad.text}'")
    timeout = timeout or tunables.default("VERI_TIMEOUT")
    kill_poll, bad = tunables.resolve("VERI_KILL_POLL")
    if bad:
        return Refusal(f"supervise: VERI_KILL_POLL must be {bad[1]}: {bad[0]}")
    numbers = []
    for var in ("VERI_HEARTBEAT", "VERI_TOOL_IDLE", "VERI_STUCK_RETRIES"):
        value = tunables.get(var, unless_empty=True)
        if refused := whole_number_refusal(var, value):
            return refused
        numbers.append(value)
    heartbeat, tool_idle, retries = numbers
    poll = tunables.read("VERI_POLL", unless_empty="1")
    name = argv[0]
    if top := event.toplevel():
        os.chdir(top)
    tolerated(name, "create", ".tdd", lambda: os.makedirs(".tdd", exist_ok=True))
    log, rcfile, exitfile = (run_dir.run_file("", f"{name}.{ext}") for ext in ("log", "rc", "exit"))
    role = model = ""
    watched = not name.startswith("verdict-")
    if watched:
        found = leaf_role(name)
        if found is not None:
            role = " ".join(f"{k}={v}" for k, v in found.items())
        model = leaf_model(name)
    skill_commit = answered("git", "-C", HERE, "rev-parse", "HEAD") or tunables.read("VERI_SKILL_COMMIT") or "unknown"
    leaf_env = {**os.environ}
    leaf_env.update(VERI_LEAF_MODEL=model, VERI_SKILL_COMMIT=skill_commit,
                    PYTEST_LEG_LOCK_WAIT_MARKER=full_run_lock.wait_marker(os.getpid()))
    step = tunables.read("VERI_STEP")
    if "VERI_STEP" in tunables.environment() and not step:
        return launch_refused(role, leaf_env, name, "VERI_STEP is set but empty")
    if "--step" in argv and argv[argv.index("--step") + 1:][:1] == [""]:
        return launch_refused(role, leaf_env, name, "--step is empty")
    runs_leaf = os.path.basename(argv[1]) == "run-leaf.sh"
    if runs_leaf and len(argv) < 3:
        return launch_refused(role, leaf_env, name, "run-leaf.sh was given no prompt argument")
    if runs_leaf and not os.path.exists(argv[2]):
        return launch_refused(role, leaf_env, name, f"the prompt file {argv[2]} does not exist")
    if runs_leaf and os.path.isfile(argv[2]) and not os.path.getsize(argv[2]):
        return launch_refused(role, leaf_env, name, f"the prompt file {argv[2]} is empty")
    stopfile = run_dir.run_file("", "stop")
    if os.path.isfile(stopfile):
        with open(stopfile) as f:
            if (mode := f.read().strip()) in ("at-leaf", "now"):
                return launch_refused(role, leaf_env, name, f"a stop ({mode}) is pending")
    refusing = f"supervise: refusing to launch {name}: "
    if name.startswith("develop-green") and step and red_awaits_pass(step) and not ci_repair_step(issue, step):
        return Refusal(f"{refusing}step {step} has no verify-red PASS after its latest red leaf", exit_file=exitfile)
    if name.startswith(("verify-red", "verify-green")) and not work_tree_hash():
        return Refusal(f"{refusing}the work-tree hash could not be computed", exit_file=exitfile)
    if name.startswith(("verify-red", "verify-green")) \
            and not ((text := step_text(issue, step) if step else None) is not None and pass_marker_current(text)):
        return Refusal(f"{refusing}step {step or '(unset)'} has no current check-earlier pass marker"
                       " (run tests-frozen.sh check-earlier first)", exit_file=exitfile)
    ownerfile = run_dir.run_file("", "leaf.owner")
    owner = still_alive_owner(ownerfile)
    if owner is not None:
        owner_pid, owner_name = owner
        return Refusal(f"{refusing}leaf {owner_name or '?'} (pid {owner_pid}) is still alive in this worktree",
                       exit_file=exitfile if owner_name != name else None)
    changed = snapshot_change(issue)
    if changed:
        return launch_refused(role, leaf_env, name, changed)
    return Launch(name, argv[1:], role, model, leaf_env, log, rcfile, exitfile, ownerfile, retries,
                  Watch(watched, timeout, heartbeat, poll, kill_poll, tool_idle))


def main(argv):
    ignored = {sig for sig in TRAPPED if signal.getsignal(sig) is signal.SIG_IGN}
    if signal.SIGINT not in ignored:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    plan = launch_plan(argv)
    if isinstance(plan, Refusal):
        return plan.perform()
    name, cmd, role, model, leaf_env, log, rcfile, exitfile, ownerfile, retries, watch = plan
    watched, kill_poll = watch.watched, watch.kill_poll
    if watched and not name.startswith("conductor-"):
        started = ps_field("lstart", os.getpid())
        owner = f"{os.getpid()} {name}\n{started}" if started else f"{os.getpid()} {name}"
        tolerated(name, "write", ownerfile, write_line, ownerfile, owner)
    mark(role, leaf_env, "launch", *launch_fields(name, cmd, model))
    pidfile = run_dir.run_file("", f"{name}.pid")
    tolerated(name, "write", pidfile, record, pidfile, os.getpid())
    discard(exitfile)
    records = mutation_records() if name.startswith(("develop-", "revise-")) else None
    production = production_files() if name.startswith(("develop-red", "revise-red")) else None
    holder = LeafHolder()
    preexec = leaf_dispositions(ignored)
    trap(holder, exitfile, kill_poll, ignored)
    tries = 0
    while True:
        status, reason, rc, a0 = attempt_once(holder, name, cmd, log, rcfile, leaf_env, preexec, watch)
        if status != "killed-stuck":
            break
        preserve_killed_attempt(name, tries + 1, leaf_env)
        if tries >= int(retries, 10):
            break
        tries += 1
        mark(role, leaf_env, "retry", f"cause={reason}", f"name={name}")
        print(f"supervise[{name}]: retry {tries}/{retries} after killed-stuck", file=sys.stderr)
    if records is not None:
        restore_mutation_records(records, role, leaf_env, name)
    if production is not None:
        restore_production_files(production, role, leaf_env, name)
    ec = {"success": 0, "failure": 1, "killed-stuck": 2, "killed-external": 2}[status]
    if rc == "2":
        ec = 2
    secs = awake_seconds() - a0
    if watched:
        sys.stderr.flush()
        harvest_usage.harvest(name, leaf_env)
    print(f"supervise[{name}]: {status}" + (f" — {reason}" if reason else ""), file=sys.stderr)
    sys.stderr.flush()
    mark(role, leaf_env, "exit", f"status={ec}", *([f"cause={reason}"] if reason else []), f"secs={secs}", f"name={name}")
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
