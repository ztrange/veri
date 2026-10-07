"""orchestrate.sh's loop, run in-process."""
import os
import re
import signal
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONDUCTOR = os.path.join(SCRIPTS, "run-conductor.sh")


def main(argv):
    budget = os.environ.get("VERI_CONDUCTOR_CTX_BUDGET") or "120000"
    if not re.fullmatch(r"[0-9]+", budget):
        sys.stderr.write("orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: %s\n" % budget)
        return 2
    while True:
        answer = subprocess.run([os.path.join(SCRIPTS, "solvable-issues.sh")], stdout=subprocess.PIPE)
        if answer.returncode == 3:
            return 0
        if answer.returncode != 0:
            sys.stderr.write("orchestrate.sh: solvable-issues.sh exited %d; no answer about the solvable set\n"
                             % answer.returncode)
            return 2
        issue = next((n for n in os.fsdecode(answer.stdout).rstrip("\n").split("\n") if not _parked(n)), "")
        if not issue:
            return 0
        try:
            conductor = _launch(issue)
        except OSError as e:
            sys.stderr.write("orchestrate.sh: cannot start %s: %s\n" % (CONDUCTOR, e.strerror))
            continue
        for _ in conductor.stdout:
            pass
        _stop(conductor.pid)
        if _parked(issue):
            sys.stdout.write("parked %s\n" % issue)
            sys.stdout.flush()


def _launch(issue):
    ignored = (signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGXFSZ)
    saved = {sig: signal.signal(sig, signal.SIG_IGN) for sig in ignored}
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
