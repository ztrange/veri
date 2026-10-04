"""In-process cases for veri/tick_issue_criterion.py, the module tick-issue-criterion.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def tick_issue_criterion():
    return importlib.import_module("veri.tick_issue_criterion")


def test_main_returns_2_with_the_usage_line_and_no_subprocess_call_for_a_missing_or_empty_number(monkeypatch, capsys, tick_issue_criterion):
    def refuse(args, **kwargs):
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    for argv in ([], [""]):
        code = tick_issue_criterion.main(argv)
        captured = capsys.readouterr()
        assert (code, captured.out, captured.err) == (2, "", "usage: tick-issue-criterion.sh <issue-number> <matcher>\n")
