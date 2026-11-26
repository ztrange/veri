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


def test_a_key_less_grader_conf_line_is_the_model_as_main_read_it(tmp_path, monkeypatch, grade_prose):
    conf(tmp_path, monkeypatch, grade_prose, "# The grader leaf's model.\nclaude-x-4\n")

    assert grade_prose.grader_model() == "claude-x-4"


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


def test_4013_veri_effort_verifier_gives_the_grader_leaf_no_effort_and_leaves_grader_confs_own(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("VERI_EFFORT_VERIFIER", "max")
    fake = fake_processes.answers({}, default=(2, "", ""))
    launched = []
    for text in ("model=sonnet-4\neffort=low\n", "model=sonnet-4\n"):
        conf(tmp_path, monkeypatch, grade_prose, text)
        run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)
        launched.append([word for word in fake.argvs[-1] if word in ("--effort", "low", "max")])

    assert launched == [["--effort", "low"], []]


def test_an_effort_value_outside_the_five_levels_exits_2_naming_grader_conf_before_any_launch(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    monkeypatch.setenv("PATH", "")
    fake = fake_processes.answers({}, default=(2, "", ""))
    conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\neffort=extreme\n")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs, "grader.conf" in err) == (2, [], True), err


def test_a_key_grader_conf_repeats_exits_2_naming_grader_conf_and_the_key_before_any_launch(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    unit_tree(tmp_path)
    monkeypatch.setenv("PATH", "")
    fake = fake_processes.answers({}, default=(2, "", ""))
    conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\neffort=low\neffort=high\n")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs, "grader.conf" in err, "effort" in err) == (2, [], True, True), err


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

    def digest(parts):
        return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()
    assert signed == [digest([text, claims, "sonnet-4", "high"]), digest([text, claims, "sonnet-4"])]


def test_adding_changing_or_removing_the_effort_line_makes_prose_owed_list_every_unit_and_exit_1(
        tmp_path, monkeypatch, run_cli, grade_prose):
    prose_owed = importlib.import_module("veri.prose_owed")
    row = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
    (tmp_path / "a.md").write_text("The widget is blue.\n")
    (tmp_path / "b.md").write_text("The widget is round.\n")
    (tmp_path / "REQUIREMENTS.md").write_text("## a.md\n\n%s\n## b.md\n\n%s" % (row, row))
    monkeypatch.chdir(tmp_path)
    answers = []
    for before, after in (("", "effort=low\n"), ("effort=low\n", "effort=high\n"), ("effort=high\n", "")):
        conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\n" + before)
        (tmp_path / "GRADED").write_text("".join("%s %s 2026-01-01 g t\n" % (unit, grade_prose.signature("REQUIREMENTS.md", unit))
                                                 for unit in ("a.md", "b.md")))
        unchanged = run_cli(prose_owed, [str(tmp_path)])[:2]
        conf(tmp_path, monkeypatch, grade_prose, "model=sonnet-4\n" + after)
        answers.append((unchanged, run_cli(prose_owed, [str(tmp_path)])[:2]))

    assert answers == [((0, ""), (1, "a.md\nb.md\n"))] * 3


def test_grader_conf_comments_name_the_effort_line_its_five_levels_and_the_re_grade_it_owes_and_set_no_effort():
    from conftest import SCRIPTS

    lines = (SCRIPTS.parent / "grader.conf").read_text(encoding="utf-8").splitlines()
    comment = " ".join(line for line in lines if line.startswith("#"))

    assert ("effort=" in comment, [level for level in ("low", "medium", "high", "xhigh", "max") if level not in comment],
            "re-grade" in comment, [line for line in lines if line.startswith("effort=")]) == (True, [], True, [])
