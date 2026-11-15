"""The marks wait-ci.sh keeps under a run's `.tdd/` for a pull request head, so calls remember what an earlier one saw.

Three kinds, each `ci-<kind>-<sha>` holding a decimal and a newline: `deadline` (when the wait for the head's checks
ends), `queued` (when its checks were first seen queued) and `none` (when it was first seen with no check at all).
`run` is the directory holding the `.tdd/`; "" is the current directory, whose paths read `.tdd/ci-…`."""
import os
import sys
from dataclasses import dataclass

import run_dir

KINDS = ("deadline", "queued", "none")


@dataclass(frozen=True)
class Marks:
    """The marks on disk for the head: the deadline file's raw text (None: absent; "": unreadable), its path,
    and the first queued and first none sightings as seconds (None: absent or not a number)."""
    deadline: object
    deadline_path: str
    queued: object
    none: object


def path(run, kind, key):
    return run_dir.run_file(run, "ci-%s-%s" % (kind, key))


def seconds(run, kind, key):
    """The mark's number, or None when it is absent or not a whole number."""
    try:
        with open(path(run, kind, key)) as found:
            return int(found.read())
    except (OSError, ValueError):
        return None


def exists(run, kind, key):
    return os.path.exists(path(run, kind, key))


def deadline_text(run, key):
    """The deadline file's text, "" when it exists but cannot be read, None when it is absent."""
    mark = path(run, "deadline", key)
    if not os.path.exists(mark):
        return None
    try:
        with open(mark) as found:
            return found.read()
    except OSError:
        return ""


def load(run, key, head):
    """The marks a poll of <head> reads: the deadline and queued marks under <key> (the wanted sha, else the head)
    and the none mark under the head."""
    return Marks(deadline=deadline_text(run, key), deadline_path=path(run, "deadline", key),
                 queued=seconds(run, "queued", key), none=seconds(run, "none", head))


def record(run, kind, key, value):
    """Writes <value> and a newline to the mark; an unwritable mark is a warning on stderr, not a failure."""
    try:
        with open(path(run, kind, key), "w") as out:
            out.write("%s\n" % value)
    except OSError as error:
        print("wait-ci.sh: %s" % error, file=sys.stderr)


def remove(run, kind, key):
    try:
        os.remove(path(run, kind, key))
    except OSError:
        pass


def fresh_window(run, key):
    """Drops every mark of <key>, so the next wait records a fresh deadline."""
    for kind in KINDS:
        remove(run, kind, key)
