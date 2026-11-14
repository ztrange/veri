"""In-process cases for veri/reset_wait.py, the module reset-wait.sh is a shim over."""
import importlib
import time


def test_main_called_with_no_argument_exits_2_naming_reset_wait_sh_in_its_usage_line_without_waiting(
        monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait waited")

    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")

    code, out, err = run_cli(reset_wait, [])

    assert code == 2
    assert out == ""
    assert "usage:" in err and "reset-wait.sh" in err


def test_issue_3242_marker_with_the_coord_reset_marker_already_present_prints_its_time_and_exits_0_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-coord").write_text("2026-11-12T10:00:00\n")

    code, out, _ = run_cli(reset_wait, ["marker", "coord"])

    assert (code, out) == (0, "reset-request coord 2026-11-12T10:00:00\n")


def test_issue_3242_marker_with_no_dev_reset_marker_polls_at_veri_poll_until_it_appears_then_prints_its_time_and_exits_0(
        tmp_path, monkeypatch, run_cli):
    naps = []
    tdd = tmp_path / ".tdd"
    tdd.mkdir()

    def nap(seconds):
        naps.append(seconds)
        if len(naps) == 3:
            (tdd / "reset-request-dev").write_text("2026-11-12T11:30:00\n")

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["marker", "dev"], env={"VERI_POLL": "7"})

    assert (code, out, naps) == (0, "reset-request dev 2026-11-12T11:30:00\n", [7.0, 7.0, 7.0])


def test_issue_3242_marker_dev_with_no_marker_at_the_start_keeps_polling_until_the_injected_sleep_writes_it_then_prints_reset_request_dev_and_exits_0(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    naps = []

    def nap(seconds):
        naps.append(seconds)
        (tdd / "reset-request-dev").write_text("2026-11-12T12:15:00\n")

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["marker", "dev"])

    assert (code, out) == (0, "reset-request dev 2026-11-12T12:15:00\n")
    assert len(naps) == 1


def test_issue_3242_marker_with_veri_poll_0_25_sleeps_0_25_between_polls(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    naps = []

    def nap(seconds):
        naps.append(seconds)
        (tdd / "reset-request-dev").write_text("2026-11-12T13:00:00\n")

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, _, _ = run_cli(reset_wait, ["marker", "dev"], env={"VERI_POLL": "0.25"})

    assert (code, naps) == (0, [0.25])


def test_issue_3242_marker_dev_with_lane_waits_on_the_lane_marker_not_the_plain_dev_marker_and_prints_reset_request_dev_and_its_time(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T09:00:00\n")
    (tdd / "reset-request-dev-a").write_text("2026-11-12T14:45:00\n")

    code, out, _ = run_cli(reset_wait, ["marker", "dev", "--lane", "a"])

    assert (code, out) == (0, "reset-request dev 2026-11-12T14:45:00\n")


def test_issue_3242_recovered_coord_with_the_marker_present_prints_the_recovered_at_written_after_it_and_exits_0(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-coord").write_text("2026-11-12T10:00:00\n")

    def nap(seconds):
        (tdd / "role-coord.state").write_text(
            "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:02:30\nsession-id=s1\n")
        (tdd / "reset-request-coord").unlink()

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["recovered", "coord", "60"])

    assert (code, out) == (0, "recovered coord 2026-11-12T10:02:30\n")


def test_issue_3242_recovered_coord_keeps_waiting_through_a_state_file_with_no_recovered_at_and_one_not_later_than_the_marker_and_returns_on_the_later_one(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-coord").write_text("2026-11-12T10:00:00\n")
    states = iter([
        "reset-at=2026-11-12T10:00:00\nsession-id=s1\n",
        "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:00:00\n",
        "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:03:10\n",
    ])
    naps = []

    def nap(seconds):
        naps.append(seconds)
        (tdd / "role-coord.state").write_text(next(states))

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["recovered", "coord", "60"])

    assert (code, out) == (0, "recovered coord 2026-11-12T10:03:10\n")
    assert len(naps) == 3


def test_issue_3242_recovered_coord_with_lane_waits_on_the_lane_marker_and_lane_recovered_at_not_the_plain_roles(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-coord").write_text("2026-11-12T09:00:00\n")
    (tdd / "reset-request-coord-a").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-coord.state").write_text("recovered-at=2026-11-12T09:30:00\n")

    def nap(seconds):
        (tdd / "role-coord-a.state").write_text(
            "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:04:00\n")
        (tdd / "reset-request-coord-a").unlink()

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["recovered", "coord", "--lane", "a", "60"])

    assert (code, out) == (0, "recovered coord 2026-11-12T10:04:00\n")


def test_issue_3242_recovered_coord_with_no_recovered_at_later_than_the_marker_once_the_seconds_pass_prints_not_recovered_coord_and_exits_1(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-coord").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-coord.state").write_text("reset-at=2026-11-12T10:00:00\nsession-id=s1\n")
    now = [1_000_000.0]
    naps = []

    def nap(seconds):
        naps.append(seconds)
        if len(naps) > 50:
            raise AssertionError("recovered never gave up waiting")
        now[0] += seconds

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait, "main_tree", lambda cwd: str(tmp_path), raising=False)

    code, out, _ = run_cli(reset_wait, ["recovered", "coord", "60"], env={"VERI_POLL": "20"})

    assert len(naps) <= 50, "recovered never gave up waiting"
    assert (code, out) == (1, "not-recovered coord\n")
