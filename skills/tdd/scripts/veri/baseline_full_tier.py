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
        max_days, bad = tunables.resolve("VERI_FULL_TIER_MAX_AGE_DAYS")
        if bad:
            sys.stderr.write("baseline-full-tier: VERI_FULL_TIER_MAX_AGE_DAYS must be %s, got '%s'\n" % (bad[1], bad[0]))
            return 2
        record = full_tier_time.record_path()
        times = full_tier_time.read_times(record)
        if argv[1] in times:
            age = full_tier_time.age(record, argv[1])
            if age is not None and 0 <= age <= max_days * 86400:
                print("reuse " + times[argv[1]])
                return 0
            sys.stderr.write("baseline-full-tier: timing '%s' again: its recorded time is %s old, "
                             "VERI_FULL_TIER_MAX_AGE_DAYS=%d\n"
                             % (argv[1], "unknown" if age is None or age < 0 else "%d days" % (age // 86400), max_days))
    print("run")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
