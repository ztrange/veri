"""In-process cases for github.trusted_comment, the one rule every reader of issue comments shares (PRD 022.3)."""
import importlib

import pytest


@pytest.fixture
def github(monkeypatch):
    module = importlib.import_module("veri.github")
    monkeypatch.setattr(module, "authenticated_login", lambda: "veri-operator")
    return module


def comment(association, login="someone", body="hello", **more):
    return {"author_association": association, "user": {"login": login, "type": "User"}, "body": body, **more}


DONE = "### ✅ Done — https://github.com/o/r/pull/9"


@pytest.mark.parametrize("record, trusted", [
    (comment("OWNER"), True),
    (comment("COLLABORATOR"), True),
    (comment("MEMBER"), False),
    (comment("CONTRIBUTOR"), False),
    (comment("FIRST_TIME_CONTRIBUTOR"), False),
    (comment("NONE"), False),
    (comment("NONE", body=DONE), False),
    (comment("NONE", body=DONE, created_at="2026-11-01T00:00:00Z", updated_at="2026-11-02T00:00:00Z"), False),
    (comment("OWNER", body=DONE, created_at="2026-11-01T00:00:00Z", updated_at="2026-11-02T00:00:00Z"), True),
    ({"author_association": "NONE", "user": {"login": "some-app[bot]", "type": "Bot"}, "body": DONE,
      "performed_via_github_app": {"slug": "some-app"}}, False),
], ids=["owner", "collaborator", "member", "contributor", "first-time-contributor", "none",
        "stranger-with-veri-marker-text", "stranger-edited", "owner-edited", "bot-not-veri"])
def test_a_comment_is_trusted_by_its_owner_or_collaborator_association_and_never_by_its_body(github, record, trusted):
    assert github.trusted_comment(record) is trusted


@pytest.mark.parametrize("record, association, trusted", [
    ({"author_association": "OWNER"}, "OWNER", True),
    ({"author_association": "MEMBER"}, "MEMBER", True),
    ({"author_association": "COLLABORATOR"}, "COLLABORATOR", True),
    ({"author_association": "CONTRIBUTOR"}, "CONTRIBUTOR", False),
    ({"author_association": "FIRST_TIME_CONTRIBUTOR"}, "FIRST_TIME_CONTRIBUTOR", False),
    ({"author_association": "FIRST_TIMER"}, "FIRST_TIMER", False),
    ({"author_association": "NONE"}, "NONE", False),
    ({}, "unknown", False),
    ({"author_association": None}, "unknown", False),
    ({"author_association": ["OWNER"]}, "unknown", False),
    (None, "unknown", False),
])
def test_an_issue_author_is_trusted_by_owner_member_or_collaborator_and_one_that_cannot_be_read_is_unknown_3977(
        github, record, association, trusted):
    assert (github.author_association(record), github.trusted_author(record, github.ISSUE_AUTHOR_ASSOCIATIONS)) == (
        association, trusted)


def test_a_member_whose_login_is_the_authenticated_gh_users_is_trusted(github):
    assert github.trusted_comment(comment("MEMBER", login="veri-operator", body=DONE)) is True


def test_the_authenticated_login_is_read_at_most_once_per_process(github, monkeypatch):
    reads = []
    monkeypatch.setattr(github, "authenticated_login", lambda: reads.append("user") or "veri-operator")
    answers = [github.trusted_comment(comment(association, login=login))
               for association, login in (("NONE", "a"), ("MEMBER", "veri-operator"), ("CONTRIBUTOR", "b"))]
    assert (answers, reads) == ([False, True, False], ["user"])


def test_with_the_authenticated_login_unreadable_the_association_alone_answers_and_nothing_raises(github, monkeypatch):
    reads = []

    def no_answer():
        reads.append("user")
        raise github.NoAnswer("", "HTTP 502")

    monkeypatch.setattr(github, "authenticated_login", no_answer)
    answers = [github.trusted_comment(comment(association, login="veri-operator"))
               for association in ("NONE", "MEMBER", "OWNER", "COLLABORATOR")]
    assert (answers, reads) == ([False, False, True, True], ["user", "user"])


def test_a_failed_login_read_is_not_kept_so_a_later_read_that_answers_trusts_the_gh_users_comment(github, monkeypatch):
    answers = [None, "veri-operator"]

    def login():
        answer = answers.pop(0)
        if answer is None:
            raise github.NoAnswer("", "HTTP 502")
        return answer

    monkeypatch.setattr(github, "authenticated_login", login)
    mine = comment("MEMBER", login="veri-operator")
    assert [github.trusted_comment(mine), github.trusted_comment(mine)] == [False, True]


@pytest.mark.parametrize("record, login_readable", [
    ({"author_association": "OWNER", "body": DONE}, True),
    ({"author_association": "OWNER", "user": None, "body": DONE}, True),
    ({"author_association": "COLLABORATOR", "user": {}, "body": DONE}, True),
    ({"author_association": "OWNER", "user": {"login": ""}, "body": DONE}, True),
    ({"author_association": "OWNER", "user": {"login": 7}, "body": DONE}, True),
    ({"author_association": "NONE", "user": None, "body": DONE}, False),
    ({"author_association": "NONE", "user": {}, "body": DONE}, False),
    ({"user": {"login": "someone"}, "body": DONE}, True),
    (comment("owner"), True),
    (comment("MANNEQUIN"), True),
    (comment(["OWNER"]), True),
    (DONE, True),
    (None, True),
    ([comment("OWNER")], True),
], ids=["no-user", "deleted-user", "user-without-login", "empty-login", "login-not-text", "deleted-user-login-unreadable",
        "no-login-login-unreadable", "no-association", "association-lowercase", "association-unlisted",
        "association-not-text", "a-bare-body", "null", "a-list"])
def test_a_comment_whose_author_cannot_be_read_or_whose_association_the_rule_does_not_list_is_not_trusted(
        github, monkeypatch, record, login_readable):
    def no_answer():
        raise github.NoAnswer("")

    if not login_readable:
        monkeypatch.setattr(github, "authenticated_login", no_answer)
    assert github.trusted_comment(record) is False
