"""In-process `record --step` cases for veri/tests_frozen.py, on a case history fed by fed_history (PRD 017.5)."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
PY_SUITE, SH_SUITE = "tests/test_suite.py", "tests/suite.test.sh"
NEW, HELPER = "tests/test_new.py", "tests/helper.test.sh"


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


def recorded(run_cli, tests_frozen, tmp_path, step, name):
    """The record `record --step <step> <name>` writes, as text."""
    run_cli(tests_frozen, ["record", "--step", step, name], cwd=tmp_path)
    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    return (tmp_path / record_path.rstrip("\n")).read_text()


def test_record_step_holds_a_helper_test_file_red_changed_beside_its_test_path_so_check_step_exits_0_1733(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({NEW: "one\n", HELPER: "one\n"})
    step = "step one adds a case"
    (tmp_path / NEW).write_text("one\ntwo\n")
    (tmp_path / HELPER).write_text("one\nred's helper\n")
    run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)

    code, out, _ = run_cli(tests_frozen, ["check", "--step", step], cwd=tmp_path)

    assert (code, out) == (0, "")


def test_record_step_lists_by_name_the_pytest_function_red_added_to_a_test_file_1765(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case():\n    assert True\n"})
    step = "step one adds a case"
    (tmp_path / PY_SUITE).write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_added_by_red_1765():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert "test_added_by_red_1765" in record


def test_record_step_lists_by_name_the_bash_case_red_added_to_a_test_sh_suite_1765(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SH_SUITE: 'name="older case"\ncheck_older\n'})
    step = "step one adds a bash case"
    (tmp_path / SH_SUITE).write_text('name="older case"\ncheck_older\nname="added by red 1765"\ncheck_added\n')

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert ("case: added by red 1765\n" in record, "older case" in record) == (True, False)


def test_record_step_lists_by_name_the_pytest_function_red_edited_and_not_the_one_it_left_alone_1765(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_edited_by_red_1765():\n    assert 1 == 2\n\n\n"
                              "def test_left_alone_1765():\n    assert True\n"})
    step = "step one edits a case"
    (tmp_path / PY_SUITE).write_text("def test_edited_by_red_1765():\n    assert 1 == 1\n\n\n"
                                     "def test_left_alone_1765():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_edited_by_red_1765\n" in record, "test_left_alone_1765" in record) == (True, False)


def test_record_step_lists_only_the_bash_case_red_added_before_the_finish_trailer_not_the_previous_last_case_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SH_SUITE: 'name="first case"\ncheck_first\nok\n\n'
                              'name="last case"\ncheck_last\nok\n\nfinish\n'})
    step = "step one adds a case before finish"
    (tmp_path / SH_SUITE).write_text('name="first case"\ncheck_first\nok\n\n'
                                     'name="last case"\ncheck_last\nok\n\n'
                                     'name="added by red 1861"\ncheck_added\nok\n\nfinish\n')

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert ("case: added by red 1861\n" in record, "last case" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_inserted_at_file_start_above_an_older_one_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "\ndef test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the older one"
    (tmp_path / PY_SUITE).write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_that_had_one_blank_line_above_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "LIMIT = 1\n\ndef test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the older one"
    (tmp_path / PY_SUITE).write_text("LIMIT = 1\n\n\ndef test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_in_a_class_and_a_wrong_test_naming_the_older_one_routes_red_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
                              "    def test_older_case_1861(self):\n        assert True\n"})
    step = "step one inserts a method above the older one"
    (tmp_path / PY_SUITE).write_text(
        "import pytest\n\n\nclass TestSuite:\n    def test_first_1861(self):\n        assert True\n\n"
        "    def test_inserted_by_red_1861(self):\n        assert True\n\n"
        "    def test_older_case_1861(self):\n        assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_bash_case_red_inserted_above_an_older_one_whose_blank_lines_above_changed_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SH_SUITE: 'setup\n\nname="older case"\ncheck_older\nok\n\nfinish\n'})
    step = "step one inserts a bash case above the older one"
    (tmp_path / SH_SUITE).write_text('setup\n\nname="inserted by red 1861"\ncheck_added\nok\n'
                                     'name="older case"\ncheck_older\nok\n\nfinish\n')

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert ("case: inserted by red 1861\n" in record, "older case" in record) == (True, False)


def test_record_step_lists_only_the_pytest_function_red_appended_after_an_older_one_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case_1861():\n    assert True\n"})
    step = "step one appends a case after the older one"
    (tmp_path / PY_SUITE).write_text("def test_older_case_1861():\n    assert True\n\n\n"
                                     "def test_appended_by_red_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_appended_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_bash_case_red_appended_at_the_end_of_a_suite_with_no_finish_trailer_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({SH_SUITE: 'name="older case"\ncheck_older\nok\n'})
    step = "step one appends a bash case with no trailer"
    (tmp_path / SH_SUITE).write_text('name="older case"\ncheck_older\nok\n\n\n'
                                     'name="appended by red 1861"\ncheck_added\nok\n')

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert ("case: appended by red 1861\n" in record, "older case" in record) == (True, False)


# run-finished.test.sh as it stood before #1378 replaced it with pytest cases, frozen
REAL_SUITE = Path(__file__).resolve().parents[2] / "fixtures" / "tests-frozen" / "run-finished.test.sh.txt"


def test_record_step_lists_only_the_case_red_appended_to_a_real_copy_of_a_bash_suite_with_its_finish_trailer_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    real = REAL_SUITE.read_text()
    committed_once({SH_SUITE: real})
    step = "step one appends a case to a real suite"
    head, _, _ = real.rpartition("\nfinish\n")
    (tmp_path / SH_SUITE).write_text(head + '\n\nname="appended by red 1861"\ncheck_added\nok\n\nfinish\n')

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: appended by red 1861"]


def test_record_step_lists_only_the_pytest_function_red_inserted_above_an_older_one_on_the_files_first_line_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "def test_older_case_1861():\n    assert True\n"})
    step = "step one inserts a case above the one on line one"
    (tmp_path / PY_SUITE).write_text("def test_inserted_by_red_1861():\n    assert True\n\n\n"
                                     "def test_older_case_1861():\n    assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_only_the_pytest_method_red_inserted_above_an_older_method_directly_under_its_class_line_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    committed_once({PY_SUITE: "class TestSuite:\n    def test_older_case_1861(self):\n        assert True\n"})
    step = "step one inserts a method under the class line"
    (tmp_path / PY_SUITE).write_text("class TestSuite:\n    def test_inserted_by_red_1861(self):\n        assert True\n\n"
                                     "    def test_older_case_1861(self):\n        assert True\n")

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert ("case: test_inserted_by_red_1861\n" in record, "test_older_case_1861" in record) == (True, False)


def test_record_step_lists_the_last_bash_case_red_edited_below_a_heredoc_finish_line_when_no_finish_trailer_ends_the_file_1773(
        tmp_path, run_cli, tests_frozen, committed_once):
    suite = 'name="first case"\ncheck_first\nok\n\nname="heredoc case"\ncat > script.sh <<\'EOF\'\nfinish\nEOF\ncheck_heredoc %s\n'
    committed_once({SH_SUITE: suite % "one"})
    step = "step one edits the last case below a heredoc finish with no trailer"
    (tmp_path / SH_SUITE).write_text(suite % "two")

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: heredoc case"]


def test_record_step_lists_the_bash_case_red_edited_below_an_indented_finish_line_inside_its_body_1861(
        tmp_path, run_cli, tests_frozen, committed_once):
    suite = ('name="first case"\ncheck_first\nok\n\n'
             'name="finishing case"\nif true; then\n  finish_up\n  finish\nfi\ncheck_finishing %s\n')
    committed_once({SH_SUITE: suite % "one"})
    step = "step one edits below an indented finish inside a case"
    (tmp_path / SH_SUITE).write_text(suite % "two")

    record = recorded(run_cli, tests_frozen, tmp_path, step, SH_SUITE)

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: finishing case"]


def test_record_step_run_outside_any_git_repository_exits_2_with_stderr_naming_the_missing_repository_and_writes_no_record_1960(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / NEW).write_text("one\n")
    monkeypatch.setattr(tests_frozen, "_toplevel", lambda: None)
    step = "step one adds a case"

    code, out, err = run_cli(tests_frozen, ["record", "--step", step, NEW], cwd=tmp_path)

    assert (code, out, "repository" in err,
            [p.name for p in (tmp_path / ".tdd").iterdir() if p.name != "events.jsonl"]) == (2, "", True, [])


def test_record_step_for_a_red_whose_only_test_change_deletes_a_tracked_test_file_records_the_deletion_and_exits_0_1960(
        tmp_path, run_cli, tests_frozen, committed_once):
    old = "tests/test_old.py"
    committed_once({old: "one\n"})
    step = "step one deletes a test file"
    (tmp_path / old).unlink()

    code, out, _ = run_cli(tests_frozen, ["record", "--step", step], cwd=tmp_path)

    _, record_path, _ = run_cli(tests_frozen, ["path", step], cwd=tmp_path)
    record = tmp_path / record_path.strip()
    assert (code, out, record.read_text() if record.exists() else None) == (0, "", "deleted  %s\n" % old)


def test_record_step_lists_the_pytest_function_red_edited_below_a_finish_line_inside_its_multiline_string_1773(
        tmp_path, run_cli, tests_frozen, committed_once):
    body = ('def test_first():\n    assert True\n\n\n'
            'def test_last():\n    text = """\nfinish\n"""\n    assert text == {!r}\n')
    committed_once({PY_SUITE: body.format("one")})
    step = "step one edits a function below a string finish"
    (tmp_path / PY_SUITE).write_text(body.format("two"))

    record = recorded(run_cli, tests_frozen, tmp_path, step, PY_SUITE)

    assert [line for line in record.splitlines() if line.startswith("case: ")] == ["case: test_last"]
