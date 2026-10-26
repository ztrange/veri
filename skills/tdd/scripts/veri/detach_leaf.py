"""detach-leaf.sh's launch, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import signal
import subprocess
import sys
import warnings

import detach

USAGE = "usage: detach-leaf.sh <cmd> [args…]"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            detach.start(argv, subprocess.DEVNULL, None, None, xfsz=signal.SIG_DFL)
    except OSError as error:
        print(f"detach-leaf.sh: {argv[0]}: {error.strerror}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
