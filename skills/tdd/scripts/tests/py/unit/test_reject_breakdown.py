"""In-process cases for veri/reject_breakdown.py, the module reject-breakdown.sh is a shim over (#4568)."""
import importlib

import pytest

PHASE_HEADER = (
    "| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read"
    " | cache creation | $ |\n"
    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")


def phase_row(phase, passes, rejects):
    return f"| {phase} | {passes + rejects} | {passes} | {rejects} | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0.01 |\n"


def report(*rows, tail=""):
    return ("### 📊 Metrics — issue 1\n\n#### By phase\n\n" + PHASE_HEADER + "".join(rows)
            + "\n#### By step\n\n| step |\n| --- |\n" + tail)


@pytest.fixture
def breakdown():
    return importlib.import_module("veri.reject_breakdown")


def test_prints_one_reject_per_verify_line_per_week_summing_the_by_phase_verdicts_of_its_reports(
        tmp_path, run_cli, breakdown):
    first = tmp_path / "issue-1-metrics.md"
    first.write_text(report(phase_row("green", 7, 1), phase_row("refactor", 2, 0)))
    second = tmp_path / "issue-2-metrics.md"
    second.write_text(report(phase_row("green", 3, 1)))
    later = tmp_path / "issue-3-metrics.md"
    later.write_text(report(phase_row("green", 1, 1), phase_row("pin", 1, 1)))
    stdin = f"2026-10-21 {first}\n2026-10-25 {second}\n2026-10-27 {later}\n"

    code, out, err = run_cli(breakdown, [], stdin=stdin)

    weeks = [line for line in out.splitlines() if line.startswith("week ")]
    assert (code, weeks) == (0, [
        "week 2026-10-19: REJECT per verify 14.3% (2 of 14)",
        "week 2026-10-26: REJECT per verify 50.0% (2 of 4)",
    ])


def test_prints_under_each_week_one_line_per_verifier_phase_with_a_verdict_that_week(tmp_path, run_cli, breakdown):
    first = tmp_path / "issue-1-metrics.md"
    first.write_text(report(phase_row("green", 7, 1), phase_row("red", 0, 0), phase_row("refactor", 2, 0)))
    second = tmp_path / "issue-2-metrics.md"
    second.write_text(report(phase_row("green", 3, 1), phase_row("pin", 0, 2)))

    code, out, err = run_cli(breakdown, [], stdin=f"2026-10-21 {first}\n2026-10-22 {second}\n")

    assert (code, out.splitlines()[1:]) == (0, [
        "  phase green: 2 of 12",
        "  phase pin: 2 of 2",
        "  phase refactor: 0 of 2",
    ])
