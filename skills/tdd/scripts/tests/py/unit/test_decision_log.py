"""In-process cases for veri/decision_log.py, decision-log.sh's work: the judge's decisions about no issue, one JSON
line each in `.tdd/decisions.jsonl` of the main working tree."""
import datetime
import importlib
import json

import pytest


@pytest.fixture
def decision_log(tmp_path, monkeypatch):
    """veri.decision_log with the main working tree at <tmp_path>."""
    module = importlib.import_module("veri.decision_log")
    monkeypatch.setattr(module.run_dir, "main_tree_from_files", lambda cwd=None: str(tmp_path))
    return module


def test_issue_4072_record_appends_one_json_line_with_the_four_fields_and_an_offset_time_and_exits_0(
        decision_log, tmp_path, run_cli):
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / ".tdd" / "decisions.jsonl"
    log.write_text('{"question": "q0", "decision": "d0", "rule": "r0", "by": "dev", "at": "2026-11-16T09:00:00+00:00"}\n')

    code, out, err = run_cli(decision_log, ["record", "Raise N to 4?", "kept N at 3", "use plan capacity", "dev"])

    lines = log.read_text().splitlines()
    record = json.loads(lines[-1])
    at = datetime.datetime.fromisoformat(record.pop("at"))
    assert (code, out, err, len(lines), record, at.utcoffset() is not None) == (
        0, "", "", 2, {"question": "Raise N to 4?", "decision": "kept N at 3", "rule": "use plan capacity", "by": "dev"},
        True)


@pytest.mark.parametrize("argv", [
    ["record"],
    ["record", "Raise N to 4?", "kept N at 3", "use plan capacity"],
    ["record", "Raise N to 4?", "", "use plan capacity", "dev"],
    ["record", "Raise N to 4?", "kept N at 3", "use plan capacity", " "],
    ["record", "Raise N to 4?", "kept N at 3", "use plan capacity", "dev", "extra"],
    [],
])
def test_issue_4072_record_with_an_argument_missing_or_empty_exits_2_and_writes_nothing(
        decision_log, tmp_path, run_cli, argv):
    code, out, err = run_cli(decision_log, argv)

    assert (code, out, err, (tmp_path / ".tdd" / "decisions.jsonl").exists()) == (2, "", decision_log.USAGE, False)


def test_issue_4072_record_writes_a_token_shape_or_a_listed_variables_value_as_redacted(
        decision_log, tmp_path, run_cli, monkeypatch):
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SECRET")
    monkeypatch.setenv("FAKE_SECRET", "hunter2-correct-horse")
    token = "ghp_" + "a1B2c3D4e5" * 4

    code, _, _ = run_cli(decision_log, ["record", "Use token %s?" % token, "no; hunter2-correct-horse stays local",
                                        "an established tool", "coord"])

    text = (tmp_path / ".tdd" / "decisions.jsonl").read_text()
    record = json.loads(text)
    assert (code, token in text, "hunter2-correct-horse" in text, record["question"], record["decision"]) == (
        0, False, False, "Use token [redacted]?", "no; [redacted] stays local")


@pytest.mark.parametrize("by", ["judge", "Owner", "vdev", "mario"])
def test_issue_4072_record_by_anything_but_a_role_name_or_owner_exits_2_and_writes_nothing(
        decision_log, tmp_path, run_cli, by):
    code, out, err = run_cli(decision_log, ["record", "Raise N to 4?", "kept N at 3", "use plan capacity", by])

    assert (code, out, err, (tmp_path / ".tdd" / "decisions.jsonl").exists()) == (2, "", decision_log.USAGE, False)


@pytest.mark.parametrize("by", ["coord", "dev", "owner"])
def test_issue_4072_record_by_a_role_name_or_owner_is_recorded_with_that_by(decision_log, tmp_path, run_cli, by):
    code, _, _ = run_cli(decision_log, ["record", "Raise N to 4?", "N=4", "the owner's answer", by])

    assert (code, json.loads((tmp_path / ".tdd" / "decisions.jsonl").read_text())["by"]) == (0, by)
