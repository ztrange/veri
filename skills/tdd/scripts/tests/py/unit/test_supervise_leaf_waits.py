"""The signal case's leaf waits outlast load-induced delay and still fail named (#2356, #2360)."""
import pytest

from leaf_waits import leaf_left, leaf_started


@pytest.fixture
def no_ps(monkeypatch):
    """The `ps` probe of a pid that is no child of ours, answered as it would for pid 4242: not a zombie."""
    monkeypatch.setattr("leaf_waits._zombie", lambda pid: False)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def test_a_leaf_that_dies_after_more_than_2_s_reads_as_no_leaf_left(no_ps):
    clock = FakeClock()
    left = leaf_left(4242, lambda _pid: clock.now < 7.5, clock.sleep, clock)
    assert (left, clock.now >= 7.5) == (False, True)


def test_a_leaf_that_never_dies_reads_as_left(no_ps):
    clock = FakeClock()
    assert leaf_left(4242, lambda _pid: True, clock.sleep, clock) is True


def test_a_leaf_that_starts_after_more_than_10_s_is_still_found():
    clock = FakeClock()
    assert leaf_started(lambda: 4242 if clock.now >= 17.0 else None, clock.sleep, clock) == 4242


def test_a_leaf_that_never_starts_fails_with_the_leaf_never_started():
    clock = FakeClock()
    with pytest.raises(AssertionError, match="^the leaf never started$"):
        leaf_started(lambda: None, clock.sleep, clock)


def test_a_leaf_that_dies_after_more_than_the_old_30_s_bound_reads_as_gone_2940(no_ps):
    clock = FakeClock()
    assert leaf_left(4242, lambda _pid: clock.now < 45.0, clock.sleep, clock) is False


def test_a_zombie_leaf_that_a_nonblocking_reap_answers_reads_as_gone_3293(monkeypatch):
    clock = FakeClock()
    reaps = []

    def fake_waitpid(pid, flags):
        reaps.append((pid, flags))
        return (pid, 0)

    monkeypatch.setattr("os.waitpid", fake_waitpid)
    assert leaf_left(4242, lambda _pid: True, clock.sleep, clock) is False


def test_a_running_leaf_that_a_nonblocking_reap_has_nothing_for_reads_as_left_3293(monkeypatch):
    clock = FakeClock()

    monkeypatch.setattr("os.waitpid", lambda pid, flags: (0, 0))
    assert leaf_left(4242, lambda _pid: True, clock.sleep, clock) is True


@pytest.mark.process("a forked parent whose exited child stays an unreaped zombie that the test process cannot wait on")
def test_a_zombie_leaf_orphaned_to_a_parent_that_never_reaps_it_reads_as_gone_3431():
    import os
    import time

    told, tell = os.pipe()
    hold_read, hold_write = os.pipe()
    parent = os.fork()
    if parent == 0:
        try:
            os.close(told)
            os.close(hold_write)
            child = os.fork()
            if child == 0:
                os._exit(0)
            os.write(tell, b"%d\n" % child)
            os.read(hold_read, 1)
        finally:
            os._exit(0)
    os.close(tell)
    os.close(hold_read)
    try:
        leaf = int(os.read(told, 32))
        left = leaf_left(leaf, lambda pid: os.kill(pid, 0) is None, time.sleep, time.monotonic, bound=1.0)
    finally:
        os.close(hold_write)
        os.waitpid(parent, 0)
        os.close(told)

    assert left is False
