"""In-process cases for veri/status.py, the module status.sh is a shim over."""
import importlib
import json
import pathlib
import subprocess
import sys
import time

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(autouse=True)
def text_mode(monkeypatch):
    monkeypatch.delenv("STATUS_JSON", raising=False)


@pytest.fixture
def status():
    return importlib.import_module("veri.status")


def write_events(path, events):
    path.write_text("".join(json.dumps(event) + "\n" for event in events))


def fake_git(monkeypatch, main_tree, branches=None):
    """subprocess.run answering `git worktree list` with <main_tree> and `symbolic-ref` from <branches>."""
    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            stdout = "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree
        elif "symbolic-ref" in args:
            stdout = branches[str(args[args.index("-C") + 1]).rstrip("/")] + "\n"
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.delenv("VERI_LABEL", raising=False)


def test_run_activity_reports_the_last_launch_its_attempts_usage_and_state(tmp_path, monkeypatch, status):
    def ev(ts, phase, step, event, attempt, **rest):
        return {"ts": ts, "issue": "9", "actor": "developer", "phase": phase, "step": step,
                "event": event, "attempt": attempt, "skill_commit": "abc", **rest}

    events = tmp_path / "events.jsonl"
    write_events(events, [
        ev(9700, "red", "a cog exists", "launch", "1", name="develop-red"),
        ev(9750, "red", "a cog exists", "usage", "1", total_cost_usd="0.50",
           input_tokens="1000", output_tokens="200", cache_read_input_tokens="3000",
           cache_creation_input_tokens="500"),
        ev(9800, "green", "two cogs mesh", "launch", "1", name="develop-green"),
        ev(9850, "green", "two cogs mesh", "usage", "1", total_cost_usd="1.25",
           input_tokens="2000", output_tokens="300", cache_read_input_tokens="4000",
           cache_creation_input_tokens="0"),
        ev(9900, "green", "two cogs mesh", "launch", "2", name="develop-green"),
        ev(9950, "green", "two cogs mesh", "done", "2", pr="77"),
    ])
    monkeypatch.setattr(time, "time", lambda: 10000)

    line = status.run_activity(str(events), str(tmp_path / "conductor.pid"), 900)

    assert line == "green  developer  develop-green 100s  attempt 2  $1.75  11000 tokens  done 77"


def test_scope_totals_sums_attempts_outcomes_wall_and_dollars_over_the_runs(tmp_path, status):
    def ev(ts, event, **rest):
        return {"ts": ts, "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists",
                "event": event, "attempt": "1", "skill_commit": "abc", **rest}

    finished, bailed = tmp_path / "finished.jsonl", tmp_path / "bailed.jsonl"
    write_events(finished, [
        ev(100, "launch", name="develop-red"),
        ev(200, "usage", total_cost_usd="0.50", input_tokens="10", output_tokens="2",
           cache_read_input_tokens="0", cache_creation_input_tokens="0"),
        ev(400, "done", pr="77"),
    ])
    write_events(bailed, [
        ev(1000, "launch", name="develop-red"),
        ev(1100, "usage", total_cost_usd="1.25", input_tokens="20", output_tokens="3",
           cache_read_input_tokens="0", cache_creation_input_tokens="0"),
        ev(1600, "bail", classification="process"),
    ])

    line = status.scope_totals("veri", "4", [str(finished), str(bailed)])

    assert line == "scope veri  attempted 2  done 1  bailed 1  wall 900s  $1.75  solvable 4"


def test_run_object_merges_the_ledger_fields_with_the_activity_object(status):
    activity = json.dumps({"phase": "green", "actor": "developer", "state": "running"})

    obj = status.run_object("9", "a cog — meshes", "tdd/9-cog", "2 of 3", activity)

    assert obj == ('{"issue": "9", "title": "a cog \\u2014 meshes", "branch": "tdd/9-cog", '
                   '"step": "2 of 3", "phase": "green", "actor": "developer", "state": "running"}')


def test_main_renders_a_three_step_ledger_with_one_ticked_as_step_2_of_3(tmp_path, monkeypatch, capsys, status):
    run = tmp_path / ".tdd" / "wt" / "31"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-31.md").write_text(
        "# Plan for #31 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n- [ ] a lamp dims\n")

    fake_git(monkeypatch, tmp_path, {str(run): "tdd/31-lamps"})

    status.main([])

    assert "step 2 of 3" in capsys.readouterr().out


def test_main_renders_every_run_as_status_sh_does_and_returns_0(tmp_path, monkeypatch, capsys, status):
    ledgers = {"31": "# Plan for #31 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n",
               "32": "# Plan for #32 — bells ring\n\n- [ ] a bell rings\n"}
    for issue, text in ledgers.items():
        (tmp_path / ".tdd" / "wt" / issue / ".tdd").mkdir(parents=True)
        (tmp_path / ".tdd" / "wt" / issue / ".tdd" / ("issue-%s.md" % issue)).write_text(text)
    fake_git(monkeypatch, tmp_path, {str(tmp_path / ".tdd" / "wt" / "31"): "tdd/31-lamps",
                                     str(tmp_path / ".tdd" / "wt" / "32"): "tdd/32-bells"})

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#31  lamps glow  tdd/31-lamps  step 2 of 2\n"
                                                  "#32  bells ring  tdd/32-bells  step 1 of 1\n")


def test_main_prints_no_runs_and_returns_3_when_the_main_working_tree_holds_none(tmp_path, monkeypatch, capsys, status):
    fake_git(monkeypatch, tmp_path)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (3, "no runs\n")


def test_main_shows_a_runs_phase_actor_leaf_elapsed_seconds_and_attempts_in_the_step(tmp_path, monkeypatch, capsys, status):
    run = tmp_path / ".tdd" / "wt" / "8"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-8.md").write_text("# Plan for #8 — gears turn\n\n- [x] a gear exists\n- [ ] a gear turns\n")

    def ev(ts, actor, phase, step, event, attempt, name=None):
        return {"ts": ts, "issue": "8", "actor": actor, "phase": phase, "step": step, "event": event,
                "attempt": attempt, "skill_commit": "abc", **({"name": name} if name else {})}

    write_events(run / ".tdd" / "events.jsonl", [
        ev(9100, "conductor", "", "a gear exists", "step-start", ""),
        ev(9110, "developer", "red", "a gear exists", "launch", "1", "develop-red"),
        ev(9200, "developer", "green", "a gear exists", "launch", "1", "develop-green"),
        ev(9300, "verifier", "green", "a gear exists", "launch", "1", "verify-green"),
        ev(9400, "conductor", "", "a gear exists", "step-done", ""),
        ev(9500, "conductor", "", "a gear turns", "step-start", ""),
        ev(9600, "developer", "green", "a gear turns", "launch", "1", "develop-green"),
        ev(9900, "developer", "green", "a gear turns", "launch", "2", "develop-green"),
    ])
    fake_git(monkeypatch, tmp_path, {str(run): "tdd/8-gears-turn"})
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setattr(time, "time", lambda: 10000)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#8  gears turn  tdd/8-gears-turn  step 2 of 2  green  developer  "
                                                  "develop-green 100s  attempt 2  $0.00  0 tokens  running\n")
