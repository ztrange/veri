"""In-process cases for veri/coverage_blocker.py: the body it writes names the new issue as a blocker."""
import importlib
import pathlib

import pytest

from veri.blocked_by import blockers


@pytest.fixture
def coverage_blocker():
    return importlib.import_module("veri.coverage_blocker")


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_body_has_no_blocked_by_heading(
        monkeypatch, coverage_blocker):
    original = "## Problem\n\nx"
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: original)
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    body = written.get("60", "")
    assert (code, blockers(body, ""), all(line in body.split("\n") for line in original.split("\n"))) == (0, [77], True)
