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


def call(name, *args, cwd=None, env=None, into=None):
    """Run one inner call and print a line naming it and its exit code, then its stdout, and pass its stderr through
    unchanged (FC1). With <into>, a path under <cwd>, its stdout goes to that file instead, as `> <into>` would send it,
    and the line names the redirection."""
    code, out, err = run_script(name, *args, cwd=cwd, env=env)
    if into is not None:
        with open(os.path.join(cwd or ".", into), "w") as f:
            f.write(out)
    shown = label(name, *args) + (" > " + into if into is not None else "")
    sys.stdout.write(shown + " exit " + str(code) + "\n" + (out if into is None else ""))
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
        shown = label(name, *args) + (" > " + kw["into"] if kw.get("into") is not None else "")
        raise Stop(where, shown + " exit " + str(code), code)
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
