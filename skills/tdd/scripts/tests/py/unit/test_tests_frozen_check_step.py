"""In-process `check --step` cases for veri/tests_frozen.py, on a case history fed by fed_history (PRD 017.4)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
NEW, OTHER, GONE, LATER = "tests/test_new.py", "tests/test_other.py", "tests/test_gone.py", "tests/test_later.py"
UNTRACKED, EXTRA, OLD_SH = "tests/test_untracked.py", "tests/test_extra.py", "tests/old.test.sh"
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
    """`files` committed, red's edit to NEW (and the deletion of each of `deleted`) recorded under `step`."""
    def record(files, deleted=(), step=STEP):
        committed_once(files)
        (tmp_path / NEW).write_text("one\ntwo\n")
        for name in deleted:
            (tmp_path / name).unlink()
        run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)
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
