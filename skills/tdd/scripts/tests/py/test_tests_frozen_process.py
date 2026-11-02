"""Cases for veri/tests_frozen.py that run git in a real repository under tmp_path."""
import importlib
from pathlib import Path
import subprocess

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


def git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_modified_test_file_red_did_not_record_and_not_a_modified_non_test_file_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_other.py", "lib.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    (tmp_path / "lib.py").write_text("one, changed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_other.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_run_from_a_subdirectory_still_exits_1_naming_a_test_file_red_did_not_record_1773(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_other.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "sub/.tdd").symlink_to("../.tdd")
    (tmp_path / "sub/tests").symlink_to("../tests")

    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path / "sub")

    assert (code, out) == (1, "tests/test_other.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which untracked test files exist")
def test_check_step_run_from_a_subdirectory_exits_1_naming_an_untracked_test_file_outside_it_by_its_path_from_the_root_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "sub/.tdd").symlink_to("../.tdd")
    (tmp_path / "sub/tests").symlink_to("../tests")
    (tmp_path / "tests/test_untracked.py").write_text("new\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path / "sub")

    assert (code, out) == (1, "tests/test_untracked.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_test_file_red_did_not_record_that_was_deleted_since_head_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_other.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_other.py").unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_other.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD at record time")
def test_check_step_exits_0_when_the_only_change_outside_the_record_is_a_test_file_red_deleted_1772(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_gone.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    (tmp_path / "tests/test_gone.py").unlink()
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD at record time")
def test_check_step_exits_1_naming_a_test_file_the_record_holds_as_deleted_that_exists_again_1772(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_gone.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    (tmp_path / "tests/test_gone.py").unlink()
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_gone.py").write_text("back\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_gone.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD at record time")
def test_check_step_exits_1_naming_a_test_file_deleted_after_record_step_held_another_deletion_1772(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_gone.py", "tests/test_later.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    (tmp_path / "tests/test_gone.py").unlink()
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_later.py").unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_later.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which untracked test files exist")
def test_check_step_exits_1_naming_an_untracked_test_file_red_did_not_record_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_extra.py").write_text("added by green\n")
    (tmp_path / "notes.py").write_text("not a test\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_extra.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which files differ from HEAD")
def test_check_step_exits_0_printing_nothing_when_only_non_test_files_changed_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    for name in ("lib.py", "gone.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests", "lib.py", "gone.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "lib.py").write_text("one, changed\n")
    (tmp_path / "gone.py").unlink()
    (tmp_path / "notes.py").write_text("not a test\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD at record time")
def test_record_step_holds_a_helper_test_file_red_changed_beside_its_test_path_so_check_step_exits_0_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/helper.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    (tmp_path / "tests/helper.test.sh").write_text("one\nred's helper\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_0_on_a_replaces_case_step_when_only_the_suite_it_names_changed_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/old.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "⟦replaces-case⟧ replaces 'old case' in tests/old.test.sh"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/old.test.sh").write_text("case deleted\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_replaces_case_step_exits_1_naming_another_unrecorded_test_file_and_not_the_suite_it_names_1733(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/old.test.sh", "tests/test_other.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "⟦replaces-case⟧ replaces 'old case' in tests/old.test.sh"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/old.test.sh").write_text("case deleted\n")
    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_other.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
@pytest.mark.parametrize("mark", ["⟦suite-repair⟧", "⟦ci-repair⟧"])
def test_check_step_still_exits_0_on_a_repair_step_when_an_unrecorded_test_file_differs_from_head_1733(
        tmp_path, run_cli, tests_frozen, mark):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_other.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "Repair the red CI run %s" % mark

    (tmp_path / "tests/test_other.py").write_text("one, repaired\n")
    (tmp_path / "tests/test_extra.py").write_text("added\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_by_name_the_pytest_function_red_added_to_a_test_file_1765(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_added_by_red_1765():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "test_added_by_red_1765" in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_by_name_the_bash_case_red_added_to_a_test_sh_suite_1765(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/suite.test.sh").write_text('name="older case"\ncheck_older\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a bash case"
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="older case"\ncheck_older\nname="added by red 1765"\ncheck_added\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: added by red 1765\n" in record
    assert "older case" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_by_name_the_pytest_function_red_edited_and_not_the_one_it_left_alone_1765(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_edited_by_red_1765():\n    assert 1 == 2\n\n\n"
        "def test_left_alone_1765():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one edits a case"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_edited_by_red_1765():\n    assert 1 == 1\n\n\n"
        "def test_left_alone_1765():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_edited_by_red_1765\n" in record
    assert "test_left_alone_1765" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_bash_case_red_added_before_the_finish_trailer_not_the_previous_last_case_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="last case"\ncheck_last\nok\n\nfinish\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case before finish"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="last case"\ncheck_last\nok\n\n'
                     'name="added by red 1861"\ncheck_added\nok\n\nfinish\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: added by red 1861\n" in record
    assert "last case" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_function_red_inserted_at_file_start_above_an_older_one_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("\ndef test_older_case_1861():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a case above the older one"
    suite.write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                     "def test_older_case_1861():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_inserted_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_that_had_one_blank_line_above_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("LIMIT = 1\n\ndef test_older_case_1861():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a case above the older one"
    suite.write_text("LIMIT = 1\n\n\ndef test_inserted_by_red_1861():\n    assert True\n\n\n"
                     "def test_older_case_1861():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_inserted_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_in_a_class_and_a_wrong_test_naming_the_older_one_routes_red_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
                     "    def test_older_case_1861(self):\n        assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a method above the older one"
    suite.write_text("import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
                     "    def test_inserted_by_red_1861(self):\n        assert True\n\n"
                     "    def test_older_case_1861(self):\n        assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_inserted_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_bash_case_red_inserted_above_an_older_one_whose_blank_lines_above_changed_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text('setup\n\nname="older case"\ncheck_older\nok\n\nfinish\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a bash case above the older one"
    suite.write_text('setup\n\nname="inserted by red 1861"\ncheck_added\nok\n'
                     'name="older case"\ncheck_older\nok\n\nfinish\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: inserted by red 1861\n" in record
    assert "older case" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_function_red_appended_after_an_older_one_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case_1861():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one appends a case after the older one"
    suite.write_text("def test_older_case_1861():\n    assert True\n\n\n"
                     "def test_appended_by_red_1861():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_appended_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_bash_case_red_appended_at_the_end_of_a_suite_with_no_finish_trailer_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text('name="older case"\ncheck_older\nok\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one appends a bash case with no trailer"
    suite.write_text('name="older case"\ncheck_older\nok\n\n\n'
                     'name="appended by red 1861"\ncheck_added\nok\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: appended by red 1861\n" in record
    assert "older case" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_case_red_appended_to_a_real_copy_of_a_bash_suite_with_its_finish_trailer_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    # run-finished.test.sh as it stood before #1378 replaced it with pytest cases, frozen
    real = (Path(__file__).resolve().parents[1] / "fixtures" / "tests-frozen" / "run-finished.test.sh.txt").read_text()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text(real)
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one appends a case to a real suite"
    head, trailer, _ = real.rpartition("\nfinish\n")
    suite.write_text(head + '\n\nname="appended by red 1861"\ncheck_added\nok\n\nfinish\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: appended by red 1861"]


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_on_the_files_first_line_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case_1861():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a case above the one on line one"
    suite.write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                     "def test_older_case_1861():\n    assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_inserted_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_directly_under_its_class_line_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("class TestSuite:\n    def test_older_case_1861(self):\n        assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one inserts a method under the class line"
    suite.write_text("class TestSuite:\n    def test_inserted_by_red_1861(self):\n        assert True\n\n"
                     "    def test_older_case_1861(self):\n        assert True\n")

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert "case: test_inserted_by_red_1861\n" in record
    assert "test_older_case_1861" not in record


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_the_last_bash_case_red_edited_below_a_heredoc_finish_line_when_no_finish_trailer_ends_the_file_1773(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="heredoc case"\ncat > script.sh <<\'EOF\'\nfinish\nEOF\ncheck_heredoc one\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one edits the last case below a heredoc finish with no trailer"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="heredoc case"\ncat > script.sh <<\'EOF\'\nfinish\nEOF\ncheck_heredoc two\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: heredoc case"]


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_the_bash_case_red_edited_below_an_indented_finish_line_inside_its_body_1861(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/suite.test.sh"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="finishing case"\nif true; then\n  finish_up\n  finish\nfi\ncheck_finishing one\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one edits below an indented finish inside a case"
    suite.write_text('name="first case"\ncheck_first\nok\n\n'
                     'name="finishing case"\nif true; then\n  finish_up\n  finish\nfi\ncheck_finishing two\n')

    run_cli(tests_frozen, ["record", "--step", step, "tests/suite.test.sh"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: finishing case"]


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_run_from_a_subdirectory_exits_1_naming_a_tracked_test_file_green_edited_again_after_record_step_from_that_subdirectory_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "sub/.tdd").symlink_to("../.tdd")
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    recorded = run_cli(tests_frozen, ["record", "--step", step, "../tests/test_new.py"], cwd=tmp_path / "sub")[0]

    (tmp_path / "tests/test_new.py").write_text("one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path / "sub")[:2]

    assert (recorded, checked) == (0, (1, "tests/test_new.py\n"))


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_record_and_check_by_step_key_an_unmarked_steps_record_by_path_and_reject_an_edit_to_its_test_file_1586(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.sh"
    suite.write_text("case one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "a.test.sh")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds case one"
    key = run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].rstrip("\n")

    recorded = run_cli(tests_frozen, ["record", "--step", step, "a.test.sh"], cwd=tmp_path)[0]
    suite.write_text("case one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, (tmp_path / key).is_file(), checked) == (0, True, (1, "a.test.sh\n"))


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_an_unmarked_step_quoting_a_repair_mark_in_its_prose_is_still_frozen_1586(tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "a.test.sh"
    suite.write_text("case one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "a.test.sh")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "A `⟦ci-repair⟧` step's verify-green judges only the CI log ⟦added⟧ ⟦criterion 2⟧"

    recorded = run_cli(tests_frozen, ["record", "--step", step, "a.test.sh"], cwd=tmp_path)[0]
    suite.write_text("case one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, checked) == (0, (1, "a.test.sh\n"))


@pytest.mark.process("git asked for the repository toplevel from a directory under tmp_path that is in none")
def test_check_step_run_outside_any_git_repository_exits_2_with_stderr_naming_the_missing_repository_1773(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    step = "step one adds a case"
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    code, out, err = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out, "repository" in err) == (2, "", True)


@pytest.mark.process("git asked for the repository toplevel from a directory under tmp_path that is in none")
def test_record_step_run_outside_any_git_repository_exits_2_with_stderr_naming_the_missing_repository_and_writes_no_record_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    step = "step one adds a case"

    code, out, err = run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    assert (code, out, "repository" in err, list((tmp_path / ".tdd").iterdir())) == (2, "", True, [])


@pytest.mark.process("a real git repository with no commits under tmp_path, asked which test files differ from HEAD")
def test_check_step_in_a_repository_with_no_commits_exits_2_with_stderr_naming_the_missing_head_over_a_staged_test_edit_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    step = "step one adds a case"
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)
    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    git(tmp_path, "add", "tests/test_other.py")

    code, out, err = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    refusals = [line for line in err.splitlines() if line.startswith("tests-frozen.sh:") and "HEAD" in line]
    assert (code, out, len(refusals)) == (2, "", 1)


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_record_step_for_a_red_whose_only_test_change_deletes_a_tracked_test_file_records_the_deletion_and_exits_0_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_old.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one deletes a test file"
    (tmp_path / "tests/test_old.py").unlink()

    code, out, _ = run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path)

    _, recorded, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / recorded.strip()).read_text() if (tmp_path / recorded.strip()).exists() else None
    assert (code, out, record) == (0, "", "deleted  tests/test_old.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_the_old_name_when_green_restores_a_test_file_red_renamed_with_git_mv_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_old.py").write_text("one\ntwo\nthree\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one renames a test file"
    git(tmp_path, "mv", "tests/test_old.py", "tests/test_new.py")
    run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path)

    (tmp_path / "tests/test_old.py").write_text("one\ntwo\nthree\n")
    git(tmp_path, "add", "tests/test_old.py")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_old.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_record_step_lists_the_pytest_function_red_edited_below_a_finish_line_inside_its_multiline_string_1773(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    body = ('def test_first():\n    assert True\n\n\n'
            'def test_last():\n    text = """\nfinish\n"""\n    assert text == {!r}\n')
    suite.write_text(body.format("one"))
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one edits a function below a string finish"
    suite.write_text(body.format("two"))

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = (tmp_path / record_path.rstrip("\n")).read_text()

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: test_last"]


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_fixture_repair_step_exits_1_naming_a_test_file_that_is_neither_its_fixture_file_nor_reds_case_1947(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/test_other.py", "tests/conftest.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'db' in tests/conftest.py, "
            "reproduced by a case in tests/test_new.py ⟦fixture-repair⟧")
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    recorded = run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)[0]
    record = run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].rstrip("\n")

    (tmp_path / "tests/conftest.py").write_text("one, repaired\n")
    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert (recorded, (tmp_path / record).exists(), checked) == (0, True, (1, "tests/test_other.py\n"))


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_fixture_repair_step_exits_0_silently_when_only_its_fixture_file_was_edited_1947(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/conftest.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'db' in tests/conftest.py, "
            "reproduced by a case in tests/test_new.py ⟦fixture-repair⟧")
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/conftest.py").write_text("one, repaired\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_fixture_repair_step_exits_1_naming_the_fixture_file_when_green_changed_the_recorded_case_body_2359(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    fixture = tmp_path / "tests/test_fixture.py"
    fixture.write_text("def helper():\n    return 1\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'helper' in tests/test_fixture.py, "
            "reproduced by a case in tests/test_fixture.py ⟦fixture-repair⟧")
    fixture.write_text("def helper():\n    return 1\n\n\ndef test_red_2359():\n    assert helper() == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_fixture.py"], cwd=tmp_path)

    fixture.write_text("def helper():\n    return 2\n\n\ndef test_red_2359():\n    assert True\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_fixture.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_fixture_repair_step_exits_0_when_green_changed_the_fixture_file_outside_the_recorded_case_2359(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    fixture = tmp_path / "tests/test_fixture.py"
    fixture.write_text("def helper():\n    return 1\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'helper' in tests/test_fixture.py, "
            "reproduced by a case in tests/test_fixture.py ⟦fixture-repair⟧")
    fixture.write_text("def helper():\n    return 1\n\n\ndef test_red_2359():\n    assert helper() == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_fixture.py"], cwd=tmp_path)

    fixture.write_text("def helper():\n    return 2\n\n\ndef test_red_2359():\n    assert helper() == 2\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_fixture_repair_step_exits_1_naming_a_fixture_file_the_record_holds_no_case_bodies_for_2404(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    fixture = tmp_path / "tests/fixture_data.py"
    fixture.write_text("TABLE = [1]\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'TABLE' in tests/fixture_data.py, "
            "reproduced by a case in tests/test_other.py ⟦fixture-repair⟧")
    fixture.write_text("TABLE = [1, 2]\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/fixture_data.py"], cwd=tmp_path)

    fixture.write_text("TABLE = [9, 9, 9]\nOTHER = {}\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/fixture_data.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_on_a_step_without_the_fixture_repair_mark_exits_1_naming_the_file_its_text_calls_a_fixture_1947(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/conftest.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = ("the case passes: repairs the fixture 'db' in tests/conftest.py, "
            "reproduced by a case in tests/test_new.py")
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/conftest.py").write_text("one, repaired\n")
    checked = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)[:2]

    assert checked == (1, "tests/conftest.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_0_when_a_green_edit_touches_the_guard_subject_the_step_names_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a guard ⟦guard-subject: tests/no-thing.test.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_0_when_a_green_edit_touches_both_guard_subjects_the_step_names_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh", "tests/lib-helper.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step two ⟦guard-subject: tests/no-thing.test.sh⟧ ⟦guard-subject: tests/lib-helper.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    (tmp_path / "tests/lib-helper.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_an_unrecorded_test_file_other_than_the_guard_subject_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh", "tests/test_other.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a guard ⟦guard-subject: tests/no-thing.test.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    (tmp_path / "tests/test_other.py").write_text("one, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_other.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_the_recorded_test_file_even_with_the_guard_subject_edited_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a guard ⟦guard-subject: tests/no-thing.test.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/test_new.py").write_text("one\ntwo, weakened\n")
    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_new.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_only_the_recorded_file_the_marker_does_not_name_when_the_guard_subject_was_recorded_too_2663(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/conftest.py"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦guard-subject: tests/conftest.py⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    (tmp_path / "tests/conftest.py").write_text("one\nleaky\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py", "tests/conftest.py"], cwd=tmp_path)

    (tmp_path / "tests/test_new.py").write_text("one\ntwo, weakened\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/test_new.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_recorded_guard_subject_deleted_since_the_record_2663(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/conftest.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦guard-subject: tests/conftest.py⟧"
    (tmp_path / "tests/conftest.py").write_text("one\nleaky\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/conftest.py"], cwd=tmp_path)

    (tmp_path / "tests/conftest.py").unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/conftest.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_0_for_a_recorded_guard_subject_whose_content_changed_since_the_record_2663(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/conftest.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦guard-subject: tests/conftest.py⟧"
    (tmp_path / "tests/conftest.py").write_text("one\nleaky\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/conftest.py"], cwd=tmp_path)

    (tmp_path / "tests/conftest.py").write_text("one\nworking\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_the_file_of_a_guard_subject_marker_quoted_in_the_steps_prose_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "A step quoting `⟦guard-subject: tests/no-thing.test.sh⟧` in its prose ⟦added⟧ ⟦criterion 4⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/no-thing.test.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_test_file_the_steps_prose_names_as_plain_text_with_no_marker_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "A step fixing tests/no-thing.test.sh, named as plain text ⟦added⟧ ⟦criterion 4⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/no-thing.test.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_test_file_under_a_directory_a_trailing_guard_subject_marker_names_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests/lib").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/lib/harness.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦guard-subject: tests/lib⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/lib/harness.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/lib/harness.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_test_file_a_trailing_guard_subject_glob_would_match_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests/lib").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/lib/harness.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦guard-subject: tests/*⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/lib/harness.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/lib/harness.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_a_test_file_a_trailing_phases_marker_names_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests/lib").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/lib/harness.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a helper ⟦phases: tests/lib/harness.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/lib/harness.sh").write_text("one, fixed\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/lib/harness.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which tracked test files differ from HEAD")
def test_check_step_exits_1_naming_the_guard_subject_a_green_deleted_1775(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    for name in ("tests/test_new.py", "tests/no-thing.test.sh"):
        (tmp_path / name).write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one fixes a guard ⟦guard-subject: tests/no-thing.test.sh⟧"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    (tmp_path / "tests/no-thing.test.sh").unlink()
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (1, "tests/no-thing.test.sh\n")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_step_from_a_subdirectory_exits_1_naming_an_untracked_test_file_a_green_weakened_by_its_root_path_1960(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / "sub/.tdd").mkdir(parents=True)
    (tmp_path / "lib.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("def test_a():\n    assert f() == 1\n")
    run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path / "sub")

    (tmp_path / "tests/test_new.py").write_text("def test_a():\n    assert True\n")
    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path / "sub")

    assert (code, out) == (1, "tests/test_new.py\n")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_an_earlier_step_recorded_and_the_step_when_a_later_leaf_weakened_it_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2125():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2125():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert "test_pinned_2125" in out and earlier in out


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_for_an_earlier_steps_case_renamed_with_its_text_otherwise_unchanged_2329(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two renames it"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2329():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_and_renamed_2329():\n    assert 1 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_old_case_and_its_step_when_an_earlier_steps_case_is_renamed_and_its_body_changed_2329(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two renames and weakens it"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2329():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_and_renamed_2329():\n    assert True\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert "test_pinned_2329" in out and earlier in out


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_exactly_one_case_when_two_identical_earlier_cases_are_removed_for_one_added_case_2419(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds two cases", "step two folds them into one"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_alpha_2419():\n    assert 1 == 1\n"
        "\n\ndef test_beta_2419():\n    assert 1 == 1\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_gamma_2419():\n    assert 1 == 1\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert code == 1
    assert len(out.splitlines()) == 1


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_exactly_the_third_of_three_identical_earlier_cases_removed_for_two_added_cases_2419(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds three cases", "step two folds them into two"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_alpha_2419():\n    assert 1 == 1\n"
        "\n\ndef test_beta_2419():\n    assert 1 == 1\n"
        "\n\ndef test_delta_2419():\n    assert 1 == 1\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_gamma_2419():\n    assert 1 == 1\n"
        "\n\ndef test_epsilon_2419():\n    assert 1 == 1\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "step two")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_delta_2419 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_and_its_step_when_the_case_or_its_whole_file_was_deleted_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    recorded = "def test_older_case():\n    assert True\n\n\ndef test_pinned_2125():\n    assert 1 == 2\n"
    (tmp_path / "tests/test_suite.py").write_text(recorded)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "commit", "-q", "-am", "step one")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    argv = ["check-earlier", str(ledger), "--step", current]

    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    case_removed = run_cli(tests_frozen, argv, cwd=tmp_path)
    (tmp_path / "tests/test_suite.py").unlink()
    file_deleted = run_cli(tests_frozen, argv, cwd=tmp_path)

    expected = "test_pinned_2125 (%s)\n" % earlier
    assert [case_removed[:2], file_deleted[:2]] == [(1, expected), (1, expected)]


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_the_current_step_only_adds_cases_and_skips_a_step_with_no_record_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, unrecorded, current = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    recorded = "def test_older_case():\n    assert True\n\n\ndef test_pinned_2125():\n    assert 1 == 2\n"
    (tmp_path / "tests/test_suite.py").write_text(recorded)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, unrecorded, current))
    (tmp_path / "tests/test_suite.py").write_text(recorded + "\n\ndef test_added_now():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_except_exempts_each_case_named_and_still_exits_1_for_a_changed_case_not_named_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds cases", "step two adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n"
        "def test_named_a_2125():\n    assert 1 == 2\n\n\n"
        "def test_named_b_2125():\n    assert 1 == 3\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n"
        "def test_named_a_2125():\n    assert True\n\n\n"
        "def test_named_b_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 4\n")
    argv = ["check-earlier", str(ledger), "--step", current,
            "--except", "test_named_a_2125", "--except", "test_named_b_2125"]

    named_only = run_cli(tests_frozen, argv, cwd=tmp_path)
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n"
        "def test_named_a_2125():\n    assert True\n\n\n"
        "def test_named_b_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert True\n")
    unnamed_too = run_cli(tests_frozen, argv, cwd=tmp_path)

    assert [named_only[:2], unnamed_too[:2]] == [
        (0, ""), (1, "test_unnamed_2125 (%s)\n" % earlier)]


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_without_except_exempts_the_cases_a_replaces_case_step_names_and_the_fixture_file_a_fixture_repair_step_names_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier = "step one adds cases"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n"
        "def test_named_2125():\n    assert 1 == 2\n\n\n"
        "def test_unnamed_2125():\n    assert 1 == 3\n")
    (tmp_path / "tests/test_fixture.py").write_text("def test_in_fixture_file_2125():\n    assert 1 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py", "tests/test_fixture.py"],
            cwd=tmp_path)
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n"
        "def test_named_2125():\n    assert True\n\n\n"
        "def test_unnamed_2125():\n    assert True\n")
    (tmp_path / "tests/test_fixture.py").write_text("def test_in_fixture_file_2125():\n    assert True\n")
    replaces = "⟦replaces-case⟧ replaces 'test_named_2125' in tests/test_suite.py.test.sh"
    repair = "repairs the fixture 'f' in tests/test_fixture.py, reproduced by a case ⟦fixture-repair⟧"
    results = []
    for current in (replaces, repair):
        ledger = tmp_path / ".tdd/ledger.md"
        ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
        results.append(run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)[:2])

    assert results == [
        (1, "test_unnamed_2125 (%s)\ntest_in_fixture_file_2125 (%s)\n" % (earlier, earlier)),
        (1, "test_named_2125 (%s)\ntest_unnamed_2125 (%s)\n" % (earlier, earlier))]


@pytest.mark.process("a real git repository under tmp_path, asked for its top level")
def test_check_earlier_prints_usage_naming_check_earlier_and_exits_2_without_a_ledger_or_step_or_with_an_unreadable_ledger_2125(
        tmp_path, run_cli, tests_frozen):
    git(tmp_path, "init", "-q")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] step\n")

    results = [run_cli(tests_frozen, argv, cwd=tmp_path)[::2] for argv in (
        ["check-earlier"],
        ["check-earlier", str(ledger)],
        ["check-earlier", str(tmp_path / "missing.md"), "--step", "step"])]

    assert [code for code, _ in results] == [2, 2, 2]
    assert all("usage:" in err and "check-earlier" in err for _, err in results)
    scripts = Path(__file__).resolve().parents[2]
    header = (scripts / "tests-frozen.sh").read_text().split("\nexec ")[0]
    assert "tests-frozen.sh check-earlier" in header
    assert "check-earlier" in (scripts.parent / "SCRIPTS.md").read_text()


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_a_later_step_re_recorded_a_case_and_a_still_later_step_left_it_alone_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_a():\n    assert 0\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    one, two, three = "step one", "step two", "step three"
    suite.write_text("def test_a():\n    assert 1\n")
    run_cli(tests_frozen, ["record", "--step", one, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_a():\n    assert 2\n")
    run_cli(tests_frozen, ["record", "--step", two, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_a():\n    assert 2\n\n\ndef test_c():\n    assert 3\n")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (one, two, three))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", three], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path per route, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_for_a_later_step_that_leaves_alone_a_case_each_re_recording_route_edited_2125(
        tmp_path, run_cli, tests_frozen):
    routes = {
        "red-contradicted": "step two red-contradicted re-edits test_a",
        "red-supersede": "step two red-supersede re-edits test_a",
        "repair": "step two red-repair re-edits test_a, a case its green report superseded",
        "replaces-case": "⟦replaces-case⟧ replaces 'test_a' in tests/test_suite.py.test.sh",
        "fixture-repair": "repairs the fixture 'f' in tests/test_suite.py, reproduced by a case ⟦fixture-repair⟧"}
    results = {}
    for route, two in routes.items():
        repo = tmp_path / route
        (repo / "tests").mkdir(parents=True)
        (repo / ".tdd").mkdir()
        suite = repo / "tests/test_suite.py"
        suite.write_text("def test_a():\n    assert 0\n")
        git(repo, "init", "-q")
        git(repo, "add", "tests")
        git(repo, "commit", "-q", "-m", "base")
        one, three = "step one", "step three adds test_c"
        suite.write_text("def test_a():\n    assert 1\n")
        run_cli(tests_frozen, ["record", "--step", one, "tests/test_suite.py"], cwd=repo)
        suite.write_text("def test_a():\n    assert 2\n")
        run_cli(tests_frozen, ["record", "--step", two, "tests/test_suite.py"], cwd=repo)
        suite.write_text("def test_a():\n    assert 2\n\n\ndef test_c():\n    assert 3\n")
        ledger = repo / ".tdd/ledger.md"
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (one, two, three))
        results[route] = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", three], cwd=repo)[:2]

    assert results == {route: (0, "") for route in routes}


@pytest.mark.process("git asked for the repository toplevel from a directory under tmp_path that is in none")
def test_check_earlier_exits_2_never_1_printing_usage_on_stderr_for_an_empty_step_an_empty_except_an_odd_except_count_and_outside_a_repository_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] step one\n")
    base = ["check-earlier", str(ledger)]
    runs = [run_cli(tests_frozen, base + argv, cwd=tmp_path) for argv in (
        ["--step", ""],
        ["--step", "step one", "--except", ""],
        ["--step", "step one", "--except"],
        ["--step", "step one"])]

    assert [(code, out, "usage" in err) for code, out, err in runs] == [(2, "", True)] * 4


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_and_its_step_when_a_line_below_an_inner_comment_of_a_recorded_bash_case_is_edited_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/suite.test.sh").write_text('name="older case"\ncheck_older\nok\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a bash case", "step two adds another"
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="c1"\nrun_it\n\n# now check\nassert_eq 1 1\n\nname="c2"\ncheck_second\nok\n\nfinish\n')
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/suite.test.sh"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="c1"\nrun_it\n\n# now check\nassert_eq 1 2\n\nname="c2"\ncheck_second\nok\n\nfinish\n')

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "c1 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_and_its_step_when_a_decorator_is_added_above_a_recorded_case_followed_by_an_undecorated_case_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a first case", "step two adds a second case"
    first = "def test_first_2177():\n    assert 1 == 2\n"
    second = "def test_second_2177():\n    assert True\n"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n" + first + "\n\n" + second)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n@pytest.mark.skip\n" + first + "\n\n" + second)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_first_2177 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_and_its_step_when_a_decorator_is_added_above_a_recorded_case_last_in_its_file_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a last case", "step two adds another"
    body = "def test_last_2177():\n    assert 1 == 2\n"
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n\n\n" + body)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n@pytest.mark.skip\n" + body)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_last_2177 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_a_python_def_case_whose_format_2_record_differs_from_its_current_digest_though_the_old_cut_matches_2591(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a def case", "step two adds a sibling"
    first = "def test_def_2591():\n    assert 1 == 2\n"
    second = "def test_sibling_2591():\n    assert True\n"
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n\n\n" + first + "\n\n" + second)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n@pytest.mark.skip\n" + first + "\n\n" + second)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_def_2591 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_for_a_case_the_current_step_recorded_and_has_since_changed_2125(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    current = "step one adds a case"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_own_2125():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", current, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % current)
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_own_2125():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_for_a_record_written_with_the_old_cut_against_an_unchanged_file_2177(
        tmp_path, run_cli, tests_frozen):
    import hashlib
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    git(tmp_path, "init", "-q")
    earlier, current = "step one adds a case", "step two adds a decorated case"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\n@pytest.mark.timeout(60)\n"
        "def test_second_2177():\n    assert True\n")
    old_body = "def test_first_2177():\n    assert 1 == 2\n\n\n@pytest.mark.timeout(60)"
    digest = hashlib.sha256(old_body.encode()).hexdigest()
    _, record, _ = run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)
    (tmp_path / record.strip()).write_text(
        "case: test_first_2177\nbody: tests/test_suite.py\ttest_first_2177\t%s\n" % digest)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_a_case_changed_since_a_record_written_with_the_old_cut_2177(
        tmp_path, run_cli, tests_frozen):
    import hashlib
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    git(tmp_path, "init", "-q")
    earlier, current = "step one adds a case", "step two adds a decorated case"
    old_body = "def test_first_2177():\n    assert 1 == 2\n\n\n@pytest.mark.timeout(60)"
    digest = hashlib.sha256(old_body.encode()).hexdigest()
    _, record, _ = run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)
    (tmp_path / record.strip()).write_text(
        "case: test_first_2177\nbody: tests/test_suite.py\ttest_first_2177\t%s\n" % digest)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_first_2177():\n    assert 1 == 3\n\n\n@pytest.mark.timeout(60)\n"
        "def test_second_2177():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_first_2177 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_a_helper_function_is_inserted_between_two_recorded_bash_cases_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/suite.test.sh").write_text('name="older case"\ncheck_older\nok\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds two bash cases", "step two adds another"
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="first case"\ncheck_first\nok\n\nname="second case"\ncheck_second\nok\n\nfinish\n')
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/suite.test.sh"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="first case"\ncheck_first\nok\n\n# shared between the cases\nhelper() {\n  echo shared\n}\n'
        'one_liner() { echo shared; }\n\nname="second case"\ncheck_second\nok\n\nfinish\n')

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_an_uncommented_one_line_helper_follows_a_blank_line_between_two_recorded_bash_cases_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/suite.test.sh").write_text('name="older case"\ncheck_older\nok\n')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds two bash cases", "step two adds another"
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="first case"\ncheck_first\nok\n\nname="second case"\ncheck_second\nok\n\nfinish\n')
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/suite.test.sh"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/suite.test.sh").write_text(
        'name="first case"\ncheck_first\nok\n\none_liner() { echo shared; }\n\n'
        'name="second case"\ncheck_second\nok\n\nfinish\n')

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_1_naming_the_case_and_its_step_when_only_the_recorded_cases_own_decorator_is_edited_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a decorated case", "step two adds another"
    body = "def test_decorated_2177():\n    assert 1 == 2\n"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n@pytest.mark.timeout(5)\n" + body)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\n@pytest.mark.timeout(60)\n" + body)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (1, "test_decorated_2177 (%s)\n" % earlier)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_a_module_level_helper_is_inserted_between_two_recorded_cases_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds two cases", "step two adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\ndef test_second_2177():\n    assert 3 == 4\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_first_2177():\n    assert 1 == 2\n\n\n# shared between the cases\nLIMIT = 3\n\n\n"
        "def _helper():\n    return LIMIT\n\n\ndef test_second_2177():\n    assert 3 == 4\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_check_earlier_exits_0_printing_nothing_when_a_later_step_appends_a_decorated_case_after_an_earlier_recorded_one_2177(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds a decorated case"
    recorded = "def test_older_case():\n    assert True\n\n\ndef test_first_2177():\n    assert 1 == 2\n"
    (tmp_path / "tests/test_suite.py").write_text(recorded)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "tests/test_suite.py").write_text(
        recorded + '\n\n@pytest.mark.process("a real process")\n@pytest.mark.timeout(60)\n'
        "def test_second_2177():\n    assert True\n")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD by check-earlier")
def test_check_earlier_exit_0_writes_a_pass_marker_under_tdd_naming_the_step_and_the_head_it_checked_2206(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "a.txt").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "a.txt")
    git(tmp_path, "commit", "-q", "-m", "first")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    step = "add the second case"
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] %s\n" % step)

    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=tmp_path)

    markers = [path for path in (tmp_path / ".tdd").rglob("*")
               if path.is_file() and step in path.read_text() and head in path.read_text()]
    assert (code, out, len(markers)) == (0, "", 1)


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD by check-earlier")
def test_check_earlier_exit_1_removes_the_pass_marker_of_that_step_and_leaves_another_steps_marker_2206(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current, other = "step one adds a case", "step two adds another", "step three adds more"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2206():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, current, other))
    passes = [run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=tmp_path)[0]
              for step in (current, other)]
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2206():\n    assert True\n")

    code, _, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    kept = [path.read_text() for path in (tmp_path / ".tdd").rglob("*")
            if path.is_file() and "head: " in path.read_text()]
    assert (passes, code, [("step: %s\n" % current in text, "step: %s\n" % other in text) for text in kept]) == (
        [0, 0], 1, [(False, True)])


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD by check-earlier")
def test_check_earlier_exit_2_for_an_unreadable_ledger_removes_the_pass_marker_of_that_step_and_leaves_another_steps_marker_2206(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    current, other = "step two adds another", "step three adds more"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n- [ ] %s\n" % (current, other))
    passes = [run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=tmp_path)[0]
              for step in (current, other)]

    code, _, _ = run_cli(tests_frozen, ["check-earlier", str(tmp_path / "missing.md"), "--step", current],
                         cwd=tmp_path)

    kept = [path.read_text() for path in (tmp_path / ".tdd").rglob("*")
            if path.is_file() and "head: " in path.read_text()]
    assert (passes, code, [("step: %s\n" % current in text, "step: %s\n" % other in text) for text in kept]) == (
        [0, 0], 2, [(False, True)])


@pytest.mark.process("a real git repository under tmp_path, then git asked for the toplevel from a directory in none")
def test_check_earlier_exit_2_outside_any_git_repository_removes_the_pass_marker_of_that_step_2206(
        tmp_path, run_cli, tests_frozen):
    repo, plain = tmp_path / "repo", tmp_path / "plain"
    (repo / ".tdd").mkdir(parents=True)
    (plain / ".tdd").mkdir(parents=True)
    (repo / "a.txt").write_text("one\n")
    git(repo, "init", "-q")
    git(repo, "add", "a.txt")
    git(repo, "commit", "-q", "-m", "first")
    step = "add the second case"
    ledger = repo / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    passed = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=repo)[0]
    for marker in (repo / ".tdd").glob("check-earlier-*.pass"):
        (plain / ".tdd" / marker.name).write_text(marker.read_text())

    code, _, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", step], cwd=plain)

    assert (passed, code, list((plain / ".tdd").glob("check-earlier-*.pass"))) == (0, 2, [])


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD and the work tree's content")
def test_check_earlier_pass_marker_differs_after_a_work_tree_edit_and_is_the_same_without_one_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / "lib.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    argv = ["check-earlier", str(ledger), "--step", current]

    def marker():
        code = run_cli(tests_frozen, argv, cwd=tmp_path)[0]
        (path,) = (tmp_path / ".tdd").glob("check-earlier-*.pass")
        return code, path.read_text()

    first = marker()
    again = marker()
    (tmp_path / "lib.py").write_text("two\n")
    edited = marker()
    (tmp_path / "notes.txt").write_text("untracked\n")
    untracked = marker()

    assert [first[0], again[0], edited[0], untracked[0]] == [0, 0, 0, 0]
    assert first[1] == again[1]
    assert len({first[1], edited[1], untracked[1]}) == 3
    assert "step: %s\nhead: " % current in edited[1]


@pytest.mark.process("a real git repository under tmp_path holding a nested repository made by git init")
def test_check_earlier_exits_2_naming_the_work_tree_hash_and_writes_no_pass_marker_for_an_untracked_nested_repo_with_no_commits_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "nested").mkdir()
    git(tmp_path / "nested", "init", "-q")

    code, out, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out, "work-tree hash" in err, list((tmp_path / ".tdd").glob("check-earlier-*.pass"))) == (
        2, "", True, [])


@pytest.mark.process("a real git repository under tmp_path whose .gitignore lists .tdd/")
def test_check_earlier_exits_0_and_writes_a_pass_marker_when_the_repository_gitignores_tdd_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests", ".gitignore")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, _, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, len(list((tmp_path / ".tdd").glob("check-earlier-*.pass")))) == (0, 1), err


@pytest.mark.process("a real git repository under tmp_path, asked for the version of a test file at HEAD")
def test_record_step_again_for_a_case_committed_unchanged_keeps_its_body_entry_at_the_current_digest_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("def test_one():\n    assert 1\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("def test_one():\n    assert 1\n\n\ndef test_two():\n    assert 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    first = [l for l in record.read_text().splitlines() if l.startswith("body: ")]

    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)

    again = [l for l in record.read_text().splitlines() if l.startswith("body: ")]
    assert (len(first), again) == (1, first)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_for_a_diff_checked_step_rewrites_the_changed_case_so_a_later_check_earlier_names_nothing_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_a_changed_frozen_case_of_a_step_not_diff_checked_is_not_rerecorded_and_check_earlier_names_it_2199(
        tmp_path, run_cli, tests_frozen):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two edits it", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")

    ticked = run_cli(tick_ledger, [str(ledger), "step two"], cwd=tmp_path)[0]
    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (ticked, rerecorded, code, "test_pinned_2199 (%s)" % earlier in out) == (0, 3, 1, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_keeps_the_record_of_a_case_edited_in_a_commit_before_the_step_base_and_check_earlier_names_it_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit before the step base")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, "test_pinned_2199 (%s)" % earlier in out) == (0, 1, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_leaves_the_ticked_steps_own_record_byte_for_byte_and_rewrites_the_earlier_steps_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    paths = [Path(run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()) for step in (earlier, edit)]
    paths = [p if p.is_absolute() else tmp_path / p for p in paths]
    paths[1].write_text(paths[0].read_text())
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n" % (earlier, edit))
    git(tmp_path, "add", ".tdd")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")
    own_before, earlier_before = paths[1].read_bytes(), paths[0].read_bytes()

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]

    assert (rerecorded, paths[1].read_bytes() == own_before, paths[0].read_bytes() != earlier_before) == (0, True, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_keeps_the_record_of_a_frozen_case_edited_only_in_the_working_tree_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 6⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", "-f", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, "test_pinned_2199 (%s)" % earlier in out) == (0, 1, True)


def _diff_checked_repo(tmp_path, run_cli, tests_frozen, commit_ledger=True):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    steps = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", steps[0], "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % steps)
    if commit_ledger:
        git(tmp_path, "add", "-f", ".tdd/ledger.md")
        git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")
    return ledger, steps


@pytest.mark.process("a real git repository under tmp_path, asked for the commit that last touched the ledger")
def test_rerecord_earlier_run_from_a_subdirectory_with_a_relative_ledger_path_rewrites_the_changed_case_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (_, edit, later) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", "../.tdd/ledger.md", "--step", edit],
                         cwd=tmp_path / "tests")[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked for the commit that last touched the ledger")
def test_rerecord_earlier_with_a_ledger_no_commit_touched_is_exit_2_and_rewrites_no_record_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, commit_ledger=False)
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, "ledger" in err) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path whose blob at HEAD is corrupted, so git show fails")
def test_rerecord_earlier_when_git_show_fails_on_a_recorded_file_is_exit_2_not_read_as_no_cases_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)
    blob = subprocess.run(["git", "rev-parse", "HEAD:tests/test_suite.py"], cwd=tmp_path, check=True,
                          capture_output=True, text=True).stdout.strip()
    loose = tmp_path / ".git/objects" / blob[:2] / blob[2:]
    loose.chmod(0o644)
    loose.write_bytes(b"not a zlib stream")
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, "tests/test_suite.py" in err) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path, the earlier record's write made to raise")
def test_rerecord_earlier_returns_2_naming_the_record_when_writing_it_raises_2199(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)
    record = run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_earlier(str(ledger), edit)

    assert (code, record in capfd.readouterr().err) == (2, True)


@pytest.mark.process("a real git repository under tmp_path, with a PATH-first git that fails git diff")
def test_check_step_exits_2_with_gits_stderr_when_git_cannot_list_the_differing_test_files_2579(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    import os
    import shutil
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_new.py").write_text("one\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step one adds a case"
    (tmp_path / "tests/test_new.py").write_text("one\ntwo\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_new.py"], cwd=tmp_path)
    stub = tmp_path / "stub-bin"
    stub.mkdir()
    (stub / "git").write_text(
        '#!/bin/sh\nif [ "$1" = "diff" ]; then echo "fatal: stubbed diff failure" >&2; exit 128; fi\nexec %s "$@"\n'
        % shutil.which("git"))
    (stub / "git").chmod(0o755)
    monkeypatch.setenv("PATH", str(stub) + ":" + os.environ["PATH"])

    code, out, err = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "stubbed diff failure" in err


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_re_records_an_earlier_case_changed_only_upstream_so_check_earlier_exits_0_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]
    usage = run_cli(tests_frozen, [], cwd=repo)[2]

    assert (stale, code, after) == (1, 0, 0)
    assert "rerecord-rebased" in usage


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_keeps_every_non_body_line_of_the_record_and_rewrites_only_the_body_line_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_text().splitlines()
    ledger = repo / ".tdd/ledger.md"

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    new = record.read_text().splitlines()

    assert code == 0
    assert [line for line in new if not line.startswith("body: ")] == [
        line for line in old if not line.startswith("body: ")]
    assert [line for line in new if line.startswith("body: ")] != [
        line for line in old if line.startswith("body: ")]
    assert any(line.startswith("case: ") for line in old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_run_from_a_subdirectory_re_records_the_same_upstream_only_case_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", "../.tdd/ledger.md", before], cwd=repo / "tests")
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    assert (stale, code, after) == (1, 0, 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_the_branch_changed_since_its_record_and_names_it_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    suite.write_text(case % (9, 1))
    git(repo, "commit", "-q", "-a", "-m", "step two edits the frozen case")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_the_branch_and_origin_both_edited_identically_since_its_record_because_its_pre_rebase_body_no_longer_matches_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    suite.write_text(case % (1, 3))
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-a", "-m", "step two edits the frozen case as origin will")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_whose_head_body_differs_from_origins_though_the_record_matched_before_the_rebase_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_1_naming_only_the_refused_case_while_re_recording_the_other_stale_one_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    case = "def test_%s_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suites = {name: repo / ("tests/test_%s.py" % name) for name in ("kept", "refused")}
    for name, suite in suites.items():
        suite.write_text(case % (name, 1, 1))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    steps = {"kept": "step one pins the kept case", "refused": "step two pins the refused case"}
    current = "step three adds another"
    git(repo, "checkout", "-q", "-b", "work")
    for name, suite in suites.items():
        suite.write_text(case % (name, 5 if name == "refused" else 1, 2 if name == "kept" else 1))
        run_cli(tests_frozen, ["record", "--step", steps[name], "tests/test_%s.py" % name], cwd=repo)
        git(repo, "add", "tests")
        git(repo, "commit", "-q", "-m", "step " + name)
    suites["refused"].write_text(case % ("refused", 9, 1))
    git(repo, "commit", "-q", "-a", "-m", "step three edits the refused case")
    (repo / ".tdd/ledger.md").write_text(
        "- [x] %s\n- [x] %s\n- [ ] %s\n" % (steps["kept"], steps["refused"], current))

    git(repo, "checkout", "-q", "main")
    suites["kept"].write_text(case % ("kept", 1, 2))
    git(repo, "commit", "-q", "-a", "-m", "upstream 2")
    for name, suite in suites.items():
        suite.write_text(case % (name, 1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream 3")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    records = sorted((repo / ".tdd").glob("tests-frozen-*.record"))
    old = {path: path.read_bytes() for path in records}

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    changed = [path for path in records if path.read_bytes() != old[path]]
    kept_check = run_cli(tests_frozen, ["check-earlier", str(repo / ".tdd/ledger.md"), "--step", current],
                         cwd=repo)[1]
    assert (code, len(changed)) == (1, 1)
    assert out.splitlines() == ["test_refused_2552 (%s)" % steps["refused"]]
    assert "test_kept_2552" not in kept_check


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_3_and_rewrites_no_record_when_no_earlier_recorded_case_is_stale_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord with a missing ledger")
def test_rerecord_rebased_exits_2_naming_an_unreadable_ledger_on_stderr_and_writes_no_record_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    suite.write_text("def test_config_2552():\n    assert f() == 1\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    ledger = repo / ".tdd/unreadable-ledger.md"
    ledger.mkdir()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), head], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)
    assert str(ledger) in err


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord with no ledger file")
def test_rerecord_rebased_with_no_ledger_file_exits_3_with_no_output_and_rewrites_no_record_2718(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    (repo / "tests/test_suite.py").write_text("def test_config_2718():\n    assert f() == 1\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/no-ledger-yet.md"), head], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_2_and_rewrites_no_record_when_the_pre_rebase_sha_names_no_commit_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), "0" * 40], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, an earlier record that cannot be read")
def test_rerecord_rebased_exits_2_naming_the_record_when_an_earlier_steps_record_exists_but_cannot_be_read_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    suite.write_text("def test_config_2552():\n    assert f() == 1\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    earlier, current = "step one pins the config", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    record.unlink()
    record.mkdir()
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), head], cwd=repo)

    assert (code, out, record.name in err) == (2, "", True)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_skips_a_ticked_earlier_step_with_no_record_file_and_still_re_records_the_stale_one_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    unrecorded, earlier, current = "step zero recorded nothing", "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (unrecorded, earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    assert (code, out, after) == (0, "", 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, the stale record's write made to raise")
def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_2552(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / ".tdd/ledger.md"), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, the stale record's write made to raise")
def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_file_not_found_so_it_is_not_read_as_a_missing_ledger_2718(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise FileNotFoundError(2, "No such file or directory", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / ".tdd/ledger.md"), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"


def _ledger(repo, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (repo / ".tdd/issue-9.md").write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS)))


def _commit(repo, message):
    git(repo, "commit", "-q", "-am", message)


def _plan_repo(repo, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "9")
    (repo / ".tdd").mkdir()
    (repo / "test_suite.py").write_text(CASE % ("base", 0))
    _ledger(repo)
    (repo / ".tdd/issue-8.md").write_text("- [x] %s\n" % STEPS[1])
    git(repo, "init", "-q")
    git(repo, "add", "test_suite.py", ".tdd/issue-9.md", ".tdd/issue-8.md")
    git(repo, "commit", "-q", "-m", "plan")


def _names(repo, tests_frozen, step):
    record = (repo / tests_frozen._record_path(step)).read_text()
    return sorted(l[6:] for l in record.splitlines() if l.startswith("case: "))


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_on_head_keeps_a_pin_and_rename_committed_in_green_and_a_successor_a_later_step_renamed_2673(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("rejects_a_body_that_is_not_valid_json", 3),
                                  CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    suite.write_text(suite.read_text().replace("rejects_a_body", "rejects_to_a_body"))
    _commit(tmp_path, "A renames in green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _ledger(tmp_path, A="pending")
    _commit(tmp_path, "A green")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A refactor verified")
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("later_step", 9))
    _ledger(tmp_path, A="done", B="pending")
    _commit(tmp_path, "B green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_rejects_to_a_body_that_is_not_valid_json",
            "test_two"])


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_on_head_mid_step_keeps_a_case_the_current_unticked_step_committed_not_an_earlier_steps_2673(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("early", 7))
    _ledger(tmp_path, Z="pending")
    _commit(tmp_path, "Z green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _commit(tmp_path, "A pin, not ticked yet")

    code = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (0, ["test_one", "test_pin_committed"])


@pytest.mark.process("a real git repository under tmp_path, its committed ledger walked for the step's line")
def test_rerecord_on_head_exits_2_naming_the_step_when_no_committed_ledger_line_of_it_is_found_2673(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", "step C that no ledger names"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text(CASE % ("base", 0) + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    before = (tmp_path / tests_frozen._record_path(step)).read_text()
    _commit(tmp_path, "one")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 2))
    _commit(tmp_path, "later")

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)

    assert (code, step in err, (tmp_path / tests_frozen._record_path(step)).read_text()) == (2, True, before)


PHASED_STEP = STEPS[1] + " ⟦phases: expand, migrate⟧"


def _phased_ledger(repo, marks="", **state):
    """The ledger with step A listing its phases: its box stays open whatever `⟂ <phase> done` marks it gains."""
    _ledger(repo, **state)
    ledger = repo / ".tdd/issue-9.md"
    ledger.write_text(ledger.read_text().replace(STEPS[1], PHASED_STEP + marks))


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_on_head_keeps_the_pins_and_renames_of_a_step_whose_ledger_line_went_through_phase_marks_2724(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    expand, migrate = " ⟂ expand done", " ⟂ expand done ⟂ migrate done"
    _plan_repo(tmp_path, monkeypatch)
    _phased_ledger(tmp_path)
    _commit(tmp_path, "plan the phases")
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", PHASED_STEP, "test_suite.py"], cwd=tmp_path)
    _phased_ledger(tmp_path, expand)
    _commit(tmp_path, "A expand")
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("pin_committed", 5))
    _phased_ledger(tmp_path, migrate)
    _commit(tmp_path, "A migrate")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _phased_ledger(tmp_path, migrate, B="pending")
    _commit(tmp_path, "B green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", PHASED_STEP, "test_suite.py"], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, PHASED_STEP)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_two"])


REPAIR_STEP = "repairs the fixture 'f' in test_suite.py, reproduced by a case ⟦fixture-repair⟧"


def _repair_ledger(repo, **state):
    _ledger(repo, **state)
    ledger = repo / ".tdd/issue-9.md"
    ledger.write_text(ledger.read_text().replace(STEPS[1], REPAIR_STEP))


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_on_head_keeps_the_pins_and_renames_of_a_fixture_repair_step_whose_ledger_line_ends_in_the_marker_2724(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    _repair_ledger(tmp_path)
    _commit(tmp_path, "plan the repair")
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1), CASE % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", REPAIR_STEP, "test_suite.py"], cwd=tmp_path)
    suite.write_text(suite.read_text().replace("test_one", "test_one_renamed") + "\n\n" + CASE % ("pin_committed", 5))
    _repair_ledger(tmp_path, A="pending")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _repair_ledger(tmp_path, A="pending", B="pending")
    _commit(tmp_path, "B green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", REPAIR_STEP, "test_suite.py"], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, REPAIR_STEP)) == (
        0, ["test_one_renamed", "test_pin_committed", "test_pin_wip", "test_two"])


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_on_head_keeps_a_case_the_steps_own_refactor_commit_renamed_before_the_next_step_began_2724(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), CASE % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _ledger(tmp_path, A="pending")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text().replace("pin_committed", "pin_tidied"))
    _commit(tmp_path, "A refactor renames the pin")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A refactor verified")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later_step", 9))
    _ledger(tmp_path, A="done", B="pending")
    _commit(tmp_path, "B green")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_wip", 4))

    code = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)[0]

    assert (code, _names(tmp_path, tests_frozen, step)) == (0, ["test_one", "test_pin_tidied", "test_pin_wip"])


BODY = "def test_%s():\n    x = %d\n    assert x\n"


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_case_the_verified_refactor_tidied_and_leaves_one_already_stale_at_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    suite.write_text(suite.read_text().replace("x = 2\n    assert x\n", "x = 3\n    assert x\n"))
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2], "--except", "test_two"],
                     cwd=tmp_path)[:2]
    refused = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, spared, refused) == (0, (0, ""), (1, "test_two (%s)\n" % step))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_body_the_refactor_moved_into_a_shared_helper_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    helper = "def _value(n):\n    return n\n\n\n"
    suite.write_text(helper + suite.read_text().replace("x = 1\n", "x = _value(1)\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_assertion_line_the_refactor_only_reformatted_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    assert x == 1\n"]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("assert x == 1\n", "assert x==1\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_python_cases_record_when_the_refactor_changed_an_assertion_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n    assert x\n", "x = 1\n    assert x > 5\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_javascript_cases_record_when_the_refactor_changed_an_expect_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.js"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("it('one', () => {\n  const x = 1;\n  expect(x).toBe(1);\n});\n")
    git(tmp_path, "add", "suite.test.js")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.js"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("expect(x).toBe(1)", "expect(x).toBeGreaterThan(5)"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("before, after", [
    ('t.Fatalf("got %d", x)', 't.Fatalf("got %d, want 5", x+1)'),
    ('t.Errorf("got %d", x)', 't.Errorf("got %d, want 5", x+1)'),
    ('t.Fail()', 't.FailNow()'),
    ('require.Equal(t, 1, x)', 'require.Equal(t, 5, x)'),
])
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_changed_its_check_line_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, before, after):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\t%s\n\t}\n}\n" % before)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace(before, after))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_after_the_last_case_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_between_two_cases_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    two = 'func TestTwo(t *testing.T) {\n\tif 2 != 2 {\n\t\tt.Fatal("c")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n'
              + two)
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n\n' + two)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_0_for_a_go_case_after_a_helper_is_appended_at_eof_following_the_rerecord_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text(extracted + '\nfunc later(t *testing.T) {\n\tt.Fatal("z")\n}\n')
    _commit(tmp_path, "later helper")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_1_for_a_go_case_after_an_assertion_is_deleted_from_it_with_a_trailing_helper_following_the_rerecord_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    healed = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]
    suite.write_text(extracted.replace('\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n', ''))
    _commit(tmp_path, "assertion deleted from the case")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (healed, checked) == (0, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_the_record_and_check_earlier_exits_1_for_a_go_case_whose_refactor_moved_checks_into_a_helper_after_it_and_dropped_one_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + chk("c") + '}\n'
    dropped = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
               'func check(t *testing.T, x int) {\n' + chk("a") + '}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(dropped)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (0, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_prints_one_stderr_line_naming_each_case_it_left_unrecorded_and_still_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n'
    dropped = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '}\n'
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(dropped)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, err.splitlines().count("skipped: suite_test.go TestOne")) == (0, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_a_case_gone_at_head_a_digest_mismatch_and_an_assertionless_shape_change_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
    fn = lambda name, body: 'func %s(t *testing.T) {\n%s}\n\n' % (name, body)
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n" + chk) + fn("TestBare", "\tx := 1\n"))
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 1\n"))
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 2\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, sorted(l for l in err.splitlines() if l.startswith("skipped:"))) == (0, [
        "skipped: suite_test.go TestBare", "skipped: suite_test.go TestGone", "skipped: suite_test.go TestMismatch"])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_0_for_a_format_2_go_record_cut_with_the_body_running_past_the_closing_brace_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    import hashlib
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    text = ('func TestOne(t *testing.T) {\n\tx := 1\n\tcheck(t, x)\n}\n\n'
            'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(text)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    old_digest = hashlib.sha256(text.rstrip().encode()).hexdigest()
    record.write_text("".join(
        "body: suite_test.go\tTestOne\t%s\n" % old_digest if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_heals_a_format_2_go_record_cut_with_the_body_running_past_the_closing_brace_so_check_earlier_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    import hashlib
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    other = '\nfunc other(t *testing.T) {\n\tt.Fatal("z")\n}\n'
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n' + other
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n' + chk("a") + '}\n' + other)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    old_digest = hashlib.sha256(inline.rstrip().encode()).hexdigest()
    record.write_text("".join(
        "body: suite_test.go\tTestOne\t%s\n" % old_digest if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_the_record_of_a_case_with_no_assertion_line_when_the_refactor_changed_its_body_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\tpanic(x)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("panic(x)", "panic(x + 1)"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_cases_record_when_the_refactor_changed_its_title_and_body_together_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("def test_one():\n    x = 1\n", "def test_uno():\n    x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_still_re_records_the_other_cases_when_the_refactor_renamed_one_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n")
                     .replace("x = 2\n", "x = 3 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2], "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_still_re_records_the_other_cases_when_an_earlier_refactor_renamed_one_before_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n"))
    _commit(tmp_path, "A refactor renames a case")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 2\n", "x = 3 - 1\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C", "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_nothing_and_exits_3_unless_verdict_refactor_exit_holds_0_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    verdict, ledger = tmp_path / ".tdd/verdict-refactor.exit", ".tdd/issue-9.md"

    def records():
        return {str(p): p.read_bytes() for p in sorted((tmp_path / ".tdd").rglob("*"))
                if p.is_file() and p != verdict}
    before, outcomes = records(), []
    for held in (None, "1"):
        if held is not None:
            verdict.write_text(held)
        outcomes.append((run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0],
                         records() == before))

    assert outcomes == [(3, True), (3, True)]


@pytest.mark.process("git asked for the repository toplevel from a directory under tmp_path that is in none")
def test_rerecord_refactored_run_outside_any_git_repository_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    ledger, record = tmp_path / ".tdd/issue-9.md", tmp_path / ".tdd/record"
    ledger.write_text("- [x] step one\n")
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


@pytest.mark.process("git asked for the repository toplevel from a repository under tmp_path")
def test_rerecord_refactored_unreadable_ledger_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    _plan_repo(tmp_path, monkeypatch)
    (tmp_path / ".tdd/issue-9.md").unlink(missing_ok=True)
    (tmp_path / ".tdd/issue-9.md").mkdir()
    record = tmp_path / ".tdd/record"
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_2_naming_the_record_when_writing_it_raises_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_refactored(".tdd/issue-9.md", green)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the step's commits to HEAD")
def test_check_earlier_names_a_case_changed_in_a_refactor_commit_as_stale_against_a_verified_refactor_not_as_edited_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "refactor: tidy the cases of step A")

    code, out, _ = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)

    assert (code, out.startswith("test_one (%s)" % step), "stale" in out, "edited" in out) == (1, True, True, False)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the step's commits to HEAD")
def test_check_earlier_names_a_case_deleted_from_the_tree_after_a_refactor_commit_as_removed_not_as_stale_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "refactor: tidy the cases of step A")
    suite.write_text(CASE % ("base", 0))

    code, out, _ = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)

    assert (code, out) == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_case_with_no_assertion_line_when_the_refactor_only_changed_whitespace_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    check(x)\n"]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("check(x)\n", "check( x )\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_its_t_fatal_line_without_moving_it_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t}\n}\n")
    _commit(tmp_path, "A refactor drops the check")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_t_fatal_lines_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_its_t_fatal_lines_moved_into_another_test_function_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestShared(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tTestShared(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into another test")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_python_case_whose_assert_line_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("def test_one():\n    x = 1\n    assert x == 1\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    _commit(tmp_path, "A refactor moves the assert into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_a_later_commit_deleted_a_t_fatal_line_from_the_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the checks into a helper")
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor drops a check from the helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_one_of_two_identical_t_fatal_lines_while_moving_the_other_into_a_helper_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"bad\")\n\tt.Error(\"mid\")\n\tt.Fatal(\"bad\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T) {\n\tt.Fatal(\"bad\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t)\n\tt.Error(\"mid\")\n}\n")
    _commit(tmp_path, "A refactor moves one check into a helper and drops the other")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatal_lines_a_refactor_moved_into_a_helper_ahead_of_later_assertions_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_helper_lines_sort_before_its_own_remaining_assertion_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n\tt.Fatal(\"z later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tsetupX(t)\n\tt.Fatal(\"z later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_run_again_with_the_same_green_sha_heals_an_order_changing_helper_extractions_stale_record_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    ledger = ".tdd/issue-9.md"
    verdict = tmp_path / ".tdd/verdict-refactor.exit"
    verdict.write_text("1")
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    verdict.write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_1_for_a_go_case_after_a_t_fatal_line_is_deleted_from_its_helper_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the checks into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "later commit drops a check from the helper")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_1_for_a_python_case_after_an_assert_line_is_deleted_from_its_helper_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("def test_one():\n    x = 1\n    assert x == 1\n    assert x < 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("def check_one(x):\n    assert x == 1\n    assert x < 2\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    _commit(tmp_path, "A refactor moves the asserts into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    _commit(tmp_path, "later commit drops an assert from the helper")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_does_not_call_is_added_above_it_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text("func otherX(t *testing.T) {\n\tt.Fatal(\"unrelated\")\n}\n\n"
                     "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "later commit adds a helper the case does not call")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_0_for_a_go_case_after_an_assertion_line_is_deleted_from_a_helper_it_does_not_call_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    other = "func otherX(t *testing.T) {\n\tt.Fatal(\"first\")\n\tt.Fatal(\"second\")\n}\n\n"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text(other + "func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(other + "func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text(suite.read_text().replace("\tt.Fatal(\"second\")\n", ""))
    _commit(tmp_path, "later commit deletes an assertion line from a helper the case does not call")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_0_for_a_go_case_after_a_helper_it_calls_changes_keeping_every_assertion_line_following_the_rerecord_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tt.Log(\"checking\")\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "later commit changes the helper but keeps its assertion line")

    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the red commit to HEAD")
def test_check_earlier_passes_a_record_written_without_helper_data_when_nothing_changed_and_exits_1_when_the_case_body_changes_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    source = ("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
              "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    suite.write_text(source)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    ledger = ".tdd/issue-9.md"
    unchanged = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    suite.write_text(source.replace("x := 1\n\tcheckX", "x := 2\n\tcheckX"))
    _commit(tmp_path, "later commit changes the case body")
    changed = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)

    assert unchanged == (0, "")
    assert changed[0] == 1
    assert "TestX" in changed[1]


@pytest.mark.process("a real git repository under tmp_path, its history walked from the red commit to HEAD")
def test_check_earlier_exits_1_naming_the_case_when_its_body_changes_after_a_record_without_helper_data_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    source = "func TestX(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
    suite.write_text(source)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")

    suite.write_text(source.replace("1 != 1", "1 != 2"))
    _commit(tmp_path, "later commit changes the case body")
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)

    assert checked[0] == 1
    assert "TestX" in checked[1]


@pytest.mark.process("a real git repository under tmp_path, its record file read back by check")
def test_check_exits_0_on_a_record_holding_helper_data_when_no_test_file_changed_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T) {\n\tt.Fatal(\"bad\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tcheckX(t)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % ("0" * 64))

    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_check_earlier_exits_1_for_a_go_case_after_a_later_rerecord_refactored_over_a_t_fatal_line_deleted_from_its_helper_2867(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the checks into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "later commit drops a check from the helper")
    later_green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                                 text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("func checkX(t *testing.T, x int) {\n", "func checkX(t *testing.T, x int) {\n\tt.Log(\"checking\")\n"))
    _commit(tmp_path, "a second refactor touches only the helper")

    run_cli(tests_frozen, ["rerecord-refactored", ledger, later_green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)
