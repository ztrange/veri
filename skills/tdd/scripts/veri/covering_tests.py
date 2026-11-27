"""A red report's `COVERING_TESTS:` line, the ids of the existing tests a `HOLDS` report says already cover the step's
criterion (PRD 044.2, D7, D8)."""

MOST = 5


def ids(line, tracked):
    """The ids <line> holds, space-separated; ValueError, naming the line, when it holds none, more than MOST, or one
    whose path (the part before `::`) is not in <tracked>, the paths `git ls-files` lists."""
    found = line.split()
    if not found:
        raise ValueError("COVERING_TESTS: holds no id")
    if len(found) > MOST:
        raise ValueError("COVERING_TESTS: holds %d ids, at most %d" % (len(found), MOST))
    for found_id in found:
        path = found_id.split("::", 1)[0]
        if path not in tracked:
            raise ValueError("COVERING_TESTS: %s is not tracked" % path)
    return found
