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


def test_a_member_whose_login_is_the_authenticated_gh_users_is_trusted(github):
    assert github.trusted_comment(comment("MEMBER", login="veri-operator", body=DONE)) is True
