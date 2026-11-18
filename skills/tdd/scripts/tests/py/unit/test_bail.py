"""In-process cases for veri/bail.py, the module bail.sh is a shim over."""
import importlib
import os

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


def test_a_known_cause_snapshots_resets_then_writes_the_bail_event_with_the_phase_and_classification_in_order(
        run_cli, fake_processes, bail, tmp_path):
    fake = fake_processes.answers(
        {"ledger-steps.sh current-or-last-done": (0, "3\n", ""),
         "classify-bail.sh tests-red": (0, "process\n", "")}, default=(0, "", ""))

    code, out, err = run_cli(bail, ["7", "tests-red", "red", "--note-file", "n.md", "--attempt", "2"], cwd=tmp_path)

    ordered = [line for line in fake.calls
               if line.startswith(("preserve-attempt.sh", "git reset", "event.sh"))]
    assert ordered == ["preserve-attempt.sh 7 3 red 2 bail", "git reset --hard HEAD",
                       "event.sh bail cause=tests-red classification=process"]
    event_env = [kwargs.get("env") or {} for argv, kwargs in fake.seen if os.path.basename(argv[0]) == "event.sh"][0]
    assert event_env.get("VERI_PHASE") == "red"


def test_without_attempt_the_snapshot_is_taken_as_attempt_1(run_cli, fake_processes, bail, tmp_path):
    fake = fake_processes.answers(
        {"ledger-steps.sh current-or-last-done": (0, "3\n", ""),
         "classify-bail.sh tests-red": (0, "process\n", "")}, default=(0, "", ""))

    code, out, err = run_cli(bail, ["7", "tests-red", "red", "--note-file", "n.md"], cwd=tmp_path)

    assert code == 0
    assert [c for c in fake.calls if c.startswith("preserve-attempt.sh")] == ["preserve-attempt.sh 7 3 red 1 bail"]
