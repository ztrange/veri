"""In-process cases for veri/capture_spec.py, the module capture-spec.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>\n"


@pytest.fixture
def capture_spec():
    return importlib.import_module("veri.capture_spec")


def fake_gh(monkeypatch, labels, body):
    """subprocess.run answering `gh issue view <n> --json labels|body` with <labels>, <body>;
    every subprocess call, run or Popen, recorded in the returned list."""
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if list(args[:3]) == ["gh", "issue", "view"] and "labels" in args:
            stdout = labels
        elif list(args[:3]) == ["gh", "issue", "view"] and "body" in args:
            stdout = body
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    def fake_popen(args, *rest, **kwargs):
        calls.append(list(args))
        raise AssertionError("unexpected Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_main_refuses_a_missing_or_empty_issue_number_with_exit_2_and_answers_0_for_one(monkeypatch, capsys, capture_spec):
    calls = fake_gh(monkeypatch, "enhancement\n", "lamps glow\n")

    for argv in ([], [""]):
        code = capture_spec.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err, calls) == (argv, 2, "", USAGE, [])

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "lamps glow\n", "")
    assert calls == [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "issue", "view", "7", "--json", "body", "-q", ".body"],
    ]
