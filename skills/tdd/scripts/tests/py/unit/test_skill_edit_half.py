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


def test_4450_it_then_runs_skill_edit_step_detached_by_starting_then_waiting_on_skill_edit_n(
        monkeypatch, run_cli, tmp_path):
    """SKH2: skill-edit-step.sh runs as detach-command.sh start skill-edit-<n>, then wait skill-edit-<n>."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    detached = [args[:2] for name, args in calls if name == "detach-command.sh"]
    assert detached == [("start", "skill-edit-12"), ("wait", "skill-edit-12")], calls


def test_4450_the_detached_start_is_given_skill_edit_step_then_the_body_file_then_the_steps_unit(
        monkeypatch, run_cli, tmp_path):
    """SKH2: detach-command.sh start skill-edit-<n> runs skill-edit-step.sh on the body file and the step's unit."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    _, label, script, body_file, unit = start[0]
    assert (label, os.path.basename(script), body_file, unit) == (
        "skill-edit-12", "skill-edit-step.sh", ".tdd/issue-12-body", "skills/tdd/SKILL.md"), start


def test_4450_after_skill_edit_step_exits_0_it_calls_step_tick_with_n_and_exits_0(
        monkeypatch, run_cli, tmp_path):
    """SKH1, criterion 1: step-tick.sh <n> is called through fused.script() after the detached wait, exit 0."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert [c for c in calls if c[0] == "step-tick.sh"] == [("step-tick.sh", ("12",))], calls
    assert calls[-1][0] == "step-tick.sh", calls
    assert code == 0


def test_4450_it_prints_one_line_per_call_it_makes_naming_the_call_and_its_exit_code(
        monkeypatch, run_cli, tmp_path):
    """Criterion 13: stdout holds one line per call, naming it and its exit code, and never a call's own output."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "gh":
            return 0, BODY, ""
        if base == "step-tick.sh":
            return 7, "", ""
        return 0, ("leaf transcript\n" if args[:1] == ("wait",) else ""), ""

    monkeypatch.setattr(fused, "run_script", fake)

    _, out, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    lines = out.splitlines()
    assert [line.rsplit(" exit ", 1)[-1] for line in lines] == ["0", "0", "0", "7"], out
    assert [line.split(" ", 1)[0] for line in lines] == [
        "gh", "detach-command.sh", "detach-command.sh", "step-tick.sh"], out


def test_4450_on_a_step_carrying_added_it_passes_added_and_the_step_first_to_skill_edit_step(
        monkeypatch, run_cli, tmp_path):
    """Criterion 1: --added "<step>" is the first argument skill-edit-step.sh gets when the line carries ⟦added⟧."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦added⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    passed = start[0][3:]
    assert passed[0] == "--added", start
    assert "reword the prompt in" in passed[1], start


def test_4450_given_change_it_passes_change_after_added_and_before_the_body_file(
        monkeypatch, run_cli, tmp_path):
    """Criterion 1: --change "<change>" follows --added "<step>" and precedes the issue body file."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦added⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, BODY if os.path.basename(name) == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12", "--change", "tighten the wording"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    passed = start[0][3:]
    assert passed[0] == "--added", start
    assert passed[2:5] == ("--change", "tighten the wording", ".tdd/issue-12-body"), start
