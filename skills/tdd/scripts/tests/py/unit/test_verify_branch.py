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
