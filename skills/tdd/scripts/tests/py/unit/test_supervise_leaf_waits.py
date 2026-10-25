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
