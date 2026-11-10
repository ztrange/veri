"""baseline-full-tier.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import full_tier_time
import tunables

USAGE = "usage: baseline-full-tier.sh <issue> <full-tier-command>"


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    pin = os.path.join(os.path.dirname(full_tier_time.record_path()), "issue-%s-baseline-full-tier" % argv[0])
    mode = tunables.read("VERI_BASELINE_FULL_TIER", "run")
    if os.path.exists(pin):
        with open(pin) as f:
            mode = f.read().strip()
    if mode == "reuse":
        times = full_tier_time.read_times(full_tier_time.record_path())
        if argv[1] in times:
            print("reuse " + times[argv[1]])
            return 0
    print("run")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
