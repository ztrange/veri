"""detach-leaf.sh's launch, run in-process."""
import subprocess
import sys

import detach

USAGE = "usage: detach-leaf.sh <cmd> [args…]"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        detach.start(argv, subprocess.DEVNULL, None, None)
    except OSError as error:
        print(f"detach-leaf.sh: {argv[0]}: {error.strerror}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
