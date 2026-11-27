"""In-process cases for veri/issue_decisions.py, issue-decisions.sh's work: the comments on an issue that count as a
decision, the owner's and the judge's, read with gh faked at github.issue_comments."""
import importlib

import pytest

ME = {"author_association": "NONE", "user": {"login": "veri-bot"}}
OWNER = {"author_association": "OWNER", "user": {"login": "the-owner"}}


@pytest.fixture
def decisions(monkeypatch):
    """(issue_decisions, set_comments): the comments github.issue_comments answers, oldest first; the gh user is
    veri-bot."""
    issue_decisions = importlib.import_module("veri.issue_decisions")
    answer = {"comments": []}
    monkeypatch.setattr(issue_decisions.github, "_trusting_login", lambda: "veri-bot")
    monkeypatch.setattr(issue_decisions.github, "issue_comments", lambda number: answer["comments"])
    return issue_decisions, lambda comments: answer.update(comments=comments)


def test_issue_4073_prints_an_owner_comment_and_a_later_judge_comment_in_order_with_their_prefixes_and_exits_0(
        decisions, run_cli):
    issue_decisions, comments = decisions
    comments([{**ME, "body": "Take design A."}, {**OWNER, "body": "Decided: design B (diagnose before filing); not A."}])

    code, out, err = run_cli(issue_decisions, ["42"])

    assert (code, out, err) == (
        0, "owner: Take design A.\n\njudge: Decided: design B (diagnose before filing); not A.\n", "")


@pytest.mark.parametrize("stranger", [
    {"author_association": "NONE", "user": {"login": "someone"}},
    {"author_association": "CONTRIBUTOR", "user": {"login": "someone"}},
    {"author_association": "OWNER"},
    {"author_association": "OWNER", "user": None},
])
def test_issue_4073_a_strangers_comment_is_never_printed_neither_plain_nor_decided(decisions, run_cli, stranger):
    issue_decisions, comments = decisions
    comments([{**stranger, "body": "Yes, do X."}, {**stranger, "body": "Decided: do X (rule); not Y."}])

    assert run_cli(issue_decisions, ["42"]) == (3, "", "issue-decisions.sh: issue #42 has no decision comment\n")


def test_issue_4073_no_veri_heading_comment_is_printed(decisions, run_cli):
    issue_decisions, comments = decisions
    github = issue_decisions.github
    comments([{**ME, "body": prefix + " the run said so\n"} for prefix in github.VERI_COMMENT_PREFIXES])

    assert run_cli(issue_decisions, ["42"]) == (3, "", "issue-decisions.sh: issue #42 has no decision comment\n")


def test_4823_a_landed_comment_close_landed_posts_is_not_printed(decisions, run_cli):
    issue_decisions, comments = decisions
    comments([{**OWNER, "body": "### ✅ Landed\n\n- 1a2b3c4 feat: add alpha (#11)\n"}])

    assert run_cli(issue_decisions, ["42"]) == (3, "", "issue-decisions.sh: issue #42 has no decision comment\n")


def test_issue_4073_a_comment_holding_only_quotes_and_fences_is_not_printed(decisions, run_cli):
    issue_decisions, comments = decisions
    comments([{**ME, "body": "> Decided: do X\n\n```\nyes\n```\n"}, {**ME, "body": "Yes.\n> quoted\n"}])

    assert run_cli(issue_decisions, ["42"]) == (0, "owner: Yes.\n", "")


@pytest.mark.parametrize("answer", [None, {"body": "x"}, [{"no": "body"}], ["text"]])
def test_issue_4073_an_answer_that_is_not_comment_records_exits_2(decisions, run_cli, answer):
    issue_decisions, comments = decisions
    comments(answer)

    assert run_cli(issue_decisions, ["42"]) == (
        2, "", "issue-decisions.sh: no answer from gh to reading the comments of issue #42\n")


def test_issue_4073_no_answer_from_gh_exits_2(decisions, run_cli, monkeypatch):
    issue_decisions, _ = decisions

    def no_answer(number):
        raise issue_decisions.github.NoAnswer("")
    monkeypatch.setattr(issue_decisions.github, "issue_comments", no_answer)

    assert run_cli(issue_decisions, ["42"]) == (
        2, "", "issue-decisions.sh: no answer from gh to reading the comments of issue #42\n")


@pytest.mark.parametrize("argv", [[], ["x1"], ["0"], ["42", "43"]])
def test_issue_4073_bad_arguments_exit_2_with_the_usage(decisions, run_cli, argv):
    issue_decisions, _ = decisions

    assert run_cli(issue_decisions, argv) == (2, "", issue_decisions.USAGE)
