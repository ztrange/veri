"""`metrics.sh <n> --json`: the run's metrics as one JSON object, built from the same Fold as the markdown report
(PRD 035.1, MJ1 to MJ10)."""
import importlib
import json

import pytest

from test_metrics_page import build_rich_root


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


@pytest.fixture(autouse=True)
def no_records_on_origin(monkeypatch):
    """origin carries no refs/veri/runs/<n>: the fallback read answers None and starts no git."""
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "read", lambda issue, name, cwd: None)


@pytest.fixture
def rich(tmp_path, monkeypatch):
    transcripts = build_rich_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_SESSION_TRANSCRIPTS", str(transcripts))
    monkeypatch.setenv("VERI_LABEL", "lane-x")
    return tmp_path


def as_json(metrics, capsys, argv=("108", "--json")):
    code = metrics.main(list(argv))
    out, err = capsys.readouterr()
    assert code == 0, err
    return json.loads(out)


def test_json_prints_one_object_with_the_five_top_level_keys_and_the_markdown_report_is_unchanged(
        rich, monkeypatch, capsys, metrics):
    markdown = metrics.report("108", ".tdd/events.jsonl", ".tdd/issue-108.md")

    printed = as_json(metrics, capsys)
    code = metrics.main(["108"])
    again, _ = capsys.readouterr()

    assert sorted(printed) == ["conductor", "phases", "run", "steps", "total"]
    assert (code, again) == (0, markdown)
