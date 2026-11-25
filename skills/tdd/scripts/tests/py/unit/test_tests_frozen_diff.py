"""In-process `diff --step` cases for veri/tests_frozen.py."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


NEW = "tests/test_new.py"
STEP = "step one adds a case"


def test_diff_step_prints_the_unified_diff_from_the_recorded_content_to_the_current_content_of_an_edited_recorded_file(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-two" in lines and "+two, changed" in lines
    assert " one" in lines


def test_diff_step_prints_a_unified_diff_from_empty_content_for_an_unrecorded_test_file_that_differs_from_head(
        tmp_path, run_cli, tests_frozen, fed_history):
    other = "tests/test_other.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    (tmp_path / other).write_text("alpha\n")
    fed_history(("base", "base", {NEW: "one\n", other: "alpha\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / other).write_text("alpha\nbeta\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "+alpha" in lines and "+beta" in lines
    assert not any(line.startswith("-") and not line.startswith("---") for line in lines)


def test_diff_step_prints_an_edited_recorded_file_once_with_no_second_diff_from_empty_content(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-two" in lines and "+two, changed" in lines
    assert "+one" not in lines
    assert sum(1 for line in lines if line.startswith("--- ")) == 1


def test_diff_step_prints_a_unified_diff_to_empty_content_for_a_recorded_test_file_deleted_since_the_record(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / NEW).unlink()
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-one" in lines and "-two" in lines
    assert not any(line.startswith("+") and not line.startswith("+++") for line in lines)


def test_diff_step_prints_nothing_and_exits_0_when_no_test_file_changed_since_the_record(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0
    assert run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)[0] == 0

    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    assert out == ""


def test_diff_step_exits_2_and_prints_nothing_when_the_step_has_no_record(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")

    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 2
    assert out == ""
