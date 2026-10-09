"""orchestrate.sh's loop, run in-process."""
import math
import os
import re
import signal
import subprocess
import sys

import entry

try:
    from context_budget import START, watch
except ImportError:
    from .context_budget import START, watch

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONDUCTOR = os.path.join(SCRIPTS, "run-conductor.sh")


def main(argv):
    budget = os.environ.get("VERI_CONDUCTOR_CTX_BUDGET") or "120000"
    if not re.fullmatch(r"[0-9]+", budget):
        sys.stderr.write("orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: %s\n" % budget)
        return 2
    raw_stop_timeout = os.environ.get("VERI_CONDUCTOR_STOP_TIMEOUT") or "10"
    try:
        stop_timeout = float(raw_stop_timeout)
        if not math.isfinite(stop_timeout) or stop_timeout <= 0:
            raise ValueError
    except ValueError:
        sys.stderr.write("orchestrate.sh: VERI_CONDUCTOR_STOP_TIMEOUT must be a positive number of seconds: %s\n"
                         % raw_stop_timeout)
        return 2
    while True:
        answer = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE)
        if answer.returncode == 3:
            return 0
        if answer.returncode != 0:
            sys.stderr.write("orchestrate.sh: solvable-issues.sh exited %d; no answer about the solvable set\n"
                             % answer.returncode)
            return 2
        issue = next((n for n in os.fsdecode(answer.stdout).split("\n") if n and not _parked(n)), "")
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


def _watch(issue, stream, budget):
    state = START
    for line in stream:
        if not line.endswith(b"\n"):
            return
        state, readings, exceeded = watch(state, [line], int(budget))
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
