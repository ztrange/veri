"""What every fused script after preflight shares (PRD 027 FC1-FC4, FC10): run an inner call from this skill's own
scripts directory, print it, and stop at the first call that is not clean."""
import os
import subprocess
import sys

SCRIPTS = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def script(name):
    """<name> in this skill's own scripts directory, never from PATH or another clone (FC10)."""
    return os.path.join(SCRIPTS, name)


def run_script(name, *args, cwd=None, env=None):
    proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def label(name, *args):
    return " ".join([os.path.basename(name), *args])


def call(name, *args, cwd=None, env=None, shown=None):
    """Run one inner call and print a line naming it (<shown> when given) and its exit code, then its stdout, and pass
    its stderr through unchanged (FC1)."""
    code, out, err = run_script(name, *args, cwd=cwd, env=env)
    sys.stdout.write((shown or label(name, *args)) + " exit " + str(code) + "\n" + out)
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
        raise Stop(where, label(name, *args) + " exit " + str(code), code)
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
