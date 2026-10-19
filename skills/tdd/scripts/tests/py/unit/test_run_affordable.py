"""Cases for veri/run_affordable.py, the module run-affordable.sh is a shim over, run against the real siblings.

Each case sets VERI_STEP_BUDGET and VERI_RUN_BUDGET in its environment and writes .tdd/events.jsonl in its own scratch tree.
"""
import importlib
import io
import os
import sys

import pytest


@pytest.fixture
def run_affordable():
    return importlib.import_module("veri.run_affordable")


@pytest.fixture
def scratch(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
    monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
    return tmp_path


def _log(scratch, steps):
    """Write a usage event log in which each '<dollars> <leaves>' line of <steps> is one step."""
    lines = []
    for number, line in enumerate(steps.splitlines()):
        dollars, leaves = line.split()
        for leaf in range(int(leaves)):
            lines.append('{"ts": 1, "event": "usage", "step": "step %d", "total_cost_usd": "%s"}\n'
                         % (number, dollars if leaf == 0 else "0"))
    (scratch / ".tdd" / "events.jsonl").write_text("".join(lines))


def _answer(run_affordable, capsys, scratch, monkeypatch, remaining, ceiling, steps):
    _log(scratch, steps)
    monkeypatch.setenv("VERI_RUN_BUDGET", ceiling)
    code = run_affordable.main([remaining])
    out, err = capsys.readouterr()
    return (code, out, err)


def test_main_refuses_a_bad_argument_with_2_and_answers_1_or_3_from_the_siblings(capsys, monkeypatch, scratch, run_affordable):
    usage = "usage: run-affordable.sh <steps-remaining> (a whole number)\n"
    monkeypatch.setenv("VERI_RUN_BUDGET", "50")
    for argv, shown in (([], ""), ([""], ""), (["two"], "two")):
        code = run_affordable.main(argv)
        out, err = capsys.readouterr()
        assert (argv, code, out, err) == (
            argv, 2, "",
            "run-affordable.sh: <steps-remaining> is not a whole number: '%s'\n" % shown + usage,
        )

    seen = _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", "5.25 6\n7.50 6\n9.75 6\n")
    assert seen == (1, "spent 22.50, steps remaining 4, median 7.50, projection 52.50\n", "")

    seen = _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", "100.00 2\n100.00 2\n")
    assert seen == (3, "", "")


def test_main_passes_the_exit_statuses_of_the_budget_and_the_log_through(capsys, monkeypatch, scratch, run_affordable):
    steps = "5.25 6\n7.50 6\n9.75 6\n"
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "60", steps) == (0, "", "")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", steps)[:2] == (
        1, "spent 22.50, steps remaining 4, median 7.50, projection 52.50\n")

    monkeypatch.setenv("VERI_STEP_BUDGET", "many")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", steps)[:2] == (2, "")
    monkeypatch.delenv("VERI_STEP_BUDGET")

    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "fifty", steps)[:2] == (2, "")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", "1.00 2\n1.00 1\n")[:2] == (3, "")

    (scratch / ".tdd" / "events.jsonl").unlink()
    code = run_affordable.main(["4"])
    out, _ = capsys.readouterr()
    assert (code, out) == (2, "")


def test_main_answers_in_full_when_starting_any_process_is_refused(capsys, monkeypatch, scratch, run_affordable):
    import subprocess

    def refuse_start(self, argv, *args, **kwargs):
        raise OSError("start refused: %s" % (argv,))

    monkeypatch.setattr(subprocess.Popen, "__init__", refuse_start)
    steps = "5.25 6\n7.50 6\n9.75 6\n"
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", steps) == (
        1, "spent 22.50, steps remaining 4, median 7.50, projection 52.50\n", "")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "60", steps) == (0, "", "")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", "100.00 2\n") == (3, "", "")
    monkeypatch.setenv("VERI_STEP_BUDGET", "many")
    assert _answer(run_affordable, capsys, scratch, monkeypatch, "4", "50", steps)[:2] == (2, "")


def test_main_reads_steps_remaining_first_refusing_all_but_whole_numbers_and_echoing_them_byte_for_byte(monkeypatch, scratch, run_affordable):
    usage = b"usage: run-affordable.sh <steps-remaining> (a whole number)\n"
    monkeypatch.setenv("VERI_RUN_BUDGET", "fifty")
    _log(scratch, "5.25 6\n7.50 6\n9.75 6\n")

    def run(argv):
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors="backslashreplace",
                                                            write_through=True))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding="utf-8", errors="backslashreplace",
                                                            write_through=True))
        code = run_affordable.main(argv)
        sys.stdout.flush()
        sys.stderr.flush()
        return (code, out.getvalue(), err.getvalue())

    bad = {" 3": b" 3", "--": b"--", "1.5": b"1.5", "-1": b"-1", "3\n": b"3\n", os.fsdecode(b"\xff"): b"\xff"}
    seen = {arg: run([arg]) for arg in bad}
    wanted = {arg: (2, b"", b"run-affordable.sh: <steps-remaining> is not a whole number: '" + shown + b"'\n" + usage)
              for arg, shown in bad.items()}
    assert seen == wanted

    monkeypatch.setenv("VERI_RUN_BUDGET", "40")
    seen = {"007": run(["007"]), "3 extra": run(["3", "extra"]), "3": run(["3"])}
    assert seen == {
        "007": (1, b"spent 22.50, steps remaining 7, median 7.50, projection 75.00\n", b""),
        "3 extra": (1, b"spent 22.50, steps remaining 3, median 7.50, projection 45.00\n", b""),
        "3": (1, b"spent 22.50, steps remaining 3, median 7.50, projection 45.00\n", b""),
    }


def test_main_projects_from_the_median_full_step_counting_every_step_toward_spent_and_comparing_strictly(capsys, monkeypatch, scratch, run_affordable):
    def run(remaining, ceiling, steps):
        return _answer(run_affordable, capsys, scratch, monkeypatch, remaining, ceiling, steps)

    seen = {
        "odd": run("1", "0", "5.00 6\n1.00 6\n2.00 2\n3.00 3\n"),
        "even": run("2", "0", "3.00 6\n1.00 6\n2.00 2\n4.00 6\n2.00 6\n"),
        "pins only": run("4", "1", "100 2\n100 2\n"),
        "at the ceiling": run("0", "9", "9.00 6\n"),
        "over the ceiling": run("0", "8.98", "8.99 6\n"),
    }
    assert seen == {
        "odd": (1, "spent 11.00, steps remaining 1, median 3.00, projection 14.00\n", ""),
        "even": (1, "spent 12.00, steps remaining 2, median 2.50, projection 17.00\n", ""),
        "pins only": (3, "", ""),
        "at the ceiling": (0, "", ""),
        "over the ceiling": (1, "spent 8.99, steps remaining 0, median 8.99, projection 8.99\n", ""),
    }


def test_main_sums_in_sort_order_formats_unlocalised_wraps_the_count_and_returns_2_when_stdout_is_closed(capsys, monkeypatch, scratch, run_affordable):
    def run(remaining, ceiling, steps):
        return _answer(run_affordable, capsys, scratch, monkeypatch, remaining, ceiling, steps)

    seen = {"sort order": run("0", "0", "62867166030098.60 6\n0.08 2\n0.69 2\n"),
            "half-cent median": run("1", "0", "1.02 6\n1.01 6\n")}
    monkeypatch.setenv("LC_ALL", "de_DE.UTF-8")
    seen["de_DE locale"] = run("1", "0", "3.00 6\n")
    monkeypatch.delenv("LC_ALL")
    seen["past 2^63"] = run("99999999999999999999", "0", "4.50 6\n")
    monkeypatch.setattr(sys, "stdout", None)
    seen["stdout closed, over"] = run("1", "0", "3.00 6\n")[0]
    seen["stdout closed, within"] = run("1", "100", "3.00 6\n")[0]
    assert seen == {
        "sort order": (1, "spent 62867166030099.38, steps remaining 0, median 62867166030098.60, "
                          "projection 62867166030099.38\n", ""),
        "half-cent median": (1, "spent 2.03, steps remaining 1, median 1.02, projection 3.05\n", ""),
        "de_DE locale": (1, "spent 3.00, steps remaining 1, median 3.00, projection 6.00\n", ""),
        "past 2^63": (1, "spent 4.50, steps remaining -9223372036854775808, median 4.50, "
                         "projection 450000000000000000000.00\n", ""),
        "stdout closed, over": 2,
        "stdout closed, within": 0,
    }


def test_main_answers_the_contract_cases_from_step_budget_and_step_cost_as_run_affordable_sh_did(capsys, monkeypatch, scratch, run_affordable):
    def run(budget, argv, steps, log=True):
        log_file = scratch / ".tdd" / "events.jsonl"
        if log:
            _log(scratch, steps)
        elif log_file.exists():
            log_file.unlink()
        monkeypatch.setenv("VERI_RUN_BUDGET", budget)
        code = run_affordable.main(argv)
        out, _ = capsys.readouterr()
        return (code, out)

    three_full = "1.50 6\n2.25 6\n3.75 6\n"
    seen = {
        "even count out of order": run("50", ["5"], "9.00 6\n3.00 6\n7.00 6\n5.00 6\n"),
        "mostly pins": run("50", ["3"], "0.50 2\n6.00 6\n0.50 2\n0.50 2\n8.00 6\n0.50 2\n10.00 6\n0.50 2\n"),
        "argument missing": run("50", [], three_full),
        "argument ''": run("50", [""], three_full),
        "argument two": run("50", ["two"], three_full),
        "argument 1.5": run("50", ["1.5"], three_full),
        "no event log": run("50", ["3"], three_full, log=False),
        "VERI_RUN_BUDGET fifty": run("fifty", ["3"], three_full),
        "VERI_RUN_BUDGET -5": run("-5", ["3"], three_full),
        "VERI_RUN_BUDGET ''": run("", ["3"], three_full),
        "8 of 9 steps": run("60", ["1"], "5.50 6\n5.80 6\n6.00 6\n6.10 6\n6.20 6\n6.40 6\n6.56 6\n6.80 6\n"),
        "early in a long plan": run("50", ["10"], "7.00 6\n8.00 6\n"),
    }
    assert seen == {
        "even count out of order": (1, "spent 24.00, steps remaining 5, median 6.00, projection 54.00\n"),
        "mostly pins": (1, "spent 26.50, steps remaining 3, median 8.00, projection 50.50\n"),
        "argument missing": (2, ""),
        "argument ''": (2, ""),
        "argument two": (2, ""),
        "argument 1.5": (2, ""),
        "no event log": (2, ""),
        "VERI_RUN_BUDGET fifty": (2, ""),
        "VERI_RUN_BUDGET -5": (2, ""),
        "VERI_RUN_BUDGET ''": (2, ""),
        "8 of 9 steps": (0, ""),
        "early in a long plan": (1, "spent 15.00, steps remaining 10, median 7.50, projection 90.00\n"),
    }


def _events(scratch, steps):
    """Write a usage event log of <steps> '<name>|<dollars>...' lines, as bytes so a step name may hold any byte."""
    out = b""
    for line in steps:
        name, *dollars = line.split("|")
        for d in dollars:
            out += b'{"ts": 1, "issue": "453", "actor": "developer", "phase": "red", "step": "%s", "event": "usage", "total_cost_usd": "%s"}\n' % (
                name.encode("latin-1"), d.encode())
    (scratch / ".tdd" / "events.jsonl").write_bytes(out)


THREE_FULL = ["step one|0.25|1.00|1.00|1.00|1.00|1.00", "step two|0.50|1.00|1.50|1.50|1.50|1.50",
              "step three|0.75|1.50|1.50|2.00|2.00|2.00"]


def _cli(run_cli, run_affordable, scratch, remaining):
    return run_cli(run_affordable, [remaining], env={"VERI_RUN_BUDGET": "50"}, cwd=scratch)


def test_a_log_with_only_pins_or_no_usage_at_all_exits_3_printing_nothing(run_cli, scratch, run_affordable):
    _events(scratch, ["pin one|0.25|0.25", "pin two|0.25|0.25"])
    assert _cli(run_cli, run_affordable, scratch, "3") == (3, "", "")
    (scratch / ".tdd" / "events.jsonl").write_text('{"ts": 1, "issue": "453", "actor": "conductor", "event": "phase-start"}\n')
    assert _cli(run_cli, run_affordable, scratch, "3") == (3, "", "")


def test_run_from_another_working_directory_it_answers_from_that_directorys_event_log(run_cli, scratch, run_affordable):
    _events(scratch, THREE_FULL)
    assert _cli(run_cli, run_affordable, scratch, "4") == (
        1, "spent 22.50, steps remaining 4, median 7.50, projection 52.50\n", "")

    (scratch / ".tdd" / "events.jsonl").unlink()
    code, out, err = _cli(run_cli, run_affordable, scratch, "4")
    assert (code, out) == (2, "")
    assert "cannot read .tdd/events.jsonl in %s " % os.path.realpath(scratch) in err


def test_an_event_log_step_cost_cannot_decode_exits_2_printing_nothing(run_cli, scratch, run_affordable):
    _events(scratch, THREE_FULL + ["step \xff|1.00|1.00|1.00"])
    code, out, _ = _cli(run_cli, run_affordable, scratch, "4")
    assert (code, out) == (2, "")
