"""baseline-full-tier.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import full_tier_time
import run_dir
import run_pins
import tunables

USAGE = "usage: baseline-full-tier.sh <issue> <full-tier-command>"


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    mode = run_pins.baseline_full_tier(argv[0], run_dir.main_tree_from_files(os.getcwd()))
    if mode is None:
        mode = tunables.get("VERI_BASELINE_FULL_TIER")
    if mode == "reuse":
        record = full_tier_time.record_path()
        times = full_tier_time.read_times(record)
        if argv[1] in times:
            try:
                recorded_at = full_tier_time.read_recorded_at(record).get(argv[1])
            except (OSError, ValueError):
                recorded_at = None
            if recorded_at is not None:
                print("reuse " + times[argv[1]])
                return 0
            sys.stderr.write("baseline-full-tier: timing '%s' again: its recorded time's age is unknown, "
                             "VERI_FULL_TIER_MAX_AGE_DAYS=%s\n" % (argv[1], tunables.get("VERI_FULL_TIER_MAX_AGE_DAYS")))
    print("run")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
