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


def test_3990_a_rate_limited_queue_read_whose_reset_cannot_be_read_pauses_the_queue_for_one_overlap_poll_then_launches(
        dispatch, monkeypatch):
    monkeypatch.setenv("VERI_DISPATCH_OVERLAP_POLL", "300")
    limited = importlib.import_module("veri.watch_runs").QueueUnreadable("gh: API rate limit exceeded for user\n")
    world = FakeWorld({"queue": limited, "reset": None, "clock": 1000},
                      {"queue": ["12"], "clock": 1299},
                      {"queue": ["12"], "clock": 1300})
    state, codes = dispatch.State(target=1), []
    for _ in range(3):
        state, code = dispatch.step(state, world)
        codes.append(code)
        world.wait()

    assert (codes, len(world.complained), "reset" in "".join(world.complained),
            [tick for key, tick in world.reads if key == "queue"], world.launched) == (
        [None, None, None], 1, True, [0, 2], ["12"])


def test_4605_a_run_launched_per_dispatch_log_that_ended_done_before_a_fresh_call_says_done_before_any_launch(dispatch):
    class LoggedWorld(FakeWorld):
        def launched_runs(self):
            return ["7"]

    world = LoggedWorld({"queue": ["12"], "closing": {"7": "done 7 https://github.com/o/r/pull/9"}})

    state, code = dispatch.step(dispatch.State(target=1), world)

    assert (code, world.said, world.launched) == (0, ["done 7 https://github.com/o/r/pull/9\n"], [])


def test_4605_a_run_launched_per_dispatch_log_that_ended_with_a_bail_before_a_fresh_call_says_bail_before_any_launch(dispatch):
    class LoggedWorld(FakeWorld):
        def launched_runs(self):
            return ["7"]

    world = LoggedWorld({"queue": ["12"], "closing": {"7": "bail 7"}})

    state, code = dispatch.step(dispatch.State(target=1), world)

    assert (code, world.said, world.launched) == (0, ["bail 7\n"], [])
