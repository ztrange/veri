"""Cases for harvest-usage.sh, driven through its command-line interface."""
import importlib
import json
import os
import subprocess

import pytest

from conftest import SCRIPTS

USAGE = "usage: harvest-usage.sh <leaf-name>\n"
RESULT = {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 228265, "duration_api_ms": 84513,
          "num_turns": 13, "result": "VERDICT: PASS", "total_cost_usd": 0.74,
          "usage": {"input_tokens": 41, "cache_creation_input_tokens": 52890,
                    "cache_read_input_tokens": 1287431, "output_tokens": 8203}}
MODELED = dict(RESULT, modelUsage={"claude-opus-5-5": {"inputTokens": 41, "costUSD": 0.74}})


@pytest.fixture
def harvest_usage():
    return importlib.import_module("veri.harvest_usage")


def write_log(directory, leaf, *lines):
    (directory / ".tdd").mkdir(exist_ok=True)
    (directory / ".tdd" / ("%s.log" % leaf)).write_text("".join(line + "\n" for line in lines))


def test_a_finished_leaf_appends_one_usage_event_with_the_numbers_of_its_closing_result_record(
        tmp_path, run_cli, harvest_usage, events):
    write_log(tmp_path, "verify-refactor", '{"type":"system","subtype":"init"}',
              '{"type":"assistant","message":{"content":[]}}', json.dumps(RESULT), "VERDICT: PASS")

    code, out, err = run_cli(harvest_usage, ["verify-refactor"], cwd=tmp_path)

    assert (code, out, err) == (0, "", "")
    assert events.records(tmp_path) == [{
        "event": "usage", "issue": "", "actor": "verifier", "phase": "refactor", "step": "", "attempt": "1",
        "skill_commit": "", "duration_ms": "228265", "duration_api_ms": "84513", "num_turns": "13",
        "total_cost_usd": "0.74", "input_tokens": "41", "output_tokens": "8203",
        "cache_read_input_tokens": "1287431", "cache_creation_input_tokens": "52890", "model": ""}]


def test_a_log_with_no_closing_result_record_appends_no_usage_event_and_says_so_naming_itself_and_the_leaf(
        tmp_path, run_cli, harvest_usage, events):
    write_log(tmp_path, "develop-green", '{"type":"system","subtype":"init"}',
              '{"type":"assistant","message":{"content":[{"type":"te')

    code, out, err = run_cli(harvest_usage, ["develop-green"], cwd=tmp_path)

    assert (code, out) == (3, "")
    assert err == ("harvest-usage.sh: no closing result record in .tdd/develop-green.log"
                   " — no usage event appended for develop-green\n")
    assert events.records(tmp_path) == []


def test_a_leaf_name_leaf_role_refuses_appends_no_usage_event_and_exits_2_naming_itself_and_the_leaf(
        tmp_path, run_cli, harvest_usage, events):
    write_log(tmp_path, "frobnicate-red", json.dumps(RESULT))

    code, out, err = run_cli(harvest_usage, ["frobnicate-red"], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert err == ("leaf-role: leaf name 'frobnicate-red' has an unknown leading word"
                   " (want develop-*|revise-*|verify-*|conductor-*)\n")
    assert events.records(tmp_path) == []


@pytest.mark.process("harvest-usage.sh run through a symlink to the scripts directory, its shim starting python3")
def test_cli_run_through_a_symlink_from_another_directory_answers_as_in_place(tmp_path):
    (tmp_path / "linked-scripts").symlink_to(SCRIPTS)
    answers = []
    for name, script in (("in-place", SCRIPTS / "harvest-usage.sh"),
                         ("linked", tmp_path / "linked-scripts" / "harvest-usage.sh")):
        run = tmp_path / name
        run.mkdir()
        write_log(run, "verify-green", json.dumps(MODELED))
        done = subprocess.run([str(script), "verify-green"], cwd=run, env=dict(os.environ), capture_output=True)
        lines = (run / ".tdd" / "events.jsonl").read_text().splitlines()
        usage = [json.loads(text) for text in lines]
        answers.append((done.returncode, done.stdout, done.stderr,
                        [{k: v for k, v in record.items() if k not in ("ts", "awake")} for record in usage]))

    assert answers[0][0] == 0
    assert [record["model"] for record in answers[0][3]] == ["claude-opus-5-5"]
    assert answers[1] == answers[0]


def test_a_missing_log_exits_1_a_log_with_no_record_exits_3_and_no_argument_exits_2_with_exactly_its_usage_line(
        tmp_path, run_cli, harvest_usage, events):
    (tmp_path / ".tdd").mkdir()

    missing = run_cli(harvest_usage, ["develop-green"], cwd=tmp_path)
    write_log(tmp_path, "develop-green", '{"type":"system"}')
    unrecorded = run_cli(harvest_usage, ["develop-green"], cwd=tmp_path)
    bare = run_cli(harvest_usage, [], cwd=tmp_path)

    assert missing[0] == 1
    assert unrecorded[0] == 3
    assert bare == (2, "", USAGE)
    assert events.records(tmp_path) == []
