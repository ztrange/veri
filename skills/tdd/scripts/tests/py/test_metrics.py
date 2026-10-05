"""In-process cases for veri/metrics.py, the module metrics.sh is a shim over."""
import importlib
import json
import pathlib
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
