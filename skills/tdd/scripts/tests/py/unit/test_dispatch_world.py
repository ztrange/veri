"""dispatch.main driven through FakeWorld, the scripted second adapter of its world: no patch, no exception escape."""
import importlib

import pytest

from dispatch_world import FakeWorld


@pytest.fixture
def dispatch():
    return importlib.import_module("veri.dispatch")


def test_a_free_slot_launches_the_first_solvable_issue_and_a_spent_script_ends_the_loop_quietly(dispatch):
    world = FakeWorld({"live": ["5"], "queue": ["12", "15"]}, {"live": ["5", "12"], "queue": ["15"]})

    code = dispatch.main(["--target", "2"], world=world)

    assert (code, world.launched, world.said, world.complained, world.waits) == (None, ["12"], [], [], 2)


def test_a_run_whose_conductor_exits_with_a_done_comment_prints_done_with_its_pr_url_and_exits_0(dispatch):
    world = FakeWorld({"live": ["7"]}, {"closing": {"7": "done 7 https://github.com/o/r/pull/9"}}, {})

    code = dispatch.main(["--target", "1"], world=world)

    assert (code, world.said, world.launched) == (0, ["done 7 https://github.com/o/r/pull/9\n"], [])


def test_a_run_whose_conductor_exits_with_a_bail_comment_prints_bail_and_exits_0(dispatch):
    world = FakeWorld({"live": ["7"]}, {"closing": {"7": "bail 7"}}, {})

    code = dispatch.main(["--target", "1"], world=world)

    assert (code, world.said) == (0, ["bail 7\n"])


def test_an_empty_queue_with_no_live_run_prints_queue_empty_and_exits_3(dispatch):
    unreadable = importlib.import_module("veri.watch_runs").QueueUnreadable("")
    world = FakeWorld({"queue": unreadable}, {})

    code = dispatch.main(["--target", "1"], world=world)

    assert (code, world.said, world.launched) == (3, ["queue-empty\n"], [])


def test_a_seen_run_silent_for_the_stall_window_prints_stalled_and_exits_0(dispatch):
    world = FakeWorld({"live": ["7"], "clock": 0}, {"live": ["7"], "activity": {"7": 100}, "clock": 3700}, {})

    code = dispatch.main(["--target", "1"], world=world)

    assert (code, world.said, world.complained) == (0, ["stalled 7\n"], [])


def test_a_malformed_n_line_in_the_role_state_exits_2_naming_the_line_and_the_file_and_launches_nothing(dispatch):
    world = FakeWorld({"queue": ["12"]}, role_state=["n=two"], role_state_file="/main/.tdd/role-dev.state")

    code = dispatch.main([], world=world)

    assert (code, world.said, world.launched, world.complained) == (
        2, [], [], ["dispatch.sh: malformed n line: n=two in /main/.tdd/role-dev.state\n"])
