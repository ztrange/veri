"""In-process cases for veri/capture_spec.py, the module capture-spec.sh is a shim over."""
import importlib
import json
import re
import sys

import pytest

USAGE = "capture-spec: usage: capture-spec.sh <issue-number>\n"


@pytest.fixture
def capture_spec():
    return importlib.import_module("veri.capture_spec")


def fake_gh(fake_processes, labels, body):
    """`gh issue view <n> --json labels|body` answered with <labels>, <body>; any other process, run or Popen,
    fails the case. Returns the fake: its argvs are every call, in order."""
    def view(line, **kwargs):
        words = line.split()
        if "labels" in words:
            return 0, labels, ""
        if "body" in words:
            return 0, body, ""
        raise AssertionError("unexpected command: %s" % line)

    return fake_processes.answers({"gh issue view": view})


def test_main_refuses_a_missing_or_empty_issue_number_with_exit_2_and_answers_0_for_one(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_gh(fake_processes, "enhancement\n", "lamps glow\n")

    for argv in ([], [""]):
        code = capture_spec.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err, fake.argvs) == (argv, 2, "", USAGE, [])

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "lamps glow\n", "")
    assert fake.argvs == [
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


def test_main_appends_a_bug_section_naming_the_body_headings_for_a_bug_labelled_issue(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.err) == (0, "")
    assert captured.out.startswith(BUG_BODY)
    assert "\n## Bug\n" in captured.out[len(BUG_BODY) - 1:]


def test_main_carries_each_bug_heading_text_once_in_the_body_and_names_the_headings_in_the_bug_section(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    out = capsys.readouterr().out

    bug_section = out[out.index("\n## Bug\n"):]
    texts = ("ticked the same step twice.", "ticks a step once.", "twice against the same step text.", "bash 5.2 on macOS 15.6.")
    headings = ("What happened", "Expected", "Steps to reproduce", "Environment")
    assert (code, [out.count(t) for t in texts], [h in bug_section for h in headings]) == (0, [1, 1, 1, 1], [True] * 4)


def test_main_returns_2_with_nothing_on_stdout_when_gh_api_exits_non_zero_with_a_json_error_body(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_processes.answers({
        "gh issue view": (1, "", ""),
        "gh api": (1, '{"message":"Not Found","documentation_url":"https://docs.github.com/rest","status":"404"}', None)})

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out) == (2, "")
    assert fake.argvs == [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
    ]


def test_main_returns_2_not_a_type_error_when_a_failing_gh_api_leaves_stderr_unset_3582(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    fake_processes.answers({"gh api": (1, "", None)})

    code = capture_spec.main(["7"])

    assert (code, capsys.readouterr().out) == (2, "")


PLAIN_BODY = """## What to build

tick-ledger.sh grows a `--dry-run` flag.

## Acceptance criteria

- [ ] `--dry-run` prints the tick it would make and writes nothing
"""


def test_main_appends_no_bug_section_for_an_unlabelled_issue_and_a_refactor_section_for_a_refactor_labelled_one(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, "", PLAIN_BODY)
    code = capture_spec.main(["113"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, PLAIN_BODY, "")

    fake_gh(fake_processes, "refactor\n", PLAIN_BODY)
    code = capture_spec.main(["499"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, PLAIN_BODY + (
        "\n## Refactor\n"
        "\nRun kind: refactor. This issue changes structure, not behaviour.\n"
    ), "")


def refuse_graphql(fake_processes, labels, body):
    """subprocess.run refusing every `gh issue view` with the 403 and answering
    `gh api repos/{owner}/{repo}/issues/<n>` with the issue's REST JSON, <body> None for null."""
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"

    def view(line, **kwargs):
        if kwargs.get("stderr") is None:
            sys.stderr.write(refusal)
        return 1, "", refusal

    def api(line, **kwargs):
        n = line.rsplit("/", 1)[1]
        issue = {"number": int(n), "body": body, "labels": [{"name": label} for label in labels]}
        return 0, json.dumps(issue), None

    fake_processes.answers({"gh issue view": view, "gh api repos/{owner}/{repo}/issues/": api})


def test_main_against_a_gh_refusing_graphql_answers_through_rest_as_a_working_gh_does_a_null_body_reading_as_empty(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    for labels, body, rest_body in ((["bug", "refactor"], BUG_BODY, BUG_BODY), ([], "", None)):
        fake_gh(fake_processes, "".join(label + "\n" for label in labels), body)
        working = (capture_spec.main(["112"]), capsys.readouterr())

        refuse_graphql(fake_processes, labels, rest_body)
        refused = (capture_spec.main(["112"]), capsys.readouterr())

        assert (labels, refused[0], refused[1].out, refused[1].err) == (labels, working[0], working[1].out, working[1].err)
        assert working[0] == 0


REFACTOR_SECTION = "\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n"


def test_main_keeps_the_text_rules_of_body_echo_label_match_and_section_extraction(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    def spec(labels, body):
        fake_gh(fake_processes, labels, body)
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
    code, out, err = spec("bug\nrefactor\n", mixed)
    assert (code, err) == (0, "")
    assert out.startswith(mixed) and "\n## Bug\n" in out[len(mixed) - 1:]
    assert out.endswith(REFACTOR_SECTION)

    crlf = BUG_BODY.replace("\n", "\r\n")
    code, out, err = spec("bug\n", crlf)
    assert (code, err) == (0, "")
    assert out.startswith(crlf) and "\n## Bug\n" in out[len(crlf) - 1:]


def test_main_asks_labels_before_the_body_of_its_first_argument_and_fails_both_routes_with_exit_2_and_gh_apis_error_then_the_json_decode_line(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"
    unreachable = "error connecting to api.github.com\ncheck your internet connection or https://githubstatus.com\n"
    decode_line = "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n"

    def fake_gh_failing(labels_answer):
        def view(line, **kwargs):
            if "labels" in line.split() and labels_answer is not None:
                return 0, labels_answer, ""
            if kwargs.get("stderr") is None:
                sys.stderr.write(refusal)
            return 1, "", refusal

        def api(line, **kwargs):
            if kwargs.get("stderr") is None:
                sys.stderr.write(unreachable)
            return 1, "", unreachable

        return fake_processes.answers({"gh issue view": view, "gh api": api})

    fake = fake_gh_failing(None)
    code = capture_spec.main(["abc", "extra"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err, fake.argvs) == (2, "", unreachable + decode_line, [
        ["gh", "issue", "view", "abc", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "api", "repos/{owner}/{repo}/issues/abc"],
    ])

    fake = fake_gh_failing("bug\n")
    code = capture_spec.main(["7"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err, fake.argvs) == (2, "", unreachable + decode_line, [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "issue", "view", "7", "--json", "body", "-q", ".body"],
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
    ])


def test_main_reads_the_issue_through_gh_api_only_when_veri_gh_driver_is_unset_or_rest_1114(monkeypatch, capsys, capture_spec, fake_processes):
    for driver in (None, "rest"):
        if driver is None:
            monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
        else:
            monkeypatch.setenv("VERI_GH_DRIVER", driver)
        def view(line, **kwargs):
            return 0, "bug\n" if "labels" in line.split() else BUG_BODY, ""

        issue = {"number": 7, "body": BUG_BODY, "labels": [{"name": "bug"}]}
        fake = fake_processes.answers({"gh issue view": view,
                                       "gh api repos/{owner}/{repo}/issues/7": (0, json.dumps(issue), None)})

        code = capture_spec.main(["7"])
        captured = capsys.readouterr()

        assert (driver, code, captured.err, fake.argvs) == (driver, 0, "", [
            ["gh", "api", "repos/{owner}/{repo}/issues/7"],
            ["gh", "api", "repos/{owner}/{repo}/issues/7"],
        ])
        assert captured.out.startswith(BUG_BODY) and "\n## Bug\n" in captured.out


def test_main_reads_the_issue_through_gh_issue_view_only_when_veri_gh_driver_is_graphql_and_a_graphql_failure_is_exit_2_with_no_gh_api_call_1114(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    fake = fake_gh(fake_processes, "bug\n", BUG_BODY)

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.err, fake.argvs) == (0, "", [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
        ["gh", "issue", "view", "7", "--json", "body", "-q", ".body"],
    ])
    assert captured.out.startswith(BUG_BODY) and "\n## Bug\n" in captured.out

    issue = {"number": 7, "body": BUG_BODY, "labels": [{"name": "bug"}]}
    fake = fake_processes.answers({"gh issue view": (1, "", ""),
                                   "gh api repos/{owner}/{repo}/issues/7": (0, json.dumps(issue), None)})

    code = capture_spec.main(["7"])
    captured = capsys.readouterr()

    assert (code, captured.out, fake.argvs) == (2, "", [
        ["gh", "issue", "view", "7", "--json", "labels", "-q", ".labels[].name"],
    ])


def test_main_refuses_an_empty_or_unknown_veri_gh_driver_with_exit_2_nothing_on_stdout_a_stderr_line_naming_it_and_no_gh_process_1114(monkeypatch, capsys, capture_spec, fake_processes):
    for driver in ("", "bogus"):
        monkeypatch.setenv("VERI_GH_DRIVER", driver)
        fake = fake_gh(fake_processes, "bug\n", BUG_BODY)

        code = capture_spec.main(["7"])
        captured = capsys.readouterr()

        lines = captured.err.splitlines()
        assert (driver, code, captured.out, fake.argvs, len(lines)) == (driver, 2, "", [], 1)
        assert "VERI_GH_DRIVER" in lines[0] and "'%s'" % driver in lines[0]


def gh_answering(fake_processes, answers):
    """fake_processes answering each gh command line with answers[line] = (code, stdout); the lines run, in order."""
    return fake_processes(lambda line, **kwargs: (answers[line][0], answers[line][1], "") if line in answers else (_ for _ in ()).throw(AssertionError("unexpected command: " + line)))


def view_lines(issue):
    return ("gh issue view %s --json labels -q .labels[].name" % issue, "gh issue view %s --json body -q .body" % issue)


def test_a_bug_labelled_issue_spec_carries_its_body_and_a_bug_section(fake_processes, run_cli, capture_spec):
    labels, body = view_lines(112)
    calls = gh_answering(fake_processes, {labels: (0, "bug\n"), body: (0, BUG_BODY)})

    code, out, err = run_cli(capture_spec, ["112"], env={"VERI_GH_DRIVER": "auto"})

    assert (code, err, calls) == (0, "", [labels, body])
    assert out.startswith(BUG_BODY)
    assert re.search(r"^## Bug$", out, re.M)


def test_with_no_argument_the_cli_exits_2_prints_nothing_on_stdout_and_its_usage_line_on_stderr(fake_processes, run_cli, capture_spec):
    calls = gh_answering(fake_processes, {})

    assert run_cli(capture_spec, [], env={"VERI_GH_DRIVER": "auto"}) == (2, "", USAGE)
    assert calls == []


def test_against_a_gh_that_fails_both_routes_the_cli_exits_2_with_nothing_on_stdout(fake_processes, run_cli, capture_spec):
    labels, _ = view_lines(7)
    api = "gh api repos/{owner}/{repo}/issues/7"
    calls = gh_answering(fake_processes, {labels: (1, ""), api: (1, "")})

    code, out, _ = run_cli(capture_spec, ["7"], env={"VERI_GH_DRIVER": "auto"})

    assert (code, out, calls) == (2, "", [labels, api])


def test_with_veri_gh_driver_unset_the_cli_reads_the_issue_through_gh_api_only_prints_the_spec_and_runs_no_gh_issue_view(monkeypatch, fake_processes, run_cli, capture_spec):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    api = "gh api repos/{owner}/{repo}/issues/7"
    issue = json.dumps({"labels": [], "body": "## What to build\n\ntick-ledger.sh grows a flag.\n"})
    calls = gh_answering(fake_processes, {api: (0, issue)})

    code, out, err = run_cli(capture_spec, ["7"])

    assert (code, out, err) == (0, "## What to build\n\ntick-ledger.sh grows a flag.\n", "")
    assert [c for c in calls if c.startswith("gh issue view")] == []
    assert calls and set(calls) == {api}


def test_with_veri_gh_driver_graphql_a_failing_gh_issue_view_makes_the_cli_exit_2_with_nothing_on_stdout_and_no_gh_api_call(fake_processes, run_cli, capture_spec):
    labels, _ = view_lines(7)
    calls = gh_answering(fake_processes, {labels: (1, "")})

    code, out, _ = run_cli(capture_spec, ["7"], env={"VERI_GH_DRIVER": "graphql"})

    assert (code, out) == (2, "")
    assert calls and [c for c in calls if c.startswith("gh api")] == []


def test_main_appends_a_legacy_section_for_a_legacy_labelled_issue_as_it_does_a_refactor_one_4106(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake_gh(fake_processes, "legacy\n", PLAIN_BODY)

    code = capture_spec.main(["4106"])
    captured = capsys.readouterr()

    assert (code, captured.err) == (0, "")
    assert captured.out.startswith(PLAIN_BODY)
    assert re.search(r"^## Legacy$", captured.out[len(PLAIN_BODY):], re.M)
    assert "## Refactor" not in captured.out


def test_main_refuses_an_issue_labelled_both_legacy_and_refactor_with_exit_2_naming_both_labels_and_nothing_on_stdout_4106(monkeypatch, capsys, capture_spec, fake_processes):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    for labels in ("legacy\nrefactor\n", "refactor\nbug\nlegacy\n"):
        fake_gh(fake_processes, labels, PLAIN_BODY)

        code = capture_spec.main(["4106"])
        captured = capsys.readouterr()

        assert (labels, code, captured.out) == (labels, 2, "")
        assert "`legacy`" in captured.err and "`refactor`" in captured.err
