"""orchestrate.sh's loop, run in-process."""
import os
import paths
import signal
import subprocess
import sys

import entry
import tunables

try:
    from context_budget import START, watch
    from solvable_issues import solvable_in_scope
except ImportError:
    from .context_budget import START, watch
    from .solvable_issues import solvable_in_scope

SCRIPTS = paths.scripts_of(__file__)
CONDUCTOR = os.path.join(SCRIPTS, "run-conductor.sh")


def main(argv):
    budget = _tunable("VERI_CONDUCTOR_CTX_BUDGET")
    if budget is None:
        return 2
    stop_timeout = _tunable("VERI_CONDUCTOR_STOP_TIMEOUT")
    if stop_timeout is None:
        return 2
    while True:
        code, numbers = solvable_in_scope()
        if code == 3:
            return 0
        if code != 0:
            sys.stderr.write("orchestrate.sh: solvable-issues.sh exited %d; no answer about the solvable set\n"
                             % code)
            return 2
        issue = next((str(n) for n in numbers if n != "" and not _parked(str(n))), "")
        if not issue:
            return 0
        try:
            conductor = _launch(issue)
        except OSError as e:
            sys.stderr.write("orchestrate.sh: cannot start %s: %s\n" % (CONDUCTOR, e.strerror))
            return 2
        try:
            _watch(issue, conductor.stdout, budget)
        finally:
            _stop(conductor.pid)
        _drain(conductor.stdout, stop_timeout)
        if _parked(issue):
            _say("parked %s\n" % issue)


def _tunable(name):
    value, bad = tunables.resolve(name)
    if bad:
        sys.stderr.write("orchestrate.sh: %s must be %s: %s\n" % (name, bad[1], bad[0]))
    return value


def _watch(issue, stream, budget):
    state = START
    for line in stream:
        if not line.endswith(b"\n"):
            return
        state, readings, exceeded = watch(state, [line], budget)
        for context in readings:
            _say("context %s %d\n" % (issue, context))
        if exceeded:
            return


class _StopTimeout(Exception):
    pass


def _drain(stream, timeout):
    def expire(signum, frame):
        raise _StopTimeout
    previous = signal.signal(signal.SIGALRM, expire)
    try:
        signal.setitimer(signal.ITIMER_REAL, timeout)
        try:
            for _ in stream:
                pass
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    except _StopTimeout:
        pass
    signal.signal(signal.SIGALRM, previous)
    stream.close()


def _say(text):
    if sys.stdout is None:
        raise BrokenPipeError
    sys.stdout.write(text)
    sys.stdout.flush()


def _err(text):
    sys.stderr.write(text)
    sys.stderr.flush()


def _launch(issue):
    dispositions = {signal.SIGINT: signal.SIG_IGN, signal.SIGQUIT: signal.SIG_IGN,
                    signal.SIGPIPE: signal.SIG_DFL, signal.SIGXFSZ: signal.SIG_DFL}
    saved = {sig: signal.signal(sig, handler) for sig, handler in dispositions.items()}
    try:
        return subprocess.Popen([CONDUCTOR, issue], start_new_session=True,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, restore_signals=False)
    finally:
        for sig, handler in saved.items():
            signal.signal(sig, handler)


def _stop(pid):
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
    except PermissionError:
        pass


def _parked(issue):
    return os.path.exists(os.path.join(".tdd", "parked", issue + ".md"))


def _main_stdout_gone_exits_2(argv):
    try:
        return main(argv)
    except BrokenPipeError:
        entry.silence_stdout()
        _err("orchestrate.sh: stdout is gone: its reader has exited\n")
        sys.exit(2)


if __name__ == "__main__":
    entry.run(_main_stdout_gone_exits_2, sys.argv[1:])
