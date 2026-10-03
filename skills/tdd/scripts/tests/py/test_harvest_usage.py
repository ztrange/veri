"""In-process cases for veri/harvest_usage.py, the module harvest-usage.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def harvest_usage():
    return importlib.import_module("veri.harvest_usage")


def test_main_with_no_leaf_name_prints_usage_to_stderr_and_returns_2(capsys, harvest_usage):
    code = harvest_usage.main([])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "usage: harvest-usage.sh <leaf-name>\n")


def test_main_on_a_log_ending_in_a_closing_result_record_calls_event_sh_once_as_usage_with_its_numbers_and_role_and_returns_0(
        tmp_path, monkeypatch, harvest_usage):
    record = {"type": "result", "subtype": "success", "duration_ms": 228265, "duration_api_ms": 84513,
              "num_turns": 13, "total_cost_usd": 0.74,
              "usage": {"input_tokens": 41, "cache_creation_input_tokens": 52890,
                        "cache_read_input_tokens": 1287431, "output_tokens": 8203}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-green-2.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n" + json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)
    calls = []

    def fake_run(args, **kwargs):
        calls.append((list(args), kwargs.get("env", os.environ)))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = harvest_usage.main(["develop-green-2"])

    assert code == 0
    assert len(calls) == 1
    args, env = calls[0]
    assert str(args[0]).endswith("/event.sh")
    assert args[1:] == ["usage", "duration_ms=228265", "duration_api_ms=84513", "num_turns=13",
                        "total_cost_usd=0.74", "input_tokens=41", "output_tokens=8203",
                        "cache_read_input_tokens=1287431", "cache_creation_input_tokens=52890", "model="]
    assert (env["VERI_ACTOR"], env["VERI_PHASE"], env["VERI_ATTEMPT"]) == ("developer", "green", "2")


def _closing_log(tmp_path, name):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 2, "num_turns": 3, "total_cost_usd": 0.5,
              "usage": {"input_tokens": 4, "cache_creation_input_tokens": 5,
                        "cache_read_input_tokens": 6, "output_tokens": 7}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / ("%s.log" % name)).write_text(json.dumps(record) + "\n")


def _fake_event_sh(monkeypatch, returncode):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        return subprocess.CompletedProcess(args, returncode, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_with_an_empty_leaf_name_prints_usage_to_stderr_and_returns_2(capsys, harvest_usage):
    code = harvest_usage.main([""])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "usage: harvest-usage.sh <leaf-name>\n")


def test_main_on_a_leaf_name_with_no_phase_says_so_calls_no_event_sh_and_returns_2(
        tmp_path, monkeypatch, capsys, harvest_usage):
    _closing_log(tmp_path, "develop")
    monkeypatch.chdir(tmp_path)
    calls = _fake_event_sh(monkeypatch, 0)

    code = harvest_usage.main(["develop"])

    captured = capsys.readouterr()
    assert (code, calls, captured.out) == (2, [], "")
    assert captured.err == ("leaf-role: leaf name 'develop' says no phase "
                            "(want develop-*|revise-*|verify-*|conductor-*)\n")


@pytest.mark.parametrize("event_code, expected", [(1, 1), (3, 3), (5, 2), (127, 2)])
def test_main_passes_event_sh_exit_codes_0_to_3_through_and_maps_any_other_to_2(
        tmp_path, monkeypatch, harvest_usage, event_code, expected):
    _closing_log(tmp_path, "verify-green")
    monkeypatch.chdir(tmp_path)
    _fake_event_sh(monkeypatch, event_code)

    assert harvest_usage.main(["verify-green"]) == expected
