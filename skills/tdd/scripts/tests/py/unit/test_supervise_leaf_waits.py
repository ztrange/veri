"""The signal case's leaf waits outlast load-induced delay and still fail named (#2356, #2360)."""
import pytest

from leaf_waits import leaf_left, leaf_started


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def test_a_leaf_that_dies_after_more_than_2_s_reads_as_no_leaf_left():
    clock = FakeClock()
    left = leaf_left(4242, lambda _pid: clock.now < 7.5, clock.sleep, clock)
    assert (left, clock.now >= 7.5) == (False, True)


def test_a_leaf_that_never_dies_reads_as_left():
    clock = FakeClock()
    assert leaf_left(4242, lambda _pid: True, clock.sleep, clock) is True


def test_a_leaf_that_starts_after_more_than_10_s_is_still_found():
    clock = FakeClock()
    assert leaf_started(lambda: 4242 if clock.now >= 17.0 else None, clock.sleep, clock) == 4242


def test_a_leaf_that_never_starts_fails_with_the_leaf_never_started():
    clock = FakeClock()
    with pytest.raises(AssertionError, match="^the leaf never started$"):
        leaf_started(lambda: None, clock.sleep, clock)


def test_a_leaf_that_dies_after_more_than_the_old_30_s_bound_reads_as_gone_2940():
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
