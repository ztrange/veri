"""In-process `check --step` cases for veri/tests_frozen.py, on a case history fed by fed_history (PRD 017.4)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
NEW, OTHER, GONE, LATER = "tests/test_new.py", "tests/test_other.py", "tests/test_gone.py", "tests/test_later.py"
UNTRACKED, EXTRA, OLD_SH = "tests/test_untracked.py", "tests/test_extra.py", "tests/old.test.sh"
OLD_PY, FIXTURE, SUITE = "tests/test_old.py", "tests/conftest.py", "a.test.sh"
FIXTURE_STEP = ("the case passes: repairs the fixture 'db' in %s, reproduced by a case in %s ⟦fixture-repair⟧"
                % (FIXTURE, NEW))
STEP = "step one adds a case"


@pytest.fixture
def committed_once(tmp_path, fed_history):
    """One commit ("base") holding `files`; the work tree is tmp_path, written with the same files."""
    def commit(files):
        (tmp_path / ".tdd").mkdir()
        for name, text in files.items():
            (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / name).write_text(text)
        fed_history(("base", "base", files), root=tmp_path)
    return commit


@pytest.fixture
def red_recorded(tmp_path, run_cli, tests_frozen, committed_once):
    """`files` committed, red's edit to NEW (and the deletion of each of `deleted`) recorded under `step`; record's exit code."""
    def record(files, deleted=(), step=STEP):
        committed_once(files)
        (tmp_path / NEW).write_text("one\ntwo\n")
        for name in deleted:
            (tmp_path / name).unlink()
        return run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)[0]
    return record


def from_subdirectory(root):
    """A subdirectory `sub` that reaches the root's .tdd and tests through symlinks, as the process cases built it."""
    (root / "sub").mkdir()
    (root / "sub/.tdd").symlink_to("../.tdd")
    (root / "sub/tests").symlink_to("../tests")
    return root / "sub"


def test_check_step_exits_1_naming_a_modified_test_file_red_did_not_record_and_not_a_modified_non_test_file_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", OTHER: "one\n", "lib.py": "one\n"})

    (tmp_path / OTHER).write_text("one, weakened\n")
    (tmp_path / "lib.py").write_text("one, changed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (1, OTHER + "\n")


def test_check_step_run_from_a_subdirectory_still_exits_1_naming_a_test_file_red_did_not_record_1773(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", OTHER: "one\n"})
    sub = from_subdirectory(tmp_path)

    (tmp_path / OTHER).write_text("one, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=sub)

    assert (code, out) == (1, OTHER + "\n")


def test_check_step_run_from_a_subdirectory_exits_1_naming_an_untracked_test_file_outside_it_by_its_path_from_the_root_1960(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n"})
    sub = from_subdirectory(tmp_path)

    (tmp_path / UNTRACKED).write_text("new\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=sub)

    assert (code, out) == (1, UNTRACKED + "\n")


def test_check_step_exits_1_naming_a_test_file_red_did_not_record_that_was_deleted_since_head_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", OTHER: "one\n"})

    (tmp_path / OTHER).unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (1, OTHER + "\n")


def test_check_step_exits_0_when_the_only_change_outside_the_record_is_a_test_file_red_deleted_1772(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", GONE: "one\n"}, deleted=[GONE])

    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_step_exits_1_naming_a_test_file_the_record_holds_as_deleted_that_exists_again_1772(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", GONE: "one\n"}, deleted=[GONE])

    (tmp_path / GONE).write_text("back\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (1, GONE + "\n")


def test_check_step_exits_1_naming_a_test_file_deleted_after_record_step_held_another_deletion_1772(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", GONE: "one\n", LATER: "one\n"}, deleted=[GONE])

    (tmp_path / LATER).unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (1, LATER + "\n")


def test_check_step_exits_1_naming_an_untracked_test_file_red_did_not_record_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n"})

    (tmp_path / EXTRA).write_text("added by green\n")
    (tmp_path / "notes.py").write_text("not a test\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (1, EXTRA + "\n")


def test_check_step_exits_0_printing_nothing_when_only_non_test_files_changed_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", "lib.py": "one\n", "gone.py": "one\n"})

    (tmp_path / "lib.py").write_text("one, changed\n")
    (tmp_path / "gone.py").unlink()
    (tmp_path / "notes.py").write_text("not a test\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_step_exits_0_on_a_replaces_case_step_when_only_the_suite_it_names_changed_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    step = "⟦replaces-case⟧ replaces 'old case' in %s" % OLD_SH
    red_recorded({NEW: "one\n", OLD_SH: "one\n"}, step=step)

    (tmp_path / OLD_SH).write_text("case deleted\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_step_on_a_replaces_case_step_exits_1_naming_another_unrecorded_test_file_and_not_the_suite_it_names_1733(
        tmp_path, run_cli, tests_frozen, red_recorded):
    step = "⟦replaces-case⟧ replaces 'old case' in %s" % OLD_SH
    red_recorded({NEW: "one\n", OLD_SH: "one\n", OTHER: "one\n"}, step=step)

    (tmp_path / OLD_SH).write_text("case deleted\n")
    (tmp_path / OTHER).write_text("one, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, OTHER + "\n")


@pytest.mark.parametrize("mark", ["⟦suite-repair⟧", "⟦ci-repair⟧"])
def test_check_step_still_exits_0_on_a_repair_step_when_an_unrecorded_test_file_differs_from_head_1733(
        tmp_path, run_cli, tests_frozen, committed_once, mark):
    committed_once({OTHER: "one\n"})
    step = "Repair the red CI run %s" % mark

    (tmp_path / OTHER).write_text("one, repaired\n")
    (tmp_path / EXTRA).write_text("added\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_check_step_run_from_a_subdirectory_exits_1_naming_a_tracked_test_file_green_edited_again_after_record_step_from_that_subdirectory_1960(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({NEW: "one\n"})
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub/.tdd").symlink_to("../.tdd")
    (tmp_path / NEW).write_text("one\ntwo\n")
    recorded = run_cli(tests_frozen, ["record", "--step", STEP, "../" + NEW], cwd=tmp_path / "sub")[0]

    (tmp_path / NEW).write_text("one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path / "sub")[:2]

    assert (recorded, checked) == (0, (1, NEW + "\n"))


def test_record_and_check_by_step_key_an_unmarked_steps_record_by_path_and_reject_an_edit_to_its_test_file_1586(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SUITE: "case one\n"})
    step = "step one adds case one"
    key = run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].rstrip("\n")

    recorded = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)[0]
    (tmp_path / SUITE).write_text("case one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, (tmp_path / key).is_file(), checked) == (0, True, (1, SUITE + "\n"))


def test_an_unmarked_step_quoting_a_repair_mark_in_its_prose_is_still_frozen_1586(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SUITE: "case one\n"})
    step = "A `⟦ci-repair⟧` step's verify-green judges only the CI log ⟦added⟧ ⟦criterion 2⟧"

    recorded = run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=tmp_path)[0]
    (tmp_path / SUITE).write_text("case one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, checked) == (0, (1, SUITE + "\n"))


def test_check_step_run_outside_any_git_repository_exits_2_with_stderr_naming_the_missing_repository_1773(
        tmp_path, run_cli, tests_frozen, fed_history, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / NEW).write_text("one\n")
    fed_history(root=tmp_path)
    monkeypatch.setattr(tests_frozen.case_history, "toplevel", lambda: None)
    run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)

    code, out, err = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    assert (code, out, "repository" in err) == (2, "", True)


def test_check_step_in_a_repository_with_no_commits_exits_2_with_stderr_naming_the_missing_head_over_a_staged_test_edit_1960(
        tmp_path, run_cli, tests_frozen, fed_history):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / NEW).write_text("one\n")
    fed_history(root=tmp_path)
    run_cli(tests_frozen, ["record", "--step", STEP, NEW], cwd=tmp_path)
    (tmp_path / OTHER).write_text("one, weakened\n")

    code, out, err = run_cli(tests_frozen, ["check", "--step", STEP], cwd=tmp_path)

    refusals = [line for line in err.splitlines() if line.startswith("tests-frozen.sh:") and "HEAD" in line]
    assert (code, out, len(refusals)) == (2, "", 1)


def test_check_step_exits_1_naming_the_old_name_when_green_restores_a_test_file_red_renamed_with_git_mv_1960(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({OLD_PY: "one\ntwo\nthree\n"})
    step = "step one renames a test file"
    (tmp_path / OLD_PY).rename(tmp_path / NEW)
    run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path)

    (tmp_path / OLD_PY).write_text("one\ntwo\nthree\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, OLD_PY + "\n")


def test_check_step_on_a_fixture_repair_step_exits_1_naming_a_test_file_that_is_neither_its_fixture_file_nor_reds_case_1947(
        tmp_path, run_cli, tests_frozen, red_recorded):
    recorded = red_recorded({NEW: "one\n", OTHER: "one\n", FIXTURE: "one\n"}, step=FIXTURE_STEP)
    record = run_cli(tests_frozen, ["path", FIXTURE_STEP], cwd=tmp_path)[1].rstrip("\n")

    (tmp_path / FIXTURE).write_text("one, repaired\n")
    (tmp_path / OTHER).write_text("one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", FIXTURE_STEP], cwd=tmp_path)[:2]

    assert (recorded, (tmp_path / record).exists(), checked) == (0, True, (1, OTHER + "\n"))


def test_check_step_on_a_fixture_repair_step_exits_0_silently_when_only_its_fixture_file_was_edited_1947(
        tmp_path, run_cli, tests_frozen, red_recorded):
    red_recorded({NEW: "one\n", FIXTURE: "one\n"}, step=FIXTURE_STEP)

    (tmp_path / FIXTURE).write_text("one, repaired\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", FIXTURE_STEP], cwd=tmp_path)

    assert (code, out) == (0, "")
