"""Waits on a real leaf's start and death, bounded far above load-induced delay (#2356, #2360).

Each returns as soon as its condition holds, so a passing run pays nothing for the bound;
`sleep` and `clock` are injected so the unit tier can drive them without real waits.
"""

LEAF_START_BOUND = 30.0
LEAF_DEATH_BOUND = 30.0


def leaf_started(read_pid, sleep, clock, bound=LEAF_START_BOUND, step=0.02):
    """The pid <read_pid>() answers once the leaf has written it; AssertionError if it never does within <bound> s."""
    deadline = clock() + bound
    while True:
        pid = read_pid()
        if pid is not None:
            return pid
        if clock() >= deadline:
            raise AssertionError("the leaf never started")
        sleep(step)


def leaf_left(pid, alive, sleep, clock, bound=LEAF_DEATH_BOUND, step=0.1):
    """True when <pid> is still alive after <bound> s; False as soon as it is gone."""
    deadline = clock() + bound
    while alive(pid):
        if clock() >= deadline:
            return True
        sleep(step)
    return False
