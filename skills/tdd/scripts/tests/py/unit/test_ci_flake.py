"""In-process cases for veri/ci_flake.py, the module ci-flake.sh is a shim over."""
import importlib

import pytest

HEAD = "0123456789abcdef0123456789abcdef01234567"
ALONE = 'make test TESTS="$1"'
PREFIX = "test\tRun make test\t2026-11-13T18:30:0%d.1234567Z "
RED_LOG = "".join(PREFIX % i + text + "\n" for i, text in enumerate([
    "============ short test summary info ============",
    "FAILED skills/a/test_x.py::test_one - AssertionError: boom",
    "FAILED skills/a/test_y.py::test_two",
    "##[error]Process completed with exit code 1.",
]))
TARGETS = ["skills/a/test_x.py::test_one", "skills/a/test_y.py::test_two"]


@pytest.fixture
def ci_flake():
    return importlib.import_module("veri.ci_flake")


def _log(tmp_path, text=RED_LOG):
    path = tmp_path / "ci-failed.log"
    path.write_text(text)
    return str(path)


def test_4018_reads_the_targets_of_a_gh_prefixed_failed_log_and_runs_each_once_alone_with_the_target_as_1(
        tmp_path, run_cli, fake_processes, ci_flake):
    fake = fake_processes.answers({"sh -c": (1, "", "")})

    run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path)], cwd=tmp_path)

    assert fake.argvs == [["sh", "-c", ALONE, "sh", target] for target in TARGETS]


@pytest.mark.parametrize("log, alone", [
    (PREFIX % 0 + "##[error]Process completed with exit code 2.\n", []),
    (RED_LOG, [(0, "", ""), (1, "", "")]),
], ids=["no-target", "one-target-stays-red"])
def test_4018_exits_1_writing_no_event_and_making_no_re_run_when_the_log_names_no_target_or_one_stays_red_alone(
        tmp_path, run_cli, fake_processes, ci_flake, log, alone):
    fake = fake_processes.answers({"sh -c": alone, "gh": (0, "", "")})

    code, out, _ = run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path, log)], cwd=tmp_path)

    assert (code, out, [c for c in fake.calls if c.startswith("gh")]) == (1, "", [])
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()
