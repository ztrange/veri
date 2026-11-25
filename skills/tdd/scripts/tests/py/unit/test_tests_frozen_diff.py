"""In-process `diff --step` cases for veri/tests_frozen.py."""
import importlib
import pathlib

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


def test_diff_step_prints_the_unified_diff_from_its_head_content_for_an_unrecorded_tracked_test_file_so_a_removed_line_shows_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    other = "tests/test_other.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    (tmp_path / other).write_text("alpha\nassert ok\n")
    fed_history(("base", "base", {NEW: "one\n", other: "alpha\nassert ok\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / other).write_text("alpha\nbeta\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-assert ok" in lines and "+beta" in lines and " alpha" in lines
    assert "+alpha" not in lines


def test_diff_step_prints_a_unified_diff_from_empty_content_for_an_untracked_test_file_outside_the_record_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    other = "tests/test_other.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / other).write_text("alpha\nbeta\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "+alpha" in lines and "+beta" in lines
    assert not any(line.startswith("-") and not line.startswith("---") for line in lines)


def test_diff_step_prints_nothing_and_exits_0_when_the_record_holds_a_deleted_test_file_still_deleted_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    gone = "tests/test_gone.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n", gone: "gone\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0
    assert run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)[0] == 0

    code, out, err = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert (code, out, err) == (0, "", "")


def test_diff_step_prints_a_unified_diff_from_empty_content_for_a_test_file_the_record_holds_as_deleted_that_exists_again_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    gone = "tests/test_gone.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n", gone: "gone\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / gone).write_text("back\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "+back" in lines
    assert not any(line.startswith("-") and not line.startswith("---") for line in lines)


def test_diff_step_prints_a_unified_diff_from_its_head_content_to_empty_for_an_unrecorded_tracked_test_file_deleted_since_the_record_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    other = "tests/test_other.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    (tmp_path / other).write_text("alpha\n")
    fed_history(("base", "base", {NEW: "one\n", other: "alpha\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / other).unlink()
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert "-alpha" in lines
    assert not any(line.startswith("+") and not line.startswith("+++") for line in lines)


def test_diff_step_prints_nothing_on_a_replaces_case_step_when_only_the_suite_it_names_changed_as_check_passes_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    suite = "tests/old.py"
    step = "⟦replaces-case⟧ replaces 'old case' in %s" % suite
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    (tmp_path / suite).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n", suite: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)[0] == 0

    (tmp_path / suite).write_text("case deleted\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", step], cwd=tmp_path)

    assert (checked, code, out) == (0, 0, "")


def test_usage_names_diff_step_4730(tests_frozen):
    assert "diff --step <step-text>" in tests_frozen.USAGE


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


def test_diff_step_exits_2_and_prints_nothing_when_an_edited_recorded_files_kept_content_is_missing_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0
    record = tests_frozen.record_path(STEP)
    kept = tests_frozen._kept_path(str(tmp_path / record), NEW)
    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    pathlib.Path(kept).unlink()

    code, out, err = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert err != ""


def test_diff_without_step_exits_2_with_the_usage_line_4730(tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    (tmp_path / NEW).write_text("one\n")
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)[0] == 0
    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    record = tests_frozen.record_path(STEP)

    code, out, err = run_cli(tests_frozen, ["diff", record], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert tests_frozen.USAGE in err


def test_diff_step_diffs_each_of_two_edited_recorded_files_from_its_own_recorded_content_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    other = "tests/test_other.py"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / NEW).parent.mkdir(parents=True)
    fed_history(("base", "base", {NEW: "one\n", other: "alpha\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    (tmp_path / other).write_text("alpha\nbeta\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, NEW, other], cwd=tmp_path)[0] == 0

    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    (tmp_path / other).write_text("alpha\nbeta, changed\n")
    code, out, _ = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=tmp_path)

    assert code == 0
    lines = out.splitlines()
    assert ["-two", "+two, changed"] == [line for line in lines if line in ("-two", "+two, changed")]
    assert ["-beta", "+beta, changed"] == [line for line in lines if line in ("-beta", "+beta, changed")]
    assert not any(line.startswith(("+alpha", "-alpha", "+one", "-one")) for line in lines)


def test_diff_step_run_from_a_subdirectory_reads_the_kept_content_beside_the_record_it_named_there_4730(
        tmp_path, run_cli, tests_frozen, fed_history):
    sub = tmp_path / "tests"
    (sub / ".tdd").mkdir(parents=True)
    fed_history(("base", "base", {NEW: "one\n"}), root=tmp_path)
    (tmp_path / NEW).write_text("one\ntwo\n")
    assert run_cli(tests_frozen, ["record", "--step", STEP, "test_new.py"], cwd=sub)[0] == 0

    (tmp_path / NEW).write_text("one\ntwo, changed\n")
    code, out, err = run_cli(tests_frozen, ["diff", "--step", STEP], cwd=sub)

    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert "-two" in lines and "+two, changed" in lines
