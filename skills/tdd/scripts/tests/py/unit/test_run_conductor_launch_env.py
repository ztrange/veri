"""In-process cases for veri/run_conductor.py, the module run-conductor.sh is a shim over."""
import importlib


def test_3402_a_launch_with_veri_step_growth_18_leaves_a_record_under_dot_tdd_holding_veri_step_growth_18(tmp_path, monkeypatch):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setenv("VERI_STEP_GROWTH", "18")
    monkeypatch.setattr(run_conductor.event, "toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(run_conductor.github, "gh_issue_view", lambda issue, field: "")
    monkeypatch.setattr(run_conductor, "prompt", lambda base, issue, commit: b"prompt")
    monkeypatch.setattr(run_conductor, "sweep_dead_runs", lambda run_state: None)
    monkeypatch.setattr(run_conductor, "conduct", lambda text, issue, env: 0)

    code = run_conductor.launch(str(tmp_path), "7", None)

    records = [p.read_text() for p in (tmp_path / ".tdd").rglob("*") if p.is_file()]
    assert (code, any("VERI_STEP_GROWTH=18" in r.splitlines() for r in records)) == (0, True)


def test_3402_the_launch_record_holds_veri_variables_and_no_other_variable_of_the_launching_environment(tmp_path, monkeypatch):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setenv("VERI_STEP_GROWTH", "18")
    monkeypatch.setenv("NOT_VERI_MARKER_3402", "leaked")
    monkeypatch.setattr(run_conductor.event, "toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(run_conductor.github, "gh_issue_view", lambda issue, field: "")
    monkeypatch.setattr(run_conductor, "prompt", lambda base, issue, commit: b"prompt")
    monkeypatch.setattr(run_conductor, "sweep_dead_runs", lambda run_state: None)
    monkeypatch.setattr(run_conductor, "conduct", lambda text, issue, env: 0)

    code = run_conductor.launch(str(tmp_path), "7", None)

    lines = [l for p in (tmp_path / ".tdd").rglob("issue-7-launch-env") for l in p.read_text().splitlines()]
    assert (code, "VERI_STEP_GROWTH=18" in lines, [l for l in lines if not l.startswith("VERI_")]) == (0, True, [])


def test_3402_the_launch_record_excludes_veri_new_skill_and_keeps_another_veri_knob(tmp_path, monkeypatch):
    run_conductor = importlib.import_module("veri.run_conductor")
    monkeypatch.setenv("VERI_NEW_SKILL", "1")
    monkeypatch.setenv("VERI_STEP_GROWTH", "18")
    monkeypatch.setattr(run_conductor.event, "toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(run_conductor.github, "gh_issue_view", lambda issue, field: "")
    monkeypatch.setattr(run_conductor, "prompt", lambda base, issue, commit: b"prompt")
    monkeypatch.setattr(run_conductor, "sweep_dead_runs", lambda run_state: None)
    monkeypatch.setattr(run_conductor, "conduct", lambda text, issue, env: 0)

    code = run_conductor.launch(str(tmp_path), "7", None)

    lines = [l for p in (tmp_path / ".tdd").rglob("issue-7-launch-env") for l in p.read_text().splitlines()]
    assert (code, "VERI_STEP_GROWTH=18" in lines, [l for l in lines if l.startswith("VERI_NEW_SKILL")]) == (0, True, [])
