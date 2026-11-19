"""In-process cases for veri/run_pr.py, the module run-pr.sh is a shim over (PRD 038.11): each stage is spied on
through fused.call, so no stage script runs."""
import importlib
import os


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

    assert calls == [(s, ("12",)) for s in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh")]
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

    monkeypatch.setattr(fused, "call", spy)
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
    assert "abc1234deadbeef" in open(fused.settled_file(str(wt), "12", "run-pr")).read()


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

    assert calls == ["branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"]
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

    monkeypatch.setattr(fused, "call", spy)
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

    monkeypatch.setattr(fused, "call", spy)
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

    monkeypatch.setattr(fused, "call", spy)
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
    assert set(calls) == stages
    assert "gh" not in ran and "pr-body.sh" not in ran
    assert set(run_pr.CALLS) == stages and len(run_pr.CALLS) == 5
