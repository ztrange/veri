"""In-process cases for veri/branch_gate.py, the module branch-gate.sh is a shim over (PRD 027.7, #4030)."""
import importlib
import json
import os

import pytest

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
FULL = "make test"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, mode="local"):
        self.answers, self.calls, self.mode = dict(answers or {}), [], mode

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "branch-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "detect-test-command.sh":
            return 0, FULL + "\n", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 0, "PASSED 812\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def gate(monkeypatch, run_cli, tmp_path):
    """gate(answers=None, fake=None, missing=(), ledger=LEDGER, argv=None) runs branch-gate for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    branch_gate = importlib.import_module("veri.branch_gate")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), ledger=LEDGER, argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_bytes(text) if isinstance(text, bytes) else path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(branch_gate, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4030_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(gate):
    code, out, err, fake = gate(argv=())

    assert (code, "branch-gate.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.branch_gate").__file__)
    assert os.path.exists(os.path.join(here, "..", "branch-gate.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4030_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(gate, missing, named):
    code, out, err, fake = gate(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("ledger", ["# Plan\n\n- [x] one\n- [ ] two ⟦criterion 2⟧\n",
                                    "# Plan\n\n- [x] one\n- [ ] re-pin it ⟦diff-checked⟧\n"],
                         ids=["an unchecked step", "an unchecked diff-checked step"])
def test_4030_a_step_next_unchecked_would_still_hand_out_is_exit_2_before_any_inner_call(gate, ledger):
    code, out, err, fake = gate(ledger=ledger)

    assert (code, fake.calls) == (2, [])
    assert "unchecked step" in err


@pytest.mark.parametrize("ledger, refused", [
    ("# Plan\n\n- [x] one\n- [\0 ] two ⟦criterion 2⟧\n".encode(), True),
    ("# Plan\n\n- [x] one ⟦criterion 1⟧\r- [ ] two ⟦criterion 2⟧\n".encode(), False)],
    ids=["a NUL inside an open step's box", "a lone carriage return"])
def test_4030_the_ledger_is_read_as_next_unchecked_reads_it(gate, ledger, refused):
    code, out, err, fake = gate(ledger=ledger)

    assert (code == 2 and fake.calls == []) == refused


def test_4030_only_full_suite_and_human_owed_lines_left_unchecked_let_it_run(gate):
    code, out, err, fake = gate(ledger=LEDGER + "- [ ] a human reads it ⟦human-owed⟧\n")

    assert code == 0 and fake.calls


def test_4030_under_ci_it_settles_branch_suite_ci_and_runs_nothing_more(gate):
    code, out, err, fake = gate(fake=Fake(mode="ci"))

    assert (code, out.splitlines()[-1]) == (0, "branch_suite=ci")
    assert [(c[0], c[1], c[2]) for c in fake.calls] == [("branch-suite.sh", (), str(gate.wt))]
    assert (gate.wt / ".tdd" / "issue-12-branch-gate").read_text() == "branch_suite=ci\n"


def test_4030_under_local_it_runs_the_full_command_inside_the_full_suite_stage_records_its_time_and_settles_local(
        gate, monkeypatch):
    clock = iter([1000.0, 1042.0])
    monkeypatch.setattr("time.time", lambda: next(clock))
    code, out, err, fake = gate()

    assert (code, out.splitlines()[-1]) == (0, "branch_suite=local")
    assert [(c[0], c[1]) for c in fake.calls] == [
        ("branch-suite.sh", ()), ("detect-test-command.sh", ("--tier", "all")),
        ("event.sh", ("stage-start", "stage=full-suite")), ("detach-command.sh", ("start", "branch-full-12", "sh", "-c", "make test")),
        ("detach-command.sh", ("wait", "branch-full-12")),
        ("event.sh", ("stage-end", "stage=full-suite", "status=0", "secs=42")),
        ("full-tier-time.sh", ("--record", "42", FULL))]
    for c in fake.calls:
        if c[0] == "event.sh":
            assert (c[3]["VERI_ISSUE"], c[3]["VERI_ACTOR"]) == ("12", "conductor")
    assert all(c[2] == str(gate.wt) for c in fake.calls)
    assert (gate.wt / ".tdd" / "issue-12-branch-gate").read_text() == "branch_suite=local\n"


def test_4030_it_ticks_no_full_suite_line_and_commits_nothing(gate):
    code, out, err, fake = gate()

    assert (gate.wt / ".tdd" / "issue-12.md").read_text() == LEDGER
    assert not {"tick-ledger.sh", "tick-issue-criterion.sh", "push-branch.sh", "git"} & set(fake.names())


@pytest.mark.parametrize("inner", [1, 2])
def test_4030_a_red_wait_ends_the_stage_with_its_code_and_stops_before_any_flake_rerun_repair_or_bail(gate, inner):
    code, out, err, fake = gate(answers={("detach-command.sh", "wait"): (inner, "FAILED 3\n")})

    assert (code, out.splitlines()[-1]) == (inner, "stopped at opening detach-command.sh wait branch-full-12 exit %d"
                                            % inner)
    assert fake.call("event.sh", "stage-end")[1][2] == "status=%d" % inner
    assert fake.calls[-1][0] == "event.sh"
    assert not {"full-tier-time.sh", "add-ledger-step.sh", "classify-bail.sh", "preflight-refused.sh",
                "suite-red-resume.sh", "detach-leaf.sh", "comment.sh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "event.sh" and c[1][:1] in (("bail",), ("suite-flake",))]
    assert not (gate.wt / ".tdd" / "issue-12-branch-gate").exists()
    assert "FAILED 3" in out


def test_4030_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(gate):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in ("branch-suite.sh", "detect-test-command.sh"):
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = gate(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    assert lines[:2] == ["branch-suite.sh exit 0", "local"]
    for i, c in enumerate(fake.calls, 1):
        if c[0] in ("branch-suite.sh", "detect-test-command.sh"):
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit 0") and "ERR<%d>" % i in err
    assert "PASSED 812" in lines


def test_4030_every_inner_call_in_the_ordered_list_is_a_script_the_opening_paragraphs_name():
    from pathlib import Path
    branch_gate = importlib.import_module("veri.branch_gate")
    draft = (Path(branch_gate.__file__).resolve().parents[2] / "DRAFT-PR.md").read_text()
    opening = draft[:draft.index("\n1. Run `$S/pr-prepare.sh")]

    assert [name for name in branch_gate.CALLS if "$S/" + name not in opening] == []


def test_4030_a_local_run_makes_the_calls_of_the_ordered_list_in_its_order(gate):
    branch_gate = importlib.import_module("veri.branch_gate")
    code, out, err, fake = gate()

    made = fake.names()
    assert code == 0 and set(made) == set(branch_gate.CALLS)
    firsts = [made.index(name) for name in branch_gate.CALLS]
    assert firsts == sorted(firsts)


def _pid(gate, text):
    (gate.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4030_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line_ending_no_stage(gate):
    code, out, err, fake = gate(answers={("detach-command.sh", "wait"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on branch-full-12")
    assert "stage-end" not in [c[1][0] for c in fake.calls if c[0] == "event.sh"]
    assert not (gate.wt / ".tdd" / "issue-12-branch-gate").exists()


def test_4030_called_again_after_an_exit_3_it_only_waits_again_then_goes_on_once(gate, monkeypatch):
    clock = iter([1000.0, 1100.0])
    monkeypatch.setattr("time.time", lambda: next(clock))
    _pid(gate, "111\nTue Nov 17 07:00:00 2026\n")
    first = gate(answers={("detach-command.sh", "wait"): (3, "")})[0]
    code, out, err, fake = gate()

    assert (first, code) == (3, 0)
    assert [(c[0], c[1]) for c in fake.calls] == [
        ("detach-command.sh", ("wait", "branch-full-12")),
        ("event.sh", ("stage-end", "stage=full-suite", "status=0", "secs=100")),
        ("full-tier-time.sh", ("--record", "100", FULL))]
    assert not (gate.wt / ".tdd" / "issue-12-branch-gate-wait").exists()


def test_4030_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(gate):
    _pid(gate, "111\nTue Nov 17 07:00:00 2026\n")
    gate(answers={("detach-command.sh", "wait"): (3, "")})

    record = json.loads((gate.wt / ".tdd" / "issue-12-branch-gate-wait").read_text())
    assert (record["conductor"], record["at"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                   "branch-full-12")


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4030_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(gate, second):
    _pid(gate, "111\nTue Nov 17 07:00:00 2026\n")
    gate(answers={("detach-command.sh", "wait"): (3, "")})
    if second is None:
        (gate.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(gate, second)
    code, out, err, fake = gate()

    assert (code, fake.calls[0][0]) == (0, "branch-suite.sh")
    assert [c[1][0] for c in fake.calls if c[0] == "detach-command.sh"] == ["start", "wait"]


@pytest.mark.parametrize("script, first, inner", [("branch-suite.sh", None, 2), ("detect-test-command.sh", None, 2),
                                                  ("detach-command.sh", "start", 2), ("full-tier-time.sh", None, 2),
                                                  ("event.sh", "stage-start", 2)])
def test_4030_an_inner_call_that_fails_stops_it_with_its_code_and_runs_nothing_later(gate, script, first, inner):
    code, out, err, fake = gate(answers={(script, first): (inner, "")})

    assert code == inner
    assert (fake.calls[-1][0], out.splitlines()[-1].startswith("stopped at opening " + script)) == (script, True)


def test_4856_a_compound_full_command_starts_through_sh_c_so_and_and_never_reaches_the_tool(gate):
    code, out, err, fake = gate({("detect-test-command.sh", None): (0, "make lint && make test\n")})

    assert fake.call("detach-command.sh", "start")[1] == ("start", "branch-full-12", "sh", "-c",
                                                          "make lint && make test")
