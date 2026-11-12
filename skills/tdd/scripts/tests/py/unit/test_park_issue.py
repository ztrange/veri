"""In-process cases for park-issue.sh's `--blocked-by`: the parked issue names its blocker under `## Blocked by`."""
import importlib

import pytest

BODY = "## What happened\n\nIt broke.\n\n## Blocked by\n\nNone.\n\nTest command: make test\n"


@pytest.fixture
def park(monkeypatch):
    """park_issue with every gh write faked; returns (module, calls, edited bodies)."""
    park_issue = importlib.import_module("veri.park_issue")
    github = park_issue.github
    calls, edited = [], []

    def edit(number, body_file):
        calls.append(("edit", number))
        edited.append(open(body_file).read())

    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: calls.append(("view", number, field)) or BODY)
    monkeypatch.setattr(github, "gh_issue_edit", edit)
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: calls.append(("ensure", label)))
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: calls.append(("label", number, label)))
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: calls.append(("unlabel", number, label)))
    monkeypatch.setattr(github, "gh_issue_comment", lambda number, body: calls.append(("comment", number)))
    return park_issue, calls, edited


def test_blocked_by_replaces_none_with_the_blocker_keeps_test_command_last_and_still_parks(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert edited == ["## What happened\n\nIt broke.\n\n## Blocked by\n\n- #9\n\nTest command: make test\n"]
    assert ("label", "42", "parked") in calls and ("comment", "42") in calls


def test_blocked_by_may_come_before_the_pr_argument(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "--blocked-by", "9", "cause", "unblock", "77"])

    assert (code, err) == (0, "")
    assert "- #9" in edited[0]
    assert ("label", "77", "parked") in calls


def test_a_blocker_already_listed_is_not_written_again(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    monkeypatch.setattr(park_issue.github, "gh_issue_view", lambda number, field: BODY.replace("None.", "- #9"))

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "9"])

    assert (code, edited) == (0, [])
    assert ("label", "42", "parked") in calls


def test_without_the_flag_the_body_is_never_read_or_written(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock"])

    assert code == 0
    assert [call for call in calls if call[0] in ("view", "edit")] == []


@pytest.mark.parametrize("argv", [
    ["42", "cause", "unblock", "--blocked-by"],
    ["42", "cause", "unblock", "--blocked-by", "x9"],
    ["42", "cause", "unblock", "--blocked-by", "0"],
    ["42", "cause", "unblock", "--blocked-by", "9", "--blocked-by", "10"],
    ["42", "cause", "unblock", "--blocked-by", "42"],
])
def test_a_malformed_or_self_blocker_exits_2_and_writes_nothing(park, run_cli, argv):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, argv)

    assert code == 2
    assert calls == []
    assert err


def test_no_answer_on_the_body_edit_exits_2_before_the_issue_is_labelled_parked(park, run_cli, monkeypatch):
    park_issue, calls, edited = park

    def refuse(number, body_file):
        raise park_issue.github.NoAnswer("")

    monkeypatch.setattr(park_issue.github, "gh_issue_edit", refuse)

    code, out, err = run_cli(park_issue, ["42", "cause", "unblock", "--blocked-by", "9"])

    assert code == 2
    assert "no answer from gh to the Blocked by write" in err
    assert not [call for call in calls if call[0] in ("label", "comment")]


def test_issue_3683_the_parked_comment_carries_one_blocked_by_line_beside_cause_and_unblock(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert "Cause: pin-recheck exit 2" in lines
    assert "Unblock: #9 lands" in lines
    assert lines.count("Blocked by: #9") == 1


def test_issue_3683_a_comma_separated_blocker_list_names_every_blocker_under_blocked_by(park, run_cli):
    park_issue, calls, edited = park

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 and #10 land", "--blocked-by", "9,10"])

    assert (code, err) == (0, "")
    assert len(edited) == 1
    assert park_issue.blocked_by.blockers(edited[0], "") == [9, 10]
    assert "None." not in edited[0]


def test_issue_3683_a_comma_separated_blocker_list_is_one_blocked_by_line_in_the_parked_comment(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 and #10 land", "--blocked-by", "9,10"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert lines.count("Blocked by: #9, #10") == 1
    assert len([l for l in lines if l.startswith("Blocked by:")]) == 1


def test_issue_3683_the_parked_comment_with_a_pr_argument_carries_both_the_pr_line_and_the_blocked_by_line(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "cause", "#9 lands", "77", "--blocked-by", "9"])

    assert (code, err) == (0, "")
    assert len(comments) == 1
    lines = comments[0].splitlines()
    assert lines.count("PR: 77") == 1
    assert lines.count("Blocked by: #9") == 1


def test_issue_3683_without_blocked_by_the_parked_comment_is_exactly_cause_and_unblock(park, run_cli, monkeypatch):
    park_issue, calls, edited = park
    comments = []
    monkeypatch.setattr(park_issue.github, "gh_issue_comment", lambda number, body: comments.append(body))

    code, out, err = run_cli(park_issue, ["42", "pin-recheck exit 2", "#9 lands"])

    assert (code, err) == (0, "")
    assert comments == ["### ⏸ Parked\nCause: pin-recheck exit 2\nUnblock: #9 lands\n"]
