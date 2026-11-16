"""In-process cases for veri/ci_flake.py, the module ci-flake.sh is a shim over."""
import importlib
import json
import pathlib

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


REAL_LOG = pathlib.Path(__file__).parents[2] / "fixtures" / "ci-failed-log" / "run-43927348629.log"
REAL_TARGET = ("skills/tdd/scripts/tests/py/unit/test_local_process_fakes.py::"
               "test_no_test_file_outside_the_list_installs_its_own_fake_on_subprocess")


def test_4018_a_real_gh_failed_log_with_its_byte_order_mark_before_the_first_timestamp_yields_its_one_failed_target(
        tmp_path, run_cli, fake_processes, ci_flake):
    fake = fake_processes.answers({"sh -c": (1, "", "")})

    code, _, err = run_cli(ci_flake, ["4018", HEAD, "43927348629", ALONE, str(REAL_LOG)], cwd=tmp_path)

    assert (code, fake.argvs, err) == (1, [["sh", "-c", ALONE, "sh", REAL_TARGET]], "")


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


@pytest.mark.parametrize("case", ["alone-run-hangs", "alone-run-killed-by-a-signal", "alone-run-child-killed-137", "unprefixed-line", "glued-line", "event-unwritable"])
def test_4018_exits_2_when_an_alone_run_gets_no_answer_the_log_holds_a_line_without_gh_s_prefix_or_the_event_is_not_written(
        tmp_path, run_cli, fake_processes, ci_flake, events, monkeypatch, case):
    from process_fakes import HANGS
    started = []
    monkeypatch.setattr(ci_flake.github.os, "killpg",
                        lambda pid, sig: [p.send_signal(sig) for p in started[0].popens if p.pid == pid])
    log = {"unprefixed-line": RED_LOG + "FAILED skills/a/test_z.py::test_three\n",
           "glued-line": RED_LOG.replace("\n", " ", 1)}.get(case, RED_LOG)
    if case == "event-unwritable":
        monkeypatch.setattr(ci_flake.event, "mark", lambda *args, **kwargs: 2)
    fake = fake_processes.answers({"sh -c": HANGS if case == "alone-run-hangs" else
                                   [(0, "", ""), (-9, "", "")] if case == "alone-run-killed-by-a-signal" else
                                   [(0, "", ""), (137, "", "")] if case == "alone-run-child-killed-137" else (0, "", ""),
                                   "gh run rerun": (0, "", "")})
    started.append(fake)

    code, out, err = run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path, log)], cwd=tmp_path)

    assert (code, out, "Traceback" in err, bool(err.strip())) == (2, "", False, True)
    assert [c for c in fake.calls if c.startswith("gh")] == (
        ["gh run rerun 12345 --failed"] if case == "event-unwritable" else [])


OTHER = "f" * 40


def _journal(tmp_path, *lines):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(
        json.dumps(dict({"ts": 1763300000 + i, "awake": 0}, **fields)) + "\n" for i, fields in enumerate(lines)))


START = {"issue": "4018", "event": "conductor-start", "pid": "7", "started": ""}


@pytest.mark.parametrize("knob, journal, answer", [
    ("0", [START], 3),
    ("x", [START], 2),
    (None, [START, {"issue": "4018", "event": "ci-rerun", "head": OTHER, "run": "9", "files": "t"}], 3),
    ("5", [{"issue": "4018", "event": "ci-rerun", "head": HEAD, "run": "9", "files": "t"}, START], 3),
    (None, [{"issue": "4018", "event": "ci-rerun", "head": OTHER, "run": "9", "files": "t"}, START], 0),
    (None, [START, {"issue": "77", "event": "ci-rerun", "head": OTHER, "run": "9", "files": "t"}], 0),
], ids=["knob-0", "knob-not-whole", "budget-spent-this-run", "head-re-run-in-an-earlier-run", "spent-in-an-earlier-run-only",
        "another-issues-re-run"])
def test_4018_exits_3_running_nothing_and_writing_no_event_when_the_run_s_re_runs_are_spent_or_the_head_was_re_run(
        tmp_path, run_cli, fake_processes, ci_flake, events, knob, journal, answer):
    _journal(tmp_path, *journal)
    before = events.records(tmp_path)
    fake = fake_processes.answers({"sh -c": (0, "", ""), "gh run rerun": (0, "", "")})
    env = {} if knob is None else {"VERI_CI_FLAKE_RERUNS": knob}

    code, out, _ = run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path)], env=env, cwd=tmp_path)

    assert code == answer
    if answer in (2, 3):
        assert (out, fake.calls, events.records(tmp_path)) == ("", [], before)


def test_4018_counts_only_ci_rerun_events_re_running_with_other_budgets_spent_and_a_ci_repair_step_and_never_readies_the_pr(
        tmp_path, run_cli, fake_processes, ci_flake):
    _journal(tmp_path, START,
             {"issue": "4018", "event": "adjudicated", "cause": "ci-timeout", "outcome": "retry", "reason": ""},
             {"issue": "4018", "event": "revise", "budget": "0"})
    (tmp_path / ".tdd" / "issue-4018.md").write_text(
        "# Plan for #4018\n\n- [x] a step\n- [ ] ⟦ci-repair⟧ CI red: test_x fails\n")
    fake = fake_processes.answers({"sh -c": (0, "", ""), "gh run rerun 12345 --failed": (0, "", "")})

    code, out, _ = run_cli(ci_flake, ["4018", HEAD, "12345", ALONE, _log(tmp_path)],
                           env={"REVISE_BUDGET": "0", "VERI_ADJUDICATE_BUDGET": "0"}, cwd=tmp_path)

    assert (code, out.splitlines()) == (0, TARGETS)
    assert [c for c in fake.calls if c.startswith("gh")] == ["gh run rerun 12345 --failed"]


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
