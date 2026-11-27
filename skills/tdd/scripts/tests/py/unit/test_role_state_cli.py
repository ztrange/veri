"""veri/role_state_cli.py: role-state.sh's entry point, a written `set n` writing the lane's test budget entry (PRD 036.5)."""
import importlib
import os

import pytest


def test_4453_dev_set_n_writes_the_lanes_entry_and_prints_n_its_need_the_other_lanes_c_with_its_source_and_the_t_a_leg_reads_now(tmp_path, monkeypatch, run_cli):
    import hashlib
    import os
    import time

    import watch_runs
    role_state = importlib.import_module("veri.role_state")
    role_state_cli = importlib.import_module("veri.role_state_cli")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["41"])
    ceiling = os.environ["VERI_TEST_CEILING_FILE"]
    with open(ceiling, "w") as f:
        f.write("10\n2026-11-19\n")
    root = os.environ["VERI_TEST_BUDGET_DIR"]
    os.makedirs(root)
    with open(os.path.join(root, "main@0123456789abcdef"), "w") as f:
        f.write("4\n%d\n" % (time.time() + 3600))
    own = "mu@" + hashlib.sha256(os.path.realpath(str(tmp_path)).encode()).hexdigest()[:16]

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "1"])

    with open(os.path.join(root, own)) as f:
        written = f.read().split("\n")[0]
    assert (code, out, written) == (0, "N=1; lane mu needs 2 (max(N, 1 live conductors) x 2); other lanes: main=4; "
                                       "C=10 from the ceiling record %s; T=6\n" % ceiling, "2"), err


@pytest.fixture
def lane_mu(tmp_path, monkeypatch):
    """role_state_cli with the main working tree at tmp_path, a ceiling record of 10 and an empty budget directory;
    yields (module, the budget directory, lane mu's entry path)."""
    import hashlib
    role_state = importlib.import_module("veri.role_state")
    role_state_cli = importlib.import_module("veri.role_state_cli")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
        f.write("10\n2026-11-19\n")
    root = os.environ["VERI_TEST_BUDGET_DIR"]
    os.makedirs(root)
    own = "mu@" + hashlib.sha256(os.path.realpath(str(tmp_path)).encode()).hexdigest()[:16]
    return role_state_cli, root, os.path.join(root, own)


def test_4453_dev_set_n_1_beside_3_live_conductors_writes_a_need_of_3_times_d(lane_mu, monkeypatch, run_cli):
    import watch_runs
    role_state_cli, _, own = lane_mu
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["41", "42", "43"])

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "1"])

    with open(own) as f:
        assert (code, f.read().split("\n")[0], "lane mu needs 6 " in out) == (0, "6", True), err


def test_4453_a_refused_dev_set_n_minus_1_exits_2_and_writes_no_lane_entry(lane_mu, monkeypatch, run_cli):
    import watch_runs
    role_state_cli, root, _ = lane_mu
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: [])

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "-1"])

    assert (code, out, os.listdir(root)) == (2, "", []), err


@pytest.fixture
def auto_world(lane_mu, monkeypatch):
    """lane_mu with one live conductor (41), W_other 3 and a queue of 12 and 13, 13 overlapping an open run draft PR."""
    import leg_registry
    import watch_runs
    dispatch = importlib.import_module("veri.dispatch")
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["41"])
    monkeypatch.setattr(leg_registry, "other_workers", lambda legs: 3)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "13"])
    monkeypatch.setattr(dispatch, "run_pr_paths", lambda: {})
    monkeypatch.setattr(dispatch, "overlap", lambda issue, changed: ("a.py", "https://x/pull/9") if issue == "13" else None)
    return lane_mu, dispatch


def test_4805_dev_set_n_auto_writes_c_as_the_lanes_need_and_prints_the_target_its_t_w_other_d_and_queue_cap(auto_world, run_cli):
    (role_state_cli, _, own), _ = auto_world

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "auto"])

    with open(own) as f:
        written = f.read().split("\n")[0]
    assert (code, out, written) == (
        0, "N=auto (2 now: floor((T=10 - W_other=3)/2), queue cap 2); lane mu needs C=10\n", "10"), err


def test_4805_dev_set_n_auto_with_the_queue_unreadable_prints_the_uncapped_target_and_queue_cap_unread(auto_world, monkeypatch, run_cli):
    import watch_runs
    (role_state_cli, _, _), dispatch = auto_world

    def unreadable():
        raise watch_runs.QueueUnreadable("gh: offline\n")

    monkeypatch.setattr(dispatch, "solvable_issues", unreadable)

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "auto"])

    assert (code, out) == (0, "N=auto (3 now: floor((T=10 - W_other=3)/2), queue cap unread); lane mu needs C=10\n"), err
