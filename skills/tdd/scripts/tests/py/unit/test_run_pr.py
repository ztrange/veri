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
