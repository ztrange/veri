"""In-process cases for veri/metrics.py, the module metrics.sh is a shim over."""
import importlib
import json
import pathlib
import re
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def test_main_refuses_a_missing_or_empty_issue_number_with_its_usage_before_reading_any_tdd_file(tmp_path, monkeypatch, capsys, metrics):
    (tmp_path / ".tdd" / "events.jsonl").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-.md").mkdir()
    monkeypatch.chdir(tmp_path)

    seen = []
    for argv in ([], [""]):
        code = metrics.main(argv)
        out, err = capsys.readouterr()
        seen.append((code, out, err))

    assert seen == [(2, "", "usage: metrics.sh <issue-number>\n")] * 2


def write_log(root, events, raw=""):
    tdd = root / ".tdd"
    tdd.mkdir(exist_ok=True)
    (tdd / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events) + raw)


ONE_STEP = [{"event": "step-start", "step": "1", "ts": 100},
            {"event": "step-done", "step": "1", "ts": 160}]


def render(metrics, capsys, argv=("108",)):
    code = metrics.main(list(argv))
    out, err = capsys.readouterr()
    assert code == 0, err
    return out


def table(out, heading):
    """The rows under <heading>, one dict per row keyed by the header cells."""
    lines = out.split("\n")
    at = lines.index(heading) + 2
    head = [cell.strip() for cell in lines[at].strip("|").split("|")]
    rows = []
    for line in lines[at + 2:]:
        if not line.startswith("|"):
            break
        rows.append(dict(zip(head, (cell.strip() for cell in line[1:-1].split("|")))))
    return rows


def test_main_renders_the_report_for_an_issue_and_ignores_arguments_after_the_first(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP)
    monkeypatch.chdir(tmp_path)

    alone = render(metrics, capsys, ["108"])
    extra = render(metrics, capsys, ["108", "extra"])

    assert alone.startswith("### 📊 Metrics — issue 108\n")
    assert extra == alone


def test_the_planned_count_is_the_number_of_ledger_steps_records_not_of_checkboxes(tmp_path, monkeypatch, capsys, metrics):
    ledger = importlib.import_module("veri.ledger")
    text = ("# Plan\n"
            "  - [X] an indented done step\n"
            "-\t[ ] a tab after the dash\n"
            "* [ ] a star bullet\n"
            "- [y] a box that is neither open nor done\n"
            "text - [ ] a box mid-line\n"
            "- [ ] a plain open step\n")
    write_log(tmp_path, ONE_STEP)
    (tmp_path / ".tdd" / "issue-108.md").write_text(text)
    monkeypatch.chdir(tmp_path)

    out = render(metrics, capsys)

    assert len(ledger.ledger_steps(text)) == 3
    assert "Steps done: 1 of %d planned.\n" % len(ledger.ledger_steps(text)) in out


@pytest.mark.parametrize("ledger", ["no step line", "a directory", "missing"])
def test_the_planned_count_is_unknown_for_a_ledger_with_no_step_line_or_none_readable(tmp_path, monkeypatch, capsys, metrics, ledger):
    write_log(tmp_path, ONE_STEP)
    path = tmp_path / ".tdd" / "issue-108.md"
    if ledger == "no step line":
        path.write_text("# Plan\n\n* [ ] not a step\n")
    elif ledger == "a directory":
        path.mkdir()
    monkeypatch.chdir(tmp_path)

    assert "Steps done: 1 of unknown planned.\n" in render(metrics, capsys)


def test_the_planned_count_drops_nul_bytes_before_reading_the_ledger(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP)
    (tmp_path / ".tdd" / "issue-108.md").write_bytes(b"- \0[ ] a step split by a NUL\n")
    monkeypatch.chdir(tmp_path)

    assert "Steps done: 1 of 1 planned.\n" in render(metrics, capsys)


def test_a_non_utf8_byte_outside_a_step_line_still_renders_the_report(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP)
    (tmp_path / ".tdd" / "issue-108.md").write_bytes(b"# Plan \xff\n- [ ] a step\n")
    monkeypatch.chdir(tmp_path)

    assert "Steps done: 1 of 1 planned.\n" in render(metrics, capsys)


def test_a_non_utf8_byte_in_a_step_line_raises_after_the_header_lines(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP)
    (tmp_path / ".tdd" / "issue-108.md").write_bytes(b"# Plan\n- [ ] a step \xff\n")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnicodeDecodeError):
        metrics.main(["108"])

    out = capsys.readouterr().out
    assert out.startswith("### 📊 Metrics — issue 108\n")
    assert "Steps done:" not in out


def test_the_planned_count_counts_every_line_break_splitlines_finds_in_a_step_text(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP)
    (tmp_path / ".tdd" / "issue-108.md").write_bytes(
        b"- [ ] a\x0bb\n- [ ] c\x1cd\x1ee\n- [ ] f\rg\n")
    monkeypatch.chdir(tmp_path)

    assert "Steps done: 1 of 7 planned.\n" in render(metrics, capsys)


@pytest.mark.parametrize("log, raised", [
    (None, FileNotFoundError),
    ("not json\n", ValueError),
    ("[1, 2]\n", AttributeError),
])
def test_a_missing_or_malformed_log_raises_before_anything_is_printed(tmp_path, monkeypatch, capsys, metrics, log, raised):
    (tmp_path / ".tdd").mkdir()
    if log is not None:
        write_log(tmp_path, ONE_STEP, raw=log)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(raised):
        metrics.main(["108"])

    assert capsys.readouterr().out == ""


def test_a_non_numeric_secs_raises_while_the_log_is_read_before_the_first_line(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "exit", "step": "1", "phase": "red", "attempt": "1",
                                     "status": "0", "secs": "abc"}])
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError):
        metrics.main(["108"])

    assert capsys.readouterr().out == ""


def test_an_exception_after_the_first_line_leaves_the_lines_before_it_on_stdout(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "usage", "step": "1", "phase": "red", "attempt": "1",
                                     "actor": "developer", "model": 5}])
    monkeypatch.chdir(tmp_path)

    with pytest.raises(AttributeError):
        metrics.main(["108"])

    out = capsys.readouterr().out
    assert out.startswith("### 📊 Metrics — issue 108\n")
    assert "Steps done: 1 of unknown planned.\n" in out
    assert "Models requested" not in out


@pytest.mark.parametrize("ending, outcome", [
    ({"event": "done"}, "Outcome: the run landed — its draft PR is unknown.\n"),
    ({"event": "bail"}, "Outcome: the run bailed — unknown, a unknown failure.\n"),
    ({"event": "stop"}, "Outcome: the run was stopped — mode unknown, at unknown.\n"),
])
def test_an_ending_mark_missing_its_keys_prints_unknown_in_their_place(tmp_path, monkeypatch, capsys, metrics, ending, outcome):
    write_log(tmp_path, ONE_STEP + [ending])
    monkeypatch.chdir(tmp_path)

    assert outcome in render(metrics, capsys)


def test_a_resume_after_a_done_keeps_the_run_landed(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "done", "pr": "https://example.test/pr/1"},
                                    {"event": "resume"}])
    monkeypatch.chdir(tmp_path)

    assert "Outcome: the run landed — its draft PR is https://example.test/pr/1.\n" in render(metrics, capsys)


def test_an_exit_whose_status_is_the_integer_2_is_not_counted_as_a_kill(tmp_path, monkeypatch, capsys, metrics):
    attempt = {"step": "1", "phase": "red", "attempt": "1", "secs": "0"}
    write_log(tmp_path, ONE_STEP + [dict(attempt, event="launch"), dict(attempt, event="exit", status=2),
                                    dict(attempt, event="launch", phase="green"),
                                    dict(attempt, event="exit", phase="green", status="2")])
    monkeypatch.chdir(tmp_path)

    phases = {row["phase"]: row["kills"] for row in table(render(metrics, capsys), "#### By phase")}

    assert phases == {"red": "0", "green": "1"}


def test_the_answered_models_are_comma_split_deduplicated_sorted_and_blank_names_dropped(tmp_path, monkeypatch, capsys, metrics):
    usage = {"event": "usage", "step": "1", "phase": "red", "actor": "developer"}
    write_log(tmp_path, ONE_STEP + [dict(usage, attempt="1", model="zeta,alpha"),
                                    dict(usage, attempt="2", model="alpha"),
                                    dict(usage, attempt="3", model=",mid,")])
    monkeypatch.setenv("VERI_MODEL", "")
    monkeypatch.setenv("VERI_MODEL_DEVELOPER", "opus")
    monkeypatch.delenv("VERI_MODEL_VERIFIER", raising=False)
    monkeypatch.chdir(tmp_path)

    assert ("Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER opus, VERI_MODEL_VERIFIER unset; "
            "models that answered: alpha, mid, zeta.\n") in render(metrics, capsys)


def test_a_revise_mark_with_no_budget_prints_a_question_mark_for_it(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "launch", "step": "1", "phase": "red", "attempt": "1"},
                                    {"event": "launch", "step": "2", "phase": "red", "attempt": "1"},
                                    {"event": "revise", "step": "1", "phase": "green"},
                                    {"event": "revise", "step": "2", "phase": "red"},
                                    {"event": "revise", "step": "2", "phase": "green", "budget": "2"}])
    monkeypatch.chdir(tmp_path)

    steps = {row["step"]: row["revise"] for row in table(render(metrics, capsys), "#### By step")}

    assert steps == {"1": "1/?", "2": "red 1/?, green 1/2"}


def test_a_refactor_mark_with_empty_transforms_prints_its_by_step_and_per_pass_cells(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "launch", "step": "1", "phase": "refactor", "attempt": "1"},
                                    {"event": "refactor", "step": "1", "pass": "1", "transforms": "",
                                     "budget": "3", "stopped": "budget"}])
    monkeypatch.chdir(tmp_path)

    out = render(metrics, capsys)

    assert [row["refactor"] for row in table(out, "#### By step")] == ["?/3"]
    assert [row["refactor"] for row in table(out, "#### By refactor pass")] == ["/3"]


def test_test_runs_without_seconds_are_skipped_and_a_run_without_a_tier_lands_in_unknown_padded(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "test-run", "tier": "fast", "seconds": 3},
                                    {"event": "test-run", "tier": "fast", "seconds": ""},
                                    {"event": "test-run", "tier": "fast"},
                                    {"event": "test-run", "tier": "fast", "seconds": 4},
                                    {"event": "test-run", "seconds": 7}])
    monkeypatch.chdir(tmp_path)

    out = render(metrics, capsys)

    assert ("#### Test-command seconds, by tier\n\n"
            "| tier | run 1 s | run 2 s |\n"
            "| --- | ---: | ---: |\n"
            "| fast | 3 | 4 |\n"
            "| unknown | 7 |  |\n") in out


def test_a_structural_pass_mark_with_neither_stopped_nor_transforms_prints_stopped_question_mark(tmp_path, monkeypatch, capsys, metrics):
    write_log(tmp_path, ONE_STEP + [{"event": "structural-pass"}])
    monkeypatch.chdir(tmp_path)

    assert "#### Structural pass\n\nStopped: ?\n" in render(metrics, capsys)


def test_two_main_calls_in_one_process_render_independent_reports(tmp_path, monkeypatch, capsys, metrics):
    one, many = tmp_path / "one", tmp_path / "many"
    attempt = {"step": "1", "phase": "red", "attempt": "1", "secs": "5"}
    for root, launches in ((one, 1), (many, 3)):
        root.mkdir()
        write_log(root, ONE_STEP + [dict(attempt, event="launch"), dict(attempt, event="exit", status="0")] * launches
                  + [{"event": "done", "pr": "p"}])

    monkeypatch.chdir(one)
    first = render(metrics, capsys)
    monkeypatch.chdir(many)
    render(metrics, capsys)
    monkeypatch.chdir(one)
    again = render(metrics, capsys)

    assert again == first
    assert [row["attempts"] for row in table(first, "#### By phase")] == ["1"]


def leaf(step, ts, actor, phase, attempt, secs, status="0", usage=None, verdict=None, retries=0):
    mark = {"issue": "108", "actor": actor, "phase": phase, "step": step, "attempt": str(attempt)}
    events = [dict(mark, ts=ts, event="launch", name="%s-%s" % (actor, phase))]
    events += [dict(mark, ts=ts + i + 1, event="retry", cause="no heartbeat") for i in range(retries)]
    events.append(dict(mark, ts=ts + secs, event="exit", status=status, secs=str(secs)))
    if usage is not None:
        events.append(dict(mark, ts=ts + secs, event="usage", **usage))
    if verdict is not None:
        events.append(dict(mark, ts=ts + secs, event="verdict", verdict=verdict))
    return events


def conductor(step, ts, event, phase="", **fields):
    return [{"ts": ts, "issue": "108", "actor": "conductor", "phase": phase, "step": step, "event": event,
             "attempt": "", **fields}]


def cost(turns, dollars, tokens, api_ms="0"):
    return dict(zip(["input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"],
                    map(str, tokens)),
                duration_ms="0", duration_api_ms=str(api_ms), num_turns=str(turns), total_cost_usd=dollars)


def cells(out, heading, columns):
    rows = table(out, heading)
    key = next(iter(rows[0]))
    return {row[key]: [row[c] for c in columns] for row in rows}


def test_main_reports_counts_budgets_times_costs_rework_and_waste_per_phase_and_step(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    COUNTS = ["attempts", "PASS", "REJECT", "kills"]
    COSTS = ["turns", "input", "output", "cache read", "cache creation", "$"]
    LOST = ["rework wall s", "rework $", "waste wall s", "waste $"]

    phases = report("phases", conductor("s", 990, "step-start")
                    + leaf("s", 1000, "developer", "red", 1, 100) + leaf("s", 1110, "verifier", "red", 1, 20, verdict="PASS")
                    + leaf("s", 1200, "developer", "green", 1, 100) + leaf("s", 1310, "verifier", "green", 1, 20, verdict="REJECT")
                    + leaf("s", 1340, "developer", "green", 2, 60) + leaf("s", 1410, "verifier", "green", 2, 20, verdict="REJECT")
                    + leaf("s", 1440, "developer", "green", 3, 60, status="2") + leaf("s", 1510, "developer", "green", 3, 60, status="2")
                    + leaf("s", 1580, "developer", "green", 3, 60, status="2") + leaf("s", 1650, "developer", "green", 3, 50)
                    + leaf("s", 1710, "verifier", "green", 3, 20, verdict="PASS") + conductor("s", 1740, "step-done"))
    assert cells(phases, "#### By phase", COUNTS) == {"red": ["2", "1", "0", "0"], "green": ["9", "1", "2", "3"]}

    steps = report("steps", conductor("one", 2000, "step-start")
                   + leaf("one", 2010, "developer", "red", 1, 90) + leaf("one", 2110, "verifier", "red", 1, 20, verdict="PASS")
                   + leaf("one", 2200, "developer", "green", 1, 100) + leaf("one", 2310, "verifier", "green", 1, 20, verdict="PASS")
                   + conductor("one", 2340, "step-done") + conductor("two", 2400, "step-start")
                   + leaf("two", 2410, "developer", "red", 1, 90) + leaf("two", 2510, "verifier", "red", 1, 20, verdict="PASS")
                   + leaf("two", 2600, "developer", "green", 1, 100) + leaf("two", 2710, "verifier", "green", 1, 20, verdict="REJECT")
                   + leaf("two", 2740, "developer", "green", 2, 120, status="2", retries=1)
                   + leaf("two", 2870, "developer", "green", 2, 180, status="2", retries=2)
                   + leaf("two", 3060, "developer", "green", 2, 120, status="2", retries=1)
                   + leaf("two", 3190, "developer", "green", 2, 60) + leaf("two", 3260, "verifier", "green", 2, 20, verdict="REJECT"))
    assert cells(steps, "#### By step", COUNTS + ["retries"]) == {
        "one": ["4", "2", "0", "0", "0"], "two": ["9", "1", "2", "3", "4"]}

    def budgeted(step, ts, revises, transforms, stopped):
        events = conductor(step, ts, "step-start") + leaf(step, ts + 10, "developer", "red", 1, 90)
        events += leaf(step, ts + 110, "verifier", "red", 1, 20, verdict="PASS")
        for attempt in range(1, revises + 2):
            at = ts + 100 * attempt + 100
            events += leaf(step, at, "developer", "green", attempt, 60)
            events += leaf(step, at + 70, "verifier", "green", attempt, 20,
                           verdict="PASS" if attempt == revises + 1 else "REJECT")
            if attempt <= revises:
                events += conductor(step, at + 90, "revise", phase="green", attempt=str(attempt), budget="3")
        at = ts + 100 * revises + 300
        events += leaf(step, at, "developer", "refactor", 1, 150)
        events += conductor(step, at + 160, "refactor", phase="refactor", transforms=transforms, budget="5", stopped=stopped)
        events += leaf(step, at + 170, "verifier", "refactor", 1, 20, verdict="PASS")
        return events + conductor(step, at + 200, "step-done")

    budgets = report("budgets", budgeted("frugal", 4000, 1, "2", "nothing left to tidy")
                     + budgeted("spendthrift", 5000, 3, "5", "budget"))
    assert cells(budgets, "#### By step", ["revise", "refactor", "stopped"]) == {
        "frugal": ["1/3", "2/5", "nothing left to tidy"], "spendthrift": ["3/3", "5/5", "budget"]}

    def api(ms):
        return cost(9, "0.5", (1000, 2000, 3000, 4000), api_ms=ms)

    times = report("times", conductor("brisk", 7000, "step-start")
                   + leaf("brisk", 7010, "developer", "red", 1, 90, usage=api(70000))
                   + leaf("brisk", 7110, "verifier", "red", 1, 20, usage=api(15000), verdict="PASS")
                   + leaf("brisk", 7200, "developer", "green", 1, 100, usage=api(80000))
                   + leaf("brisk", 7310, "verifier", "green", 1, 20, usage=api(10000), verdict="PASS")
                   + conductor("brisk", 7400, "step-done") + conductor("slow", 8000, "step-start")
                   + leaf("slow", 8010, "developer", "red", 1, 80, usage=api(60000))
                   + leaf("slow", 8110, "verifier", "red", 1, 20, usage=api(10000), verdict="PASS")
                   + leaf("slow", 8200, "developer", "green", 1, 100, usage=api(85000))
                   + leaf("slow", 8310, "verifier", "green", 1, 20, usage=api(10000), verdict="REJECT")
                   + conductor("slow", 8340, "revise", phase="green", attempt="1", budget="3")
                   + leaf("slow", 8350, "developer", "green", 2, 70, status="2")
                   + leaf("slow", 8430, "developer", "green", 2, 60, usage=api(45000))
                   + leaf("slow", 8500, "verifier", "green", 2, 20, usage=api(10000), verdict="PASS")
                   + conductor("slow", 8600, "step-done") + conductor("slow", 8700, "done", pr="https://example.test/pr/999"))
    assert cells(times, "#### By phase", ["wall s", "API s"]) == {"red": ["210", "155"], "green": ["390", "240"]}
    assert cells(times, "#### By step", ["wall s", "API s"]) == {"brisk": ["400", "175"], "slow": ["600", "220"]}
    assert "Wall time for the issue: 1700 s," in times

    def priced(step, ts, red, verify_red, green, verify_green):
        return (conductor(step, ts, "step-start")
                + leaf(step, ts + 10, "developer", "red", 1, 90, usage=cost(*red))
                + leaf(step, ts + 110, "verifier", "red", 1, 20, usage=cost(*verify_red), verdict="PASS")
                + leaf(step, ts + 200, "developer", "green", 1, 100, usage=cost(*green))
                + leaf(step, ts + 310, "verifier", "green", 1, 20, usage=cost(*verify_green), verdict="PASS")
                + conductor(step, ts + 400, "step-done"))

    costs = report("costs", priced("cheap", 9000, (3, "0.10", (100, 200, 1000, 400)), (2, "0.05", (50, 30, 500, 100)),
                                   (7, "0.40", (300, 600, 4000, 900)), (4, "0.20", (120, 70, 900, 300)))
                   + priced("dear", 9500, (6, "0.25", (210, 340, 2200, 600)), (2, "0.05", (40, 60, 700, 200)),
                            (9, "0.55", (500, 800, 6000, 1500)), (3, "0.15", (90, 110, 1100, 400)))
                   + conductor("dear", 9910, "done", pr="https://example.test/pr/999"))
    assert cells(costs, "#### By phase", COSTS) == {
        "red": ["13", "400", "630", "4400", "1300", "0.45"], "green": ["23", "1010", "1580", "12000", "3100", "1.30"]}
    assert cells(costs, "#### By step", COSTS) == {
        "cheap": ["16", "570", "900", "6400", "1700", "0.75"], "dear": ["20", "840", "1310", "10000", "2700", "1.00"]}
    assert cells(costs, "#### Total", COSTS) == {"total": ["36", "1410", "2210", "16400", "4400", "1.75"]}
    assert ("Cost is every leaf of the run, and the conductor own spending is not in it: "
            "this log carries no usage record of the conductor own.\n") in costs

    counted = report("counted", conductor("one", 9000, "step-start")
                     + leaf("one", 9010, "developer", "red", 1, 90, usage=cost(3, "0.10", (100, 200, 1000, 400)))
                     + conductor("one", 9110, "step-done")
                     + [dict(conductor("", 9200, "usage")[0], **cost(12, "0.90", (800, 400, 20000, 2500)))])
    assert ("Cost is every leaf of the run, and the conductor own closing accounting with them, "
            "which this log carries.\n") in counted

    def reworked(step, ts, red, verify_red, green):
        events = (conductor(step, ts, "step-start")
                  + leaf(step, ts + 10, "developer", "red", 1, red[0], usage=cost(3, red[1], (1, 1, 1, 1)))
                  + leaf(step, ts + 50, "verifier", "red", 1, verify_red[0], usage=cost(2, verify_red[1], (1, 1, 1, 1)),
                         verdict="PASS"))
        for attempt, (secs, dollars, verify_secs, verify_dollars, verdict) in enumerate(green, 1):
            at = ts + 100 * attempt
            events += leaf(step, at, "developer", "green", attempt, secs, usage=cost(5, dollars, (1, 1, 1, 1)))
            events += leaf(step, at + secs, "verifier", "green", attempt, verify_secs,
                           usage=cost(2, verify_dollars, (1, 1, 1, 1)), verdict=verdict)
            if verdict == "REJECT":
                events += conductor(step, at + secs + verify_secs, "revise", phase="green", attempt=str(attempt), budget="3")
        return events

    rework = report("rework", reworked("unrejected", 100, (90, "0.11"), (20, "0.07"), [(80, "0.22", 10, "0.13", "PASS")])
                    + conductor("unrejected", 400, "step-done")
                    + reworked("recovered", 500, (30, "0.03"), (10, "0.02"),
                               [(100, "0.40", 20, "0.10", "REJECT"), (60, "0.24", 20, "0.06", "PASS")])
                    + conductor("recovered", 900, "step-done") + conductor("recovered", 910, "done", pr="p"))
    assert cells(rework, "#### Rework and waste, by phase", LOST) == {
        "red": ["0", "0.00", "0", "0.00"], "green": ["120", "0.50", "0", "0.00"]}

    bail = report("bail", reworked("landed", 7000, (30, "0.03"), (10, "0.02"), [(40, "0.05", 10, "0.01", "PASS")])
                  + conductor("landed", 7200, "step-done")
                  + reworked("bailed", 7300, (100, "0.40"), (20, "0.10"),
                             [(60, "0.20", 20, "0.05", "REJECT"), (50, "0.10", 10, "0.05", "REJECT")])
                  + conductor("bailed", 7700, "bail", phase="green", cause="revise-budget", classification="process"))
    assert cells(bail, "#### Rework and waste, by phase", LOST) == {
        "red": ["0", "0.00", "120", "0.50"], "green": ["0", "0.00", "140", "0.40"]}


def test_main_reports_steps_done_of_planned_the_outcome_and_the_issue_wall_summed_over_a_resumed_run(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events, done, pending=()):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        (root / ".tdd" / "issue-108.md").write_text(
            "".join("- [x] %s\n" % step for step in done) + "".join("- [ ] %s\n" % step for step in pending))
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    def ran(step, ts, gap=100):
        return conductor(step, ts, "step-start") + conductor(step, ts + gap, "step-done")

    resumed_wall = "Wall time for the issue: 200 s, from the last `resume`"
    first_event_wall = "Wall time for the issue: 250 s, from the last `resume`, or the first event of the log"

    system = report("system", ran("a", 11000) + conductor("b", 11200, "step-start")
                    + conductor("b", 11300, "bail", phase="green", cause="killed-stuck", classification="system"),
                    ["a"], ["b", "c"])
    assert "Steps done: 1 of 3 planned." in system
    assert "Outcome: the run bailed — killed-stuck, a system failure." in system

    process = report("process", ran("a", 12000) + ran("b", 12200) + conductor("c", 12400, "step-start")
                     + conductor("c", 12500, "bail", phase="green", cause="revise-exhausted", classification="process"),
                     ["a", "b"], ["c", "d"])
    assert "Steps done: 2 of 4 planned." in process
    assert "Outcome: the run bailed — revise-exhausted, a process failure." in process

    landed = report("landed", ran("a", 13000) + ran("b", 13200)
                    + conductor("b", 13400, "done", pr="https://github.com/ztrange/veri/pull/999"), ["a", "b"])
    assert "Steps done: 2 of 2 planned." in landed
    assert "Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/999." in landed
    assert "Wall time for the issue: 400 s," in landed

    unmarked = report("unmarked", leaf("a", 14000, "developer", "red", 1, 100)
                      + leaf("a", 14110, "verifier", "red", 1, 20, verdict="PASS"), [], ["a", "b"])
    assert "Steps done: unknown of 2 planned." in unmarked

    pinned = report("pinned", ran("a", 15000) + conductor("b", 15200, "step-start") + conductor("b", 15300, "pin", phase="pin"),
                    ["a", "b"])
    assert "Steps done: 2 of 2 planned." in pinned

    two_pins = report("two_pins", conductor("a", 16000, "step-start") + conductor("a", 16100, "pin", phase="pin")
                      + conductor("b", 16200, "step-start") + conductor("b", 16300, "pin", phase="pin") + ran("c", 16400),
                      ["a", "b", "c"])
    assert "Steps done: 3 of 3 planned." in two_pins

    unpinned = report("unpinned", ran("a", 17000) + ran("b", 17200) + conductor("c", 17400, "step-start")
                      + leaf("c", 17500, "developer", "red", 1, 10)[:1], ["a", "b"], ["c"])
    assert "Steps done: 2 of 3 planned." in unpinned

    rerun = report("rerun", conductor("a", 18000, "step-start")
                   + conductor("a", 18100, "bail", cause="poisoned-baseline", classification="system")
                   + conductor("a", 18200, "resume") + conductor("a", 18300, "step-done")
                   + conductor("a", 18400, "done", pr="https://github.com/ztrange/veri/pull/998"), ["a"])
    assert "Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/998." in rerun
    assert "bail" not in rerun.split("Outcome:")[1].split("\n")[0]
    assert resumed_wall in rerun

    single = report("single", ran("a", 19000, gap=150)
                    + conductor("a", 19250, "bail", phase="green", cause="killed-stuck", classification="system"), ["a"])
    assert first_event_wall in single
    assert "Outcome: the run bailed — killed-stuck, a system failure." in single

    accrued = report("accrued", conductor("a", 20000, "step-start")
                     + leaf("a", 20010, "developer", "red", 1, 100, usage=cost(3, "0.25", (100, 200, 300, 400)))
                     + leaf("a", 20120, "verifier", "red", 1, 20, usage=cost(2, "0.10", (10, 20, 30, 40)), verdict="REJECT")
                     + conductor("a", 20200, "bail", cause="poisoned-baseline", classification="system")
                     + conductor("a", 20300, "resume")
                     + leaf("a", 20310, "developer", "red", 2, 60, usage=cost(4, "0.40", (1000, 2000, 3000, 4000)))
                     + leaf("a", 20380, "verifier", "red", 2, 30, usage=cost(1, "0.05", (1, 2, 3, 4)), verdict="PASS")
                     + conductor("a", 20500, "step-done")
                     + conductor("a", 20600, "done", pr="https://github.com/ztrange/veri/pull/997"), ["a"])
    assert cells(accrued, "#### By phase", ["attempts", "PASS", "REJECT", "kills", "wall s"]) == {
        "red": ["4", "1", "1", "0", "210"]}
    assert cells(accrued, "#### By phase", ["turns", "input", "output", "cache read", "cache creation", "$"]) == {
        "red": ["10", "1111", "2222", "3333", "4444", "0.80"]}
    assert cells(accrued, "#### Total", ["turns", "input", "output", "cache read", "cache creation", "$"]) == {
        "total": ["10", "1111", "2222", "3333", "4444", "0.80"]}


def test_main_reports_relaunches_triage_stops_budget_crossings_splits_tier_seconds_and_stop_outcomes(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    def relaunch(ts):
        return [dict(leaf("s", ts, "verifier", "green", 1, 20)[1], event="relaunch", cause="no-verdict")]

    relaunched = report("relaunched", conductor("s", 30000, "step-start")
                        + leaf("s", 30010, "developer", "green", 1, 90)
                        + leaf("s", 30110, "verifier", "green", 1, 20) + relaunch(30110)
                        + leaf("s", 30140, "verifier", "green", 1, 20) + relaunch(30140)
                        + leaf("s", 30170, "verifier", "green", 1, 20, verdict="REJECT")
                        + conductor("s", 30200, "revise", phase="green", attempt="1", budget="3")
                        + leaf("s", 30210, "developer", "green", 2, 120, retries=1)
                        + leaf("s", 30340, "verifier", "green", 2, 20, verdict="PASS")
                        + conductor("s", 30370, "step-done"))
    assert cells(relaunched, "#### By step", ["attempts", "PASS", "REJECT", "kills", "retries", "no-verdict"]) == {"s": ["6", "1", "1", "0", "1", "2"]}

    def triaged(step, ts, transforms, stopped):
        return (conductor(step, ts, "step-start") + leaf(step, ts + 2, "developer", "refactor", 1, 6)
                + conductor(step, ts + 10, "refactor", phase="refactor", transforms=transforms, budget="5", stopped=stopped)
                + conductor(step, ts + 20, "step-done"))

    triage = report("triage", triaged("tidied", 40000, "1", "nothing-structural")
                    + triaged("owing", 41000, "3", "structural-owed"))
    assert cells(triage, "#### By step", ["stopped"]) == {"tidied": ["nothing-structural"], "owing": ["structural-owed"]}

    def worked(step, ts, *marks):
        return conductor(step, ts, "step-start") + leaf(step, ts + 2, "developer", "green", 1, 6) + list(marks)

    crossing = report("crossing", worked("crossed", 42000, *conductor("crossed", 42010, "step-over-budget",
                                                                      spent="12.40", budget="10.00"))
                      + conductor("crossed", 42020, "step-done")
                      + worked("under", 43000) + conductor("under", 43020, "step-done"))
    assert cells(crossing, "#### By step", ["crossed at"]) == {"crossed": ["12.40"], "under": [""]}

    exhausted = report("exhausted", worked("split", 44000, *conductor("split", 44010, "step-split", at="exhausted")))
    over = report("over", worked("split", 44000, *conductor("split", 44010, "step-split", at="over-budget")))
    assert exhausted != over
    assert cells(exhausted, "#### By step", ["split"]) == {"split": ["exhausted"]}
    assert cells(over, "#### By step", ["split"]) == {"split": ["over-budget"]}

    def ran_tests(step, ts, actor, *runs):
        return [dict(conductor(step, ts + i, "test-run")[0], actor=actor, phase="green", attempt="1",
                     tier=tier, suites="metrics.test.sh", seconds=seconds) for i, (tier, seconds) in enumerate(runs)]

    tiers = report("tiers", conductor("t", 50000, "step-start")
                   + ran_tests("t", 50010, "developer", ("fast", "4"), ("all", "120"))
                   + ran_tests("t", 50050, "verifier", ("fast", "6"), ("all", "100"), ("fast", "5"), ("all", "140"))
                   + conductor("t", 50950, "step-done"))
    assert cells(tiers, "#### Test-command seconds, by tier", ["run 1 s", "run 2 s", "run 3 s"]) == {
        "fast": ["4", "6", "5"], "all": ["120", "100", "140"]}

    stopped = report("stopped", conductor("h", 60000, "step-start") + conductor("h", 60200, "step-done")
                     + conductor("h", 60340, "stop", phase="green", mode="at-ledger", at="green"))
    assert "Outcome: the run was stopped — mode at-ledger, at green." in stopped
    assert "Wall time for the issue: 340 s," in stopped

    resumed = report("resumed", conductor("r", 70000, "step-start")
                     + conductor("r", 70100, "stop", phase="red", mode="at-leaf", at="red")
                     + conductor("r", 70200, "resume") + conductor("r", 70300, "step-start"))
    outcome = [line for line in resumed.split("\n") if line.startswith("Outcome:")]
    assert outcome == ["Outcome: unknown — the log carries no mark ending the run."]


def test_main_reads_walls_off_the_awake_clock_and_falls_back_to_the_wall_clock_saying_so(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    def run(ts_awake, attempts=(), done=True):
        (start, start_awake), *rest = ts_awake
        events = conductor("s", start, "step-start")
        if start_awake is not None:
            events[0]["awake"] = start_awake
        for (ts, awake, phase_event, fields) in attempts:
            event = {"ts": ts, "issue": "108", "actor": "developer", "phase": "red", "step": "s",
                     "event": phase_event, **fields}
            if awake is not None:
                event["awake"] = awake
            events.append(event)
        for (ts, awake), kind in zip(rest, ["step-done", "done"] if done else ["step-done"]):
            extra = {"pr": "https://github.com/ztrange/veri/pull/998"} if kind == "done" else {}
            events += conductor("s", ts, kind, **extra)
            if awake is not None:
                events[-1]["awake"] = awake
        return events

    def line(out, prefix):
        found = [l for l in out.split("\n") if l.startswith(prefix)]
        return found[0][len(prefix):].split(" s", 1)[0] if found else None

    def walls(out):
        return (line(out, "Wall time for the issue: "),
                cells(out, "#### By step", ["wall s"]).get("s", [None])[0],
                {row["phase"]: row["wall s"] for row in table(out, "#### By phase")})

    def wall_clock(out):
        return "Every figure in this report is wall-clock" in out

    not_running = "Seconds the machine was not running inside that span: "

    slept = report("slept", run([(80000, 5000), (80100, 5100), (90217, 5217)]))
    assert line(slept, "Wall time for the issue: ") == "217"
    assert line(slept, not_running) == "10000"

    level = report("level", run([(70000, 4000), (70100, 4100), (70217, 4217)]))
    assert line(level, not_running) == "0"

    ahead = report("ahead", run([(70000, 4000), (70100, 4100), (70217, 4218)]))
    assert line(ahead, not_running) == "0"
    assert int(line(ahead, "Wall time for the issue: ")) <= 217

    step_slept = report("step_slept", run([(60000, 3000), (70100, 3100), (70150, 3150)], attempts=[
        (60010, 3010, "launch", {"attempt": "1", "name": "develop-red"}),
        (70050, 3050, "exit", {"attempt": "1", "status": "0", "secs": "40"})]))
    assert walls(step_slept)[1] == "100"
    assert not wall_clock(step_slept)

    phase_slept = report("phase_slept", run([(50000, 2000), (60100, 2100), (60150, 2150)], attempts=[
        (50010, 2010, "launch", {"attempt": "1", "name": "develop-red"}),
        (60050, 2050, "exit", {"attempt": "1", "status": "0", "secs": "10040"})]))
    assert walls(phase_slept)[2] == {"red": "40"}

    unclocked = report("unclocked", run([(40000, None), (40100, None), (40150, None)], attempts=[
        (40010, None, "launch", {"attempt": "1", "name": "develop-red"}),
        (40050, None, "exit", {"attempt": "1", "status": "0", "secs": "40"})]))
    assert walls(unclocked) == ("150", "100", {"red": "40"})
    assert wall_clock(unclocked)

    mixed = report("mixed", run([(30000, None), (40100, 1100), (40150, 1150)], attempts=[
        (30010, None, "launch", {"attempt": "1", "name": "develop-red"}),
        (30040, None, "exit", {"attempt": "1", "status": "2", "cause": "no heartbeat for 300s (window 120s)", "secs": "30"}),
        (30050, 1050, "launch", {"attempt": "2", "name": "develop-red"}),
        (40090, 1090, "exit", {"attempt": "2", "status": "0", "secs": "10040"})]))
    assert walls(mixed) == ("10150", "10100", {"red": "10070"})
    assert wall_clock(mixed)

    empty = report("empty", [])
    assert wall_clock(empty)


def test_main_renders_per_phase_revise_cells_the_by_step_kind_and_the_note_naming_turns_dollars_and_the_model_knobs(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    def revise(step, ts, phase, attempt, budget):
        return conductor(step, ts, "revise", phase, attempt=str(attempt), budget=budget)

    def red_launch(step, ts):
        return leaf(step, ts, "developer", "red", 1, 5)[:1]

    def revise_cells(out):
        return cells(out, "#### By step", ["revise"])

    def entries(cell):
        return set(re.findall(r"([a-z]+) ([0-9]+)/([0-9?]+)", cell))

    phased = report("phased", conductor("p", 9000, "step-start") + red_launch("p", 9010)
                    + revise("p", 9100, "red", 1, "3") + revise("p", 9200, "red", 2, "3")
                    + revise("p", 9300, "refactor", 1, "3") + conductor("p", 9400, "step-done"))
    assert entries(revise_cells(phased)["p"][0]) == {("red", "2", "3"), ("refactor", "1", "3")}

    twice = report("twice", conductor("t", 9500, "step-start") + red_launch("t", 9510)
                   + revise("t", 9600, "red", 1, "2") + revise("t", 9700, "refactor", 1, "2")
                   + conductor("t", 9800, "step-done"))
    assert entries(revise_cells(twice)["t"][0]) == {("red", "1", "2"), ("refactor", "1", "2")}

    spent = report("spent", conductor("s", 9900, "step-start") + red_launch("s", 9910)
                   + revise("s", 9920, "red", 1, "2") + revise("s", 9930, "red", 2, "2")
                   + conductor("s", 9940, "step-done"))
    assert re.fullmatch(r"(red )?2/2", revise_cells(spent)["s"][0])

    unrevised = report("unrevised", conductor("u", 10000, "step-start") + red_launch("u", 10010)
                       + conductor("u", 10020, "step-done"))
    assert revise_cells(unrevised)["u"] == ["unknown"]

    def full_step(step, t):
        events = conductor(step, t, "step-start")
        for i, phase in enumerate(["red", "green", "refactor"]):
            events += leaf(step, t + 10 + 30 * i, "developer", phase, 1, 5)[:1]
            events += leaf(step, t + 20 + 30 * i, "verifier", phase, 1, 10, verdict="PASS")
        return events + conductor(step, t + 100, "step-done")

    def satisfied_red(step, t, rejects=0):
        events = conductor(step, t, "step-start")
        for attempt in range(1, rejects + 1):
            events += leaf(step, t + 30 * attempt, "verifier", "red", attempt, 0, verdict="REJECT")[-1:]
        events += leaf(step, t + 70, "verifier", "pin", 1, 0, verdict="PASS")[-1:]
        return events

    def kinds(out):
        return {step: cell for step, [cell] in cells(out, "#### By step", ["kind"]).items()}

    pinned = report("pinned", full_step("full", 18000) + satisfied_red("pinned", 18200)
                    + conductor("pinned", 18240, "pin", "pin"))
    assert kinds(pinned) == {"full": "full", "pinned": "pin"}

    satisfied = report("satisfied", full_step("full", 19000) + satisfied_red("satisfied", 19200))
    assert kinds(satisfied) == {"full": "full", "satisfied": "already-satisfied"}

    leafcount = report("leafcount", satisfied_red("many-pin", 20000, rejects=2)
                       + conductor("many-pin", 20090, "pin", "pin")
                       + satisfied_red("many-sat", 20100, rejects=2)
                       + conductor("two-leaf", 20200, "step-start")
                       + leaf("two-leaf", 20210, "developer", "green", 1, 5)[:1]
                       + leaf("two-leaf", 20220, "verifier", "green", 1, 10, verdict="PASS")
                       + conductor("two-leaf", 20240, "step-done"))
    assert kinds(leafcount) == {"many-pin": "pin", "many-sat": "already-satisfied", "two-leaf": "full"}

    all_full = report("all_full", full_step("first", 21000) + full_step("second", 21200))
    assert kinds(all_full) == {"first": "full", "second": "full"}

    lines = all_full.split("\n")
    at = lines.index("#### By step") + 1
    while not lines[at].startswith("|"):
        at += 1
    while lines[at].startswith("|"):
        at += 1
    note = next(line for line in lines[at:] if line.strip())
    assert not note.startswith("#")
    for word in ("turns", "dollars", "comparable", "VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER"):
        assert word in note
