"""pin-fast-tier.sh's fast-tier run over the tree a pin would commit."""
import os
import subprocess
import sys


def main(argv):
    if not argv or not argv[0]:
        sys.stderr.write("usage: pin-fast-tier.sh <fast-cmd>\n")
        return 2
    os.makedirs(".tdd", exist_ok=True)
    run = subprocess.run(["sh", "-c", argv[0]], stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if run.returncode == 0:
        return 0
    with open(".tdd/verify-pin.reason", "wb") as reason:
        reason.write(run.stdout.rstrip(b"\n") + b"\n")
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
