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


def test_issue_3242_marker_with_the_dev_reset_marker_already_present_prints_its_time_and_exits_0_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    code, out, _ = run_cli(reset_wait, ["marker", "dev"])

    assert (code, out) == (0, "reset-request dev 2026-11-12T10:00:00\n")


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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T09:00:00\n")
    (tdd / "reset-request-dev-a").write_text("2026-11-12T14:45:00\n")

    code, out, _ = run_cli(reset_wait, ["marker", "dev", "--lane", "a"])

    assert (code, out) == (0, "reset-request dev 2026-11-12T14:45:00\n")


def test_issue_3242_recovered_dev_with_the_marker_present_prints_the_recovered_at_written_after_it_and_exits_0(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    def nap(seconds):
        (tdd / "role-dev.state").write_text(
            "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:02:30\nsession-id=s1\n")
        (tdd / "reset-request-dev").unlink()

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "60"])

    assert (code, out) == (0, "recovered dev 2026-11-12T10:02:30\n")


def test_issue_3242_recovered_dev_keeps_waiting_through_a_state_file_with_no_recovered_at_and_one_not_later_than_the_marker_and_returns_on_the_later_one(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    states = iter([
        "reset-at=2026-11-12T10:00:00\nsession-id=s1\n",
        "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:00:00\n",
        "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:03:10\n",
    ])
    naps = []

    def nap(seconds):
        naps.append(seconds)
        (tdd / "role-dev.state").write_text(next(states))

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "60"])

    assert (code, out) == (0, "recovered dev 2026-11-12T10:03:10\n")
    assert len(naps) == 3


def test_issue_3242_recovered_dev_with_lane_waits_on_the_lane_marker_and_lane_recovered_at_not_the_plain_roles(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T09:00:00\n")
    (tdd / "reset-request-dev-a").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-dev.state").write_text("recovered-at=2026-11-12T09:30:00\n")

    def nap(seconds):
        (tdd / "role-dev-a.state").write_text(
            "reset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:04:00\n")
        (tdd / "reset-request-dev-a").unlink()

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "--lane", "a", "60"])

    assert (code, out) == (0, "recovered dev 2026-11-12T10:04:00\n")


def test_issue_3242_recovered_dev_with_no_recovered_at_later_than_the_marker_once_the_seconds_pass_prints_not_recovered_dev_and_exits_1(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-dev.state").write_text("reset-at=2026-11-12T10:00:00\nsession-id=s1\n")
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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "60"], env={"VERI_POLL": "20"})

    assert len(naps) <= 50, "recovered never gave up waiting"
    assert (code, out) == (1, "not-recovered dev\n")


def test_issue_3242_recovered_dev_with_no_seconds_and_veri_reset_ack_timeout_50_gives_up_after_50_injected_seconds_printing_not_recovered_dev_and_exits_1(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-dev.state").write_text("reset-at=2026-11-12T10:00:00\nsession-id=s1\n")
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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev"],
                           env={"VERI_RESET_ACK_TIMEOUT": "50", "VERI_POLL": "20"})

    assert (code, out) == (1, "not-recovered dev\n")
    assert 50 <= now[0] - 1_000_000.0 < 70


def test_issue_3242_recovered_dev_with_no_seconds_and_veri_reset_ack_timeout_unset_is_still_waiting_at_299_injected_seconds_and_gives_up_at_300_printing_not_recovered_dev_and_exits_1(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-dev.state").write_text("reset-at=2026-11-12T10:00:00\nsession-id=s1\n")
    now = [1_000_000.0]
    naps = []

    def nap(seconds):
        naps.append(seconds)
        if len(naps) > 400:
            raise AssertionError("recovered never gave up waiting")
        now[0] += seconds

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: now[0])
    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    monkeypatch.delenv("VERI_RESET_ACK_TIMEOUT", raising=False)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev"], env={"VERI_POLL": "1"})

    assert (code, out) == (1, "not-recovered dev\n")
    assert now[0] - 1_000_000.0 == 300.0


def test_issue_3242_recovered_dev_with_no_reset_marker_for_the_role_exits_3_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "60"])

    assert (code, out) == (3, "")


def test_issue_3242_a_verb_other_than_marker_or_recovered_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    monkeypatch.setattr(time, "sleep", no_wait)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, err = run_cli(reset_wait, ["frobnicate", "dev"], env={"VERI_POLL": "1"})

    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "marker|recovered" in err


def test_issue_3242_marker_with_a_role_other_than_dev_or_dev_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    naps = []
    monkeypatch.setattr(time, "sleep", naps.append)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-admin").write_text("2026-11-12T10:00:00\n")

    code, out, err = run_cli(reset_wait, ["marker", "admin"], env={"VERI_POLL": "1"})

    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "marker|recovered" in err
    assert naps == []


def test_issue_3242_marker_dev_with_lane_given_no_value_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    naps = []
    monkeypatch.setattr(time, "sleep", naps.append)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    code, out, err = run_cli(reset_wait, ["marker", "dev", "--lane"], env={"VERI_POLL": "1"})

    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "marker|recovered" in err
    assert naps == []


def test_issue_3242_recovered_dev_with_seconds_abc_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    naps = []
    monkeypatch.setattr(time, "sleep", naps.append)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    code, out, err = run_cli(reset_wait, ["recovered", "dev", "abc"], env={"VERI_POLL": "1"})

    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "marker|recovered" in err
    assert naps == []


def test_issue_3242_recovered_dev_with_seconds_0_or_a_non_ascii_digit_string_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    naps = []

    def nap(seconds):
        naps.append(seconds)
        assert len(naps) < 3, "waited instead of refusing"

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    results = {}
    for bad in ("0", "٣"):
        code, out, err = run_cli(reset_wait, ["recovered", "dev", bad], env={"VERI_POLL": "1"})
        results[bad] = (code, out, err.startswith("usage:") and "marker|recovered" in err)

    assert results == {"0": (2, "", True), "٣": (2, "", True)}
    assert naps == []


def test_issue_3242_recovered_with_any_token_in_place_of_lane_exits_2_with_the_usage_and_reads_no_file(
        tmp_path, monkeypatch, run_cli):
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path / "absent"))

    code, out, err = run_cli(reset_wait, ["recovered", "dev", "x", "5", "5"])

    assert (code, out) == (2, "")
    assert err.startswith("usage: reset-wait.sh")


def test_issue_3242_bad_role_exits_2_with_the_usage_for_every_verb_before_touching_a_file(
        tmp_path, monkeypatch, run_cli):
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path / "absent"))

    results = [run_cli(reset_wait, [verb, "foo"])[0] for verb in ("marker", "recovered")]

    assert results == [2, 2]


def test_issue_3242_recovered_dev_with_two_recovered_at_lines_answers_from_the_latest_not_the_stale_first(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    (tdd / "role-dev.state").write_text(
        "recovered-at=2026-11-12T09:30:00\nreset-at=2026-11-12T10:00:00\nrecovered-at=2026-11-12T10:02:30\n")
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
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, _ = run_cli(reset_wait, ["recovered", "dev", "60"], env={"VERI_POLL": "20"})

    assert (code, out) == (0, "recovered dev 2026-11-12T10:02:30\n")


def test_issue_3242_marker_dev_with_lane_given_an_empty_value_exits_2_with_the_usage_line_on_stderr_without_sleeping(
        tmp_path, monkeypatch, run_cli):
    naps = []
    monkeypatch.setattr(time, "sleep", naps.append)
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    monkeypatch.setattr(time, "monotonic", lambda: 1_000_000.0)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")

    code, out, err = run_cli(reset_wait, ["marker", "dev", "--lane", ""], env={"VERI_POLL": "1"})

    assert (code, out) == (2, "")
    assert err.startswith("usage:") and "marker|recovered" in err
    assert naps == []


def test_recovered_with_an_empty_veri_reset_ack_timeout_reads_it_as_empty_and_fails_not_as_the_default_300(
        tmp_path, monkeypatch, run_cli):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "reset-request-dev").write_text("2026-11-12T10:00:00\n")
    clock = {"now": 1_000_000.0}

    def nap(seconds):
        clock["now"] += 100

    monkeypatch.setattr(time, "sleep", nap)
    monkeypatch.setattr(time, "monotonic", lambda: clock["now"])
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))

    code, out, err = run_cli(reset_wait, ["recovered", "dev"], env={"VERI_POLL": "1", "VERI_RESET_ACK_TIMEOUT": ""})

    assert (code, out, "ValueError" in err, clock["now"]) == (2, "", True, 1_000_000.0)


def test_issue_3890_the_idle_verb_exits_2_with_a_usage_line_naming_only_marker_and_recovered_and_reads_no_file(
        tmp_path, monkeypatch, run_cli):
    def no_wait(*args, **kwargs):
        raise AssertionError("reset_wait slept")

    reads = []
    monkeypatch.setattr(time, "sleep", no_wait)
    reset_wait = importlib.import_module("veri.reset_wait")
    monkeypatch.setattr(reset_wait.run_dir, "main_tree_from_files",
                        lambda cwd: reads.append(cwd) or str(tmp_path / "absent"))

    code, out, err = run_cli(reset_wait, ["idle", "dev"])

    first = (err.splitlines() or [""])[0]
    assert (code, out, first.startswith("usage: reset-wait.sh marker|recovered dev "), "idle" in err, reads) == (
        2, "", True, False, [])
