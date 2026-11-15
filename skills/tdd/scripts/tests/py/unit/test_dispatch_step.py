"""dispatch.step: one poll's decision from an explicit dispatch.State and a FakeWorld, asserted without any loop."""
import importlib

import pytest

from dispatch_world import FakeWorld


@pytest.fixture
def dispatch():
    return importlib.import_module("veri.dispatch")


def test_a_seen_run_gone_from_the_live_conductors_with_a_done_comment_says_done_and_ends_with_0(dispatch):
    state = dispatch.State(target=1)
    state.seen = ["7"]
    world = FakeWorld({"closing": {"7": "done 7 https://github.com/o/r/pull/9"}})

    state, code = dispatch.step(state, world)

    assert (code, world.said, world.launched) == (0, ["done 7 https://github.com/o/r/pull/9\n"], [])


def test_a_free_slot_launches_the_first_solvable_issue_and_remembers_it_as_the_previous_launch(dispatch):
    world = FakeWorld({"live": ["5"], "queue": ["12", "15"]})

    state, code = dispatch.step(dispatch.State(target=2), world)

    assert (code, world.launched, state.previous, state.seen, world.said, world.waits) == (
        None, ["12"], "12", ["5"], [], 0)


def test_a_free_slot_launches_nothing_while_the_previous_launch_has_no_ledger(dispatch):
    state = dispatch.State(target=3)
    state.previous = "12"
    world = FakeWorld({"live": ["5"], "queue": ["15"], "no_ledger": ["12"]})

    state, code = dispatch.step(state, world)

    assert (code, world.launched, state.previous) == (None, [], "12")


def test_a_silent_exit_younger_than_30_seconds_is_held_as_pending_and_its_first_absence_time_kept(dispatch):
    state = dispatch.State(target=1)
    state.seen = ["7"]
    world = FakeWorld({"clock": 1000})

    state, code = dispatch.step(state, world)

    assert (code, world.said, state.pending, state.missing, state.seen) == (None, [], ["7"], {"7": 1000}, ["7"])


def test_a_seen_run_with_no_worktree_and_no_conductor_process_is_marked_absent_without_a_grace_wait(dispatch):
    state = dispatch.State(target=0)
    state.seen = ["7"]
    world = FakeWorld({"no_worktree": ["7"]})

    state, code = dispatch.step(state, world)

    assert (code, state.absent, world.waits, world.complained) == (None, ["7"], 0, [])


def test_a_rate_limited_queue_read_pauses_launching_until_the_reset_the_world_reports(dispatch):
    limited = importlib.import_module("veri.watch_runs").QueueUnreadable("gh: API rate limit exceeded for user\n")
    world = FakeWorld({"queue": limited, "reset": 5000})

    state, code = dispatch.step(dispatch.State(target=1), world)

    assert (code, state.resume_at, world.launched, world.said, world.complained) == (None, 5000, [], [], [])
