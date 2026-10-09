"""run-verdict.sh's logic, run in-process."""
import errno
import os
import signal
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def takes_a_value(word):
    return word in ("--step", "--fast-cmd")


def unopenable(path, error):
    print(f"run-verdict.sh: {path}: {error.strerror}", file=sys.stderr)


def cannot_start(verifier, why):
    print(f"run-verdict.sh: cannot start the verifier: {verifier}{why}", file=sys.stderr)


def main(argv):
    verifier = os.path.join(SCRIPTS, "verify.sh")
    if not os.access(verifier, os.X_OK):
        cannot_start(verifier, " is missing or not executable")
        return 2
    args = list(argv)
    while args and takes_a_value(args[0]):
        args = args[2:]
    phase = args[0] if args else ""
    if phase:
        stem = f".tdd/verify-{phase}"
        reason, filing = f"{stem}.reason", f"{stem}.stderr"
        if os.path.isfile(reason):
            try:
                open(reason, "w").close()
            except OSError as e:
                unopenable(reason, e)
        if os.path.isdir(".tdd"):
            try:
                fd = os.open(filing, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
            except OSError as e:
                unopenable(filing, e)
            else:
                os.dup2(fd, 2)
                os.close(fd)
    if os.environ.get("VERI_SHIM_SET_COERCE") == "1":
        del os.environ["VERI_SHIM_SET_COERCE"]
        os.environ.pop("PYTHONCOERCECLOCALE", None)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
    try:
        os.execv(verifier, [verifier, *argv])
    except OSError as e:
        if e.errno == errno.ENOEXEC:
            os.execvp("bash", ["bash", verifier, *argv])
        else:
            cannot_start(verifier, f": {e.strerror}")
            return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
