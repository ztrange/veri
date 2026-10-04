"""run-verdict.sh's logic, run in-process."""
import os
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def takes_a_value(word):
    return word in ("--step", "--fast-cmd")


def unopenable(path, error):
    print(f"run-verdict.sh: {path}: {error.strerror}", file=sys.stderr)


def main(argv):
    verifier = os.path.join(SCRIPTS, "verify.sh")
    if not os.access(verifier, os.X_OK):
        print(f"run-verdict.sh: cannot start the verifier: {verifier} is missing or not executable",
              file=sys.stderr)
        return 2
    args = list(argv)
    while args and takes_a_value(args[0]):
        args = args[2:]
    phase = args[0] if args else ""
    if phase:
        stem = f".tdd/verify-{phase}"
        if os.path.isfile(f"{stem}.reason"):
            try:
                open(f"{stem}.reason", "w").close()
            except OSError as e:
                unopenable(f"{stem}.reason", e)
        if os.path.isdir(".tdd"):
            try:
                fd = os.open(f"{stem}.stderr", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
            except OSError as e:
                unopenable(f"{stem}.stderr", e)
            else:
                os.dup2(fd, 2)
                os.close(fd)
    os.execv(verifier, [verifier, *argv])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
