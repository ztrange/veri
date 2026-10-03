"""detect-test-command.sh's computations, run in-process."""
import os


def main(argv):
    if argv in (["--tier"], ["--issue"]):
        return 1
    mk = os.path.join(argv[0], "Makefile")
    if os.path.isfile(mk):
        with open(mk, "rb") as f:
            if f.read().startswith(b"test:"):
                print("make test")
                return 0
    return 3
