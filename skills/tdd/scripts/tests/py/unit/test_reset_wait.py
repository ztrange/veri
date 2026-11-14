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
