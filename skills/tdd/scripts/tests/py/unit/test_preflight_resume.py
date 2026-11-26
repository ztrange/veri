"""In-process cases for the resume path of veri/preflight.py (PRD 027.2, #4023)."""
import importlib
import json
import os

import pytest
from veri import run_dir

PRE = "a" * 40
POST = "b" * 40


class Fake:
    """A run_script stand-in: records every call as (script basename, args, cwd, env) and answers from <answers>,
    keyed by (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, wt, answers=None, dirty=""):
        self.wt, self.answers, self.calls, self.dirty = wt, dict(answers or {}), [], dirty

    def __call__(self, name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env))
        if base == "git" and args == ("status", "--porcelain") and cwd == str(self.wt):
            return 0, self.dirty, ""
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "issue-worktree.sh":
            return 0, str(self.wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n"}.get(args[1], "make test TESTS=$1\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "gh" and args[-1] == ".body":
            return 0, "BODY\n", ""
        if base == "rebase-onto-default.sh":
            return 0, PRE + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, POST + "\n", ""
        if base == "git" and args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "tdd/12-my-slug\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def drive(monkeypatch, run_cli, tmp_path):
    """drive(ledger=False, handed_back=False, answers=None) runs preflight for issue 12 in a worktree a conductor's
    launch made; returns (code, stdout, fake)."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(ledger=False, handed_back=False, answers=None, fake=None, dirty=""):
        if ledger:
            (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
            # The branch base a fresh launch recorded, where preflight reads it back (#4374).
            with open(run_dir.issue_file(run_dir.main_tree_from_files(str(wt)), 12, "-branch-base"), "w") as record:
                record.write("c" * 40 + "\n")
        if handed_back:
            (wt / ".tdd" / "handed-back").write_text("")
        fake = fake or Fake(wt, answers, dirty)
        monkeypatch.setattr(preflight, "run_script", fake)
        code, out, go.err = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
        return code, out, fake

    go.wt = wt
    return go


def test_4023_a_worktree_holding_a_ledger_after_issue_worktree_is_resumed_without_the_claim(drive):
    code, out, fake = drive(ledger=True)

    assert code == 0
    assert "unlabel-issue.sh" not in fake.names()
    assert fake.call("requirements-preflight.sh")[1][1:] == (".tdd/issue-12.md",)


def test_4023_a_branch_only_origin_held_whose_ledger_appears_with_issue_worktree_is_resumed(drive, monkeypatch):
    wt = drive.wt
    # The branch base travels with origin's run records, as the branch does (#4374).
    carried = {("12", "issue-12-branch-base"): "c" * 40 + "\n"}
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read",
                        lambda issue, name, cwd: carried.get((str(issue), name)))

    class Recreating(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            if os.path.basename(name) == "issue-worktree.sh":
                (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
            return super().__call__(name, *args, cwd=cwd, env=env)

    code, out, fake = drive(fake=Recreating(wt))

    assert code == 0
    assert "unlabel-issue.sh" not in fake.names()
    assert len(fake.call("requirements-preflight.sh")[1]) == 2


def test_4023_a_fresh_run_still_claims_and_passes_no_ledger(drive):
    code, out, fake = drive()

    assert code == 0
    assert "unlabel-issue.sh" in fake.names()
    assert len(fake.call("requirements-preflight.sh")[1]) == 1


def _handed_back_calls(fake):
    names = fake.names()
    start = names.index("worktree-setup.sh") + 1
    end = names.index("gh", start)
    return [(c[0], c[1]) for c in fake.calls[start:end]]


@pytest.mark.parametrize("ledger", [True, False], ids=["resume", "fresh"])
def test_4023_a_handed_back_worktree_cleans_rebases_marks_and_rerecords_before_reading_the_body(drive, ledger):
    code, out, fake = drive(ledger=ledger, handed_back=True)

    assert code == 0
    assert _handed_back_calls(fake) == [
        ("resume-clean.sh", ()), ("rebase-onto-default.sh", ()), ("git", ("rev-parse", "HEAD")),
        ("event.sh", ("resume-rebase", "from=" + PRE, "rebased=" + POST)),
        ("tests-frozen.sh", ("rerecord-rebased", ".tdd/issue-12.md", PRE))]
    env = fake.call("event.sh", "resume-rebase")[3]
    assert (env["VERI_ISSUE"], env["VERI_ACTOR"]) == ("12", "conductor")


@pytest.mark.parametrize("rebase", [1, 3])
def test_4023_a_rebase_that_did_not_move_the_branch_goes_on_with_no_event_and_no_rerecord(drive, rebase):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("rebase-onto-default.sh", None): (rebase, "")})

    assert code == 0
    assert [c[0] for c in _handed_back_calls(fake)] == ["resume-clean.sh", "rebase-onto-default.sh"]


def test_4023_a_rebase_exit_2_stops_preflight_at_3_with_no_later_call(drive):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("rebase-onto-default.sh", None): (2, "")})

    assert (code, out.splitlines()[-1], fake.names()[-1]) == (2, "stopped at 3 rebase-onto-default.sh",
                                                             "rebase-onto-default.sh")


@pytest.mark.parametrize("rerecord, stops", [(3, False), (1, True)])
def test_4023_rerecord_rebased_exit_3_goes_on_and_any_other_failure_stops(drive, rerecord, stops):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("tests-frozen.sh", None): (rerecord, "")})

    assert (code, fake.names()[-1] == "tests-frozen.sh") == ((1, True) if stops else (0, False))


LEASE = "--force-with-lease=tdd/12-my-slug:" + PRE


def test_4023_a_moved_branch_is_pushed_with_the_pinned_lease_after_the_green_fast_tier_and_before_the_full_tier(drive):
    code, out, fake = drive(ledger=True, handed_back=True)

    seq = [(c[0], c[1][:2]) for c in fake.calls]
    fast_wait = seq.index(("detach-command.sh", ("wait", "preflight-fast-12")))
    full_detect = len(seq) - 1 - seq[::-1].index(("detect-test-command.sh", ("--tier", "all")))
    assert code == 0
    assert seq[fast_wait + 1:full_detect] == [("git", ("status", "--porcelain")),
                                              ("git", ("rev-parse", "--abbrev-ref")), ("push-branch.sh", (LEASE,))]


@pytest.mark.parametrize("rebase", [1, 3])
def test_4023_a_branch_the_rebase_did_not_move_is_not_pushed(drive, rebase):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("rebase-onto-default.sh", None): (rebase, "")})

    assert (code, "push-branch.sh" in fake.names()) == (0, False)


def test_4023_a_dirty_tree_before_the_leased_push_stops_at_3_tree_check_with_exit_1_and_no_push(drive):
    code, out, fake = drive(ledger=True, handed_back=True, dirty="?? stray.txt\n")

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 tree-check")
    assert "push-branch.sh" not in fake.names()
    assert fake.calls[-1][:2] == ("git", ("status", "--porcelain"))


@pytest.mark.parametrize("push", [1, 2])
def test_4023_a_failed_leased_push_stops_with_its_code_before_the_full_tier(drive, push):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("push-branch.sh", None): (push, "")})

    assert (code, out.splitlines()[-1], fake.names()[-1]) == (push, "stopped at 3 push-branch.sh " + LEASE,
                                                             "push-branch.sh")


def test_4023_a_red_fast_tier_on_a_moved_branch_pushes_nothing(drive):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("detach-command.sh", "wait"): (1, "")})

    assert (code, "push-branch.sh" in fake.names()) == (1, False)


STRAY = {("resume-clean.sh", None): (0, " M src/a.py\n?? notes.txt\n")}


def _settled(drive):
    return (drive.wt / ".tdd" / "issue-12-preflight").read_text().splitlines()


def test_4023_a_resumed_handed_back_run_settles_run_resume_its_stray_paths_and_the_pre_rebase_sha(drive):
    code, out, fake = drive(ledger=True, handed_back=True, answers=STRAY)

    settled = _settled(drive)
    assert code == 0
    assert settled[-4:] == ["run=resume", "stray=src/a.py", "stray=notes.txt", "rebased_from=" + PRE]
    assert out.splitlines()[-len(settled):] == settled


def test_4023_a_fresh_run_settles_run_fresh_with_no_stray_or_rebased_from_line(drive):
    code, out, fake = drive()

    settled = _settled(drive)
    assert (code, settled[-1]) == (0, "run=fresh")
    assert not [line for line in settled if line.startswith(("stray=", "rebased_from="))]


def test_4023_a_rebase_that_did_not_move_the_branch_settles_its_stray_paths_and_no_rebased_from(drive):
    code, out, fake = drive(ledger=True, handed_back=True,
                            answers={**STRAY, ("rebase-onto-default.sh", None): (3, "")})

    assert _settled(drive)[-3:] == ["run=resume", "stray=src/a.py", "stray=notes.txt"]


def test_4023_a_stop_after_resume_clean_prints_its_stray_and_rebased_from_lines_before_the_stopped_at_line(drive):
    code, out, fake = drive(ledger=True, handed_back=True, answers={**STRAY, ("push-branch.sh", None): (1, "")})

    assert out.splitlines()[-4:] == ["stray=src/a.py", "stray=notes.txt", "rebased_from=" + PRE,
                                     "stopped at 3 push-branch.sh " + LEASE]
    assert not (drive.wt / ".tdd" / "issue-12-preflight").exists()


ONCE = ("resume-clean.sh", "rebase-onto-default.sh", "tests-frozen.sh", "push-branch.sh")


@pytest.mark.parametrize("tier", ["fast", "full"])
def test_4023_called_again_after_an_exit_3_repeats_no_handed_back_call_and_still_reports_their_values(drive, tier):
    first_code, _, first = drive(ledger=True, handed_back=True,
                                 answers={**STRAY, ("detach-command.sh", "wait"): (3, "")} if tier == "fast" else STRAY,
                                 fake=None if tier == "fast" else _waiting_on_full(drive.wt))
    code, out, second = drive(answers=STRAY)

    made = [c[0] for c in first.calls + second.calls]
    assert (first_code, code) == (3, 0)
    assert [made.count(name) for name in ONCE] == [1, 1, 1, 1]
    assert [c for c in second.calls if c[0] == "event.sh"] == []
    assert _settled(drive)[-4:] == ["run=resume", "stray=src/a.py", "stray=notes.txt", "rebased_from=" + PRE]


def _waiting_on_full(wt):
    class FullWaits(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            if os.path.basename(name) == "detach-command.sh" and args[:2] == ("wait", "preflight-full-12"):
                self.calls.append(("detach-command.sh", args, cwd, env))
                return 3, "", ""
            return super().__call__(name, *args, cwd=cwd, env=env)
    return FullWaits(wt, STRAY)


def _pid_file(drive, text):
    (drive.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4023_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(drive):
    _pid_file(drive, "111\nTue Nov 17 07:00:00 2026\n")
    code, _, _ = drive(ledger=True, answers={("detach-command.sh", "wait"): (3, "")})

    record = json.loads((drive.wt / ".tdd" / "issue-12-preflight-wait").read_text())
    assert (code, record["conductor"]) == (3, {"pid": "111", "started": "Tue Nov 17 07:00:00 2026"})


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", ""],
                         ids=["another pid", "another start time", "no pid file"])
def test_4023_called_under_another_conductor_it_discards_the_wait_record_and_starts_from_its_first_call(drive, second):
    _pid_file(drive, "111\nTue Nov 17 07:00:00 2026\n")
    drive(ledger=True, answers={("detach-command.sh", "wait"): (3, "")})
    if second:
        _pid_file(drive, second)
    else:
        (drive.wt / ".tdd" / "conductor.pid").unlink()
    code, out, fake = drive()

    assert code == 0
    assert fake.calls[0][:2] == ("git", ("rev-parse", "--is-inside-work-tree"))
    assert [c[1][1] for c in fake.calls if c[0] == "detach-command.sh" and c[1][0] == "start"] == [
        "preflight-fast-12", "preflight-full-12"]


def test_4023_called_again_under_the_same_conductor_it_continues_from_the_wait(drive):
    _pid_file(drive, "111\nTue Nov 17 07:00:00 2026\n")
    drive(ledger=True, answers={("detach-command.sh", "wait"): (3, "")})
    code, out, fake = drive()

    assert (code, fake.calls[0][:2]) == (0, ("detach-command.sh", ("wait", "preflight-fast-12")))


def _red(tier):
    class Red(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            if os.path.basename(name) == "detach-command.sh" and args[:2] == ("wait", "preflight-%s-12" % tier):
                self.calls.append(("detach-command.sh", args, cwd, env))
                return 1, "1 failed\n", ""
            return super().__call__(name, *args, cwd=cwd, env=env)
    return Red


@pytest.mark.parametrize("tier", ["fast", "full"])
def test_4023_a_red_tier_on_a_resume_stops_with_the_waits_code_and_runs_no_red_suite_path(drive, tier):
    code, out, fake = drive(ledger=True, handed_back=True, fake=_red(tier)(drive.wt))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 detach-command.sh wait")
    assert fake.calls[-1][:2] == ("detach-command.sh", ("wait", "preflight-%s-12" % tier))
    assert "suite-red-resume.sh" not in fake.names()
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] == ("checkout",)]
    assert [c[1][1] for c in fake.calls if c[0] == "detach-command.sh" and c[1][0] == "start"] == [
        "preflight-%s-12" % t for t in ("fast", "full")[:("fast", "full").index(tier) + 1]]
    assert not (drive.wt / ".tdd" / "issue-12-preflight").exists()


BOTH = pytest.mark.parametrize("ledger", [True, False], ids=["resume", "fresh"])


@BOTH
def test_4023_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr_on_both_paths(
        drive, ledger):
    clean = ("status", "--porcelain")
    valued = {"issue-worktree.sh", "rebase-onto-default.sh", "detect-test-command.sh", "baseline-full-tier.sh"}

    class Marked(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            code, out, _ = super().__call__(name, *args, cwd=cwd, env=env)
            if out or args == clean:
                return code, out, ""
            return code, "OUT<%d>\n" % len(self.calls), "ERR<%d>\n" % len(self.calls)

    fake = Marked(drive.wt)
    preflight = importlib.import_module("veri.preflight")
    code, out, _ = drive(ledger=ledger, handed_back=True, fake=fake)

    lines = out.splitlines()
    # The permission record's two reads (git worktree list, git remote get-url; #4093) are made unprinted, as on 027.1.
    marked = [i for i, c in enumerate(fake.calls, 1)
              if c[1] != clean and c[1][:1] not in (("worktree",), ("remote",), ("rev-parse",), ("api",))
              and c[0] not in valued]
    heads = [lines.index("OUT<%d>" % i) for i in marked]
    assert code == 0
    assert heads == sorted(heads)
    for k, i in enumerate(marked):
        base, args = fake.calls[i - 1][:2]
        between = lines[(heads[k - 1] + 1 if k else 0):heads[k]]
        assert preflight.label(base, *args) + " exit 0" == [line for line in between if line.endswith(" exit 0")][-1]
    assert all("ERR<%d>" % i in drive.err for i in marked)


@BOTH
def test_4023_no_detached_runs_output_file_is_printed_on_either_path(drive, ledger):
    for name in ("preflight-fast-12", "preflight-full-12"):
        (drive.wt / ".tdd" / (name + ".out")).write_text("SENTINEL-OUTPUT\n")

    code, out, _ = drive(ledger=ledger, handed_back=True)

    assert (code, "SENTINEL-OUTPUT" in out) == (0, False)


@BOTH
def test_4023_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line_on_either_path(drive, ledger):
    code, out, _ = drive(ledger=ledger, answers={("detach-command.sh", "wait"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on preflight-fast-12")


@BOTH
def test_4023_a_reused_full_tier_time_starts_no_full_tier_run_on_either_path(drive, ledger):
    code, out, fake = drive(ledger=ledger, answers={("baseline-full-tier.sh", None): (0, "reuse 40\n")})

    settled = dict(line.split("=", 1) for line in _settled(drive) if not line.startswith("stray="))
    assert (code, settled["full"], settled["full_tier_mode"]) == (0, "40", "reuse")
    assert [c[1][1] for c in fake.calls if c[0] == "detach-command.sh" and c[1][0] == "start"] == ["preflight-fast-12"]


@BOTH
def test_4023_the_settled_file_is_run_state_the_ignore_rule_keeps_out_of_every_commit(drive, ledger):
    import fnmatch
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE
    drive(ledger=ledger)

    name = ".tdd/" + (drive.wt / ".tdd" / "issue-12-preflight").name
    assert fnmatch.fnmatch(name, rule[0]) and not fnmatch.fnmatch(name, rule[1].lstrip("!"))


@BOTH
def test_4023_a_stop_handles_no_refusal_on_either_path(drive, ledger):
    code, out, fake = drive(ledger=ledger, handed_back=True, answers={("baseline-full-tier.sh", None): (1, "")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 baseline-full-tier.sh 12 make test")
    assert not {"preflight-refused.sh", "classify-bail.sh", "comment.sh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "event.sh" and c[1][:1] == ("bail",)]
    assert not [c for c in fake.calls if c[0] == "gh" and "comments" in " ".join(c[1])]
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("checkout",))]


@BOTH
def test_4023_the_stage_events_are_written_in_the_same_order_on_either_path(drive, ledger):
    code, _, fake = drive(ledger=ledger, handed_back=True)

    lines = [json.loads(line) for line in (drive.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert code == 0
    assert [(line["event"], line["stage"]) for line in lines] == [
        ("stage-start", "preflight"), ("stage-start", "baseline"), ("stage-end", "baseline"),
        ("stage-end", "preflight")]
    assert [c[1][0] for c in fake.calls if c[0] == "event.sh"] == ["resume-rebase"]


def test_4023_a_handed_back_resume_makes_the_calls_of_the_scripts_ordered_list_in_its_order(drive):
    preflight = importlib.import_module("veri.preflight")
    code, out, fake = drive(ledger=True, handed_back=True)

    made = [preflight.label(c[0], *c[1]) for c in fake.calls]
    at = [next(i for i, m in enumerate(made) if m.startswith(call)) for call in preflight.HANDED_BACK]
    assert (code, at) == (0, sorted(at))


def test_4023_a_worktree_not_handed_back_runs_none_of_the_handed_back_calls(drive):
    code, out, fake = drive(ledger=True)

    assert _handed_back_calls(fake) == []


TREE_4337 = "e" * 40


class Recorded(Fake):
    """A Fake whose HEAD^{tree} is TREE_4337 and whose green record answers <green> for `--green`."""

    def __init__(self, wt, green):
        super().__init__(wt)
        self.green = green

    def __call__(self, name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        if base == "git" and args == ("rev-parse", "HEAD^{tree}"):
            self.calls.append((base, args, cwd, env))
            return 0, TREE_4337 + "\n", ""
        if base == "baseline-full-tier.sh":
            self.calls.append((base, args, cwd, env))
            return 0, self.green if args[:1] == ("--green",) else "reuse 55\n", ""
        return super().__call__(name, *args, cwd=cwd, env=env)


@pytest.mark.parametrize("green, runs", [("skip\n", False), ("run\n", True), ("", True)])
def test_4337_a_resume_whose_tree_commands_pin_and_lock_match_a_recorded_green_skips_the_baseline_run(
        drive, green, runs):
    fake = Recorded(drive.wt, green)

    code, out, _ = drive(ledger=True, fake=fake)

    asked = [c[1] for c in fake.calls if c[0] == "baseline-full-tier.sh" and c[1][:1] == ("--green",)]
    starts = [c[1] for c in fake.calls if c[0] == "detach-command.sh" and c[1][:1] == ("start",)]
    assert asked == [("--green", "12", TREE_4337, "make unit", "make test")]
    assert bool(starts) is runs
    assert code == 0
