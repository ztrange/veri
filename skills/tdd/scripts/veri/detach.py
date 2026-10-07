"""lib/detach.sh's detach_exec, run in-process: one command started as the leader of a new session."""
import signal
import subprocess


def _dispositions():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    for signum in (signal.SIGINT, signal.SIGQUIT, signal.SIGXFSZ):
        signal.signal(signum, signal.SIG_IGN)


def start(argv, stdin, stdout, stderr):
    """Start argv in a session of its own with the given stdio; return its pid without waiting for it."""
    return subprocess.Popen(argv, stdin=stdin, stdout=stdout, stderr=stderr, start_new_session=True,
                            close_fds=False, restore_signals=False, preexec_fn=_dispositions).pid
