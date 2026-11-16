"""The grader's effort, set by an `effort=` line in grader.conf (PRD 024.10)."""
import hashlib
import importlib
import json

import pytest


@pytest.fixture
def grade_prose():
    return importlib.import_module("veri.grade_prose")


def conf(tmp_path, monkeypatch, grade_prose, text):
    scripts = tmp_path / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text(text)
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(scripts))


def test_the_grader_model_is_the_model_lines_value_whether_an_effort_line_sits_above_or_below_it(
        tmp_path, monkeypatch, grade_prose):
    models = []
    for text in ("# c\neffort=low\nmodel=claude-x-4\n", "model=claude-x-4\neffort=low\n"):
        conf(tmp_path, monkeypatch, grade_prose, text)
        models.append(grade_prose.grader_model())

    assert models == ["claude-x-4", "claude-x-4"]


def unit_tree(tmp_path):
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")


def test_the_grader_leaf_is_launched_with_effort_level_from_an_effort_line_and_without_effort_when_there_is_none(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    monkeypatch.setenv("PATH", "")
    fake = fake_processes.answers({}, default=(2, "", ""))
    launched = []
    for text in ("model=sonnet-4\neffort=low\n", "model=sonnet-4\n"):
        conf(tmp_path, monkeypatch, grade_prose, text)
        run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)
        launched.append([word for word in fake.argvs[-1] if word in ("--effort", "low")])

    assert launched == [["--effort", "low"], []]


def test_an_effort_value_outside_the_five_levels_exits_2_naming_grader_conf_before_any_launch(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    monkeypatch.setenv("PATH", "")
    fake = fake_processes.answers({}, default=(2, "", ""))
    conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\neffort=extreme\n")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs, "grader.conf" in err) == (2, [], True), err


def test_the_grading_event_carries_the_effort_level_or_default_when_grader_conf_has_no_effort_line(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
    monkeypatch.setenv("PATH", "")
    fake_processes.answers({}, default=(0, "", ""))
    for text in ("model=sonnet-4\neffort=medium\n", "model=sonnet-4\n"):
        conf(tmp_path, monkeypatch, grade_prose, text)
        run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    gradings = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [g.get("effort") for g in gradings if g.get("event") == "grading"] == ["medium", "default"]


def test_the_signature_stamps_the_effort_level_as_a_fourth_part_and_todays_three_parts_with_no_effort_line(
        tmp_path, monkeypatch, grade_prose):
    unit_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    claims = "A1\tThe widget is blue.\n"
    text = "The widget is painted a deep blue.\n"
    signed = []
    for line in ("effort=high\n", ""):
        conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\n" + line)
        signed.append(grade_prose.signature("REQUIREMENTS.md", "unit.md"))

    digest = lambda parts: hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()
    assert signed == [digest([text, claims, "sonnet-4", "high"]), digest([text, claims, "sonnet-4"])]
