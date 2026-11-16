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
