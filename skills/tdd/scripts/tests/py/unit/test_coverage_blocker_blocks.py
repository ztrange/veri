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


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_blocked_by_heading_has_no_none_or_list_line(
        monkeypatch, coverage_blocker):
    original = "## Problem\n\nx\n\n## Blocked by\n\nWaiting on the design.\n\n## Notes\n\ny"
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


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_only_heading_is_blocked_by_with_a_colon(
        monkeypatch, coverage_blocker):
    original = "## Problem\n\nx\n\n## Blocked by:\n\nWaiting on the design.\n\n## Notes\n\ny"
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


def test_main_1262_exits_0_with_the_new_issue_a_blocker_when_the_heading_carries_none_replaced_or_list_lines_kept(
        monkeypatch, coverage_blocker):
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    seen = []
    for original, expected in (("## Problem\n\nx\n\n## Blocked by\n\nNone.\n\nTest command: make test", [77]),
                               ("## Problem\n\nx\n\n## Blocked by\n\n- #5\n- #6\n\nTest command: make test", [5, 6, 77])):
        monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field, body=original: body)
        code = coverage_blocker.main(["60"])
        body = written.get("60", "")
        kept = [line for line in original.split("\n") if line != "None."]
        seen.append((code, sorted(blockers(body, "")), all(line in body.split("\n") for line in kept), expected))

    assert [(c, b, k) for c, b, k, _ in seen] == [(0, e, True) for *_, e in seen]


def test_main_1262_writes_nothing_exits_2_and_names_the_issue_on_stderr_when_the_create_answers_no_issue_number(
        monkeypatch, capsys, coverage_blocker):
    edits = []

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create", lambda title, text: "")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: edits.append(n))

    code = coverage_blocker.main(["60"])

    assert (code, edits, "60" in capsys.readouterr().err) == (2, [], True)


def test_main_1262_writes_nothing_and_exits_2_when_the_new_issue_is_numbered_but_the_body_it_would_write_still_reads_as_unblocked(
        monkeypatch, capsys, coverage_blocker):
    edits = []

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view",
                        lambda n, field: "## Blocked by\n\nfoo\n\n## Blocked by\n\n- #5")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: edits.append(n))

    code = coverage_blocker.main(["60"])

    assert (code, edits, "60" in capsys.readouterr().err) == (2, [], True)


def test_main_1262_writes_the_blocker_directly_under_a_heading_followed_by_prose_and_keeps_every_byte_of_the_prose(
        monkeypatch, coverage_blocker):
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view",
                        lambda n, field: "## Problem\n\nx\n\n## Blocked by\nWaiting on design.\n\n## Notes\n\ny")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    assert (code, written.get("60")) == (
        0, "## Problem\n\nx\n\n## Blocked by\n- #77\nWaiting on design.\n\n## Notes\n\ny\n")
