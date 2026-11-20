"""The leg's load-timeout plugin (PRD 036.7): in the leg's controller, appends each case its per-case timeout fails to
VERI_TEST_TIMEOUTS_FILE and records it as a `case-timeout` event; a load timeout, one appended while the file holds a
line from another test file, lowers T by 2 through VERI_TEST_LOAD_FILE, at most once per VERI_LOAD_WINDOW.

PYTEST_DONT_REWRITE: the leg imports this module before pytest loads it as a plugin."""
import os
import sys
import time

import event
import tunables
from ceiling_record import timed_out


# The leg's facts while its passes run, which the leg sets and restores: `workers`, the xdist workers it runs with,
# and `total`, the T it claimed them out of.
LEG = {}


def timeouts_path():
    return tunables.get("VERI_TEST_TIMEOUTS_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-timeouts")


def load_path():
    return tunables.get("VERI_TEST_LOAD_FILE") or os.path.join(os.path.expanduser("~"), ".veri-test-load")


def complain(what, path, error):
    sys.stderr.write("load timeouts: cannot %s %s (%s); the run goes on\n" % (what, path, error.strerror or error))
    sys.stderr.flush()


def record():
    """The load file's first two lines, stripped, as whole numbers or None each; a file it cannot read is one stderr
    line naming it, and reads as none."""
    lines = ["", ""]
    try:
        with open(load_path()) as f:
            lines = [f.readline().strip(), f.readline().strip()]
    except FileNotFoundError:
        pass
    except (OSError, UnicodeDecodeError) as error:
        complain("read the load file", load_path(), error)
    return [int(line) if line.isascii() and line.isdigit() else None for line in lines]


def held():
    """The lowered T on line 1 of the load file when it is a whole number of at least 2, else None."""
    t = record()[0]
    return t if t is not None and t >= 2 else None


def window():
    """VERI_LOAD_WINDOW: the seconds a timeouts line counts toward a load timeout; 600 for anything but a whole number."""
    raw = tunables.get("VERI_LOAD_WINDOW", unless_empty=True)
    return int(raw) if raw.isascii() and raw.isdigit() else 600


def recent(lines, since):
    """The (test file, node id) of each timeouts line appended at or after <since>."""
    fields = [line.split(" ") for line in lines]
    return [(f[2], f[3]) for f in fields if len(f) >= 4 and f[0].isdigit() and int(f[0]) >= since]


def pytest_runtest_logreport(report):
    if not LEG or os.environ.get("PYTEST_XDIST_WORKER") or not report.failed or not timed_out(report):
        return
    workers = LEG["workers"]
    now = time.time()
    test_file = report.nodeid.split("::")[0]
    since = now - window()
    context = event.context(tunables.environment())
    event.mark("", context, "case-timeout", ["nodeid=" + report.nodeid, "workers=%d" % workers])
    try:
        with open(timeouts_path(), "a+") as f:
            f.seek(0)
            window_cases = recent(f.read().splitlines(), since) + [(test_file, report.nodeid)]
            f.write("%d %d %s %s %d\n" % (now, os.getpid(), test_file, report.nodeid, workers))
    except (OSError, UnicodeDecodeError) as error:
        complain("record the timeout in the timeouts file", timeouts_path(), error)
        return
    lowered_at = record()[1]
    if len({file for file, _ in window_cases}) >= 2 and (lowered_at is None or lowered_at < since):
        old, new = LEG["total"], max(2, LEG["total"] - 2)
        cases = ",".join(nodeid for _, nodeid in window_cases)
        try:
            lower(new, now, old, cases)
        except OSError as error:
            complain("write the load file", load_path(), error)
            return
        sys.stderr.write("load timeout: %s timed out within %d s, so T is lowered from %d to %d in %s\n" % (
            cases, window(), old, new, load_path()))
        sys.stderr.flush()
        event.mark("", context, "t-lowered", ["old=%d" % old, "new=%d" % new, "cases=" + cases])


def lower(t, now, old, cases):
    """Replaces the load file whole, through a temporary file beside it: <t> on line 1, <now> on line 2, and, for
    dispatch.sh's t-lowered notice, the T it lowered from on line 3 and the window's cases on line 4."""
    path = load_path()
    temporary = "%s.%d.tmp" % (path, os.getpid())
    with open(temporary, "w") as f:
        f.write("%d\n%d\n%d\n%s\n" % (t, now, old, cases))
    os.replace(temporary, path)
