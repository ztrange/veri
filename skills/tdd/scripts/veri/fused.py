"""What every fused script after preflight shares (PRD 027 FC1-FC4, FC10): run an inner call from this skill's own
scripts directory, print it, and stop at the first call that is not clean."""
import contextlib
import os
import subprocess
import sys

SCRIPTS = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def script(name):
    """<name> in this skill's own scripts directory, never from PATH or another clone (FC10)."""
    return os.path.join(SCRIPTS, name)


def run_script(name, *args, cwd=None, env=None, stdin=None, out=None, err=None, run=subprocess.run):
    """(code, stdout, stderr) of one process. <stdin> is text fed to it; <out> and <err>, paths under <cwd>, take its
    stdout and stderr as `> <out>` and `2> <err>` would, a process it leaves running included, and come back as "".
    <run> starts it, subprocess.run's signature (github.bounded for gh)."""
    def opened(path):
        return open(os.path.join(cwd or ".", path), "w") if path is not None else subprocess.PIPE
    with contextlib.ExitStack() as files:
        stdout, stderr = (files.enter_context(f) if f is not subprocess.PIPE else f for f in map(opened, (out, err)))
        proc = run([name, *args], input=stdin, stdout=stdout, stderr=stderr, text=True, cwd=cwd, env=env)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def label(name, *args):
    """The call as one line: its script's name and its arguments, a newline inside one written `\\n`."""
    return " ".join([os.path.basename(name), *(arg.replace("\n", "\\n") for arg in args)])


def shown(name, *args, out=None, err=None, stdin=None, **_):
    """The line naming a call: its script's name, its arguments and any redirection."""
    return label(name, *args) + (" > " + out if out is not None else "") + (" 2> " + err if err is not None else "")


# Whether call() prints an inner call's stdout after the line naming it; quiet() turns it off.
ECHO = [True]


@contextlib.contextmanager
def quiet():
    """Within it, call() prints only the line naming each call, never its stdout (PRD 038.9 RVS14)."""
    ECHO.append(False)
    try:
        yield
    finally:
        ECHO.pop()


def call(name, *args, **kw):
    """Run one inner call (run_script's keywords) and print a line naming it and its exit code, then its stdout unless
    quiet(), and pass its stderr through unchanged (FC1); what it sends to a file is not printed."""
    code, out, err = run_script(name, *args, **kw)
    sys.stdout.write(shown(name, *args, **kw) + " exit " + str(code) + "\n" + (out if ECHO[-1] else ""))
    sys.stderr.write(err)
    return code, out, err


class Stop(Exception):
    """The first outcome that is not clean: where it is stated, what it was, and the inner code (FC3)."""

    def __init__(self, where, what, code):
        super().__init__(where, what, code)
        self.where, self.what, self.code = where, what, code


def checked(where, name, *args, ok=(0,), **kw):
    """call(), raising Stop at <where> on an exit outside <ok>; its stdout otherwise."""
    code, out, _ = call(name, *args, **kw)
    if code not in ok:
        raise Stop(where, shown(name, *args, **kw) + " exit " + str(code), code)
    return out


def stopped(stop):
    """Print the `stopped at <where> <what>` last line; the exit code: the inner code when neither 0 nor 3, else 1."""
    sys.stdout.write("stopped at %s %s\n" % (stop.where, stop.what))
    return stop.code if stop.code not in (0, 3) else 1


def settled_file(wt, n, name):
    return os.path.join(wt, ".tdd", "issue-%s-%s" % (n, name))


def settle(wt, n, name, lines):
    """Write <lines> to .tdd/issue-<n>-<name> in the worktree, one key=value each, and print them last (FC14)."""
    text = "".join(line + "\n" for line in lines)
    with open(settled_file(wt, n, name), "w") as f:
        f.write(text)
    sys.stdout.write(text)
    return 0


def read_settled(path):
    """{key: value} of a settled file; OSError when it cannot be read."""
    with open(path) as f:
        return read_lines(f.read().splitlines())


def read_lines(lines):
    """{key: value} of a settled file's lines, the last value of a key repeated."""
    return dict(line.split("=", 1) for line in lines if "=" in line)


def conductor(wt):
    """The conductor a call runs under, as <wt>'s `.tdd/conductor.pid` names it: {"pid", "started"}; None without one."""
    try:
        with open(os.path.join(wt, ".tdd", "conductor.pid")) as f:
            lines = f.read().split("\n")
    except OSError:
        return None
    return {"pid": lines[0].strip(), "started": (lines[1:] or [""])[0].strip()}


# What the fused halves of a step (PRD 027.4-027.6) share beyond the calls above: their entry, their leaf launches
# and waits (FC5-FC8), the reading of a leaf's report (FC2) and the tree's changed paths; their inputs and the step's
# cost check (RH4) are in fused_step.

class Waiting(Exception):
    """A leaf's wait whose slice ran out (FC5): the leaf it waits on."""

    def __init__(self, name):
        super().__init__(name)
        self.name = name


def entry(argv, name, run):
    """A fused half's main: <run>(n) for `<name> <n>`; its usage and 2 on other arguments, the `stopped at` line on
    a Stop, the `waiting on` line and 3 on a Waiting."""
    if len(argv) != 1 or not argv[0].isdigit():
        sys.stderr.write("usage: %s <n>\n" % name)
        return 2
    try:
        return run(argv[0])
    except Stop as stop:
        return stopped(stop)
    except Waiting as waiting:
        sys.stdout.write("waiting on %s\n" % waiting.name)
        return 3


def step_env(n, step, **more):
    """The run context a mark or a leaf launch carries (*Launching a leaf*): VERI_ISSUE and VERI_STEP."""
    import tunables
    return tunables.with_values(VERI_ISSUE=n, VERI_STEP=step, **more)


def mark(where, wt, n, step, *fields, **more):
    """A conductor mark, `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP=<step> event.sh <fields>`."""
    checked(where, script("event.sh"), *fields, cwd=wt, env=step_env(n, step, VERI_ACTOR="conductor", **more))


def wait_record(wt, n, owner):
    return os.path.join(wt, ".tdd", "issue-%s-%s-wait" % (n, owner))


def save_wait(wt, n, owner, at, values):
    """Record that <at>'s leaf was launched, with the conductor it runs under (FC7) and the values settled so far,
    so a second call only waits again (FC6)."""
    import json
    with open(wait_record(wt, n, owner), "w") as f:
        json.dump({"conductor": conductor(wt), "at": at, "values": values}, f)


def load_wait(wt, n, owner, step=None):
    """(at, values) a first call recorded before its wait ran out; None when there is no usable record. A record
    another conductor wrote is removed: its leaf is a dead run's (FC7)."""
    import json
    try:
        with open(wait_record(wt, n, owner)) as f:
            record = json.load(f)
        at, values, theirs = record["at"], record["values"], record.get("conductor")
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if theirs != conductor(wt):
        os.remove(wait_record(wt, n, owner))
        return None
    if step is not None and record.get("step", step) != step:
        return None
    return at, values


def launch(where, wt, name, command, *args, env, out, err, clear=()):
    """A leaf under *Launching a leaf* (FC8): the stop check, the completion files and <clear> removed, then
    detach-leaf.sh supervise.sh <name> <command> <args>, its stdout to <out> and its stderr to <err>."""
    code, said, _ = call(script("stop-requested.sh"), cwd=wt)
    mode = said.strip()
    if code not in (0, 3) or (code == 0 and mode != "at-ledger"):
        raise Stop(where, "stop-requested.sh exit %d%s" % (code, " " + mode if mode else ""), code)
    for path in (".tdd/%s.exit" % name, ".tdd/%s.pid" % name) + tuple(clear):
        with contextlib.suppress(FileNotFoundError):
            os.remove(os.path.join(wt, path))
    checked(where, script("detach-leaf.sh"), script("supervise.sh"), name, script(command), *args, cwd=wt, env=env,
            out=out, err=err)


def wait(wt, n, owner, name, rejected_step=None):
    """wait-leaf.sh <name>: raises Waiting on 3, the record kept; else removes <owner>'s wait record and returns the
    leaf's code. With <rejected_step>, a verifier's REJECT (`verdict-<phase>` exit 1) moves the record to owner
    `<owner>-rejected` instead, naming that step, so revise.sh can hand a phase stage's values back to it (PRD 038.9)
    and a record another step left is known stale (S1); revise.sh's own wait passes none, since its REJECT goes on to
    its next attempt."""
    import json
    code = call(script("wait-leaf.sh"), name, cwd=wt)[0]
    if code == 3:
        raise Waiting(name)
    with contextlib.suppress(FileNotFoundError):
        if rejected_step is not None and code == 1 and name.startswith("verdict-"):
            with open(wait_record(wt, n, owner)) as f:
                record = dict(json.load(f), step=rejected_step)
            with open(wait_record(wt, n, owner + "-rejected"), "w") as f:
                json.dump(record, f)
        os.remove(wait_record(wt, n, owner))
    return code


def report(where, wt, path, *keys, every=False):
    """{key: its last value, or None; with <every>, the list of its values} of the report extract-result.sh reads from
    <path> under the worktree (a leaf's .out, or a verifier's .log), read through report.report_values. Only the line
    naming the call and its exit is printed, never the report (FC2); an exit but 0, or no such file, stops at <where>
    with exit 2."""
    from report import report_values
    shown_as = "extract-result.sh < " + path
    try:
        with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
            stream = f.read()
    except OSError:
        raise Stop(where, "no " + path, 2)
    code, out, _ = run_script(script("extract-result.sh"), cwd=wt, stdin=stream)
    sys.stdout.write(shown_as + " exit %d\n" % code)
    if code != 0:
        raise Stop(where, shown_as + " exit %d" % code, 2 if code in (0, 3) else code)
    return {key: report_values(out, key, occurrence="every" if every else "last", splitlines=True, strip=True)
            for key in keys}


def changed_paths(where, wt):
    """The paths `git status --porcelain --untracked-files=all` lists, each file in a new directory by its own path and
    a rename by its new path."""
    listed = checked(where, "git", "status", "--porcelain", "--untracked-files=all", cwd=wt).splitlines()
    return [line[3:].split(" -> ")[-1].strip('"') for line in listed if line.strip()]
