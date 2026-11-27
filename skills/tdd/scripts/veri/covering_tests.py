"""A red report's `COVERING_TESTS:` line, the ids of the existing tests a `HOLDS` report says already cover the step's
criterion (PRD 044.2, D7, D8)."""


def ids(line):
    """The ids <line> holds, space-separated."""
    return line.split()
