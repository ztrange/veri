"""The legs registry: one entry per live pytest leg, named by its pid, holding its worker count and start time."""
import os

import pid_file


def registered_workers(legs):
    return sum(count for _, count in registered_legs(legs))


def other_workers(legs):
    """W_other (PRD 036.6): the workers of the live registered legs whose entry lacks line 3 `leaf`, the legs no
    conductor's leaf started; an older 2-line entry counts, which errs low on an `auto` lane's N."""
    return sum(count for _, count, leaf in _live_entries(legs) if not leaf)


# Line 3 of the entry of a leg claimed with PYTEST_LEG_LOCK_WAIT_MARKER set, which supervise.sh sets for every leaf.
LEAF = "leaf"


def registration(count):
    """A registry entry's text: the worker count on line 1, this process's start time on line 2 (pid_file.ps_field's
    `lstart`), or the count alone when ps cannot read it, which then holds no share in another leg's eyes; line 3 is
    `leaf` when PYTEST_LEG_LOCK_WAIT_MARKER is set and non-empty."""
    started = pid_file.ps_field("lstart", os.getpid())
    if not started:
        return "%d\n" % count
    return "%d\n%s\n" % (count, started) + (LEAF + "\n" if os.environ.get("PYTEST_LEG_LOCK_WAIT_MARKER") else "")


def leg_state(pid, started):
    """"alive" when <pid> answers `kill 0` (a PermissionError included) and a start-time read, pinned to the format the
    entry records (pid_file.ps_field), equals <started>; "stale" when it is proven not that leg: the pid is gone, or two
    such reads both succeed and each differs from <started> (a reused pid); "unknown" when neither can be shown: no start
    time recorded (an older leg's entry), or any read that fails or prints nothing. Only "stale" removes an entry, so a
    read failing under load never deletes a live leg's."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "stale"
    except PermissionError:
        pass
    except (OSError, OverflowError):
        return "unknown"
    pinned = pid_file.ps_field("lstart", pid)
    if not started or not pinned:
        return "unknown"
    if pinned == started:
        return "alive"
    again = pid_file.ps_field("lstart", pid)
    if not again:
        return "unknown"
    return "alive" if again == started else "stale"


def registered_legs(legs):
    """The (pid, workers) of each registered leg proven alive under the start time its entry records (leg_state).

    Any other entry holds no share and never fails the read: one whose name is not a pid, an unreadable or malformed one,
    one with no start time (an older leg's), or one whose pid's start time cannot be read now. An entry proven stale is
    removed; the others stay. The caller holds the claim lock, so no entry is read half-written."""
    return [(name, count) for name, count, _ in _live_entries(legs)]


def _live_entries(legs):
    """(pid, workers, whether line 3 is `leaf`) of each leg registered_legs counts."""
    if not legs or not os.path.isdir(legs):
        return []
    holders = []
    for name in sorted(os.listdir(legs)):
        if not (name.isascii() and name.isdigit()):
            continue
        path = os.path.join(legs, name)
        try:
            with open(path) as f:
                lines = f.read().split("\n")
        except (OSError, ValueError):
            continue
        count = lines[0].strip()
        state = leg_state(int(name), lines[1].strip() if len(lines) > 1 else "")
        if state == "stale":
            unregister(path)
        elif state == "alive" and count.isascii() and count.isdigit():
            holders.append((name, int(count), len(lines) > 2 and lines[2].strip() == LEAF))
    return holders


def unregister(entry):
    try:
        os.remove(entry)
    except OSError:
        pass
