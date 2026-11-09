"""baseline-full-tier.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import full_tier_time

USAGE = "usage: baseline-full-tier.sh <issue> <full-tier-command>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    if os.environ.get("VERI_BASELINE_FULL_TIER") == "reuse":
        times = full_tier_time.read_times(full_tier_time.record_path())
        if argv[1] in times:
            print("reuse " + times[argv[1]])
            return 0
    print("run")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
