"""A red report's `COVERING_TESTS:` line, the ids of the existing tests a `HOLDS` report says already cover the step's
criterion (PRD 044.2, D7, D8)."""

MOST = 5


def ids(line):
    """The ids <line> holds, space-separated; ValueError, naming the line, when it holds none or more than MOST."""
    found = line.split()
    if not found:
        raise ValueError("COVERING_TESTS: holds no id")
    if len(found) > MOST:
        raise ValueError("COVERING_TESTS: holds %d ids, at most %d" % (len(found), MOST))
    return found
