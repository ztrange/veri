"""The Gradings line of veri/metrics.py's report (PRD 024.10): what the log's gradings cost and returned."""
import importlib

import pytest
from test_metrics import render, write_log


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def grading(verdict, cost, effort=None):
    event = {"event": "grading", "unit": "a.md", "verdict": verdict, "failing": "", "cost_usd": cost, "id": "g"}
    if effort is not None:
        event["effort"] = effort
    return event


def test_the_gradings_line_gives_count_pass_reject_summed_cost_and_efforts_and_is_absent_with_no_grading(
        tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return [line for line in render(metrics, capsys).split("\n") if line.startswith("Gradings:")]

    graded = report("graded", [grading("PASS", "0.5", "low"), grading("REJECT", "0.25"),
                               grading("PASS", "0.125", "default"), grading("PASS", "1", "low")])
    ungraded = report("ungraded", [{"event": "step-start", "step": "1", "ts": 1}])

    assert (graded, ungraded) == (["Gradings: 4, PASS 3, REJECT 1, cost $1.88, efforts default, low"], [])
