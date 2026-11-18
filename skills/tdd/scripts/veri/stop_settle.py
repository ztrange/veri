"""stop-settle.sh's computation, run in-process: a stop (STOPPING.md steps 1-6) settled in one call (PRD 038.5)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused_step

NAME = "stop-settle"
USAGE = "usage: stop-settle.sh <n> <mode> [--drop]"
MODES = ("at-ledger", "at-leaf", "now")


def main(argv):
    if len(argv) not in (2, 3) or not argv[0].isdigit() or argv[1] not in MODES or argv[2:] not in ([], ["--drop"]):
        sys.stderr.write(USAGE + "\n")
        return 2
    given = fused_step.inputs(NAME + ".sh", argv[0])
    if given is None:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
