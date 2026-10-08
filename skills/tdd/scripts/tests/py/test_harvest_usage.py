"""In-process cases for veri/harvest_usage.py, the module harvest-usage.sh is a shim over."""
import importlib
import json
import os
import subprocess

import pytest


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


@pytest.mark.parametrize("models", [["claude-opus-5-5"], ["claude-opus-5-5", "claude-haiku-4-5-20251001"]])
def test_main_on_a_closing_record_with_model_usage_passes_event_sh_a_model_key_listing_every_model_named(
        tmp_path, monkeypatch, harvest_usage, models):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1, "total_cost_usd": 0.5,
              "usage": {"input_tokens": 20, "output_tokens": 4000,
                        "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
              "modelUsage": {model: {"inputTokens": 1, "outputTokens": 1, "cacheReadInputTokens": 0,
                                     "cacheCreationInputTokens": 0, "costUSD": 0.25, "canonicalModel": model}
                             for model in models}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_text(json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)
    calls = _fake_event_sh(monkeypatch, 0)

    assert harvest_usage.main(["verify-green"]) == 0

    model_args = [arg for arg in calls[0] if arg.startswith("model=")]
    assert len(model_args) == 1
    assert sorted(filter(None, model_args[0][len("model="):].split(","))) == sorted(models)


@pytest.mark.parametrize("model_usage", [
    None,
    {"claude-opus-5-5": {"inputTokens": 12, "outputTokens": 3000, "cacheReadInputTokens": 40,
                         "cacheCreationInputTokens": 7, "costUSD": 0.5, "canonicalModel": "claude-opus-5-5"},
     "claude-haiku-4-5-20251001": {"inputTokens": 8, "outputTokens": 1000, "cacheReadInputTokens": 0,
                                   "cacheCreationInputTokens": 3, "costUSD": 0.25,
                                   "canonicalModel": "claude-haiku-4-5-20251001"}},
])
def test_main_passes_event_sh_a_model_usage_key_with_each_models_figures_only_when_the_record_has_model_usage(
        tmp_path, monkeypatch, capsys, harvest_usage, model_usage):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1, "total_cost_usd": 0.75,
              "usage": {"input_tokens": 20, "output_tokens": 4000,
                        "cache_read_input_tokens": 40, "cache_creation_input_tokens": 10}}
    if model_usage is not None:
        record["modelUsage"] = model_usage
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_text(json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)
    calls = _fake_event_sh(monkeypatch, 0)

    code = harvest_usage.main(["verify-green"])

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "", "")
    assert "total_cost_usd=0.75" in calls[0] and "output_tokens=4000" in calls[0]
    carried = [json.loads(arg[len("model_usage="):]) for arg in calls[0] if arg.startswith("model_usage=")]
    assert carried == ([] if model_usage is None else [model_usage])


_RECORD = {"type": "result", "duration_ms": 228265.0, "duration_api_ms": 84513, "num_turns": 13,
           "total_cost_usd": 1e-05,
           "usage": {"input_tokens": 41, "cache_creation_input_tokens": 52890,
                     "cache_read_input_tokens": 1287431, "output_tokens": 8203}}
_NUMBERS = ["duration_ms=228265.0", "duration_api_ms=84513", "num_turns=13", "total_cost_usd=1e-05",
            "input_tokens=41", "output_tokens=8203", "cache_read_input_tokens=1287431",
            "cache_creation_input_tokens=52890", "model="]


@pytest.mark.parametrize("name, log, expected_code, expected_err, expected_calls", [
    ("bogus-green", json.dumps({"type": "system", "subtype": "init"}) + "\n", 3,
     "harvest-usage.sh: no closing result record in .tdd/bogus-green.log — no usage event appended for bogus-green\n",
     []),
    ("bogus-green", None, 1, None, []),
    ("verify-green", json.dumps({k: v for k, v in _RECORD.items() if k != "usage"}) + "\n", 1, None, []),
    ("verify-green", json.dumps({k: v for k, v in _RECORD.items() if k != "num_turns"}) + "\n", 1, None, []),
    ("verify-green", json.dumps(dict(_RECORD, usage={k: v for k, v in _RECORD["usage"].items()
                                                     if k != "output_tokens"})) + "\n", 1, None, []),
    ("verify-green", json.dumps(dict(_RECORD, num_turns=99)) + "\n" + json.dumps(_RECORD) + "\n"
     + "harvest: the leaf exited 0\n", 0, "", [["usage"] + _NUMBERS]),
], ids=["unknown-name-no-record-3", "unknown-name-no-log-1", "no-usage-1", "no-num-turns-1",
        "no-output-tokens-1", "last-result-record-before-a-trailing-line-0"])
def test_main_ports_harvest_usage_sh_quirks_exit_codes_closing_record_number_text_and_no_record_diagnostic(
        tmp_path, monkeypatch, capsys, harvest_usage, name, log, expected_code, expected_err, expected_calls):
    (tmp_path / ".tdd").mkdir()
    if log is not None:
        (tmp_path / ".tdd" / ("%s.log" % name)).write_text(log)
    monkeypatch.chdir(tmp_path)
    calls = _fake_event_sh(monkeypatch, 0)

    code = harvest_usage.main([name])

    captured = capsys.readouterr()
    assert (code, [args[1:] for args in calls], captured.out) == (expected_code, expected_calls, "")
    if expected_err is not None:
        assert captured.err == expected_err
