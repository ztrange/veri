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
    earlier, unrecorded, current = "step one adds a case", "⟦diff-checked⟧ step two", "step three adds another"
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
