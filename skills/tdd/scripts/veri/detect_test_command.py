"""detect-test-command.sh's computations, run in-process."""
import os


def main(argv):
    if argv in (["--tier"], ["--issue"]):
        return 1
    if os.path.isfile(os.path.join(argv[0], "Makefile")):
        print("make test")
        return 0
    return 3
