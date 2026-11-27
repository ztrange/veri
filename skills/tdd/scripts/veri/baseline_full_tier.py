"""baseline-full-tier.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import hashlib
import json
import os
import sys

import full_tier_time
import run_dir
import run_pins
import tunables

USAGE = ("usage: baseline-full-tier.sh <issue> <full-tier-command>\n"
         "       baseline-full-tier.sh --green <issue> <tree> <fast-command> <full-command>\n"
         "       baseline-full-tier.sh --record-green <issue> <tree> <fast-command> <full-command>")


def green_path():
    """The record of green baselines on this machine, in the main working tree's `.tdd/`."""
    return os.path.join(run_dir.main_tree_from_files(os.getcwd()), ".tdd", "baseline-green.json")


def digest_of(path):
    """The sha256 of the file's bytes, or None when it is absent."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def green_key(issue, tree, fast, full):
    """What a green baseline is recorded under: the tested tree, both commands, the run's skill commit pin and a hash of
    the dev venv lock, the last two read from the main checkout."""
    main = run_dir.main_tree_from_files(os.getcwd())
    pin = digest_of(run_dir.issue_file(main, issue, "-skill-commit"))
    lock = digest_of(os.path.join(main, "requirements-dev.txt"))
    return hashlib.sha256(json.dumps([tree, fast, full, pin, lock]).encode()).hexdigest()


def read_green(path):
    """The recorded {key: verdict}; {} when the record is absent or is not such a mapping (fail closed)."""
    try:
        with open(path) as f:
            record = json.load(f)
    except (OSError, ValueError):
        return {}
    return record if isinstance(record, dict) else {}


def green(argv):
    """`--green` prints skip when a green baseline is recorded for the key, else run; `--record-green` records one."""
    path, key = green_path(), green_key(*argv[1:5])
    record = read_green(path)
    if argv[0] == "--green":
        print("skip" if argv[2] and record.get(key) == "green" else "run")
        return 0
    if not argv[2]:
        return 0
    record[key] = "green"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    full_tier_time.write_times(path, record)
    return 0


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] in ("--green", "--record-green"):
        if len(argv) != 5:
            print(USAGE, file=sys.stderr)
            return 2
        return green(argv)
    mode = run_pins.baseline_full_tier(argv[0], run_dir.main_tree_from_files(os.getcwd()))
    if mode is None:
        mode = tunables.get("VERI_BASELINE_FULL_TIER")
    if mode == "reuse":
        max_days, bad = tunables.resolve("VERI_FULL_TIER_MAX_AGE_DAYS")
        if bad:
            sys.stderr.write("baseline-full-tier: VERI_FULL_TIER_MAX_AGE_DAYS must be %s, got '%s'\n"
                             % (bad[1], bad[0]))
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
