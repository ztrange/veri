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
        issue = next((n for n in os.fsdecode(answer.stdout).split("\n") if n and not _parked(n)), "")
        if not issue:
            return 0
        try:
            conductor = _launch(issue)
        except OSError as e:
            sys.stderr.write("orchestrate.sh: cannot start %s: %s\n" % (CONDUCTOR, e.strerror))
            return 2
        _watch(issue, conductor.stdout, budget)
        _stop(conductor.pid)
        if _parked(issue):
            _say("parked %s\n" % issue)


def _watch(issue, stream, budget):
    context, step_done = 0, False
    for line in stream:
        if not line.endswith(b"\n"):
            return
        if step_done and b'"type":"user"' in line:
            if _greater(context, budget):
                return
            step_done = False
        if b'"type":"assistant"' not in line:
            continue
        if b"event.sh step-done" in line:
            step_done = True
        read = re.search(rb'"cache_read_input_tokens":([0-9]+)', line)
        creation = re.search(rb'"cache_creation_input_tokens":([0-9]+)', line)
        if read and creation:
            context = int(read.group(1)) + int(creation.group(1))
            _say("context %s %d\n" % (issue, context))


def _say(text):
    if sys.stdout is None:
        raise BrokenPipeError
    sys.stdout.write(text)
    sys.stdout.flush()


def _err(text):
    sys.stderr.write(text)
    sys.stderr.flush()


def _greater(context, budget):
    if budget.startswith("0") and re.search("[89]", budget):
        _err('orchestrate.sh: %s: value too great for base (error token is "%s")\n' % (budget, budget))
        return False
    return context > int(budget, 8 if budget.startswith("0") else 10)


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
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:
        if sys.stdout is not None:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        _err("orchestrate.sh: stdout is gone: its reader has exited\n")
        sys.exit(2)
