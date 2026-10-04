"""run-verdict.sh's logic, run in-process."""
import os
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    verifier = os.path.join(SCRIPTS, "verify.sh")
    if not os.access(verifier, os.X_OK):
        print(f"run-verdict.sh: cannot start the verifier: {verifier} is missing or not executable",
              file=sys.stderr)
        return 2
    args = list(argv)
    while args[:1] == ["--step"]:
        args = args[2:]
    phase = args[0] if args else ""
    reason = f".tdd/verify-{phase}.reason"
    if phase and os.path.isfile(reason):
        open(reason, "w").close()
    os.execv(verifier, [verifier, *argv])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
