"""In-process cases for veri/skill_edit_half.py, the module skill-edit-half.sh is a shim over (PRD 038.4, #4450)."""
import importlib
import os


def test_run_with_no_argument_prints_its_usage_line_on_stderr_and_exits_2(run_cli):
    skill_edit_half = importlib.import_module("veri.skill_edit_half")

    code, out, err = run_cli(skill_edit_half, [])

    assert (code, out, err.strip()) == (
        2, "", 'usage: skill-edit-half.sh <n> [--change "<change>"]'), (code, out, err)


BODY = "## Acceptance criteria\n\n- [ ] the prompt says so\n"
STEP = "reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧"


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

    assert calls[:1] == [("git", ("log", "-1", "--format=%H", "--", ".tdd/issue-12.md"))], calls
    assert calls[1:2] == [("gh", ("api", "repos/{owner}/{repo}/issues/12", "-q", ".body"))], calls
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
    assert [line.rsplit(" exit ", 1)[-1] for line in lines] == ["0", "0", "0", "0", "7"], out
    assert [line.split(" ", 1)[0] for line in lines] == [
        "git", "gh", "detach-command.sh", "detach-command.sh", "step-tick.sh"], out


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


def test_4450_it_passes_the_tracked_test_file_spans_after_the_unit_in_the_steps_order_and_no_other(
        monkeypatch, run_cli, tmp_path):
    """Criterion 2: the step's backticked test-file spans after its unit that git tracks, in order, follow the unit."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword `skills/tdd/SKILL.md`, pinned by `tests/test_b.py`, "
        "`tests/test_untracked.py`, `docs/notes.md` and `tests/test_a.py` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    tracked = ["tests/test_a.py", "tests/test_b.py"]
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "git":
            return (0, "\n".join(tracked) + "\n", "") if "ls-files" in args and args[-1] not in tracked and \
                "--error-unmatch" not in args else ((0, "", "") if args[-1] in tracked else (1, "", ""))
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    assert start[0][3:] == (
        ".tdd/issue-12-body", "skills/tdd/SKILL.md", "tests/test_b.py", "tests/test_a.py"), start


def test_4450_with_every_file_tracked_it_passes_only_the_test_file_spans_after_the_unit(
        monkeypatch, run_cli, tmp_path):
    """Criterion 2: the unit, a tracked non-test file and a non-path span are left out; the later test files stay."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword `tests/test_unit.py` with `--flag`, `docs/notes.md`, "
        "`tests/test_c.py` and `tests/test_a.py` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    assert start[0][3:] == (".tdd/issue-12-body", "tests/test_unit.py", "tests/test_c.py", "tests/test_a.py"), start


def test_4450_it_passes_no_tracked_path_span_after_the_unit_that_is_not_a_test_file(
        monkeypatch, run_cli, tmp_path):
    """Criterion 2: a tracked production path after the unit is not a pin file."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword `skills/tdd/SKILL.md`, see `skills/tdd/scripts/veri/ledger.py` "
        "and `skills/tdd/SCRIPTS.md`, pinned by `tests/test_a.py` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    assert start[0][3:] == (".tdd/issue-12-body", "skills/tdd/SKILL.md", "tests/test_a.py"), start


def test_4450_it_passes_no_test_file_span_after_the_unit_that_git_does_not_track(
        monkeypatch, run_cli, tmp_path):
    """Criterion 2: a test-file span git does not track is not a pin file."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword `skills/tdd/SKILL.md`, pinned by `tests/test_gone.py` "
        "⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "git":
            return 1, "", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    start = [args for name, args in calls if name == "detach-command.sh" and args[:1] == ("start",)]
    assert len(start) == 1, calls
    assert start[0][3:] == (".tdd/issue-12-body", "skills/tdd/SKILL.md"), start


def test_4450_when_the_detached_wait_slice_runs_out_it_exits_3_and_calls_no_step_tick(
        monkeypatch, run_cli, tmp_path):
    """SKH33: detach-command.sh wait exiting 3 (its slice ran out) is the stage's exit 3, before step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 3, "", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, [c for c in calls if c[0] == "step-tick.sh"]) == (3, []), calls


def test_4450_called_again_by_the_conductor_that_wrote_the_wait_record_it_only_waits_on_skill_edit_n(
        monkeypatch, run_cli, tmp_path):
    """SKH34: a second call under the recording conductor makes no gh api call and starts no skill-edit-step.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "conductor.pid").write_text("4242\n1700000000\n")
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    fused.save_wait(str(wt), "12", "skill-edit-half", "skill-edit-12", {})
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 3, "", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, calls) == (3, [("detach-command.sh", ("wait", "skill-edit-12"))]), (code, calls)


def test_4450_when_skill_edit_step_exits_3_it_calls_step_tick_as_on_exit_0_and_does_not_exit_3(
        monkeypatch, run_cli, tmp_path):
    """SKH3: skill-edit-step.sh's exit 3 (wait reports exit 1, printing 3) is ticked as on 0, not the stage's exit 3."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 1, "3\n", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, [c for c in calls if c[0] == "step-tick.sh"]) == (0, [("step-tick.sh", ("12",))]), (code, calls)


def test_4450_skill_edit_step_exit_1_stops_with_1_before_step_tick(
        monkeypatch, run_cli, tmp_path):
    """SKH7: skill-edit-step.sh's exit 1 (wait reports exit 1, printing 1) stops the stage with 1, before step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 1, "1\n", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    starts = [c for c in calls if c[0] == "detach-command.sh" and c[1][:1] == ("start",)]
    ticks = [c for c in calls if c[0] == "step-tick.sh"]
    assert (code, len(starts), len(ticks)) == (1, 1, 0), (code, calls)


def test_4450_skill_edit_step_exit_2_stops_with_2_before_step_tick(
        monkeypatch, run_cli, tmp_path):
    """SKH16: skill-edit-step.sh's exit 2 (wait reports exit 1, printing 2) stops the stage with 2, before step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 1, "2\n", ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, [c[0] for c in calls if c[0] in ("step-tick.sh", "skill-edit-step.sh")]) == (2, []), (code, calls)


def test_4450_it_exits_2_before_any_call_when_the_open_step_does_not_carry_the_skill_edit_mark(
        monkeypatch, run_cli, tmp_path):
    """SKH42: an open step without ⟦skill-edit⟧ is refused with exit 2 before gh, skill-edit-step.sh or step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, calls) == (2, []), (code, calls)


def test_4450_it_exits_2_before_any_call_when_ledger_unit_of_finds_no_unit_in_the_open_skill_edit_step(
        monkeypatch, run_cli, tmp_path):
    """SKH43: an open ⟦skill-edit⟧ step naming no unit is refused with exit 2 before gh, skill-edit-step.sh or step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, calls) == (2, []), (code, calls)


def test_4450_it_exits_2_before_any_call_on_a_non_numeric_issue_an_unknown_option_or_change_with_no_value(
        monkeypatch, run_cli, tmp_path):
    """SKH42: bad arguments are refused with exit 2 before gh, skill-edit-step.sh or step-tick.sh."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    for issue in ("12", "abc"):
        wt = tmp_path / ".tdd" / "wt" / issue
        (wt / ".tdd").mkdir(parents=True)
        (wt / ".tdd" / ("issue-%s-preflight" % issue)).write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        (wt / ".tdd" / ("issue-%s.md" % issue)).write_text(
            "# Plan for #%s\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n" % issue)
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    for argv in (["abc"], ["12", "--bogus"], ["12", "--change"]):
        del calls[:]
        code, _, _ = run_cli(skill_edit_half, argv, cwd=str(tmp_path))
        assert (code, calls) == (2, []), (argv, code, calls)


def test_4450_it_exits_2_before_any_call_on_an_unknown_option_given_a_value(monkeypatch, run_cli, tmp_path):
    """SKH42: a three-argument call whose second argument is not --change is refused before any call."""
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
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12", "--bogus", "x"], cwd=str(tmp_path))

    assert (code, calls) == (2, []), (code, calls)


def test_4450_it_exits_2_before_any_call_when_the_preflight_file_or_the_ledger_is_missing(
        monkeypatch, run_cli, tmp_path):
    """SKH42: a missing .tdd/issue-<n>-preflight or ledger is refused with exit 2 before any call."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    calls = []

    def fake(name, *args, cwd=None, env=None, **kw):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    for missing in ("preflight", "ledger"):
        wt = tmp_path / missing / ".tdd" / "wt" / "12"
        (wt / ".tdd").mkdir(parents=True)
        if missing != "preflight":
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        if missing != "ledger":
            (wt / ".tdd" / "issue-12.md").write_text(
                "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
        del calls[:]
        code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path / missing))
        assert (missing, code, calls) == (missing, 2, []), (missing, code, calls)


def test_4450_it_never_prints_what_skill_edit_step_wrote_to_its_out_file_leaf_output_or_grader_fail_reasons(
        monkeypatch, run_cli, tmp_path):
    """Criterion 13: .tdd/skill-edit-<n>.out's content, a leaf's output or the grader's FAIL reasons, reaches no stream."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    secret = "LEAF-TRANSCRIPT-9d2f GRADER FAIL: row SE1 unmet"
    (wt / ".tdd" / "skill-edit-12.out").write_text(secret + "\n")

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "gh":
            return 0, BODY, ""
        return (1, "1", "") if args[:1] == ("wait",) else (0, "", "")

    monkeypatch.setattr(fused, "run_script", fake)

    code, out, err = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert code == 1, (code, out, err)
    assert "LEAF-TRANSCRIPT-9d2f" not in out + err and "FAIL" not in out + err, (out, err)


def test_4450_a_graded_commit_after_the_ledger_calls_step_tick_directly(
        monkeypatch, run_cli, tmp_path):
    """SKH6, SKH38: a `docs: requirements for <unit>, graded` commit after the ledger's last commit skips gh and the step."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []
    graded = "docs: requirements for skills/tdd/SKILL.md, graded"

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "git" and args[:1] == ("log",):
            if "--" in args and ".tdd/issue-12.md" in args:
                return 0, "aaaaaaa\n", ""
            return 0, "bbbbbbb %s\n%s\n" % (graded, graded), ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    names = [c[0] for c in calls]
    assert (code, "gh" in names, [c for c in calls if c[0] == "detach-command.sh"],
            [c for c in calls if c[0] == "step-tick.sh"]) == (0, False, [], [("step-tick.sh", ("12",))]), calls


def test_4450_a_graded_commit_at_or_before_the_ledgers_last_commit_runs_the_step_from_its_start(
        monkeypatch, run_cli, tmp_path):
    """SKH6, SKH38: a graded commit not after the ledger's last commit does not skip gh and the step."""
    fused = importlib.import_module("veri.fused")
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(
        "# Plan for #12\n\n- [ ] reword the prompt in `skills/tdd/SKILL.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    calls = []
    graded = "docs: requirements for skills/tdd/SKILL.md, graded"

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "git" and args[:1] == ("log",):
            if "--" in args and ".tdd/issue-12.md" in args:
                return 0, "aaaaaaa\n", ""
            if any(a.startswith("aaaaaaa..") for a in args):
                return 0, "", ""
            return 0, "%s\n" % graded, ""
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    names = [c[0] for c in calls]
    assert (code, "gh" in names, [c[1][:2] for c in calls if c[0] == "detach-command.sh"],
            [c for c in calls if c[0] == "step-tick.sh"]) == (
        0, True, [("start", "skill-edit-12"), ("wait", "skill-edit-12")],
        [("step-tick.sh", ("12",))]), calls


def _skill_edit_worktree(tmp_path):
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "conductor.pid").write_text("4242\n1700000000\n")
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [ ] %s\n" % STEP)
    return wt


def _fake_calls(monkeypatch, calls, waits):
    """fused.run_script answering each `detach-command.sh wait` with the next of <waits>, every other call with 0."""
    fused = importlib.import_module("veri.fused")
    answers = iter(waits)

    def fake(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "git":
            return 1, "", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return next(answers)
        return 0, BODY if base == "gh" else "", ""

    monkeypatch.setattr(fused, "run_script", fake)


def test_4450_a_run_out_slice_leaves_the_wait_record_so_the_next_call_starts_no_second_author(
        monkeypatch, run_cli, tmp_path):
    """SKH33, SKH34: the first call's run-out slice saves the wait record itself, so a second call by the same
    conductor makes no gh api call and starts no second skill-edit-step.sh."""
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    _skill_edit_worktree(tmp_path)
    calls = []
    _fake_calls(monkeypatch, calls, [(3, "", ""), (3, "", "")])

    first, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))
    del calls[:]
    second, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (first, second, calls) == (3, 3, [("detach-command.sh", ("wait", "skill-edit-12"))]), calls


def test_4450_a_finished_author_removes_the_wait_record_so_the_next_step_starts_its_own_author(
        monkeypatch, run_cli, tmp_path):
    """SKH34: the wait record lives only while the author runs; once its wait answers, the next call starts afresh."""
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    wt = _skill_edit_worktree(tmp_path)
    calls = []
    _fake_calls(monkeypatch, calls, [(3, "", ""), (0, "", ""), (0, "", "")])

    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))
    run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))
    del calls[:]
    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    starts = [c for c in calls if c[0] == "detach-command.sh" and c[1][:1] == ("start",)]
    assert (code, len(starts), (wt / ".tdd" / "issue-12-skill-edit-half-wait").exists()) == (0, 1, False), calls


def test_4450_an_author_killed_with_137_exits_2_and_ticks_nothing(monkeypatch, run_cli, tmp_path):
    """SKH3, SKH7: only skill-edit-step.sh's 0 or 3 ticks; a killed author (wait exit 1 printing 137) obtained no
    answer, so the stage exits 2 before step-tick.sh."""
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    _skill_edit_worktree(tmp_path)
    calls = []
    _fake_calls(monkeypatch, calls, [(1, "137\n", "")])

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, [c for c in calls if c[0] == "step-tick.sh"]) == (2, []), (code, calls)


def test_4450_a_wait_that_obtained_no_answer_exits_2_and_ticks_nothing(monkeypatch, run_cli, tmp_path):
    """SKH16: detach-command.sh wait's own exit 2 (the author died with no exit file, or a `now` stop) is the
    stage's exit 2, before step-tick.sh."""
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    _skill_edit_worktree(tmp_path)
    calls = []
    _fake_calls(monkeypatch, calls, [(2, "", "")])

    code, _, _ = run_cli(skill_edit_half, ["12"], cwd=str(tmp_path))

    assert (code, [c for c in calls if c[0] == "step-tick.sh"]) == (2, []), (code, calls)
