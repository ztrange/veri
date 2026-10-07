"""In-process cases for veri/capture_spec.py, the module capture-spec.sh is a shim over."""
import importlib
import json
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
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
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

BUG_SPEC = BUG_BODY + (
    "\n## Bug\n"
    "\n### What happened\n\n"
    "tick-ledger.sh ticked the same step twice.\n\n"
    "\n### Expected\n\n"
    "tick-ledger.sh ticks a step once.\n\n"
    "\n### Steps to reproduce\n\n"
    "Run tick-ledger.sh twice against the same step text.\n\n"
    "\n### Environment\n\n"
    "bash 5.2 on macOS 15.6.\n\n"
)


def test_main_appends_a_bug_section_carrying_each_matching_body_section_for_a_bug_labelled_issue(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(monkeypatch, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (0, BUG_SPEC, "")


def test_main_returns_2_with_nothing_on_stdout_when_gh_api_exits_non_zero_with_a_json_error_body(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
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


PLAIN_BODY = """## What to build

tick-ledger.sh grows a `--dry-run` flag.

## Acceptance criteria

- [ ] `--dry-run` prints the tick it would make and writes nothing
"""


def test_main_appends_no_bug_section_for_an_unlabelled_issue_and_a_refactor_section_for_a_refactor_labelled_one(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(monkeypatch, "", PLAIN_BODY)
    code = capture_spec.main(["113"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, PLAIN_BODY, "")

    fake_gh(monkeypatch, "refactor\n", PLAIN_BODY)
    code = capture_spec.main(["499"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, PLAIN_BODY + (
        "\n## Refactor\n"
        "\nRun kind: refactor. This issue changes structure, not behaviour.\n"
    ), "")


def refuse_graphql(monkeypatch, labels, body):
    """subprocess.run refusing every `gh issue view` with the 403 and answering
    `gh api repos/{owner}/{repo}/issues/<n>` with the issue's REST JSON, <body> None for null."""
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["gh", "issue", "view"]:
            if kwargs.get("stderr") is None:
                sys.stderr.write(refusal)
            return subprocess.CompletedProcess(args, 1, "", refusal)
        if list(args[:2]) == ["gh", "api"] and args[2].startswith("repos/{owner}/{repo}/issues/"):
            n = args[2].rsplit("/", 1)[1]
            issue = {"number": int(n), "body": body, "labels": [{"name": label} for label in labels]}
            return subprocess.CompletedProcess(args, 0, json.dumps(issue), None)
        raise AssertionError("unexpected command: %r" % (args,))

    def fake_popen(args, *rest, **kwargs):
        raise AssertionError("unexpected Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)


def test_main_against_a_gh_refusing_graphql_answers_through_rest_as_a_working_gh_does_a_null_body_reading_as_empty(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    for labels, body, rest_body in ((["bug", "refactor"], BUG_BODY, BUG_BODY), ([], "", None)):
        fake_gh(monkeypatch, "".join(label + "\n" for label in labels), body)
        working = (capture_spec.main(["112"]), capsys.readouterr())

        refuse_graphql(monkeypatch, labels, rest_body)
        refused = (capture_spec.main(["112"]), capsys.readouterr())

        assert (labels, refused[0], refused[1].out, refused[1].err) == (labels, working[0], working[1].out, working[1].err)
        assert working[0] == 0


REFACTOR_SECTION = "\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n"


def test_main_keeps_the_text_rules_of_body_echo_label_match_and_section_extraction(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    def spec(labels, body):
        fake_gh(monkeypatch, labels, body)
        code = capture_spec.main(["7"])
        captured = capsys.readouterr()
        return (code, captured.out, captured.err)

    assert spec("", "lamps glow\n\n\n") == (0, "lamps glow\n", "")
    assert spec("", "") == (0, "\n", "")

    assert spec("Bug\n", BUG_BODY) == (0, BUG_BODY, "")

    mixed = (
        "## What happened \n"
        "trailing space\n"
        "## Expected\r\n"
        "carriage return\n"
        "## Environment\n"
        "### Expected\n"
        "not a section\n"
        "## Steps to reproduce\n"
        "first\n"
        "## Other\n"
        "skipped\n"
        "## Steps to reproduce\n"
        "second\n"
    )
    assert spec("bug\nrefactor\n", mixed) == (0, mixed + (
        "\n## Bug\n"
        "\n### What happened\n\n"
        "\n### Expected\n\n"
        "\n### Steps to reproduce\n\n"
        "first\n"
        "second\n"
        "\n### Environment\n\n"
        "### Expected\n"
        "not a section\n"
    ) + REFACTOR_SECTION, "")

    crlf = BUG_BODY.replace("\n", "\r\n")
    assert spec("bug\n", crlf) == (0, crlf + (
        "\n## Bug\n"
        "\n### What happened\n\n"
        "\n### Expected\n\n"
        "\n### Steps to reproduce\n\n"
        "\n### Environment\n\n"
    ), "")


def test_main_asks_labels_before_the_body_of_its_first_argument_and_fails_both_routes_with_exit_2_and_gh_apis_error_then_the_json_decode_line(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"
    unreachable = "error connecting to api.github.com\ncheck your internet connection or https://githubstatus.com\n"
    decode_line = "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"

    def fake_gh_failing(labels_answer):
        calls = []

        def fake_run(args, **kwargs):
            calls.append(list(args))
            if list(args[:3]) == ["gh", "issue", "view"] and "labels" in args and labels_answer is not None:
                code, stdout, stderr = 0, labels_answer, ""
            elif list(args[:3]) == ["gh", "issue", "view"]:
                code, stdout, stderr = 1, "", refusal
            elif list(args[:2]) == ["gh", "api"]:
                code, stdout, stderr = 1, "", unreachable
            else:
                raise AssertionError("unexpected command: %r" % (args,))
            if kwargs.get("stderr") is None:
                sys.stderr.write(stderr)
            return subprocess.CompletedProcess(
                args, code,
                stdout if kwargs.get("stdout") == subprocess.PIPE else None,
                stderr if kwargs.get("stderr") == subprocess.PIPE else None)

        def fake_popen(args, *rest, **kwargs):
            calls.append(list(args))
            raise AssertionError("unexpected Popen: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "Popen", fake_popen)
        return calls

    calls = fake_gh_failing(None)
    code = capture_spec.main(["abc", "extra"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err, calls) == (2, "", unreachable + decode_line, [
        ["gh", "issue", "view", "abc", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/abc"],
    ])

    calls = fake_gh_failing("bug\n")
    code = capture_spec.main(["7"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err, calls) == (2, "", unreachable + decode_line, [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "issue", "view", "7", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
    ])


def test_main_reads_the_issue_through_gh_api_only_when_veri_gh_driver_is_unset_or_rest_1114(monkeypatch, capsys, capture_spec):
    for driver in (None, "rest"):
        if driver is None:
            monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
        else:
            monkeypatch.setenv("VERI_GH_DRIVER", driver)
        calls = []

        def fake_run(args, **kwargs):
            calls.append(list(args))
            if list(args[:3]) == ["gh", "issue", "view"] and "labels" in args:
                return subprocess.CompletedProcess(args, 0, "bug\n", "")
            if list(args[:3]) == ["gh", "issue", "view"] and "body" in args:
                return subprocess.CompletedProcess(args, 0, BUG_BODY, "")
            if list(args) == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
                issue = {"number": 7, "body": BUG_BODY, "labels": [{"name": "bug"}]}
                return subprocess.CompletedProcess(args, 0, json.dumps(issue), None)
            raise AssertionError("unexpected command: %r" % (args,))

        def fake_popen(args, *rest, **kwargs):
            calls.append(list(args))
            raise AssertionError("unexpected Popen: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        code = capture_spec.main(["7"])
        captured = capsys.readouterr()

        assert (driver, code, captured.out, captured.err, calls) == (driver, 0, BUG_SPEC, "", [
            ["gh", "api", "repos/{owner}/{repo}/issues/7"],
            ["gh", "api", "repos/{owner}/{repo}/issues/7"],
        ])


def test_main_reads_the_issue_through_gh_issue_view_only_when_veri_gh_driver_is_graphql_and_a_graphql_failure_is_exit_2_with_no_gh_api_call_1114(monkeypatch, capsys, capture_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    calls = fake_gh(monkeypatch, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err, calls) == (0, BUG_SPEC, "", [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "issue", "view", "7", "--json", "body", "-q", ".body"],
    ])

    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if list(args[:3]) == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        if list(args) == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            issue = {"number": 7, "body": BUG_BODY, "labels": [{"name": "bug"}]}
            return subprocess.CompletedProcess(args, 0, json.dumps(issue), None)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out, calls) == (2, "", [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
    ])
