"""In-process cases for veri/render_leaf_log.py, the module render-leaf-log.sh is a shim over."""
import importlib
import io
import json
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def render_leaf_log():
    return importlib.import_module("veri.render_leaf_log")


def test_main_discards_the_records_already_rendered_and_returns_2_on_a_line_that_is_not_json(monkeypatch, capsys, render_leaf_log):
    record = {"type": "assistant", "message": {"content": [{"type": "text", "text": "hello"}]}}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(record) + "\nnot json at all\n"))
    code = render_leaf_log.main([])
    assert (code, capsys.readouterr().out) == (2, "")


def test_main_renders_text_tool_calls_and_truncated_results_one_per_line_and_returns_0(monkeypatch, capsys, render_leaf_log):
    fixture = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "render-leaf-log" / "leaf.out"
    monkeypatch.setattr(sys, "stdin", io.StringIO(fixture.read_text(encoding="utf-8")))
    code = render_leaf_log.main([])
    assert (code, capsys.readouterr().out) == (0, (
        "Reading the suite before adding the case.\n"
        "> Bash: cat skills/tdd/scripts/tests/extract-result.test.sh\n"
        "< #!/usr/bin/env bash…\n"
        "> Read: /repo/README.md\n"
        "< # veri — a Claude Code skill suite that solves one GitHub issue under strict TDD…\n"
        "> Bash: make test\n"
        "< 3 passed, 0 failed\n"
        "The case is added and fails as predicted.\n"
    ))
