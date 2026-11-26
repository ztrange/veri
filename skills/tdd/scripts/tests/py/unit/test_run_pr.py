"""In-process cases for veri/run_pr.py, the module run-pr.sh is a shim over (PRD 038.11): each stage is spied on
through fused.call, so no stage script runs."""
import importlib
import os
import sys


def printing(spy):
    """<spy> wrapped to print what the real fused.call prints: the line naming the call and its exit code, then the
    stage's stdout; run_pr prints neither itself (RPR10)."""
    def call(name, *args, **kw):
        code, out, err = spy(name, *args, **kw)
        sys.stdout.write("%s exit %d\n%s" % (" ".join((os.path.basename(name),) + args), code, out))
        return code, out, err
    return call


def first_stages(calls):
    """<calls> without the one stage allowed between pr-checks.sh and the title seam, verify-branch.sh, which must
    directly follow pr-checks.sh when present; each call is a name or a (name, args) pair."""
    names = [c if isinstance(c, str) else c[0] for c in calls]
    if "verify-branch.sh" in names:
        assert names[names.index("verify-branch.sh") - 1] == "pr-checks.sh"
    return [c for c, n in zip(calls, names, strict=True) if n != "verify-branch.sh"]


def test_4432_the_first_call_runs_the_three_stages_then_stops_at_the_title_seam(monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert first_stages(calls) == [(s, ("12",)) for s in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh")]
    assert out.splitlines()[-1] == "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR"
    assert code == 1, err
    assert run_cli(run_pr, [], cwd=str(tmp_path))[0] == 2
    readme = os.path.join(os.path.dirname(run_pr.__file__), "README.md")
    assert "run_pr.py" in open(readme, encoding="utf-8").read()


def test_4432_no_argument_prints_the_usage_line_on_stderr_and_exits_2(run_cli):
    run_pr = importlib.import_module("veri.run_pr")

    code, out, err = run_cli(run_pr, [])

    assert code == 2
    assert "usage: run-pr.sh <n>" in err
    assert out == ""


def test_4432_called_again_after_the_title_seam_it_runs_pr_ready_wait_and_pr_finish_then_stops_at_the_body_seam(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "finish says hello\nfinish says bye\n" if name.endswith("pr-finish.sh") else "", ""

    monkeypatch.setattr(fused, "call", printing(spy))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    del calls[:]

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["pr-ready-wait.sh", "pr-finish.sh"]
    assert out.splitlines()[-3:] == ["finish says hello", "finish says bye",
                                     "seam=done code=1 reason=body next=DRAFT-PR.md#4. Draft PR"]
    assert code == 1, err


def test_4432_the_title_seam_record_holds_the_sha_of_the_ledgers_last_commit(monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    monkeypatch.setattr(fused, "call", lambda name, *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234deadbeef\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert code == 1, err
    assert (wt / ".tdd" / "issue-12-run-pr").read_text() == "seam=title\nsha=abc1234deadbeef\n"


def test_4432_a_seam_record_whose_sha_is_not_the_ledgers_last_commit_is_not_resumed_and_the_call_starts_at_branch_gate(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "aaaaaaa\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    del calls[:]
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "bbbbbbb\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert first_stages(calls) == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"]
    assert out.splitlines()[-1] == "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR"
    assert code == 1, err


def test_4432_called_again_after_the_body_seam_it_calls_no_stage_and_exits_0(monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    del calls[:]

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == []
    assert code == 0, err


def test_4432_at_the_first_stage_exiting_1_it_prints_its_output_then_the_seam_line_calls_no_later_stage_and_exits_1(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        if name.endswith("pr-prepare.sh"):
            return 1, "pr-prepare.sh: stopped at rebase\n", ""
        return 0, "", ""

    monkeypatch.setattr(fused, "call", printing(spy))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh", "pr-prepare.sh"]
    assert out.splitlines()[-2:] == ["pr-prepare.sh: stopped at rebase",
                                     "seam=pr-prepare code=1 next=DRAFT-PR.md#4. Draft PR"]
    assert code == 1, err


def test_4432_at_the_first_stage_exiting_2_it_prints_its_output_then_the_seam_line_calls_no_later_stage_and_exits_2(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        if name.endswith("pr-prepare.sh"):
            return 2, "pr-prepare.sh: stopped at fetch\n", ""
        return 0, "", ""

    monkeypatch.setattr(fused, "call", printing(spy))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh", "pr-prepare.sh"]
    assert out.splitlines()[-2:] == ["pr-prepare.sh: stopped at fetch",
                                     "seam=pr-prepare code=2 next=DRAFT-PR.md#4. Draft PR"]
    assert code == 2, err


def test_4432_at_the_first_stage_exiting_3_it_prints_its_output_then_the_seam_line_naming_run_pr_and_exits_3(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        if name.endswith("pr-prepare.sh"):
            return 3, "pr-prepare.sh: stopped at wait\n", ""
        return 0, "", ""

    monkeypatch.setattr(fused, "call", printing(spy))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh", "pr-prepare.sh"]
    assert out.splitlines()[-2:] == ["pr-prepare.sh: stopped at wait", "seam=pr-prepare code=3 next=run-pr.sh 12"]
    assert code == 3, err


def test_4432_a_stage_exiting_outside_0_to_3_stops_the_call_with_exit_2_naming_the_stage_and_its_code_on_stderr(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        if name.endswith("pr-prepare.sh"):
            return 7, "", ""
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh", "pr-prepare.sh"]
    assert code == 2
    assert "pr-prepare" in err and "7" in err


def test_4432_from_a_stage_name_starts_the_call_at_that_stage_for_each_of_the_five_stage_names(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    started = {}
    for stage in ("branch-gate", "pr-prepare", "pr-checks", "pr-ready-wait", "pr-finish"):
        del calls[:]
        run_cli(run_pr, ["12", "--from", stage], cwd=str(tmp_path))
        started[stage] = calls[:1]

    assert started == {s: [s + ".sh"] for s in started}
    in_order = [c for c in run_pr.CALLS if c[:-3] in started]
    assert in_order == [s + ".sh" for s in started]


def test_4432_hand_a_stage_stops_before_it_with_the_hand_seam_line_without_calling_it_and_exits_1(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12", "--hand", "pr-prepare"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh"]
    assert out.splitlines()[-1] == "seam=pr-prepare code=1 reason=hand next=DRAFT-PR.md#4. Draft PR"
    assert code == 1, err


def test_4432_a_from_or_hand_value_that_is_not_a_stage_name_or_an_unknown_option_is_exit_2_with_no_stage_called(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    results = {}
    for extra in (["--bogus"], ["--from", "nowhere"], ["--hand", "nowhere"]):
        del calls[:]
        results[" ".join(extra)] = (run_cli(run_pr, ["12"] + extra, cwd=str(tmp_path))[0], calls[:])

    assert results == {" ".join(e): (2, []) for e in (["--bogus"], ["--from", "nowhere"], ["--hand", "nowhere"])}


def test_4432_an_unknown_option_before_a_stage_name_or_a_bad_pair_after_a_good_one_is_exit_2_with_no_stage_called(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    extras = (["--bogus", "pr-prepare"],
              ["--from", "pr-prepare", "--bogus"],
              ["--from", "pr-prepare", "--hand", "nowhere"],
              ["--hand", "pr-prepare", "--from", "nowhere"])
    results = {}
    for extra in extras:
        del calls[:]
        results[" ".join(extra)] = (run_cli(run_pr, ["12"] + extra, cwd=str(tmp_path))[0], calls[:])

    assert results == {" ".join(e): (2, []) for e in extras}


def test_4432_in_a_stacked_run_it_stops_after_pr_checks_with_the_stacked_seam_on_every_call_and_never_calls_pr_ready_wait_or_pr_finish(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    (wt / ".tdd" / "issue-12-base").write_text("main\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    results = [run_cli(run_pr, ["12"], cwd=str(tmp_path)) for _ in range(2)]

    assert [c for c in calls if c in ("pr-ready-wait.sh", "pr-finish.sh")] == []
    assert [(r[0], r[1].splitlines()[-1]) for r in results] == [
        (1, "seam=pr-ready-wait code=1 reason=stacked next=DRAFT-PR.md#4. Draft PR")] * 2


def test_4432_in_a_stacked_run_from_pr_ready_wait_or_pr_finish_stops_again_with_the_stacked_seam_and_never_calls_them(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    (wt / ".tdd" / "issue-12-base").write_text("main\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))

    results = {}
    for stage in ("pr-ready-wait", "pr-finish"):
        res = run_cli(run_pr, ["12", "--from", stage], cwd=str(tmp_path))
        results[stage] = (res[0], res[1].splitlines()[-1:])

    assert [c for c in calls if c in ("pr-ready-wait.sh", "pr-finish.sh")] == []
    assert results == {s: (1, ["seam=pr-ready-wait code=1 reason=stacked next=DRAFT-PR.md#4. Draft PR"])
                       for s in ("pr-ready-wait", "pr-finish")}


def test_4432_its_calls_tuple_names_exactly_the_five_stage_scripts_and_a_whole_run_to_the_body_seam_calls_only_those(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []
    ran = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    def run_spy(name, *args, **kw):
        ran.append(os.path.basename(name))
        return 0, "abc1234\n", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", run_spy)

    codes = [run_cli(run_pr, ["12"], cwd=str(tmp_path))[0] for _ in range(2)]

    stages = {"branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "pr-ready-wait.sh", "pr-finish.sh"}
    assert codes == [1, 1]
    in_order = [c for c in run_pr.CALLS if c in stages]
    assert stages <= set(calls)
    assert "gh" not in ran and "pr-body.sh" not in ran
    assert in_order == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "pr-ready-wait.sh", "pr-finish.sh"]


def test_4432_every_next_it_prints_is_run_pr_or_the_draft_pr_anchor_and_that_anchor_names_a_heading_in_draft_pr_md(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    exits = {}

    def spy(name, *args, **kw):
        return exits.get(os.path.basename(name), 0), "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))
    nexts = set()
    for stage, code in (("pr-checks.sh", 0), ("branch-gate.sh", 1), ("branch-gate.sh", 3), ("pr-checks.sh", 2)):
        exits.clear()
        exits[stage] = code
        for argv in (["12"], ["12", "--hand", "pr-prepare"]):
            out = run_cli(run_pr, argv, cwd=str(tmp_path))[1]
            nexts |= {ln.split("next=", 1)[1] for ln in out.splitlines() if ln.startswith("seam=")}
    (wt / ".tdd" / "issue-12-base").write_text("main\n")
    out = run_cli(run_pr, ["12"], cwd=str(tmp_path))[1]
    nexts |= {ln.split("next=", 1)[1] for ln in out.splitlines() if ln.startswith("seam=")}

    anchors = nexts - {"run-pr.sh 12"}
    assert anchors == {"DRAFT-PR.md#4. Draft PR"}
    skill = os.path.join(os.path.dirname(run_pr.__file__), "..", "..", "DRAFT-PR.md")
    headings = [ln.strip() for ln in open(skill, encoding="utf-8") if ln.startswith("#")]
    assert any(h.lstrip("#").strip() == "4. Draft PR" for h in headings)


def test_4432_it_prints_each_stages_call_line_with_its_exit_code_and_never_the_contents_of_a_suites_output_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd" / "test-runs").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    (wt / ".tdd" / "test-runs" / "make-test.out").write_text("MARKER-4432 suite output\n")
    stages = ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh")

    monkeypatch.setattr(fused, "call", printing(lambda name, *a, **kw: (0, "", "")))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert "MARKER-4432" not in out + err
    assert [ln for ln in out.splitlines() if ln.split(" ")[0] in stages and " exit " in ln] == [
        "%s 12 exit 0" % s for s in stages]
    assert code == 1, err


def test_4432_the_resumed_late_run_prints_a_call_line_with_its_exit_code_for_pr_ready_wait_and_pr_finish_and_never_a_suites_output_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd" / "test-runs").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    (wt / ".tdd" / "test-runs" / "make-test.out").write_text("MARKER-4432 suite output\n")
    stages = ("pr-ready-wait.sh", "pr-finish.sh")

    monkeypatch.setattr(fused, "call", printing(lambda name, *a, **kw: (0, "", "")))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert "MARKER-4432" not in out + err
    assert [ln for ln in out.splitlines() if ln.split(" ")[0] in stages and " exit " in ln] == [
        "%s 12 exit 0" % s for s in stages]
    assert code == 1, err


def test_4432_a_missing_preflight_file_is_exit_2_naming_it_on_stderr_before_any_stage_is_called(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == []
    assert code == 2, err
    assert ".tdd/issue-12-preflight" in err


def _late_run(monkeypatch, run_cli, tmp_path, codes, ledger=True):
    """A worktree whose first call stopped at the title seam; <codes> maps a stage script to its exit code (0 for the
    rest). Returns (run, calls): run(argv) is (code, out, err) of one call, calls the stage scripts called by it."""
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    if ledger:
        (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        stage = os.path.basename(name)
        calls.append(stage)
        return codes.get(stage, 0), "%s stopped at here\n" % stage, ""

    monkeypatch.setattr(fused, "call", printing(spy))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "abc1234\n", ""))

    def run(argv=()):
        del calls[:]
        return run_cli(run_pr, ["12", *argv], cwd=str(tmp_path))

    return run, calls


def test_4432_a_late_stage_exiting_3_stops_there_with_next_run_pr_and_the_next_call_resumes_at_that_stage(
        monkeypatch, run_cli, tmp_path):
    for stage, before in (("pr-ready-wait.sh", []), ("pr-finish.sh", ["pr-ready-wait.sh"])):
        codes = {}
        run, calls = _late_run(monkeypatch, run_cli, tmp_path / stage, codes)
        run()
        codes[stage] = 3

        code, out, err = run()

        assert calls == before + [stage]
        assert out.splitlines()[-2:] == ["%s stopped at here" % stage, "seam=%s code=3 next=run-pr.sh 12" % stage[:-3]]
        assert code == 3, err
        del codes[stage]
        code, out, err = run()
        assert calls == LATE_FROM[stage]
        assert out.splitlines()[-1] == "seam=done code=1 reason=body next=DRAFT-PR.md#4. Draft PR"
        assert code == 1, err


LATE_FROM = {"pr-ready-wait.sh": ["pr-ready-wait.sh", "pr-finish.sh"], "pr-finish.sh": ["pr-finish.sh"]}


def test_4432_a_late_stage_exiting_1_or_2_stops_there_with_the_anchor_and_nothing_past_it_runs(
        monkeypatch, run_cli, tmp_path):
    for stage, c in (("pr-ready-wait.sh", 1), ("pr-ready-wait.sh", 2), ("pr-finish.sh", 1), ("pr-finish.sh", 2)):
        codes = {}
        run, calls = _late_run(monkeypatch, run_cli, tmp_path / ("%s-%d" % (stage, c)), codes)
        run()
        codes[stage] = c

        code, out, err = run()

        assert calls[-1] == stage
        assert "pr-finish.sh" not in calls or stage == "pr-finish.sh"
        assert out.splitlines()[-1] == "seam=%s code=%d next=DRAFT-PR.md#4. Draft PR" % (stage[:-3], c)
        assert "reason=body" not in out
        assert code == c, err
        assert run()[0] != 0


def test_4432_a_late_stage_exiting_outside_0_to_3_is_exit_2_naming_it_and_never_the_body_seam(
        monkeypatch, run_cli, tmp_path):
    for stage in ("pr-ready-wait.sh", "pr-finish.sh"):
        codes = {}
        run, calls = _late_run(monkeypatch, run_cli, tmp_path / stage, codes)
        run()
        codes[stage] = 7

        code, out, err = run()

        assert calls[-1] == stage
        assert "reason=body" not in out
        assert code == 2
        assert "%s exited 7" % stage[:-3] in err


def test_4432_hand_pr_ready_wait_or_pr_finish_is_honoured_past_the_title_seam(monkeypatch, run_cli, tmp_path):
    for stage, before in (("pr-ready-wait.sh", []), ("pr-finish.sh", ["pr-ready-wait.sh"])):
        run, calls = _late_run(monkeypatch, run_cli, tmp_path / stage, {})
        run()

        code, out, err = run(["--hand", stage[:-3]])

        assert calls == before
        assert out.splitlines()[-1] == "seam=%s code=1 reason=hand next=DRAFT-PR.md#4. Draft PR" % stage[:-3]
        assert code == 1, err


def test_4432_a_missing_ledger_is_exit_2_naming_it_on_stderr_before_any_stage_is_called(
        monkeypatch, run_cli, tmp_path):
    run, calls = _late_run(monkeypatch, run_cli, tmp_path, {}, ledger=False)

    code, out, err = run()

    assert calls == []
    assert code == 2
    assert ".tdd/issue-12.md" in err


def test_4432_the_usage_names_from_and_hand_and_the_shim_header_lists_every_exit_code(run_cli):
    run_pr = importlib.import_module("veri.run_pr")
    shim = os.path.join(os.path.dirname(os.path.dirname(run_pr.__file__)), "run-pr.sh")

    code, out, err = run_cli(run_pr, [])

    assert "usage: run-pr.sh <n> [--from <stage>] [--hand <stage>]" in err
    header = open(shim, encoding="utf-8").read()
    assert "# Usage:   run-pr.sh <n> [--from <stage>] [--hand <stage>]" in header
    lines = header.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("# Exit:"))
    block = [lines[start]] + [l for l in lines[start + 1:] if l.startswith("#    ")][:3]
    for c in ("Exit:    0 ", "; 1 ", "2 bad arguments", "; 3 "):
        assert c in " ".join(block)


def _stage_run(monkeypatch, tmp_path, codes):
    """A run whose stage scripts are faked at fused.run_script, so the real fused.call prints each call: <codes> maps a
    stage script to a list of exit codes, one per call, 0 once it runs out. Returns (run, calls)."""
    fused = importlib.import_module("veri.fused")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, **kw):
        stage = os.path.basename(name)
        if stage == "git":
            return 0, "abc1234\n", ""
        calls.append(stage)
        left = codes.get(stage, [])
        return (left.pop(0) if left else 0), "%s says hi\n" % stage, ""

    monkeypatch.setattr(fused, "run_script", fake)
    return calls


def test_4432_with_the_real_fused_call_each_stage_call_line_and_its_output_are_printed_once(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    _stage_run(monkeypatch, tmp_path, {})

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))
    code2, out2, err2 = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    lines = out.splitlines() + out2.splitlines()
    for stage in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "pr-ready-wait.sh", "pr-finish.sh"):
        assert [ln for ln in lines if ln.startswith(stage + " ") and " exit " in ln] == ["%s 12 exit 0" % stage]
        assert lines.count("%s says hi" % stage) == 1
    assert out2.splitlines()[-2:] == ["pr-finish.sh says hi", "seam=done code=1 reason=body next=DRAFT-PR.md#4. Draft PR"]
    assert (code, code2) == (1, 1), err + err2


def test_4432_a_stage_exiting_3_early_or_late_is_resumed_at_exactly_that_stage_with_no_stage_skipped(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    calls = _stage_run(monkeypatch, tmp_path, {"pr-prepare.sh": [3], "pr-finish.sh": [3]})
    seen = []
    for _ in range(4):
        del calls[:]
        code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))
        seen.append((first_stages(calls), code, out.splitlines()[-1]))

    assert seen == [
        (["branch-gate.sh", "pr-prepare.sh"], 3, "seam=pr-prepare code=3 next=run-pr.sh 12"),
        (["pr-prepare.sh", "pr-checks.sh"], 1, "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR"),
        (["pr-ready-wait.sh", "pr-finish.sh"], 3, "seam=pr-finish code=3 next=run-pr.sh 12"),
        (["pr-finish.sh"], 1, "seam=done code=1 reason=body next=DRAFT-PR.md#4. Draft PR"),
    ]


def test_4432_a_stage_exiting_4_or_a_signals_negative_code_is_exit_2_naming_the_stage(monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    for c in (4, -9):
        calls = _stage_run(monkeypatch, tmp_path / str(c), {"pr-checks.sh": [c]})

        code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path / str(c)))

        assert first_stages(calls) == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"]
        assert code == 2
        assert "pr-checks exited %d" % c in err
        assert "seam=" not in out


def test_4432_two_hand_flags_each_stop_the_call_before_their_stage(monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    calls = _stage_run(monkeypatch, tmp_path, {})
    hands = ["--hand", "pr-checks", "--hand", "pr-finish"]

    code, out, err = run_cli(run_pr, ["12", *hands], cwd=str(tmp_path))
    assert (calls, code, out.splitlines()[-1]) == (
        ["branch-gate.sh", "pr-prepare.sh"], 1, "seam=pr-checks code=1 reason=hand next=DRAFT-PR.md#4. Draft PR")
    del calls[:]
    code, out, err = run_cli(run_pr, ["12", "--from", "pr-ready-wait", *hands], cwd=str(tmp_path))
    assert (calls, code, out.splitlines()[-1]) == (
        ["pr-ready-wait.sh"], 1, "seam=pr-finish code=1 reason=hand next=DRAFT-PR.md#4. Draft PR")


def test_4432_a_missing_ledger_or_preflight_is_one_stderr_line_and_exit_2_never_a_traceback(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    calls = _stage_run(monkeypatch, tmp_path, {})
    (tmp_path / ".tdd" / "wt" / "12" / ".tdd" / "issue-12.md").unlink()

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert (calls, code, out) == ([], 2, "")
    assert err.splitlines() == ["run-pr.sh: no .tdd/issue-12.md"]


def _git_run(monkeypatch, tmp_path, git, stacked=False):
    """A run whose stage scripts all exit 0 and whose git calls are answered by <git>(args) -> (code, stdout).
    Returns calls, the stage scripts called."""
    fused = importlib.import_module("veri.fused")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    if stacked:
        (wt / ".tdd" / "issue-12-base").write_text("tdd/11-parent\n")
    calls = []

    def fake(name, *args, **kw):
        if os.path.basename(name) == "git":
            code, out = git(args)
            return code, out, ""
        calls.append(os.path.basename(name))
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)
    return calls


def test_4432_the_seam_sha_is_the_ledgers_last_commit_so_a_commit_elsewhere_still_resumes(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    heads = iter("%07d" % i for i in range(1, 100))

    def git(args):
        # git log on the ledger's path names the ledger's last commit; without the path, a HEAD that moves each call.
        return 0, ("aaaaaaa\n" if args[-2:] == ("--", ".tdd/issue-12.md") else next(heads) + "\n")

    calls = _git_run(monkeypatch, tmp_path, git)
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    del calls[:]

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["pr-ready-wait.sh", "pr-finish.sh"]
    assert code == 1, err


def test_4432_an_empty_ledger_sha_never_matches_a_record_and_the_call_restarts_at_branch_gate(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    for answer in ((128, ""), (0, "\n"), (0, "aaaaaaa\n")):
        calls = _git_run(monkeypatch, tmp_path / str(answer[0]) / str(len(answer[1])), lambda args: answer)
        cwd = str(tmp_path / str(answer[0]) / str(len(answer[1])))
        run_cli(run_pr, ["12"], cwd=cwd)
        del calls[:]

        code, out, err = run_cli(run_pr, ["12"], cwd=cwd)

        if answer[1].strip():
            assert calls[0] == "pr-ready-wait.sh"
        else:
            assert first_stages(calls) == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"]
            assert out.splitlines()[-1] == "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR"


def test_4432_a_stacked_run_called_again_with_its_seam_current_calls_no_stage_and_stops_at_the_stacked_seam(
        monkeypatch, run_cli, tmp_path):
    run_pr = importlib.import_module("veri.run_pr")
    calls = _git_run(monkeypatch, tmp_path, lambda args: (0, "aaaaaaa\n"), stacked=True)
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    assert first_stages(calls) == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"]
    del calls[:]

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == []
    assert out.splitlines()[-1] == "seam=pr-ready-wait code=1 reason=stacked next=DRAFT-PR.md#4. Draft PR"
    assert code == 1, err


def test_4472_run_pr_calls_verify_branch_after_pr_checks_and_it_prints_usage_with_no_argument(monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "call", spy)

    run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == [(s, ("12",)) for s in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "verify-branch.sh")]
    verify_branch = importlib.import_module("veri.verify_branch")
    code, out, err = run_cli(verify_branch, [])
    assert code == 2
    assert "usage: verify-branch.sh <n>" in err


def test_4472_a_verify_branch_exit_1_prints_the_rejected_seam_exits_1_and_never_readies_the_pr(monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return (1 if os.path.basename(name) == "verify-branch.sh" else 0), "", ""

    monkeypatch.setattr(fused, "call", spy)

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert out.splitlines()[-1] == "seam=verify-branch code=1 reason=rejected next=DRAFT-PR.md#4. Draft PR"
    assert code == 1, err
    assert "pr-ready-wait.sh" not in calls


def test_4472_after_a_verify_branch_reject_a_run_pr_on_the_repaired_ledgers_new_sha_restarts_at_branch_gate(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    run_pr = importlib.import_module("veri.run_pr")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")
    calls = []
    verdict = [1]

    def spy(name, *args, **kw):
        calls.append(os.path.basename(name))
        return (verdict[0] if os.path.basename(name) == "verify-branch.sh" else 0), "", ""

    monkeypatch.setattr(fused, "call", spy)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "aaaaaaa\n", ""))
    run_cli(run_pr, ["12"], cwd=str(tmp_path))
    del calls[:]
    verdict[0] = 0
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "bbbbbbb\n", ""))

    code, out, err = run_cli(run_pr, ["12"], cwd=str(tmp_path))

    assert calls == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "verify-branch.sh"]
    assert out.splitlines()[-1] == "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR"
