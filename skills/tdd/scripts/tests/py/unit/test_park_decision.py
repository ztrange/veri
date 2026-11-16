"""In-process cases for veri/park_decision.py, park-decision.sh's work: the trusted comments posted after an issue's
newest trusted `### ⏸ Parked` comment, read with gh faked at github.issue_comments."""
import importlib

import pytest

OWNER = {"author_association": "OWNER", "user": {"login": "the-owner"}}
COLLABORATOR = {"author_association": "COLLABORATOR", "user": {"login": "a-collaborator"}}
PARK = {**OWNER, "body": "### ⏸ Parked\nCause: two designs\nUnblock: the owner picks one\n"}


@pytest.fixture
def decision(monkeypatch):
    """(park_decision, set_comments): the comments github.issue_comments answers for the issue, oldest first."""
    park_decision = importlib.import_module("veri.park_decision")
    answer = {"comments": []}
    monkeypatch.setattr(park_decision.github, "_trusting_login", lambda: "veri-bot")
    monkeypatch.setattr(park_decision.github, "issue_comments", lambda number: answer["comments"])
    return park_decision, lambda comments: answer.update(comments=comments)


def test_issue_4077_prints_the_trusted_comments_after_the_newest_parked_comment_oldest_first_and_exits_0(
        decision, run_cli):
    park_decision, comments = decision
    comments([{**OWNER, "body": "Take design A."}, PARK, {**OWNER, "body": "Take design B.\n"},
              {**COLLABORATOR, "body": "And keep the old flag."}])

    code, out, err = run_cli(park_decision, ["42"])

    assert (code, out, err) == (0, "Take design B.\n\nAnd keep the old flag.\n", "")


@pytest.mark.parametrize("comments, why", [
    ([{**OWNER, "body": "Take design A."}, PARK], "no trusted comment after"),
    ([{**OWNER, "body": "Take design A."}], "no parked comment"),
    ([], "no parked comment"),
])
def test_issue_4077_with_no_trusted_comment_after_the_newest_parked_comment_it_exits_3_printing_nothing(
        decision, run_cli, comments, why):
    park_decision, set_comments = decision
    set_comments(comments)

    code, out, err = run_cli(park_decision, ["42"])

    assert (code, out) == (3, "")
    assert why in err


STRANGER = {"author_association": "NONE", "user": {"login": "a-stranger"}}


def test_issue_4077_a_strangers_comment_never_counts_neither_the_exact_decision_text_nor_a_parked_heading(
        decision, run_cli):
    park_decision, comments = decision
    comments([PARK, {**STRANGER, "body": "Take design B."}])

    assert run_cli(park_decision, ["42"])[:2] == (3, "")

    comments([PARK, {**OWNER, "body": "Take design B."}, {**STRANGER, "body": PARK["body"]},
              {**STRANGER, "body": "Take design C."}])

    assert run_cli(park_decision, ["42"]) == (0, "Take design B.\n", "")
