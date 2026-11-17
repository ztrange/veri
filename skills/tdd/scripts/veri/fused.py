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


def call(name, *args, **kw):
    """Run one inner call (run_script's keywords) and print a line naming it and its exit code, then its stdout, and
    pass its stderr through unchanged (FC1); what it sends to a file is not printed."""
    code, out, err = run_script(name, *args, **kw)
    sys.stdout.write(shown(name, *args, **kw) + " exit " + str(code) + "\n" + out)
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
        return dict(line.split("=", 1) for line in f.read().splitlines() if "=" in line)
