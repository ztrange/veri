"""The pytest leg's worker budget: T, the workers every live leg on the machine shares, out of C0 (the ceiling record
or the cores), the cap, the load file and the lane entries."""
import os
import subprocess
import sys

import budget_entries
from ceiling import LEG, cap_path, read_cap, record_path


def load_timeouts_module():
    """The leg's load_timeouts module, which reads the load file; it lives in tests/leg/ (ceiling.LEG), which this puts on
    sys.path, as ceiling.main does."""
    if LEG not in sys.path:
        sys.path.append(LEG)
    import load_timeouts
    return load_timeouts


def budget(say=True):
    """(T, its source, for the wait line): T, the workers every live leg on the machine shares, is C0 (c0()), lowered
    to the cap the human set (ceiling.read_cap) when that is below it, the source then naming the cap file beside C0 and
    C0's source (PRD 036.11), and lowered again to a load timeout's T in the load file (load_timeouts.held) when that
    is below what remains, never below 2 (PRD 036.7); that C narrowed to max(2, min(C, S)), S the needs summed over the
    unexpired lane entries (budget_entries.unexpired, PRD 036.5), while there is one, the source then naming each entry's lane and need
    beside C and its source when that narrows it. C0 from the core fallback is one stderr line naming the record and `make ceiling`; a cap
    file it cannot use is one more; with <say> false, neither is written (a wait re-reading T has said them once)."""
    total, source = capacity(say)
    needs = budget_entries.unexpired()
    narrowed = max(2, min(total, sum(need for _, need in needs)))
    if needs and narrowed < total:
        return narrowed, "the lane entries %s, below C=%d from %s" % (
            ", ".join("%s=%d" % entry for entry in needs), total, source)
    return total, source


def capacity(say=True):
    """(C, its source): C0 lowered to the cap and the load file's T, as budget() describes, before any lane entry narrows it."""
    total, source = c0()
    if source is None and say:
        sys.stderr.write("no test-worker ceiling in %s, so the budget is the %d cores; `make ceiling` measures one\n" % (
            record_path(), total))
    if source is None:
        source = "the core fallback"
    cap, complaint = read_cap()
    if complaint and say:
        sys.stderr.write(complaint)
    sys.stderr.flush()
    if cap and cap < total:
        total, source = cap, "the cap file %s, below C0=%d from %s" % (cap_path(), total, source)
    held = load_timeouts_module().held()
    if held and held < total:
        total, source = max(2, held), "the load file %s, below %d from %s" % (load_timeouts_module().load_path(), total, source)
    return total, source


def c0():
    """(C0, its source): line 1 of the ceiling record (ceiling.record_path) when it is a whole number of at least 2, its
    source naming the record; else the cores, never below 2, its source None. A record that is missing, unreadable or
    malformed only falls back, never raises."""
    path = record_path()
    try:
        with open(path) as f:
            first = f.readline().strip()
    except (OSError, ValueError):
        first = ""
    if first.isascii() and first.isdigit() and int(first) >= 2:
        return int(first), "the ceiling record " + path
    return max(2, cores()), None


def cores():
    """The physical cores on macOS (the affinity count when sysctl cannot say), the CPU-affinity count elsewhere."""
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    if sys.platform == "darwin":
        try:
            cores = int(subprocess.run(["sysctl", "-n", "hw.physicalcpu"], capture_output=True, text=True).stdout)
        except (OSError, ValueError):
            cores = affinity
    else:
        cores = affinity
    return cores
