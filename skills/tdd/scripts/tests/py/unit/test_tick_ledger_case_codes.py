"""tick-ledger.sh reads a case command's exit code: a case that could not run is exit 2, one that ran and failed exit 1."""
import importlib

import pytest

ORIGINAL = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
CASE = "tests/test_x.py::test_holds"


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


@pytest.fixture
def retire(tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text(ORIGINAL)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    pass\n")

    def run():
        code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", CASE, str(ledger), "a one"],
                                 env={"VERI_ISSUE": "42"}, cwd=tmp_path)
        return code, ledger.read_text(), (ledger.parent / "events.jsonl").exists(), err

    return run


def test_a_case_command_exiting_126_is_a_case_never_run_naming_the_code_and_the_command_3986(retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, './run-one "$1"\n', ""), "": (126, "", "")})

    code, text, events, err = retire()

    assert (code, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and "126" in err and './run-one "$1" tests/test_x.py' in err


def test_a_case_command_exiting_127_is_a_case_never_run_naming_the_code_and_the_command_3986(retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, './run-one "$1"\n', ""), "": (127, "", "")})

    code, text, events, err = retire()

    assert (code, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and "127" in err and './run-one "$1" tests/test_x.py' in err


def test_a_case_command_killed_by_a_signal_exiting_137_is_a_case_never_run_3986(retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, './run-one "$1"\n', ""), "": (137, "", "")})

    code, text, events, err = retire()

    assert (code, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and "137" in err and './run-one "$1" tests/test_x.py' in err


@pytest.mark.parametrize("declared, code, signal_name", [
    ('./run-one "$1"\n', -9, "SIGKILL"), ("", -15, "SIGTERM")], ids=["one-test-file-command", "make-fallback"])
def test_a_case_command_killed_by_a_signal_python_reports_negative_is_a_case_never_run_naming_the_signal_3986(
        retire, fake_processes, declared, code, signal_name):
    fake_processes.answers({"detect-test-command.sh": (0, declared, ""), "": (code, "", "")})

    code_, text, events, err = retire()

    assert (code_, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and signal_name in err and "fails" not in err


@pytest.mark.parametrize("case, stdout, recipe", [
    ("tests/test_gone.py::test_holds", "ERROR: file or directory not found: tests/test_gone.py\n", 4),
    (CASE, "collected 0 items\n\nno tests ran in 0.01s\n", 5)], ids=["missing-path", "no-tests-ran"])
def test_the_make_test_fallback_reads_a_missing_path_or_no_tests_ran_as_a_case_never_run_3987(
        tmp_path, run_cli, tick_ledger, fake_processes, case, stdout, recipe):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text(ORIGINAL)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    pass\n")
    fake_processes.answers({"detect-test-command.sh": (0, "", ""),
                            "make": (2, stdout, f"make: *** [test] Error {recipe}\n")})

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", case, str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (2, ORIGINAL, False), err
    assert f"case {case} never run" in err and "fails" not in err


MAKE_DECLARED = 'make test TESTS="$1"\n'


@pytest.mark.parametrize("declared, code, stdout, stderr, expected", [
    (MAKE_DECLARED, 2, "E   assert 'make: *** [test] Error 2' == ''\n", "make: *** [test] Error 1\n", 1),
    (MAKE_DECLARED, 2, "", "make: *** [test] Error 2\nmake: *** [test] Error 1\n", 2),
    (MAKE_DECLARED, 2, "*** [x] Error 1\n", "make: *** [test] Error 127\n", 2),
    ("", 2, "make: *** [test] Error 1\n", "sh: run-tests: command not found\nmake: *** [test] Error 127\n", 2),
    ("", 2, "", "make[1]: *** [inner] Error 1\nmake: *** [test] Error 2\n", 2),
    ("", 2, "", "make[1]: *** [inner] Error 2\nmake: *** [test] Error 2\n", 2),
    ("", 2, "", "make: *** [a] Error 1\nmake: *** [b] Error 127\nmake: Target `all' not remade because of errors.\n", 2),
    ("", 2, "", "make: *** [a] Error 127\nmake: *** [b] Error 1\nmake: Target `all' not remade because of errors.\n", 2),
    ("", 1, "1 failed\n", "", 2),
    ("", 2, "", "make: foo: No such file or directory\n1 failed\nmake: *** [test] Error 1\n", 1),
    ('./run-one "$1"\n', 2, "", "make: *** [t] Error 1\n", 2),
    ("", 2, "", "make[1]: *** [lint] Error 1\nmake: *** [test] Error 2\n", 2),
    ("", 2, "make: *** [test] Error 1\n", "", 2),
    (MAKE_DECLARED, 2, "make: *** [test] Error 1\n", "", 2),
    ("", 2, "", "make: *** [a] Error 2\nmake: *** [b] Error 1\nmake: Target `test' not remade because of errors.\n", 2),
    ("", 2, "", "make: *** [a] Error 2\nmake: *** [test] Error 1\n", 2),
], ids=["test-output-spoofs-error-2", "two-level-0-lines-one-not-1", "recipe-127-after-printing-error-1",
        "fallback-127-after-test-printed-error-1", "nested-inner-error-1-reads-no-answer", "nested-inner-error-2",
        "make-k-last-127", "make-k-last-1", "fallback-non-zero-with-no-make-line", "not-found-line-not-adjacent",
        "declared-non-make-runner-fakes-makes-line", "make-lint-or-true-then-exit-2", "fallback-line-only-on-stdout",
        "declared-make-line-only-on-stdout", "make-k-a-2-b-1", "level-0-error-2-then-final-error-1"])
def test_only_a_final_level_0_make_error_1_line_on_stderr_reads_as_a_case_that_fails_3987(
        retire, fake_processes, declared, code, stdout, stderr, expected):
    fake_processes.answers({"detect-test-command.sh": (0, declared, ""), "": (code, stdout, stderr)})

    got, text, events, err = retire()

    assert (got, text, events) == (expected, ORIGINAL, False), err


@pytest.mark.parametrize("stderr, expected", [
    ("no newlinemake: *** [a] Error 2\nmake: *** [b] Error 1\n", 2),
    ("make: *** [a] Killed: 9\nmake: *** [b] Error 1\n", 2),
    ("make: *** [test] Killed: 9\nmake: *** [test] Error 1\n", 2),
    ("1 failedmake: *** [test] Error 2\nmake: *** [test] Error 1\n", 2),
    ("make: *** [a]b] Error 1\n", 1),
    ("1 failed\r\nmake: *** [test] Error 1  \r\n\r\n", 1),
    ("make: [lint] Error 2 (ignored)\nmake: *** [test] Error 1\n", 1),
], ids=["j2-glued-error-2-then-error-1", "j2-killed-then-error-1", "killed-then-fake-error-1",
        "glued-error-2-then-fake-error-1", "target-holding-a-bracket", "crlf-and-trailing-blanks",
        "ignored-error-2-then-real-error-1"])
def test_any_top_level_make_line_ending_other_than_error_1_reads_as_no_answer_3987(
        retire, fake_processes, stderr, expected):
    fake_processes.answers({"detect-test-command.sh": (0, "", ""), "": (2, "", stderr)})

    got, text, events, err = retire()

    assert (got, text, events) == (expected, ORIGINAL, False), err


@pytest.mark.parametrize("stderr", [
    "make: no-such-command-xyz: No such file or directory\nmake: *** [test] Error 1\n",
    "make: ./noexec: Permission denied\nmake: *** [test] Error 1\n",
    "make[1]: no-such-xyz: No such file or directory\nmake[1]: *** [inner] Error 1\nmake: *** [test] Error 2\n",
], ids=["not-found", "not-executable", "nested-not-found"])
def test_a_recipe_command_make_itself_could_not_execute_is_a_case_never_run_3986(retire, fake_processes, stderr):
    fake_processes.answers({"detect-test-command.sh": (0, "", ""), "": (2, "", stderr)})

    code, text, events, err = retire()

    assert (code, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and "fails" not in err


def test_a_case_command_exiting_3_is_a_case_that_ran_and_failed_exit_1_3986(retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, './run-one "$1"\n', ""), "": (3, "", "")})

    code, text, events, err = retire()

    assert (code, text, events) == (1, ORIGINAL, False), err
    assert f"case {CASE} fails" in err and "never run" not in err


def test_a_case_command_exiting_2_with_makes_error_1_line_is_a_case_that_ran_and_failed_exit_1_3987(
        retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, 'make test TESTS="$1"\n', ""),
                            "": (2, "1 failed\n", "make: *** [test] Error 1\n")})

    code, text, events, err = retire()

    assert (code, text, events) == (1, ORIGINAL, False), err
    assert f"case {CASE} fails" in err and "never run" not in err


def test_a_case_command_exiting_2_with_makes_error_2_line_stays_a_case_never_run_exit_2_3987(retire, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, 'make test TESTS="$1"\n', ""),
                            "": (2, "", "make: *** [test] Error 2\n")})

    code, text, events, err = retire()

    assert (code, text, events) == (2, ORIGINAL, False), err
    assert f"case {CASE} never run" in err and "fails" not in err


def test_the_make_test_fallback_reads_makes_error_1_line_as_a_case_that_ran_and_failed_exit_1_3987(
        retire, fake_processes):
    fake = fake_processes.answers({"detect-test-command.sh": (0, "", ""),
                                   "": (2, "1 failed\n", "make: *** [test] Error 1\n")})

    code, text, events, err = retire()

    assert ["make", "test", f"TESTS={CASE}"] in fake.argvs
    assert (code, text, events) == (1, ORIGINAL, False), err
    assert f"case {CASE} fails" in err and "never run" not in err


def test_run_case_returns_the_command_it_ran_and_the_process_exit_code_with_its_answer_4298(tick_ledger, fake_processes):
    fake_processes.answers({"detect-test-command.sh": (0, './run-one "$1"\n', ""), "": (127, "", "")})

    assert tick_ledger.run_case(CASE) == (2, './run-one "$1" tests/test_x.py', 127)
