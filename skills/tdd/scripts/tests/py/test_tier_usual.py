"""In-process cases for veri/tier_usual.py, the module tier-usual.sh is a shim over."""
import importlib
import json

import pytest


@pytest.fixture
def tier_usual():
    return importlib.import_module("veri.tier_usual")


def test_main_with_no_argument_returns_2_with_nothing_on_stdout_and_the_usage_line_on_stderr(capsys, tier_usual):
    code = tier_usual.main([])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "usage: tier-usual.sh <tier>\n")


def _event(event, tier, seconds):
    return json.dumps({"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green",
                       "step": "1", "event": event, "attempt": "1", "skill_commit": "abc1234",
                       "tier": tier, "suites": "one.test.sh", "seconds": seconds})


def test_main_with_a_tier_returns_0_and_prints_the_median_of_its_last_10_test_run_events(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text("".join(_event(*e) + "\n" for e in [
        ("test-run", "fast", "100"),
        ("test-run", "fast", "200"),
        ("test-run", "fast", "7"),
        ("test-run", "fast", "3"),
        ("test-run", "all", "900"),
        ("test-run", "fast", "10"),
        ("test-run", "fast", "1"),
        ("leaf-exit", "fast", "900"),
        ("test-run", "fast", "9"),
        ("test-run", "fast", "5"),
        ("test-run", "fast", "2"),
        ("test-run", "fast", "8"),
        ("test-run", "fast", "4"),
        ("test-run", "fast", "6"),
    ]))
    monkeypatch.chdir(tmp_path)
    code = tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "5.5\n")


def test_main_with_a_tier_holding_an_odd_number_of_test_run_events_prints_the_middle_one_sorted(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text("".join(_event(*e) + "\n" for e in [
        ("test-run", "fast", "3"),
        ("test-run", "fast", "1"),
        ("test-run", "all", "900"),
        ("test-run", "fast", "4"),
        ("test-run", "fast", "9"),
        ("test-run", "fast", "7"),
    ]))
    monkeypatch.chdir(tmp_path)
    code = tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "4.0\n")


def test_main_prints_a_whole_median_as_a_float_repr_with_a_trailing_point_zero(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text("".join(_event(*e) + "\n" for e in [
        ("test-run", "fast", "3"),
        ("test-run", "fast", "5"),
    ]))
    monkeypatch.chdir(tmp_path)
    code = tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "4.0\n")


def test_main_with_no_test_run_event_for_the_tier_raises_and_prints_nothing_on_stdout(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text("".join(_event(*e) + "\n" for e in [
        ("test-run", "all", "900"),
        ("leaf-exit", "fast", "5"),
    ]))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(Exception):
        tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert out == ""


def test_main_with_no_event_log_raises_and_prints_nothing_on_stdout(capsys, monkeypatch, tmp_path, tier_usual):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(Exception):
        tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert out == ""


def test_main_with_a_line_of_the_event_log_that_is_not_json_raises_and_prints_nothing_on_stdout(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text(_event("test-run", "fast", "5") + "\n" + "not json\n")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(Exception):
        tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert out == ""


def test_main_with_a_test_run_event_whose_seconds_is_not_a_number_raises_and_prints_nothing_on_stdout(capsys, monkeypatch, tmp_path, tier_usual):
    log = tmp_path / ".tdd" / "events.jsonl"
    log.parent.mkdir()
    log.write_text("".join(_event(*e) + "\n" for e in [
        ("test-run", "fast", "5"),
        ("test-run", "fast", "slow"),
    ]))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(Exception):
        tier_usual.main(["fast"])
    out, _ = capsys.readouterr()
    assert out == ""
