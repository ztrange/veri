"""event.sh's mark, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import errno
import glob
import json
import os
import shutil
import subprocess
import sys
import time

import entry
import event_table
import run_dir
import tunables

USAGE = "usage: event.sh <event> [key=value …]\n".encode()
CONTEXT = ((b"issue", b"VERI_ISSUE"), (b"actor", b"VERI_ACTOR"), (b"phase", b"VERI_PHASE"),
           (b"step", b"VERI_STEP"), (b"event", None), (b"attempt", b"VERI_ATTEMPT"),
           (b"skill_commit", b"VERI_SKILL_COMMIT"))
# the events that end a phase, after which the issue's metrics file is rewritten (PRD 035.2, D5)
METRICS_EVENTS = (b"exit", b"step-done", b"bail", b"done", b"stage-end")
STOPPED = (b"candidates-done", b"budget-spent", b"nothing-structural")
REASONS = b", ".join(STOPPED)


def structural_pass_refusal(args):
    transforms = budget = stopped = b""
    for arg in args:
        key, sep, value = arg.partition(b"=")
        if not sep:
            continue
        if key == b"transforms":
            transforms = value
        elif key == b"budget":
            budget = value
        elif key == b"stopped":
            stopped = value
            if stopped not in STOPPED:
                return b"event.sh: structural-pass stopped=" + stopped + b" is not one of " + REASONS
    if not stopped:
        return b"event.sh: structural-pass needs stopped=, one of " + REASONS
    if stopped == b"budget-spent" and transforms != budget:
        return (b"event.sh: structural-pass stopped=budget-spent needs transforms equal to budget, got transforms="
                + transforms + b" budget=" + budget)
    return None


ESCAPES = {0x22: b'\\"', 0x5c: b"\\\\", 0x08: b"\\b", 0x0c: b"\\f", 0x0a: b"\\n", 0x0d: b"\\r",
           0x09: b"\\t"}
LEADS = ((0xE0, 0xC0, 2, 0x1F), (0xF0, 0xE0, 3, 0x0F), (0xF8, 0xF0, 4, 0x07))


def escape(value):
    out = bytearray()
    i = 0
    while i < len(value):
        byte = value[i]
        if byte in ESCAPES:
            out += ESCAPES[byte]
        elif 0x20 <= byte < 0x7f:
            out.append(byte)
        else:
            nbytes, cp = next(((n, byte & m) for mask, lead, n, m in LEADS if byte & mask == lead), (1, byte))
            for k in range(1, nbytes):
                cont = value[i + k] if i + k < len(value) else 0
                cp = (cp << 6) | (cont & 0x3F)
            if cp <= 0xFFFF:
                out += b"\\u%04x" % cp
            else:
                cp -= 0x10000
                out += b"\\u%04x\\u%04x" % (0xD800 | (cp >> 10), 0xDC00 | (cp & 0x3FF))
            i += nbytes - 1
        i += 1
    return bytes(out)


def run_clock(clock):
    path = shutil.which(clock) or clock
    try:
        try:
            return subprocess.run([path], stdout=subprocess.PIPE)
        except OSError as error:
            # hazard: a shell runs an executable with no #! line as a script; exec refuses it with ENOEXEC.
            if error.errno != errno.ENOEXEC:
                raise
            return subprocess.run(["/bin/sh", path], stdout=subprocess.PIPE)
    except (FileNotFoundError, PermissionError):
        return None


def toplevel():
    here = os.getcwd()
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return ""
        here = parent


def line(args, context, ts, awake):
    fields = [(key, context.get(key, b"") if name else args[0]) for key, name in CONTEXT]
    fields += [arg.partition(b"=")[::2] for arg in args[1:]]
    text = b'{"ts": %d, "awake": ' % ts + awake
    for key, value in fields:
        text += b', "' + escape(key) + b'": "' + escape(value) + b'"'
    return text + b"}\n"


def awake_reading():
    clock = tunables.read_bytes("VERI_AWAKE_CLOCK")
    if clock:
        result = run_clock(os.fsdecode(clock))
        if result is None:
            return 2
        if result.returncode != 0:
            return result.returncode if 0 < result.returncode <= 3 else 2
        awake = result.stdout.rstrip(b"\n")
    else:
        awake = b"%d" % time.clock_gettime(getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC))
    return awake


def common_dir(clone):
    git = os.path.join(clone, ".git")
    if os.path.isdir(git):
        return git
    with open(git, "rb") as handle:
        admin = handle.read().decode().partition("gitdir:")[2].strip()
    with open(os.path.join(admin, "commondir"), "rb") as handle:
        return os.path.join(admin, handle.read().decode().strip())


def journal_path(clone, issue):
    try:
        with open(os.path.join(common_dir(clone), "config"), "rb") as handle:
            config = handle.read().decode()
    except OSError:
        return None
    url = ""
    section = ""
    for text in config.splitlines():
        text = text.strip()
        if text.startswith("["):
            section = text
        elif section == '[remote "origin"]' and text.startswith("url") and "=" in text:
            url = text.partition("=")[2].strip()
            break
    url = url.replace(":", "/")
    owner, repo = url.removesuffix(".git").split("/")[-2:] if url.count("/") >= 2 else ("", "")
    if not (owner and repo and issue):
        return None
    home = tunables.read("VERI_HOME") or os.path.expanduser("~/.veri")
    return os.path.join(home, "runs", owner + "-" + repo, issue + ".jsonl")


def journals(who="status.sh"):
    """(path, events) of every shared journal beside the main tree's (journal_path's directory), sorted by path; a
    torn line is skipped and said on stderr as `<who>: skipped torn line <path>:<n>`."""
    sample = journal_path(run_dir.main_tree(missing=""), "0")
    for path in sorted(glob.glob(os.path.join(os.path.dirname(sample), "*.jsonl"))) if sample else []:
        events = []
        with open(path) as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    events.append(json.loads(line))
                except ValueError:
                    print(f"{who}: skipped torn line {path}:{n}", file=sys.stderr)
        yield path, events


def run_name(path):
    """The run a shared journal's path names, `#<n>`."""
    return "#" + os.path.basename(path)[:-len(".jsonl")]

def append_once(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
    try:
        written = os.write(fd, data)
    finally:
        os.close(fd)
    if written != len(data):
        sys.stderr.write("event: short write to journal " + str(path) + "\n")
        sys.exit(2)


def done_fields(path, ts, awake):
    marks = []
    try:
        with open(path, "rb") as handle:
            for text in handle.read().decode(errors="replace").splitlines():
                try:
                    mark = json.loads(text)
                except ValueError:
                    continue
                if isinstance(mark, dict):
                    marks.append(mark)
    except OSError:
        pass
    ending = {"ts": ts, "awake": int(awake) if awake.isdigit() else None}
    opening = next((m for m in reversed(marks) if m.get("event") == "resume"), marks[0] if marks else ending)
    clocked = all("awake" in m for m in marks if "ts" in m) and ending["awake"] is not None
    wall = ts - opening["ts"] if "ts" in opening else None
    span = ending["awake"] - opening["awake"] if clocked and opening.get("awake") is not None else None
    if wall is None:
        wall = span
    elif span is not None and span < wall:
        wall = span
    fields = []
    if wall is not None:
        fields.append(b"wall_seconds=%d" % wall)
    if span is not None:
        fields.append(b"awake_seconds=%d" % span)
    fields.append(b"lane=" + os.fsencode(tunables.get("VERI_LABEL", unless_empty=True)))
    return fields


def write_journal(top, context, text):
    """Append `text` to the issue's journal; the journal's path when it was written, else None."""
    journal = journal_path(top, os.fsdecode(context.get(b"issue", b"")))
    if journal:
        try:
            os.makedirs(os.path.dirname(journal), exist_ok=True)
            append_once(journal, text)
            return journal
        except OSError:
            sys.stderr.write("event: cannot write journal " + journal + "\n")
    return None


def write_metrics(top, issue, journal):
    """Rewrite `<issue>.metrics.json` beside the journal with `metrics.sh <issue> --json`'s object of the journal. A
    failure to compute or write it is one stderr line, never the event's: telemetry never bails a run."""
    target = journal.removesuffix(".jsonl") + ".metrics.json"
    try:
        import metrics
        import run_dir
        metrics.publish(target, issue, journal, run_dir.ledger(top, issue), top)
    except Exception as exc:
        sys.stderr.write("event: cannot write metrics file %s: %s\n" % (target, " ".join(str(exc).split())))


def strict_refusal(args, context=None):
    """Under VERI_EVENT_STRICT=1, why veri/event_table.py does not allow this event and its values (the run context's
    `context` included), or None."""
    context = context or {}
    name = os.fsdecode(args[0])
    if name not in event_table.EVENTS:
        return ("event.sh: VERI_EVENT_STRICT=1 refuses event %s, which veri/event_table.py does not hold; declare it "
                "with the line  %s" % (name, event_table.declaring(name, None)))
    for arg in args[1:]:
        key = os.fsdecode(arg.partition(b"=")[0])
        if key not in event_table.keys(name):
            return ("event.sh: VERI_EVENT_STRICT=1 refuses event %s key %s, which veri/event_table.py does not "
                    "declare for it; declare it with the line  %s" % (name, key, event_table.declaring(name, key)))
    missing = sorted(event_table.required(name) - {os.fsdecode(arg.partition(b"=")[0]) for arg in args[1:]})
    if missing:
        return ("event.sh: VERI_EVENT_STRICT=1 refuses event %s without its required key %s (veri/event_table.py)"
                % (name, missing[0]))
    pairs = [(None, os.fsdecode(key), os.fsdecode(context.get(key, b""))) for key, source in CONTEXT if source]
    pairs += [(name, os.fsdecode(key), os.fsdecode(value))
              for key, _, value in (arg.partition(b"=") for arg in args[1:])]
    for owner, key, value in pairs:
        if not event_table.valid(owner, key, value):
            return ("event.sh: VERI_EVENT_STRICT=1 refuses event %s key %s value %r, which its declared format %s"
                    " (veri/event_table.py) does not accept; fix the value, or the format in the line  %s"
                    % (name, key, value, event_table.stated(owner, key), event_table.declaring(owner, None)))
    return None


def append(directory, context, event, fields=(), ts=None):
    args = [os.fsencode(event)] + [os.fsencode(field) for field in fields]
    context = {os.fsencode(key): os.fsencode(value) for key, value in context.items()}
    if not args[0]:
        sys.stderr.buffer.write(USAGE)
        return 2
    if args[0] == b"structural-pass":
        refusal = structural_pass_refusal(args[1:])
        if refusal:
            sys.stderr.buffer.write(refusal + b"\n")
            return 2
    refusal = strict_refusal(args, context) if tunables.read("VERI_EVENT_STRICT") == "1" else None
    if refusal:
        sys.stderr.write(refusal + "\n")
        return 2
    top = os.fspath(directory) or toplevel()
    tdd = os.path.join(top, ".tdd")
    os.makedirs(tdd, exist_ok=True)
    ts = int(time.time()) if ts is None else ts
    awake = awake_reading()
    if isinstance(awake, int):
        return awake
    if args[0] in (b"done", b"metrics-cut"):
        args += done_fields(tdd + "/events.jsonl", ts, awake.decode())
    text = line(args, context, ts, awake)
    append_once(tdd + "/events.jsonl", text)
    journal = write_journal(top, context, text)
    if journal and args[0] in METRICS_EVENTS:
        write_metrics(top, os.fsdecode(context[b"issue"]), journal)
    state_labels(args[0], tunables.read("VERI_STATE_LABEL_ISSUE"))
    return 0


def state_labels(event, issue):
    """Mirror a bail, a stop, a resume or a launch (start) onto issue <issue>'s labels; no issue, no call;
    a refusal is named, never fatal."""
    if not issue:
        return
    import github  # pulls run_records (about 20 ms), and only a labelled run state needs it
    try:
        if event == b"bail":
            add_state_label(issue, "bailed")
            github.gh_issue_remove_label(issue, "pr-ready")
        elif event == b"stop":
            add_state_label(issue, "stopped")
        elif event == b"resume":
            github.gh_issue_remove_label(issue, "bailed")
            github.gh_issue_remove_label(issue, "stopped")
            opt_in = tunables.get("VERI_LABEL")
            github.gh_issue_add_label(issue, tunables.taken_label(opt_in))
            github.gh_issue_remove_label(issue, opt_in)
        elif event == b"start":
            github.gh_issue_remove_label(issue, "bailed")
            github.gh_issue_remove_label(issue, "stopped")
            github.gh_issue_remove_label(issue, "pr-ready")
    except github.NoAnswer:
        sys.stderr.write("event: no answer from gh labelling #%s's run state\n" % issue)


def add_state_label(issue, label):
    """Label <issue> <label> only when the repository has that label: REST's add-labels call would create a missing
    one, and veri creates no state label (ready-check.sh reports it).
    A missing label is one stderr line, never fatal."""
    import github
    if not github.gh_label_exists(label):
        sys.stderr.write("event: the repository has no `%s` label, so #%s is not labelled %s "
                         "(ready-check.sh reports it)\n" % (label, issue, label))
        return
    github.gh_issue_add_label(issue, label)


def context(environ):
    return {os.fsdecode(key): environ.get(os.fsdecode(name), "") for key, name in CONTEXT if name}


def mark(directory, context, event, fields=(), ts=None):
    try:
        return append(directory, context, event, fields, ts)
    except Exception as exc:
        sys.stderr.flush()
        os.write(2, entry.refusal(main, exc).encode())
        return 2
    finally:
        sys.stderr.flush()


def stage_mark(directory, run_context, name, fields):
    """`mark`, and a SystemExit it lets through (append_once's short write exits 2) kept from ending the stage's caller:
    inside `stage`'s finally it would replace the body's exit code. Its stderr line is already written."""
    try:
        mark(directory, run_context, name, fields)
    except SystemExit:
        pass


def stage(name, body, directory="", run_context=None):
    """Run `body()`, which returns an exit code, as stage `name` (D13): `stage-start stage=<name>` before it and
    `stage-end stage=<name> status=<code> secs=<whole seconds>` after it, on every exit; a body that raises ends its
    stage with status 2 and its error is raised on, and so does a code outside the four exit codes (a script's 4, git's
    128): no answer could be obtained, the code itself returned unchanged. Each line goes through `mark`, so a line that
    cannot be written is one stderr line and never changes what the body returns: telemetry never bails a run. With no
    `run_context`, the environment's, its issue `VERI_STATE_LABEL_ISSUE` when `VERI_ISSUE` is unset: the conductor
    exports that to every command it runs, so a script's stage reaches its issue's journal. A directory with no `.tdd/`
    runs the body unmarked: a stage never creates it, as its absence is state a body may read (wait-ci.sh's marks)."""
    if not os.path.isdir(os.path.join(os.fspath(directory) or toplevel(), ".tdd")):
        return body()
    if run_context is None:
        run_context = context(os.environ)
        run_context["issue"] = run_context["issue"] or tunables.read("VERI_STATE_LABEL_ISSUE")
    stage_mark(directory, run_context, "stage-start", ["stage=" + name])
    began = time.monotonic()
    status = 2
    try:
        status = body()
        return status
    finally:
        stage_mark(directory, run_context, "stage-end",
             ["stage=" + name, "status=%d" % (status if status in (0, 1, 2, 3) else 2),
              "secs=%d" % (time.monotonic() - began)])


def main(argv):
    if not argv:
        sys.stderr.buffer.write(USAGE)
        return 2
    context = {key: tunables.read_bytes(name) for key, name in CONTEXT if name}
    context[b"issue"] = context[b"issue"] or tunables.read_bytes("VERI_STATE_LABEL_ISSUE")
    return append("", context, argv[0], argv[1:])


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
