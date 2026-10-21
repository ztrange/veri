"""In-process cases for veri/harvest_usage.py, the module harvest-usage.sh is a shim over."""
import importlib
import json

import pytest


@pytest.fixture
def harvest_usage():
    return importlib.import_module("veri.harvest_usage")


def test_main_with_no_leaf_name_prints_usage_to_stderr_and_returns_2(capsys, harvest_usage):
    code = harvest_usage.main([])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "usage: harvest-usage.sh <leaf-name>\n")


def test_main_on_a_log_ending_in_a_closing_result_record_appends_one_usage_record_with_its_numbers_and_role_and_returns_0(
        tmp_path, monkeypatch, harvest_usage, events):
    record = {"type": "result", "subtype": "success", "duration_ms": 228265, "duration_api_ms": 84513,
              "num_turns": 13, "total_cost_usd": 0.74,
              "usage": {"input_tokens": 41, "cache_creation_input_tokens": 52890,
                        "cache_read_input_tokens": 1287431, "output_tokens": 8203}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-green-2.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n" + json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "77")
    monkeypatch.setenv("VERI_STEP", "3")

    events.refuse_event_sh()
    code = harvest_usage.main(["develop-green-2"])

    assert (code, events.records()) == (0, [{
        "issue": "77", "actor": "developer", "phase": "green", "step": "3", "event": "usage", "attempt": "2",
        "skill_commit": "", "duration_ms": "228265", "duration_api_ms": "84513", "num_turns": "13",
        "total_cost_usd": "0.74", "input_tokens": "41", "output_tokens": "8203",
        "cache_read_input_tokens": "1287431", "cache_creation_input_tokens": "52890", "model": ""}])


def _closing_log(tmp_path, name):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 2, "num_turns": 3, "total_cost_usd": 0.5,
              "usage": {"input_tokens": 4, "cache_creation_input_tokens": 5,
                        "cache_read_input_tokens": 6, "output_tokens": 7}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / ("%s.log" % name)).write_text(json.dumps(record) + "\n")


def test_main_with_an_empty_leaf_name_prints_usage_to_stderr_and_returns_2(capsys, harvest_usage):
    code = harvest_usage.main([""])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "usage: harvest-usage.sh <leaf-name>\n")


def test_main_on_a_leaf_name_with_no_phase_says_so_appends_no_record_and_returns_2(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    _closing_log(tmp_path, "develop")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["develop"])

    captured = capsys.readouterr()
    assert (code, events.records(), captured.out) == (2, [], "")
    assert captured.err == ("leaf-role: leaf name 'develop' says no phase "
                            "(want develop-*|revise-*|verify-*|conductor-*)\n")


def test_main_returns_2_with_nothing_on_stdout_when_the_usage_record_cannot_be_appended(
        tmp_path, monkeypatch, capfd, harvest_usage, events):
    _closing_log(tmp_path, "verify-green")
    events.unappendable(tmp_path)
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["verify-green"])

    assert (code, capfd.readouterr().out, events.records()) == (2, "", [])


@pytest.mark.parametrize("models", [["claude-opus-5-5"], ["claude-opus-5-5", "claude-haiku-4-5-20251001"]])
def test_main_on_a_closing_record_with_model_usage_appends_a_model_field_listing_every_model_named(
        tmp_path, monkeypatch, harvest_usage, events, models):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1, "total_cost_usd": 0.5,
              "usage": {"input_tokens": 20, "output_tokens": 4000,
                        "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
              "modelUsage": {model: {"inputTokens": 1, "outputTokens": 1, "cacheReadInputTokens": 0,
                                     "cacheCreationInputTokens": 0, "costUSD": 0.25, "canonicalModel": model}
                             for model in models}}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_text(json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    assert harvest_usage.main(["verify-green"]) == 0

    [record] = events.records()
    assert sorted(filter(None, record["model"].split(","))) == sorted(models)


@pytest.mark.parametrize("model_usage", [
    None,
    {"claude-opus-5-5": {"inputTokens": 12, "outputTokens": 3000, "cacheReadInputTokens": 40,
                         "cacheCreationInputTokens": 7, "costUSD": 0.5, "canonicalModel": "claude-opus-5-5"},
     "claude-haiku-4-5-20251001": {"inputTokens": 8, "outputTokens": 1000, "cacheReadInputTokens": 0,
                                   "cacheCreationInputTokens": 3, "costUSD": 0.25,
                                   "canonicalModel": "claude-haiku-4-5-20251001"}},
])
def test_main_appends_a_model_usage_field_with_each_models_figures_only_when_the_record_has_model_usage(
        tmp_path, monkeypatch, capsys, harvest_usage, events, model_usage):
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1, "total_cost_usd": 0.75,
              "usage": {"input_tokens": 20, "output_tokens": 4000,
                        "cache_read_input_tokens": 40, "cache_creation_input_tokens": 10}}
    if model_usage is not None:
        record["modelUsage"] = model_usage
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_text(json.dumps(record) + "\n")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["verify-green"])

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "", "")
    [record] = events.records()
    assert (record["event"], record["total_cost_usd"], record["output_tokens"]) == ("usage", "0.75", "4000")
    carried = [json.loads(record["model_usage"])] if "model_usage" in record else []
    assert carried == ([] if model_usage is None else [model_usage])


_RECORD = {"type": "result", "duration_ms": 228265.0, "duration_api_ms": 84513, "num_turns": 13,
           "total_cost_usd": 1e-05,
           "usage": {"input_tokens": 41, "cache_creation_input_tokens": 52890,
                     "cache_read_input_tokens": 1287431, "output_tokens": 8203}}
_NUMBERS = {"duration_ms": "228265.0", "duration_api_ms": "84513", "num_turns": "13", "total_cost_usd": "1e-05",
            "input_tokens": "41", "output_tokens": "8203", "cache_read_input_tokens": "1287431",
            "cache_creation_input_tokens": "52890", "model": ""}
_VERIFIER = {"issue": "", "actor": "verifier", "phase": "green", "step": "", "event": "usage", "attempt": "1",
             "skill_commit": ""}


@pytest.mark.parametrize("name, log, expected_code, expected_err, expected_records", [
    ("bogus-green", json.dumps({"type": "system", "subtype": "init"}) + "\n", 3,
     "harvest-usage.sh: no closing result record in .tdd/bogus-green.log — no usage event appended for bogus-green\n",
     []),
    ("bogus-green", None, 1, None, []),
    ("verify-green", json.dumps({k: v for k, v in _RECORD.items() if k != "usage"}) + "\n", 2,
     "harvest-usage.sh: the closing result record in .tdd/verify-green.log carries no usage — no usage event appended for verify-green\n", []),
    ("verify-green", json.dumps({k: v for k, v in _RECORD.items() if k != "num_turns"}) + "\n", 1, None, []),
    ("verify-green", json.dumps(dict(_RECORD, usage={k: v for k, v in _RECORD["usage"].items()
                                                     if k != "output_tokens"})) + "\n", 1, None, []),
    ("verify-green", json.dumps(dict(_RECORD, num_turns=99)) + "\n" + json.dumps(_RECORD) + "\n"
     + "harvest: the leaf exited 0\n", 0, "", [dict(_VERIFIER, **_NUMBERS)]),
], ids=["unknown-name-no-record-3", "unknown-name-no-log-1", "no-usage-2", "no-num-turns-1",
        "no-output-tokens-1", "last-result-record-before-a-trailing-line-0"])
def test_main_ports_harvest_usage_sh_quirks_exit_codes_closing_record_number_text_and_no_record_diagnostic(
        tmp_path, monkeypatch, capsys, harvest_usage, events, name, log, expected_code, expected_err, expected_records):
    (tmp_path / ".tdd").mkdir()
    if log is not None:
        (tmp_path / ".tdd" / ("%s.log" % name)).write_text(log)
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main([name])

    captured = capsys.readouterr()
    assert (code, events.records(), captured.out) == (expected_code, expected_records, "")
    if expected_err is not None:
        assert captured.err == expected_err


def test_main_on_a_closing_result_record_with_no_usage_key_exits_2_with_one_line_and_no_traceback_1497(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_text(
        json.dumps({k: v for k, v in _RECORD.items() if k != "usage"}) + "\n")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["verify-green"])

    captured = capsys.readouterr()
    assert (code, events.records(), captured.out) == (2, [], "")
    assert "Traceback" not in captured.err
    [line] = captured.err.splitlines()
    assert "harvest-usage.sh" in line and ".tdd/verify-green.log" in line and "carries no usage" in line


def test_main_on_a_log_that_is_not_valid_utf8_exits_2_with_one_line_and_no_traceback_1497(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.log").write_bytes(b'\xff\xfe\n' + json.dumps(_RECORD).encode() + b"\n")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["verify-green"])

    captured = capsys.readouterr()
    assert (code, events.records(), captured.out) == (2, [], "")
    assert "Traceback" not in captured.err
    [line] = captured.err.splitlines()
    assert "harvest-usage.sh" in line and ".tdd/verify-green.log" in line and "not valid UTF-8" in line


def test_main_on_a_log_path_that_is_a_directory_exits_2_with_one_line_and_no_traceback_1497(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    (tmp_path / ".tdd" / "verify-green.log").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["verify-green"])

    captured = capsys.readouterr()
    assert (code, events.records(), captured.out) == (2, [], "")
    assert "Traceback" not in captured.err
    [line] = captured.err.splitlines()
    assert "harvest-usage.sh" in line and ".tdd/verify-green.log" in line and "is a directory" in line


def test_main_on_the_grader_leaf_grade_prose_appends_a_usage_record_with_actor_grader_and_phase_prose_and_nothing_on_stderr_1887(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    _closing_log(tmp_path, "grade-prose")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "77")

    events.refuse_event_sh()
    code = harvest_usage.main(["grade-prose"])

    captured = capsys.readouterr()
    assert (code, captured.err) == (0, "")
    assert [(r["actor"], r["phase"], r["event"]) for r in events.records()] == [("grader", "prose", "usage")]


def test_main_on_the_author_leaf_author_skill_edit_1_appends_a_usage_record_with_actor_author_phase_skill_edit_and_attempt_1_1949(
        tmp_path, monkeypatch, capsys, harvest_usage, events):
    _closing_log(tmp_path, "author-skill-edit-1")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_ISSUE", "77")

    events.refuse_event_sh()
    code = harvest_usage.main(["author-skill-edit-1"])

    assert code == 0
    assert [(r["actor"], r["phase"], r["attempt"], r["event"]) for r in events.records()] == [
        ("author", "skill-edit", "1", "usage")]


def test_main_gives_every_leaf_name_the_actor_phase_and_attempt_leaf_role_gives_it_1949(
        tmp_path, monkeypatch, harvest_usage, events):
    leaf_role = importlib.import_module("veri.leaf_role")
    names = ["develop-red", "develop-red-2", "develop-red\n-2", "revise-green-3", "verify-refactor",
             "grade-prose\n-4", "author-skill-edit-1", "conductor-plan", "develop-exhausted"]
    monkeypatch.chdir(tmp_path)
    events.refuse_event_sh()
    for name in names:
        _closing_log_named(tmp_path, name)
        assert harvest_usage.main([name]) == 0, name
    got = [(r["actor"], r["phase"], r["attempt"]) for r in events.records()]
    want = [(role["VERI_ACTOR"], role["VERI_PHASE"], role["VERI_ATTEMPT"])
            for role in map(leaf_role.leaf_role, names)]
    assert got == want


def _closing_log_named(tmp_path, name):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    record = {"type": "result", "duration_ms": 1, "duration_api_ms": 2, "num_turns": 3, "total_cost_usd": 0.5,
              "usage": {"input_tokens": 4, "cache_creation_input_tokens": 5,
                        "cache_read_input_tokens": 6, "output_tokens": 7}}
    (tmp_path / ".tdd" / ("%s.log" % name)).write_text(json.dumps(record) + "\n")


def test_main_harvests_a_leading_word_added_to_leaf_roles_actor_table_with_that_actor_and_no_change_to_harvest_usage_1949(
        tmp_path, monkeypatch, harvest_usage, events):
    monkeypatch.setitem(harvest_usage.leaf_role.ACTORS, "plan", "planner")
    _closing_log_named(tmp_path, "plan-scope-2")
    monkeypatch.chdir(tmp_path)

    events.refuse_event_sh()
    code = harvest_usage.main(["plan-scope-2"])

    assert code == 0
    assert [(r["actor"], r["phase"], r["attempt"], r["event"]) for r in events.records()] == [
        ("planner", "scope", "2", "usage")]
