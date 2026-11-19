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
