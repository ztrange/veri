"""In-process cases for veri/verify_branch.py, the module verify-branch.sh is a shim over (PRD 040.1, #4472)."""
import importlib

BASE = "abc1234def5678"


def test_4472_it_launches_the_verdict_branch_leaf_through_fused_launch_with_run_verdict_and_its_stderr_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    launches = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        launches.append((name, command, args, err))

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert launches == [("verdict-branch", "run-verdict.sh",
                         ("--fast-cmd", "make unit", "--branch-base", BASE, "branch", ".tdd/issue-12-spec.md"),
                         ".tdd/verify-branch.err")]


def test_4472_the_verdict_branch_leaf_runs_with_veri_test_cmd_the_fast_command_and_veri_issue_the_issue_number(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    envs = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        envs.append((env.get("VERI_TEST_CMD"), env.get("VERI_ISSUE")))

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    monkeypatch.delenv("VERI_TEST_CMD", raising=False)
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert envs == [("make unit", "12")]


def test_4472_a_stop_requested_before_the_launch_ends_verify_branch_with_that_stops_code_and_launches_no_leaf(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    named = []

    def call(name, *args, **kw):
        named.append(name.rsplit("/", 1)[-1])
        return (1, "", "") if name.endswith("stop-requested.sh") else (0, "", "")

    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, "detach-leaf.sh" in named) == (1, False)


def test_4472_called_again_while_the_verdict_branch_leaf_still_runs_it_launches_no_second_leaf_and_exits_3(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    launches = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        launches.append(name)

    def call(name, *args, **kw):
        return (3, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    launches.clear()
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, launches) == (3, [])


def test_4472_when_the_verdict_branch_leaf_passes_it_exits_0_and_adds_no_step_to_the_ledger(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    named = []

    def call(name, *args, **kw):
        named.append(name.rsplit("/", 1)[-1])
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, "add-ledger-step.sh" in named) == (0, False)


def test_4472_on_a_pass_it_writes_the_tips_head_sha_to_the_issues_branch_verified_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    tip = "f" * 40

    def call(name, *args, **kw):
        if name == "git" and "rev-parse" in args:
            return (0, tip + "\n", "")
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, tip + "\n", "") if a[:2] == ("git", "rev-parse")
                        else (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    written = [p.read_text().strip() for p in (wt / ".tdd" / "issue-12-branch-verified",
                                               tmp_path / ".tdd" / "issue-12-branch-verified") if p.exists()]
    assert (code, written) == (0, [tip])
