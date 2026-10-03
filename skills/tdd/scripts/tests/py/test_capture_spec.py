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


BUG_BODY = """## What happened
tick-ledger.sh ticked the same step twice.

## Expected
tick-ledger.sh ticks a step once.

## Steps to reproduce
Run tick-ledger.sh twice against the same step text.

## Environment
bash 5.2 on macOS 15.6.

## Acceptance criteria

- [ ] a step is ticked once
"""


def test_main_appends_a_bug_section_carrying_each_matching_body_section_for_a_bug_labelled_issue(monkeypatch, capsys, capture_spec):
    fake_gh(monkeypatch, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (0, BUG_BODY + (
        "\n## Bug\n"
        "\n### What happened\n\n"
        "tick-ledger.sh ticked the same step twice.\n\n"
        "\n### Expected\n\n"
        "tick-ledger.sh ticks a step once.\n\n"
        "\n### Steps to reproduce\n\n"
        "Run tick-ledger.sh twice against the same step text.\n\n"
        "\n### Environment\n\n"
        "bash 5.2 on macOS 15.6.\n\n"
    ), "")


def test_main_returns_2_with_nothing_on_stdout_when_gh_api_exits_non_zero_with_a_json_error_body(monkeypatch, capsys, capture_spec):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if list(args[:3]) == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        if list(args[:2]) == ["gh", "api"]:
            return subprocess.CompletedProcess(args, 1, '{"message":"Not Found","documentation_url":"https://docs.github.com/rest","status":"404"}', None)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out) == (2, "")
    assert calls == [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
    ]
