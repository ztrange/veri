"""In-process cases for veri/skill_edit_half.py, the module skill-edit-half.sh is a shim over (PRD 038.4, #4450)."""
import importlib
import os


def test_run_with_no_argument_prints_its_usage_line_on_stderr_and_exits_2(run_cli):
    skill_edit_half = importlib.import_module("veri.skill_edit_half")

    code, out, err = run_cli(skill_edit_half, [])

    assert (code, out, err.strip()) == (
        2, "", 'usage: skill-edit-half.sh <n> [--change "<change>"]'), (code, out, err)


BODY = "## Acceptance criteria\n\n- [ ] the prompt says so\n"
STEP = "reword the prompt ⟦skill-edit⟧ ⟦criterion 1⟧"


def test_4450_on_an_open_skill_edit_step_it_first_reads_the_issue_body_into_the_body_file(
        monkeypatch, run_cli, tmp_path):
    """SKH1: the first call is gh api for the issue's .body, its output the step's .tdd/issue-<n>-body."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [ ] %s\n" % STEP)
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert calls[:1] == [("gh", ("api", "repos/{owner}/{repo}/issues/12", "-q", ".body"))], calls
    assert (wt / ".tdd" / "issue-12-body").read_text() == BODY
