"""A run's `.tdd/restart-pending` marker: the file that says a conductor restart is in flight.

restart_conductor claims it (writes its own pid) before stopping the conductor and clears it after
the relaunch; dispatch, comment and watch_runs ask in_flight() whether a live restarter holds it.
The marker is judged by one fact, whether the pid it holds answers `kill -0`; a marker that cannot
say (empty, mid-write, non-digit, unreadable, probe denied) is the caller's call, named by the one
`unreadable` argument: dispatch counts it as living, comment and watch_runs as dead (SCRIPTS.md
states each rule at its script's entry)."""
import os

import entry
import run_dir


def path(run):
    """`<run>/.tdd/restart-pending`. str, never raises."""
    return run_dir.run_file(run, "restart-pending")


def claim(run, pid):
    """Write `<pid>\\n` into the marker, creating `.tdd/` first; not atomic (a reader may see it empty)."""
    marker = path(run)
    os.makedirs(os.path.dirname(marker), exist_ok=True)
    with open(marker, "w") as f:
        f.write(f"{pid}\n")


def clear(run):
    """Remove the marker; raises FileNotFoundError when there is none."""
    os.remove(path(run))


def in_flight(run, *, unreadable):
    """True while a live restarter holds the marker.

    Missing marker, a dead pid or a pid too large to exist: False. A live pid: True. A marker that
    cannot prove either (open fails other than missing, undecodable, empty, non-digit, or the probe
    is denied) answers `unreadable`, which every caller must name."""
    try:
        with open(path(run)) as f:
            text = f.read().strip()
    except FileNotFoundError:
        return False
    except (OSError, ValueError):
        return unreadable
    pid = entry.whole_number(text, 0)
    if pid is None:
        return unreadable
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, OverflowError):
        return False
    except OSError:
        return unreadable
    return True
