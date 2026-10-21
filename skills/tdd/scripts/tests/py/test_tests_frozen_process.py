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
