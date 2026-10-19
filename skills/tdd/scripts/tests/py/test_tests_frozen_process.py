"""Cases for veri/tests_frozen.py that run git in a real repository under tmp_path."""
import importlib
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
