"""In-process cases for veri/bail.py, the module bail.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def bail():
    return importlib.import_module("veri.bail")


def test_no_argument_prints_a_usage_line_naming_bail_md_sub_step_1_on_stderr_and_exits_2_with_no_call(
        run_cli, fake_processes, bail):
    fake = fake_processes.answers({})

    code, out, err = run_cli(bail, [])

    assert (code, out, fake.calls) == (2, "", [])
    assert err.strip() != "" and "usage" in err.splitlines()[0]
    assert "BAIL.md sub-step 1" in err.splitlines()[-1]


def test_other_bad_arguments_exit_2_with_no_call_the_last_line_naming_bail_md_sub_step_1(
        run_cli, fake_processes, bail):
    bad = {
        "non-numeric n": ["abc", "tests-red", "red", "--note-file", "n.md"],
        "missing cause": ["7"],
        "missing phase": ["7", "tests-red", "--note-file", "n.md"],
        "no note file": ["7", "tests-red", "red"],
        "non-numeric attempt": ["7", "tests-red", "red", "--note-file", "n.md", "--attempt", "x"],
    }
    for label, argv in bad.items():
        fake = fake_processes.answers({})

        code, out, err = run_cli(bail, argv)

        assert (label, code, out, fake.calls) == (label, 2, "", [])
        assert "BAIL.md sub-step 1" in err.splitlines()[-1], label


def test_a_stray_argument_after_note_file_or_a_valueless_or_trailing_attempt_exits_2_with_no_call(
        run_cli, fake_processes, bail):
    bad = {
        "other flag after note file": ["7", "tests-red", "red", "--note-file", "n.md", "--force"],
        "attempt with no value": ["7", "tests-red", "red", "--note-file", "n.md", "--attempt"],
        "more arguments after attempt": ["7", "tests-red", "red", "--note-file", "n.md", "--attempt", "2", "extra"],
    }
    for label, argv in bad.items():
        fake = fake_processes.answers({})

        code, out, err = run_cli(bail, argv)

        assert (label, code, out, fake.calls) == (label, 2, "", [])
        assert "BAIL.md sub-step 1" in err.splitlines()[-1], label


def test_an_unknown_cause_exits_2_after_classify_bail_alone_with_no_reset_event_or_later_call(
        run_cli, fake_processes, bail):
    fake = fake_processes.answers(
        {"classify-bail.sh unknown-cause": (2, "", "classify-bail: unknown cause\n")}, default=(0, "", ""))

    code, out, err = run_cli(bail, ["7", "unknown-cause", "red", "--note-file", "n.md"])

    assert (code, fake.calls) == (2, ["classify-bail.sh unknown-cause"])
    assert "BAIL.md sub-step 1" in err.splitlines()[-1]
