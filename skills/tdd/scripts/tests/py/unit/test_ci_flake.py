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


def _marks(tmp_path, *shas):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    for sha in shas:
        for kind in ("deadline", "queued", "none", "head"):
            (tmp_path / ".tdd" / ("ci-%s-%s" % (kind, sha))).write_text("1763300000\n")


def test_4018_every_target_green_alone_and_the_re_run_accepted_exits_0_with_one_ci_rerun_event_fresh_marks_and_the_targets(
        tmp_path, run_cli, fake_processes, ci_flake, events):
    other = "f" * 40
    _marks(tmp_path, HEAD, other)
    fake = fake_processes.answers({"sh -c": (0, "", ""), "gh run rerun 12345 --failed": (0, "", "")})

    code, out, _ = run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path)], cwd=tmp_path)

    assert (code, out.splitlines()) == (0, TARGETS)
    assert "gh run rerun 12345 --failed" in fake.calls
    assert [(e["event"], e["issue"], e.get("head"), e.get("run"), e.get("files")) for e in events.records(tmp_path)] == [
        ("ci-rerun", "4018", HEAD, "12345", ",".join(TARGETS))]
    assert sorted(p.name for p in (tmp_path / ".tdd").glob("ci-*")) == sorted(
        "ci-%s-%s" % (kind, other) for kind in ("deadline", "queued", "none", "head"))


@pytest.mark.parametrize("argv, rerun", [
    (["4018", HEAD, "12345", ALONE], (0, "", "")),
    (["x", HEAD, "12345", ALONE, "LOG"], (0, "", "")),
    (["4018", HEAD, "run-7", ALONE, "LOG"], (0, "", "")),
    (["4018", HEAD, "12345", ALONE, "MISSING"], (0, "", "")),
    (["4018", HEAD[:7], "12345", ALONE, "LOG"], (0, "", "")),
    (["4018", HEAD.upper(), "12345", ALONE, "LOG"], (0, "", "")),
    (["4018", HEAD, "12345", ALONE, "LOG"], (1, "", "HTTP 403: Must have admin rights")),
], ids=["four-arguments", "issue-not-whole", "run-id-not-whole", "unreadable-log", "short-head", "upper-case-head",
        "gh-refuses"])
def test_4018_exits_2_writing_no_ci_rerun_event_on_bad_arguments_an_unreadable_log_a_head_not_40_hex_or_gh_refusing(
        tmp_path, run_cli, fake_processes, ci_flake, events, argv, rerun):
    log = _log(tmp_path)
    argv = [{"LOG": log, "MISSING": str(tmp_path / "absent.log")}.get(a, a) for a in argv]
    fake_processes.answers({"sh -c": (0, "", ""), "gh run rerun": rerun})

    code, out, err = run_cli(ci_flake, argv, cwd=tmp_path)

    assert (code, out, [e["event"] for e in events.records(tmp_path)]) == (2, "", [])
    assert err.strip() and "Traceback" not in err


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
