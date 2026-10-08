"""In-process cases for veri/status.py, the module status.sh is a shim over."""
import ast
import importlib
import json
import pathlib
import subprocess
import sys
import time

import pytest


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
    `symbolic-ref` from <branches>, and solvable-issues.sh with <solvable>(scope) -> (exit code, stdout)."""
    def fake_run(args, **kwargs):
        code = 0
        if list(args[:3]) == ["git", "worktree", "list"]:
            stdout = "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree
            if linked is not None:
                stdout += "worktree %s\nHEAD def\nbranch refs/heads/side\n\n" % linked
        elif "symbolic-ref" in args:
            stdout = branches[str(args[args.index("-C") + 1]).rstrip("/")] + "\n"
        elif solvable is not None and str(args[0]).endswith("/solvable-issues.sh"):
            code, stdout = solvable(kwargs["env"]["VERI_LABEL"])
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
    at_ten_thousand(monkeypatch)

    code = status.main([])

    assert (code, capsys.readouterr().out) == (0, "#17  lamps glow  tdd/17-lamps  step 1 of 1  red  developer  "
                                                  "develop-red 30s  attempt 1  $0.00  0 tokens  running\n")


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
    at_ten_thousand(monkeypatch)


def two_lamps_solvable(scope):
    return (0, "31\ta lamp dims\n32\ta lamp flickers\n") if scope == "lamps-label" else (3, "")


def last_line(out):
    return out.rstrip("\n").split("\n")[-1]


def test_main_scope_adds_the_scopes_attempted_done_bailed_wall_and_dollars_totals(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, lambda scope: (3, ""))

    code = status.main(["--scope", "lamps-label"])

    assert (code, last_line(capsys.readouterr().out)) == (
        0, "scope lamps-label  attempted 3  done 1  bailed 1  wall 360s  $2.25  solvable 0")


def test_main_with_no_scope_takes_the_scope_from_veri_label_and_adds_the_same_totals(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, lambda scope: (3, ""))
    monkeypatch.setenv("VERI_LABEL", "lamps-label")

    code = status.main([])

    assert (code, last_line(capsys.readouterr().out)) == (
        0, "scope lamps-label  attempted 3  done 1  bailed 1  wall 360s  $2.25  solvable 0")


def test_main_scope_counts_what_solvable_issues_sh_lists_for_that_scope(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, two_lamps_solvable)

    code = status.main(["--scope", "lamps-label"])

    assert (code, last_line(capsys.readouterr().out).endswith("  solvable 2")) == (0, True)


def test_main_json_emits_the_runs_and_scope_totals_as_one_document(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, two_lamps_solvable)

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


def test_main_json_emits_scope_solvable_as_a_number(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, two_lamps_solvable)

    code = status.main(["--json", "--scope", "lamps-label"])
    solvable = json.loads(capsys.readouterr().out)["scope"]["solvable"]

    assert (code, type(solvable), solvable) == (0, int, 2)


def test_main_renders_solvable_as_a_question_mark_when_solvable_issues_sh_gives_no_answer(tmp_path, monkeypatch, capsys, status):
    lamps_scope(tmp_path, monkeypatch, lambda scope: (2, ""))

    text_code = status.main(["--scope", "lamps-label"])
    text = last_line(capsys.readouterr().out)
    json_code = status.main(["--json", "--scope", "lamps-label"])
    solvable = json.loads(capsys.readouterr().out)["scope"]["solvable"]

    assert (text_code, text.endswith("  solvable ?"), json_code, solvable) == (0, True, 0, "?")


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
    fake_git(monkeypatch, tmp_path, {str(run): "tdd/9-cogs-mesh"}, lambda scope: (3, ""))
    at_ten_thousand(monkeypatch)

    text_code = status.main(["--scope", "cogs-label"])
    text = capsys.readouterr().out
    json_code = status.main(["--json", "--scope", "cogs-label"])
    doc = json.loads(capsys.readouterr().out)
    run_obj, scope = doc["runs"][0], doc["scope"]
    figures = (run_obj["leaf"], run_obj["attempts"], run_obj["dollars"], run_obj["tokens"],
               scope["dollars"], scope["wall_seconds"], scope["attempted"])

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


def test_no_case_in_this_suite_calls_a_function_of_veri_status_other_than_main():
    tree = ast.parse(pathlib.Path(__file__).read_text())

    calls = sorted({node.func.attr for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "status"
                    and node.func.attr != "main"})

    assert calls == []

