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


def test_main_returns_3_with_no_patch_and_names_the_matcher_and_issue_when_no_unchecked_criterion_matches(monkeypatch, capsys, tick_issue_criterion):
    real_run = subprocess.run
    patches = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "- [ ] alpha\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            patches.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = tick_issue_criterion.main(["7", "zeta"])

    assert (code, capsys.readouterr().err, patches) == (3, "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])
