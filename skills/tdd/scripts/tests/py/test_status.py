"""In-process cases for veri/status.py, the module status.sh is a shim over."""
import ast
import builtins
import importlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import pytest

from conftest import SCRIPTS, fake_pid_file_ps, listed, live_conductor, serve_listing, started_for_real


@pytest.fixture(autouse=True)
def text_mode(monkeypatch):
    monkeypatch.delenv("STATUS_JSON", raising=False)


@pytest.fixture
def status():
    return importlib.import_module("veri.status")


def write_events(path, events):
    path.write_text("".join(json.dumps(event) + "\n" for event in events))


def ledger_run(root, issue, text, number=None):
    """<root>/.tdd/wt/<issue> holding <text> as issue-<number>.md (default: its own)."""
    run = root / ".tdd" / "wt" / issue
    (run / ".tdd").mkdir(parents=True, exist_ok=True)
    (run / ".tdd" / ("issue-%s.md" % (number or issue))).write_text(text)
    return run


def fake_git(monkeypatch, main_tree, branches=None, solvable=None, linked=None):
    """subprocess.run answering `git worktree list` with <main_tree>, then <linked> when given,
    `symbolic-ref` from <branches>, any `gh` with exit 1 and no output, and starting any other command for real over the open-issue listing
    <solvable> = (exit code, stdout) selects to, its issues carrying the lamps-label label."""
    listing = serve_listing(main_tree / "solvable-listing", monkeypatch)
    if solvable is not None:
        listing(listed(*solvable), label="lamps-label")
        monkeypatch.chdir(main_tree)

    def fake_run(args, **kwargs):
        code = 0
        if list(args[:3]) == ["git", "worktree", "list"]:
            stdout = "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree
            if linked is not None:
                stdout += "worktree %s\nHEAD def\nbranch refs/heads/side\n\n" % linked
        elif "symbolic-ref" in args:
            stdout = branches[str(args[args.index("-C") + 1]).rstrip("/")] + "\n"
        elif args[0] == "gh":
            code, stdout = 1, ""
        elif solvable is not None:
            return started_for_real(args, **kwargs)
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, code, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.delenv("VERI_LABEL", raising=False)


def test_main_renders_a_three_step_ledger_with_one_ticked_as_step_2_of_3(tmp_path, monkeypatch, capsys, status):
    run = ledger_run(tmp_path, "31",
                     "# Plan for #31 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n- [ ] a lamp dims\n")

    lamp_git(monkeypatch, tmp_path, [run])

    status.main([])

    assert "step 2 of 3" in capsys.readouterr().out


def test_main_counts_the_ledgers_steps_alone_and_no_stray_checkbox_line_outside_them(tmp_path, monkeypatch, capsys, status):
    run = ledger_run(tmp_path, "31", "# Plan for #31 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n\n"
                                     "Notes:\n* [ ] a stray box, not a step\n")
    lamp_git(monkeypatch, tmp_path, [run])

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#31  lamps glow  tdd/31-lamps  step 2 of 2\n")


def test_main_renders_every_run_as_status_sh_does_and_returns_0(tmp_path, monkeypatch, capsys, status):
    ledgers = {"31": "# Plan for #31 — lamps glow\n\n- [x] a lamp exists\n- [ ] a lamp glows\n",
               "32": "# Plan for #32 — bells ring\n\n- [ ] a bell rings\n"}
    for issue, text in ledgers.items():
        ledger_run(tmp_path, issue, text)
    fake_git(monkeypatch, tmp_path, {str(tmp_path / ".tdd" / "wt" / "31"): "tdd/31-lamps",
                                     str(tmp_path / ".tdd" / "wt" / "32"): "tdd/32-bells"})

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#31  lamps glow  tdd/31-lamps  step 2 of 2\n"
                                                  "#32  bells ring  tdd/32-bells  step 1 of 1\n")


def test_2597_json_with_no_run_prints_a_document_with_an_empty_runs_list_and_returns_3(tmp_path, monkeypatch, capsys, status):
    fake_git(monkeypatch, tmp_path)

    code = status.main(["--json"])

    out = capsys.readouterr().out
    assert code == 3 and json.loads(out)["runs"] == [], out


def test_main_prints_no_runs_and_returns_3_when_the_main_working_tree_holds_none(tmp_path, monkeypatch, capsys, status):
    fake_git(monkeypatch, tmp_path)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (3, "no runs\n")


def test_main_shows_a_runs_phase_actor_leaf_elapsed_seconds_and_attempts_in_the_step(tmp_path, monkeypatch, capsys, status):
    run = ledger_run(tmp_path, "8", "# Plan for #8 — gears turn\n\n- [x] a gear exists\n- [ ] a gear turns\n")

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
    live_conductor(monkeypatch, run / ".tdd", "8")
    at_ten_thousand(monkeypatch)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#8  gears turn  tdd/8-gears-turn  step 2 of 2  green  developer  "
                                                  "develop-green 100s  attempt 2  $0.00  0 tokens  running\n")


def lamp_run(tmp_path, issue, ledgers=None):
    """.tdd/wt/<issue> holding a ledger per number in <ledgers> (default: its own), each '# Plan for #<n> — lamps glow'."""
    for number in ledgers if ledgers is not None else [issue]:
        run = ledger_run(tmp_path, issue, "# Plan for #%s — lamps glow\n\n- [ ] a lamp glows\n" % number, number)
    return run


def lamp_ev(ts, issue, event, **rest):
    line = {"ts": ts, "issue": issue, "actor": "developer", "phase": "red", "step": "a lamp glows",
            "event": event, "attempt": "1", "skill_commit": "abc"}
    line.update(rest)
    return line


def lamp_usage(ts, issue, dollars):
    return lamp_ev(ts, issue, "usage", total_cost_usd=dollars, input_tokens="10", output_tokens="0",
                   cache_read_input_tokens="0", cache_creation_input_tokens="0")


def lamp_git(monkeypatch, tmp_path, runs, solvable=None):
    """fake_git answering each run directory in <runs> with branch tdd/<its name>-lamps."""
    fake_git(monkeypatch, tmp_path, {str(run): "tdd/%s-lamps" % run.name for run in runs}, solvable)


def at_ten_thousand(monkeypatch):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setattr(time, "time", lambda: 10000)


def test_main_shows_a_runs_cost_in_dollars_and_tokens_summed_from_its_event_log(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "9")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9700, "9", "launch", name="develop-red"),
        lamp_ev(9750, "9", "usage", total_cost_usd="0.50", input_tokens="1000", output_tokens="200",
                cache_read_input_tokens="3000", cache_creation_input_tokens="500"),
        lamp_ev(9800, "9", "launch", phase="green", step="a lamp dims", name="develop-green"),
        lamp_ev(9900, "9", "usage", phase="green", step="a lamp dims", total_cost_usd="1.25", input_tokens="2000", output_tokens="300",
                cache_read_input_tokens="4000", cache_creation_input_tokens="0"),
    ])
    lamp_git(monkeypatch, tmp_path, [run])
    live_conductor(monkeypatch, run / ".tdd", "9")
    at_ten_thousand(monkeypatch)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#9  lamps glow  tdd/9-lamps  step 1 of 1  green  developer  "
                                                  "develop-green 200s  attempt 1  $1.75  11000 tokens  running\n")


def test_main_reports_a_finished_runs_last_attempt_count_when_its_done_event_has_an_empty_step(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "15")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9960, "15", "launch", name="develop-red"),
        lamp_ev(9970, "15", "launch", attempt="2", name="develop-red"),
        lamp_ev(9980, "15", "done", actor="conductor", phase="", step="", attempt="",
                pr="https://github.com/o/r/pull/15"),
    ])
    lamp_git(monkeypatch, tmp_path, [run])
    at_ten_thousand(monkeypatch)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#15  lamps glow  tdd/15-lamps  step 1 of 1  red  developer  "
                                                  "develop-red 30s  attempt 2  $0.00  0 tokens  "
                                                  "done https://github.com/o/r/pull/15\n")


def stop_mark(ts, issue):
    return lamp_ev(ts, issue, "stop", actor="conductor", phase="", attempt="", mode="at-leaf", at="planned")


def test_main_reads_a_run_ending_in_a_stop_mark_as_stopped_with_its_mode_in_text_and_json(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "16")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9980, "16", "launch", name="develop-red"),
        stop_mark(9990, "16"),
    ])
    lamp_git(monkeypatch, tmp_path, [run])
    at_ten_thousand(monkeypatch)

    text_code = status.main([])
    text = capsys.readouterr().out
    json_code = status.main(["--json"])
    obj = json.loads(capsys.readouterr().out)["runs"][0]

    assert (text_code, json_code, text.rstrip("\n").endswith("  stopped at-leaf"), obj["state"], obj["stop_mode"]) == (0, 0, True, "stopped", "at-leaf")


def test_main_reads_a_run_as_running_again_after_a_resume_mark_follows_its_stop_mark(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "17")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9970, "17", "launch", name="develop-red"),
        stop_mark(9980, "17"),
        lamp_ev(9990, "17", "resume", actor="conductor", phase="", attempt=""),
    ])
    lamp_git(monkeypatch, tmp_path, [run])
    live_conductor(monkeypatch, run / ".tdd", "17")
    at_ten_thousand(monkeypatch)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#17  lamps glow  tdd/17-lamps  step 1 of 1  red  developer  "
                                                  "develop-red 30s  attempt 1  $0.00  0 tokens  running\n")


def test_main_reads_a_run_whose_done_mark_is_followed_by_a_ci_repair_step_added_as_running_and_not_done_in_its_totals_1431(tmp_path, monkeypatch, capsys, status):
    run = ledger_run(tmp_path, "18", "# Plan for #18 — lamps glow\n\n- [x] a lamp glows\n"
                                     "- [ ] fix the CI failure: lamp.test.sh — FAIL - a lamp glows ⟦ci-repair⟧\n")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9900, "18", "launch", name="develop-red"),
        lamp_ev(9950, "18", "done", actor="conductor", phase="", step="", attempt="",
                pr="https://github.com/o/r/pull/18"),
        lamp_ev(9980, "18", "step-added", actor="conductor", phase="", attempt="",
                anchor="a lamp glows", added="1"),
    ])
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    live_conductor(monkeypatch, run / ".tdd", "18")
    at_ten_thousand(monkeypatch)

    code = status.main(["--scope", "lamps-label"])

    assert (code, capsys.readouterr().out) == (0, "#18  lamps glow  tdd/18-lamps  step 2 of 2  red  developer  "
                                                  "develop-red 100s  attempt 1  $0.00  0 tokens  running\n"
                                                  "scope lamps-label  attempted 1  done 0  bailed 0  wall 80s  $0.00  solvable 0\n")


def test_main_skips_a_step_added_record_with_no_ts_in_the_runs_elapsed_and_the_scope_wall_seconds_2322(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "24")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9900, "24", "launch", name="develop-red"),
        lamp_ev(9930, "24", "launch", name="develop-red"),
        {"event": "step-added", "actor": "add-ledger-step", "step": "x"},
    ])
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    live_conductor(monkeypatch, run / ".tdd", "24")
    at_ten_thousand(monkeypatch)

    code = status.main(["--scope", "lamps-label"])

    out = capsys.readouterr().out
    assert (code, last_line(out)) == (0, "scope lamps-label  attempted 1  done 0  bailed 0  wall 30s  $0.00  solvable 0")
    assert "develop-red 70s" in out


def test_main_reads_a_recent_run_whose_conductor_pid_was_reused_as_stale_at_once_with_run_ends_cause_2007(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "19")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9990, "19", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("%d\n" % os.getpid())
    fake_pid_file_ps(monkeypatch, conductor=False)
    lamp_git(monkeypatch, tmp_path, [run])
    monkeypatch.chdir(tmp_path)
    at_ten_thousand(monkeypatch)

    code = status.main(["--json"])
    obj = json.loads(capsys.readouterr().out)["runs"][0]

    assert (code, obj["state"], obj.get("cause")) == (0, "stale", "unknown")


def test_main_scope_counts_a_run_bailed_only_when_its_standing_end_is_a_bail_1488(tmp_path, monkeypatch, capsys, status):
    def bail(ts, issue):
        return lamp_ev(ts, issue, "bail", actor="conductor", attempt="", cause="stuck", classification="system")

    def resume(ts, issue):
        return lamp_ev(ts, issue, "resume", actor="conductor", phase="", step="", attempt="")

    runs = {issue: lamp_run(tmp_path, issue) for issue in ("41", "42")}
    write_events(runs["41"] / ".tdd" / "events.jsonl", [
        lamp_ev(9000, "41", "launch", name="develop-red"), bail(9100, "41"), resume(9200, "41"), bail(9300, "41")])
    write_events(runs["42"] / ".tdd" / "events.jsonl", [
        lamp_ev(9400, "42", "launch", name="develop-red"), bail(9500, "42"), resume(9600, "42"),
        lamp_ev(9700, "42", "done", actor="conductor", phase="", step="", attempt="",
                pr="https://github.com/o/r/pull/42")])
    lamp_git(monkeypatch, tmp_path, runs.values(), (3, ""))
    at_ten_thousand(monkeypatch)

    code = status.main(["--scope", "lamps-label"])
    text = last_line(capsys.readouterr().out)
    json_code = status.main(["--json", "--scope", "lamps-label"])
    scope = json.loads(capsys.readouterr().out)["scope"]

    assert (code, json_code) == (0, 0)
    assert text == "scope lamps-label  attempted 2  done 1  bailed 1  wall 600s  $0.00  solvable 0"
    assert (scope["done"], scope["bailed"]) == (1, 1)


def lamps_scope(tmp_path, monkeypatch, solvable):
    """Runs 21 (running), 22 (done) and 23 (bailed): attempted 3, done 1, bailed 1, wall 360s, $2.25."""
    endings = {"21": [],
               "22": [lamp_ev(9700, "22", "done", actor="conductor", phase="", step="", attempt="",
                              pr="https://github.com/o/r/pull/22")],
               "23": [lamp_ev(9100, "23", "bail", actor="conductor", attempt="", cause="stuck",
                              classification="system")]}
    runs = {}
    for issue, launch, usage, dollars in (("21", 9900, 9960, "0.25"), ("22", 9500, 9650, "1.50"),
                                          ("23", 9000, 9050, "0.50")):
        runs[issue] = lamp_run(tmp_path, issue)
        write_events(runs[issue] / ".tdd" / "events.jsonl",
                     [lamp_ev(launch, issue, "launch", name="develop-red"), lamp_usage(usage, issue, dollars)]
                     + endings[issue])
    lamp_git(monkeypatch, tmp_path, runs.values(), solvable)
    live_conductor(monkeypatch, runs["21"] / ".tdd", "21")
    at_ten_thousand(monkeypatch)


TWO_LAMPS_SOLVABLE = (0, "31\n32\n")


def last_line(out):
    return out.rstrip("\n").split("\n")[-1]


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_scope_adds_the_scopes_attempted_done_bailed_wall_and_dollars_totals(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, (3, ""))

    code = status.main(["--scope", "lamps-label"])

    assert (code, last_line(capsys.readouterr().out)) == (
        0, "scope lamps-label  attempted 3  done 1  bailed 1  wall 360s  $2.25  solvable 0")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_with_no_scope_takes_the_scope_from_veri_label_and_adds_the_same_totals(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, (3, ""))
    monkeypatch.setenv("VERI_LABEL", "lamps-label")

    code = status.main([])

    assert (code, last_line(capsys.readouterr().out)) == (
        0, "scope lamps-label  attempted 3  done 1  bailed 1  wall 360s  $2.25  solvable 0")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_scope_counts_what_solvable_issues_sh_lists_for_that_scope(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, TWO_LAMPS_SOLVABLE)

    code = status.main(["--scope", "lamps-label"])

    assert (code, last_line(capsys.readouterr().out).endswith("  solvable 2")) == (0, True)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_json_emits_the_runs_and_scope_totals_as_one_document(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, TWO_LAMPS_SOLVABLE)

    code = status.main(["--json", "--scope", "lamps-label"])
    doc = json.loads(capsys.readouterr().out)

    assert code == 0
    assert [(r["issue"], r["title"], r["branch"], r["state"], r["pr"], r["classification"]) for r in doc["runs"]] == [
        ("21", "lamps glow", "tdd/21-lamps", "running", "", ""),
        ("22", "lamps glow", "tdd/22-lamps", "done", "https://github.com/o/r/pull/22", ""),
        ("23", "lamps glow", "tdd/23-lamps", "bailed", "", "system"),
    ]
    assert doc["scope"] == {"name": "lamps-label", "attempted": 3, "done": 1, "bailed": 1,
                            "wall_seconds": 360, "dollars": 2.25, "solvable": 2}


def test_main_counts_the_scopes_solvable_issues_when_starting_solvable_issues_sh_is_refused(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, TWO_LAMPS_SOLVABLE)
    answering = subprocess.run

    def refusing(args, **kwargs):
        if any("solvable-issues.sh" in str(arg) for arg in args):
            raise OSError("refused: %r" % (args,))
        return answering(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", refusing)

    code = status.main(["--scope", "lamps-label"])

    assert (code, last_line(capsys.readouterr().out).endswith("  solvable 2")) == (0, True)


def test_main_scope_solvable_is_unknown_and_named_on_stderr_when_veri_priority_label_is_set_but_empty(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, TWO_LAMPS_SOLVABLE)
    monkeypatch.setenv("VERI_PRIORITY_LABEL", "")

    code = status.main(["--scope", "lamps-label"])

    captured = capsys.readouterr()
    assert (code, last_line(captured.out), captured.err) == (
        0, "scope lamps-label  attempted 3  done 1  bailed 1  wall 360s  $2.25  solvable ?",
        "solvable-issues: VERI_PRIORITY_LABEL is set but empty: name a label or leave it unset\n")


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_json_emits_scope_solvable_as_a_number(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, TWO_LAMPS_SOLVABLE)

    code = status.main(["--json", "--scope", "lamps-label"])
    solvable = json.loads(capsys.readouterr().out)["scope"]["solvable"]

    assert (code, type(solvable), solvable) == (0, int, 2)


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_renders_solvable_as_a_question_mark_when_solvable_issues_sh_gives_no_answer(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, (2, ""))

    text_code = status.main(["--scope", "lamps-label"])
    text = last_line(capsys.readouterr().out)
    json_code = status.main(["--json", "--scope", "lamps-label"])
    solvable = json.loads(capsys.readouterr().out)["scope"]["solvable"]

    assert (text_code, text.endswith("  solvable ?"), json_code, solvable) == (0, True, 0, "?")


def test_main_json_lists_every_run_with_issue_state_unknown_and_exits_0_when_github_gives_no_answer_2497(tmp_path, monkeypatch, capsys, status):
    runs = [lamp_run(tmp_path, "13"), lamp_run(tmp_path, "14")]
    lamp_git(monkeypatch, tmp_path, runs)

    code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (code, [(r["issue"], r.get("issue_state")) for r in doc["runs"]]) == (0, [("13", "unknown"), ("14", "unknown")])


def test_main_json_gives_each_run_the_issue_state_github_reports_not_one_inferred_from_its_bail_2497(tmp_path, monkeypatch, capsys, status):
    bailed, closed = lamp_run(tmp_path, "13"), lamp_run(tmp_path, "14")
    write_events(bailed / ".tdd" / "events.jsonl", [lamp_ev(9900, "13", "bail", actor="conductor", classification="process")])
    lamp_git(monkeypatch, tmp_path, [bailed, closed])
    answering = subprocess.run
    github = json.dumps([{"number": 13, "state": "OPEN"}, {"number": 14, "state": "CLOSED"}])

    def run_with_github(args, **kwargs):
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, github, "")
        return answering(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run_with_github)

    code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (code, [(r["issue"], r.get("issue_state")) for r in doc["runs"]]) == (0, [("13", "open"), ("14", "closed")])


def test_main_json_reports_state_closed_for_a_run_whose_issue_is_closed_and_bailed_for_an_open_one_2497(tmp_path, monkeypatch, capsys, status):
    open_run, closed_run = lamp_run(tmp_path, "13"), lamp_run(tmp_path, "14")
    for run, issue in ((open_run, "13"), (closed_run, "14")):
        write_events(run / ".tdd" / "events.jsonl", [
            lamp_ev(9800, issue, "launch", name="develop-red"),
            lamp_ev(9900, issue, "bail", actor="conductor", classification="process")])
    lamp_git(monkeypatch, tmp_path, [open_run, closed_run])
    answering = subprocess.run
    github = json.dumps([{"number": 13, "state": "OPEN"}, {"number": 14, "state": "CLOSED"}])

    def run_with_github(args, **kwargs):
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, github, "")
        return answering(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run_with_github)

    code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (code, [(r["issue"], r.get("state")) for r in doc["runs"]]) == (0, [("13", "bailed"), ("14", "closed")])


def test_main_json_reads_the_issue_states_through_one_github_wrapper_call_for_every_run_2497(tmp_path, monkeypatch, capsys, status):
    runs = [lamp_run(tmp_path, "13"), lamp_run(tmp_path, "14"), lamp_run(tmp_path, "15")]
    lamp_git(monkeypatch, tmp_path, runs)
    github = importlib.import_module("veri.github")
    calls = []

    def gh_issue_list(*args):
        calls.append(args)
        return json.dumps([{"number": 13, "state": "OPEN"}, {"number": 14, "state": "CLOSED"},
                           {"number": 15, "state": "OPEN"}])

    monkeypatch.setattr(github, "gh_issue_list", gh_issue_list)

    code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (code, len(doc["runs"]), len(calls)) == (0, 3, 1)


def test_main_json_reports_every_run_when_gh_answers_json_that_is_not_a_list_of_issues_2497(tmp_path, monkeypatch, capsys, status):
    runs = [lamp_run(tmp_path, "13")]
    lamp_git(monkeypatch, tmp_path, runs)
    github = importlib.import_module("veri.github")
    monkeypatch.setattr(github, "gh_issue_list", lambda *args: json.dumps({"body": "Closes #13"}))

    code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (code, [r["issue"] for r in doc["runs"]]) == (0, ["13"])


def test_main_prints_closed_in_place_of_bailed_for_a_run_whose_issue_is_closed_and_leaves_an_open_runs_line_2497(tmp_path, monkeypatch, capsys, status):
    open_run, closed_run = lamp_run(tmp_path, "13"), lamp_run(tmp_path, "14")
    for run, issue in ((open_run, "13"), (closed_run, "14")):
        write_events(run / ".tdd" / "events.jsonl", [
            lamp_ev(9800, issue, "launch", name="develop-red"),
            lamp_ev(9900, issue, "bail", actor="conductor", classification="process")])
    lamp_git(monkeypatch, tmp_path, [open_run, closed_run])
    answering = subprocess.run
    github = json.dumps([{"number": 13, "state": "OPEN"}, {"number": 14, "state": "CLOSED"}])

    def run_with_github(args, **kwargs):
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, github, "")
        return answering(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run_with_github)

    code = status.main([])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [(l.split()[0], "closed" in l.split(), "bailed" in l.split()) for l in lines]) == (
        0, [("#13", False, True), ("#14", True, False)])


def test_main_json_reports_bail_phase_from_the_bail_event_not_the_last_launch(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "13")
    write_events(run / ".tdd" / "events.jsonl", [
        lamp_ev(9900, "13", "launch", name="develop-red"),
        lamp_ev(9950, "13", "bail", actor="conductor", phase="green", attempt="", classification="process"),
    ])
    lamp_git(monkeypatch, tmp_path, [run])
    at_ten_thousand(monkeypatch)

    code = status.main(["--json"])
    obj = json.loads(capsys.readouterr().out)["runs"][0]

    assert (code, obj["phase"], obj["bail_phase"]) == (0, "red", "green")


def test_main_takes_a_run_directory_as_one_run_its_own_issues_ledger_only(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "7", ["7", "3", "5"])
    lamp_git(monkeypatch, tmp_path, [run])

    text_code = status.main([])
    text = capsys.readouterr().out
    json_code = status.main(["--json"])
    issues = [r["issue"] for r in json.loads(capsys.readouterr().out)["runs"]]

    assert (text_code, text, json_code, issues) == (0, "#7  lamps glow  tdd/7-lamps  step 1 of 1\n", 0, ["7"])


def test_main_prints_two_runs_with_their_own_totals_when_each_directory_holds_the_others_ledger(tmp_path, monkeypatch, capsys, status):
    runs = {}
    for issue, other, dollars in (("7", "9", "0.25"), ("9", "7", "1.50")):
        runs[issue] = lamp_run(tmp_path, issue, [issue, "4", other])
        write_events(runs[issue] / ".tdd" / "events.jsonl",
                     [lamp_ev(9990, issue, "launch", name="develop-red"), lamp_usage(9995, issue, dollars)])
    lamp_git(monkeypatch, tmp_path, runs.values())
    at_ten_thousand(monkeypatch)

    code = status.main(["--json"])
    pairs = [(r["issue"], r["dollars"]) for r in json.loads(capsys.readouterr().out)["runs"]]

    assert (code, pairs) == (0, [("7", 0.25), ("9", 1.5)])


def test_main_counts_no_run_for_a_directory_without_its_own_ledger_and_is_not_an_error(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "8", ["3", "5"])
    lamp_git(monkeypatch, tmp_path, [run])

    text_code = status.main([])
    text = capsys.readouterr().out
    json_code = status.main(["--json"])
    doc = json.loads(capsys.readouterr().out)

    assert (text_code, text, json_code, doc) == (0, "", 0, {"runs": [], "scope": None})


@pytest.mark.process("solvable-issues.sh started for real over a VERI_GH_JSON listing")
def test_main_takes_the_run_activity_and_scope_totals_lines_from_event_logs_one_parse_and_sum_with_figures_unchanged(tmp_path, monkeypatch, capsys, status):
    run = ledger_run(tmp_path, "9", "# Plan for #9 — cogs mesh\n\n- [x] a cog exists\n- [ ] two cogs mesh\n")
    cogs = [
        lamp_ev(9700, "9", "launch", step="a cog exists", name="develop-red"),
        lamp_ev(9750, "9", "usage", step="a cog exists", total_cost_usd="0.50", input_tokens="1000",
                output_tokens="200", cache_read_input_tokens="3000", cache_creation_input_tokens="500"),
        lamp_ev(9800, "9", "launch", phase="green", step="two cogs mesh", name="develop-green"),
        lamp_ev(9900, "9", "usage", phase="green", step="two cogs mesh", total_cost_usd="1.25",
                input_tokens="2000", output_tokens="300", cache_read_input_tokens="4000",
                cache_creation_input_tokens="0"),
    ]
    (run / ".tdd" / "events.jsonl").write_text("\n" + json.dumps(cogs[0]) + "\n" + json.dumps(cogs[1]) + "\n\n\n"
                                              + json.dumps(cogs[2]) + "\n" + json.dumps(cogs[3]) + "\n\n")
    fake_git(monkeypatch, tmp_path, {str(run): "tdd/9-cogs-mesh"}, (3, ""))
    live_conductor(monkeypatch, run / ".tdd", "9")
    at_ten_thousand(monkeypatch)

    text_code = status.main(["--scope", "cogs-label"])
    text = capsys.readouterr().out
    json_code = status.main(["--json", "--scope", "cogs-label"])
    doc = json.loads(capsys.readouterr().out)
    run_obj, scope = doc["runs"][0], doc["scope"]
    figures = (run_obj["leaf"], run_obj["attempts"], run_obj["dollars"], run_obj["tokens"],
               scope["dollars"], scope["wall_seconds"], scope["attempted"])

    (run / ".tdd" / "conductor.pid").unlink()
    standin = tmp_path / "standin"
    standin.mkdir()
    (standin / "event_log.py").write_text(
        "def read_events(path):\n"
        "    return [{'ts': 1000, 'event': 'launch', 'step': 'decoy step', 'phase': 'red',\n"
        "             'actor': 'developer', 'name': 'decoy-leaf'},\n"
        "            {'ts': 1077, 'event': 'usage'}]\n\n\n"
        "def usage_totals(events):\n"
        "    return 3.0, 1234\n")
    real_event_log = sys.modules["event_log"]
    sys.path.insert(0, str(standin))
    del sys.modules["event_log"]
    try:
        importlib.reload(status)
        decoy_code = status.main(["--scope", "cogs-label"])
        decoy = capsys.readouterr().out
    finally:
        sys.path.remove(str(standin))
        sys.modules["event_log"] = real_event_log
        importlib.reload(status)

    assert (text_code, text, json_code, figures, decoy_code, decoy) == (
        0, "#9  cogs mesh  tdd/9-cogs-mesh  step 2 of 2  green  developer  develop-green 200s  attempt 1  "
           "$1.75  11000 tokens  running\n"
           "scope cogs-label  attempted 1  done 0  bailed 0  wall 200s  $1.75  solvable 0\n",
        0, ("develop-green", 1, 1.75, 11000, 1.75, 200, 1),
        0, "#9  cogs mesh  tdd/9-cogs-mesh  step 2 of 2  red  developer  decoy-leaf 9000s  attempt 1  "
           "$3.00  1234 tokens  stale\n"
           "scope cogs-label  attempted 1  done 0  bailed 0  wall 77s  $3.00  solvable 0\n")


def test_main_resolves_the_main_working_tree_as_the_first_worktree_git_lists_as_lib_main_working_tree_sh_does(tmp_path, monkeypatch, capsys, status):
    main_tree, linked = tmp_path / "main", tmp_path / "linked"
    for tree, issue, title in ((main_tree, "5", "lamps glow"), (linked, "7", "bells ring")):
        ledger_run(tree, issue, "# Plan for #%s — %s\n\n- [ ] a step\n" % (issue, title))
    fake_git(monkeypatch, main_tree,
             {str(main_tree / ".tdd" / "wt" / "5"): "tdd/5-main", str(linked / ".tdd" / "wt" / "7"): "tdd/7-linked"},
             linked=linked)
    monkeypatch.chdir(linked)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#5  lamps glow  tdd/5-main  step 1 of 1\n")


def git_answering(main_tree, branches=None):
    """A fake_processes answer: `git worktree list` is <main_tree>, `symbolic-ref` is looked up in <branches>."""
    def answer(line, **kwargs):
        if line.startswith("git worktree list"):
            return 0, "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree, ""
        if " symbolic-ref " in line:
            return 0, branches[line.split()[2]] + "\n", ""
        raise AssertionError("unexpected command: %s" % line)
    return answer


def test_status_with_no_run_under_the_main_working_tree_prints_no_runs_and_exits_3(tmp_path, fake_processes, run_cli, status):
    fake_processes(git_answering(tmp_path))

    assert run_cli(status, []) == (3, "no runs\n", "")


def test_status_lists_a_run_under_tdd_wt_with_its_issue_number_title_branch_and_step_n_of_m(tmp_path, fake_processes, run_cli, status):
    run = ledger_run(tmp_path, "7", "# Plan for #7 \u2014 widgets spin when clicked\n\n- [x] a widget exists\n"
                                    "- [ ] a clicked widget spins\n- [ ] a spinning widget stops\n")
    git = git_answering(tmp_path, {str(run): "tdd/7-widgets-spin"})
    github = json.dumps([{"number": 7, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))

    assert run_cli(status, []) == (0, "#7  widgets spin when clicked  tdd/7-widgets-spin  step 2 of 3\n", "")


def test_status_shows_a_runs_state_running_done_with_its_pr_url_bailed_with_phase_and_classification_or_stale(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    runs = {issue: lamp_run(tmp_path, issue) for issue in ("11", "12", "13", "14")}
    launches = {"11": 9990, "12": 9980, "13": 9970, "14": 9000}
    endings = {"12": [lamp_ev(9985, "12", "done", actor="conductor", phase="", step="", attempt="",
                              pr="https://github.com/o/r/pull/12")],
               "13": [lamp_ev(9975, "13", "bail", actor="conductor", phase="green", attempt="", classification="system")]}
    for issue, run in runs.items():
        write_events(run / ".tdd" / "events.jsonl",
                     [lamp_ev(launches[issue], issue, "launch", name="develop-red")] + endings.get(issue, []))
    # #14 names a pid no process can hold (above every pid_max), so os.kill rejects it, not open.
    (runs["14"] / ".tdd" / "conductor.pid").write_text("%d\n" % (2 ** 31 - 1))
    git = git_answering(tmp_path, {str(run): "tdd/%s-lamps" % issue for issue, run in runs.items()})
    github = json.dumps([{"number": int(issue), "state": "CLOSED" if issue == "14" else "OPEN"} for issue in runs])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))
    live_conductor(monkeypatch, runs["11"] / ".tdd", "11")
    at_ten_thousand(monkeypatch)

    code, out, err = run_cli(status, [], env={"VERI_TIMEOUT": "600"})

    head = "  step 1 of 1  red  developer  develop-red "
    assert (code, err, out) == (0, "",
        "#11  lamps glow  tdd/11-lamps" + head + "10s  attempt 1  $0.00  0 tokens  running\n"
        "#12  lamps glow  tdd/12-lamps" + head + "20s  attempt 1  $0.00  0 tokens  done https://github.com/o/r/pull/12\n"
        "#13  lamps glow  tdd/13-lamps" + head + "30s  attempt 1  $0.00  0 tokens  bailed green system\n"
        "#14  lamps glow  tdd/14-lamps" + head + "1000s  attempt 1  $0.00  0 tokens  closed\n")


def test_status_watch_redraws_in_place_recomputing_every_run_from_disk_on_each_render(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    run = lamp_run(tmp_path, "41")
    events = run / ".tdd" / "events.jsonl"
    write_events(events, [lamp_ev(9990, "41", "launch", name="develop-red")])
    git = git_answering(tmp_path, {str(run): "tdd/41-lamps"})
    github = json.dumps([{"number": 41, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))
    live_conductor(monkeypatch, run / ".tdd", "41")
    at_ten_thousand(monkeypatch)
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        if len(sleeps) == 1:
            write_events(events, [lamp_ev(9990, "41", "launch", name="develop-red"),
                                  lamp_ev(9995, "41", "done", actor="conductor", phase="", step="", attempt="",
                                          pr="https://github.com/o/r/pull/41")])
        else:
            raise SystemExit(0)

    monkeypatch.setattr(time, "sleep", sleep)

    code, out, err = run_cli(status, ["--watch", "0"])

    line = "#41  lamps glow  tdd/41-lamps  step 1 of 1  red  developer  develop-red 10s  attempt 1  $0.00  0 tokens  "
    assert (code, err, sleeps, out) == (0, "", [0, 0], "\033[H\033[2J" + line + "running\n"
                                                        "\033[H\033[2J" + line + "done https://github.com/o/r/pull/41\n")


def test_status_exits_2_naming_the_failure_when_a_ledger_cannot_be_read_as_text(tmp_path, fake_processes, run_cli, status):
    run = ledger_run(tmp_path, "9", "")
    (run / ".tdd" / "issue-9.md").write_bytes(b"# Plan for #9 \xe2\x80\x94 locked\n\n- [ ] a \xff lock\n")
    git = git_answering(tmp_path, {str(run): "tdd/9-locked"})
    github = json.dumps([{"number": 9, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))

    code, out, err = run_cli(status, [])

    assert (code, out, err.startswith("status.sh: UnicodeDecodeError: ")) == (2, "", True)


def test_status_given_a_bad_argument_names_it_on_stderr_and_exits_2(tmp_path, fake_processes, run_cli, status):
    fake_processes(git_answering(tmp_path))

    assert run_cli(status, ["--bogus"]) == (2, "", "status.sh: unknown option '--bogus'\n")


@pytest.mark.process("status.sh run as a child through a symlink to the skills directory, over a real git repository")
def test_status_sh_run_through_a_symlink_to_the_skill_directory_and_from_another_working_directory_answers_as_in_place(tmp_path):
    repo = tmp_path / "repo"
    for path, branch in ((repo, "main"), (repo / ".tdd" / "wt" / "7", "tdd/7-widgets-spin")):
        subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)
    (repo / ".tdd" / "wt" / "7" / ".tdd").mkdir()
    (repo / ".tdd" / "wt" / "7" / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7 \u2014 widgets spin\n\n- [x] a widget exists\n- [ ] a clicked widget spins\n")
    (repo / "elsewhere").mkdir()
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parents[1], target_is_directory=True)

    def status_sh(script, cwd):
        ran = subprocess.run([str(script)], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr

    in_place = status_sh(SCRIPTS / "status.sh", repo)
    linked = status_sh(tmp_path / "linked-skill" / "tdd" / "scripts" / "status.sh", repo / "elsewhere")

    assert linked == in_place == (0, "#7  widgets spin  tdd/7-widgets-spin  step 2 of 2\n", "")


def test_main_json_counts_a_listed_run_in_the_scope_totals_when_its_events_vanish_after_render_read_them_2559(tmp_path, monkeypatch, capsys, status):
    runs = {issue: lamp_run(tmp_path, issue) for issue in ("41", "42")}
    for issue, run in runs.items():
        write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, issue, "launch", name="develop-red")])
    lamp_git(monkeypatch, tmp_path, runs.values(), (3, ""))
    at_ten_thousand(monkeypatch)
    activity = status.run_activity

    def activity_then_vanish(run, *args):
        shown = activity(run, *args)
        if os.path.basename(run) == "42":
            (pathlib.Path(run) / ".tdd" / "events.jsonl").unlink()
        return shown

    monkeypatch.setattr(status, "run_activity", activity_then_vanish)

    code = status.main(["--json", "--scope", "lamps-label"])
    scope = json.loads(capsys.readouterr().out)["scope"]

    assert (code, scope["attempted"]) == (0, 2)


@pytest.mark.parametrize("read", range(1, 16))
def test_main_json_exits_0_without_a_traceback_when_the_run_directory_vanishes_at_the_nth_read_of_its_files_2559(tmp_path, monkeypatch, capsys, status, read):
    run = lamp_run(tmp_path, "42")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, "42", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("0\n")
    write_events(run / ".tdd" / "conductor-42.log", [{"type": "system", "subtype": "init"},
                                                    {"type": "result", "result": "ok"}])
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    at_ten_thousand(monkeypatch)
    reads = []

    def vanish_at_the_nth(real):
        def spy(path, *args, **kwargs):
            if isinstance(path, (str, os.PathLike)) and os.fspath(path).startswith(str(run) + "/.tdd"):
                reads.append(path)
                if len(reads) == read:
                    shutil.rmtree(run)
            return real(path, *args, **kwargs)
        return spy

    monkeypatch.setattr(builtins, "open", vanish_at_the_nth(builtins.open))
    monkeypatch.setattr(os, "listdir", vanish_at_the_nth(os.listdir))
    monkeypatch.setattr(os.path, "getmtime", vanish_at_the_nth(os.path.getmtime))

    code = status.main(["--json", "--scope", "lamps-label"])

    assert (code, json.loads(capsys.readouterr().out)["scope"]["attempted"] <= 1) == (0, True)


def test_no_case_in_this_suite_calls_a_function_of_veri_status_other_than_main():
    tree = ast.parse(pathlib.Path(__file__).read_text())

    calls = sorted({node.func.attr for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "status"
                    and node.func.attr != "main"})

    assert calls == []



def test_2551_step_names_the_step_pending_refactor_and_the_next_open_one_once_it_is_finished(tmp_path, monkeypatch, capsys, status):
    head = "# Plan for #51 — lamps glow\n\n- [x] one\n- [x] two\n"
    pending = ledger_run(tmp_path, "51", head + "- [x] three ⟂ refactor pending\n- [ ] four\n")
    finished = ledger_run(tmp_path, "52", head.replace("#51", "#52") + "- [x] three\n- [ ] four\n", number="52")
    lamp_git(monkeypatch, tmp_path, [pending, finished])

    status.main(["--json"])

    runs = json.loads(capsys.readouterr().out)["runs"]
    assert [run["step"] for run in runs] == ["3 of 4", "4 of 4"]


def test_2635_main_json_renders_without_raising_a_run_whose_newest_leaf_log_holds_blank_and_prose_lines_after_stream_json(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "42")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, "42", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("0\n")
    write_events(run / ".tdd" / "conductor-42.log", [{"type": "system", "subtype": "init"},
                                                    {"type": "result", "result": "ok"}])
    leaf_log = run / ".tdd" / "develop-exhausted.log"
    leaf_log.write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n"
                        + json.dumps({"type": "assistant"}) + "\n"
                        + "\n\nThe criterion does not hold yet\n\nSTATEMENT: prose\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    at_ten_thousand(monkeypatch)

    try:
        code = status.main(["--json", "--scope", "lamps-label"])
        rendered = json.loads(capsys.readouterr().out)["scope"]["attempted"]
    except ValueError as raised:
        code, rendered = "ValueError: %s" % raised, None

    assert (code, rendered) == (0, 1)


def test_2635_main_json_renders_without_raising_a_run_whose_newest_leaf_log_holds_only_a_partial_first_line(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "42")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, "42", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("0\n")
    write_events(run / ".tdd" / "conductor-42.log", [{"type": "system", "subtype": "init"},
                                                    {"type": "result", "result": "ok"}])
    leaf_log = run / ".tdd" / "develop-exhausted.log"
    leaf_log.write_text('{"type": "syst')
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    at_ten_thousand(monkeypatch)

    try:
        code = status.main(["--json", "--scope", "lamps-label"])
        rendered = json.loads(capsys.readouterr().out)["scope"]["attempted"]
    except ValueError as raised:
        code, rendered = "ValueError: %s" % raised, None

    assert (code, rendered) == (0, 1)



def test_2635_main_json_renders_without_raising_a_run_whose_conductor_log_holds_a_result_record_then_blank_and_prose_lines(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "42")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, "42", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("0\n")
    (run / ".tdd" / "conductor-42.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n"
        + json.dumps({"type": "result", "result": "ok"}) + "\n"
        + "\n\nThe criterion does not hold yet\n\nSTATEMENT: prose\n")
    leaf_log = run / ".tdd" / "develop-exhausted.log"
    leaf_log.write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    at_ten_thousand(monkeypatch)

    try:
        code = status.main(["--json", "--scope", "lamps-label"])
        rendered = json.loads(capsys.readouterr().out)["scope"]["attempted"]
    except ValueError as raised:
        code, rendered = "ValueError: %s" % raised, None

    assert (code, rendered) == (0, 1)


def test_2635_main_json_renders_without_raising_a_run_whose_conductor_log_holds_a_partial_first_line_before_its_result_record(tmp_path, monkeypatch, capsys, status):
    run = lamp_run(tmp_path, "42")
    write_events(run / ".tdd" / "events.jsonl", [lamp_ev(9000, "42", "launch", name="develop-red")])
    (run / ".tdd" / "conductor.pid").write_text("0\n")
    (run / ".tdd" / "conductor-42.log").write_text(
        '{"type": "syst\n' + json.dumps({"type": "result", "result": "ok"}) + "\n")
    leaf_log = run / ".tdd" / "develop-exhausted.log"
    leaf_log.write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    lamp_git(monkeypatch, tmp_path, [run], (3, ""))
    at_ten_thousand(monkeypatch)

    try:
        code = status.main(["--json", "--scope", "lamps-label"])
        rendered = json.loads(capsys.readouterr().out)["scope"]["attempted"]
    except ValueError as raised:
        code, rendered = "ValueError: %s" % raised, None

    assert (code, rendered) == (0, 1)
