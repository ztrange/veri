"""One command started as the leader of a new session."""
import functools
import signal
import subprocess


def _dispositions(xfsz):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    for signum in (signal.SIGINT, signal.SIGQUIT):
        signal.signal(signum, signal.SIG_IGN)
    signal.signal(signal.SIGXFSZ, xfsz)


def start(argv, stdin, stdout, stderr, xfsz=signal.SIG_IGN):
    """Start argv in a session of its own with the given stdio; return its pid without waiting for it."""
    return subprocess.Popen(argv, stdin=stdin, stdout=stdout, stderr=stderr, start_new_session=True,
                            close_fds=False, restore_signals=False,
                            preexec_fn=functools.partial(_dispositions, xfsz)).pid
