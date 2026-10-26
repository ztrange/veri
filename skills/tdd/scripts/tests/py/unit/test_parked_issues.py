"""In-process cases for veri/parked_issues.py, the reader of the parked set."""
import importlib
import json

import pytest


@pytest.fixture
def parked_issues():
    return importlib.import_module("veri.parked_issues")


def test_main_2420_lists_only_the_parked_issue_and_exits_0_when_a_parked_pull_request_carries_no_parked_comment(
        monkeypatch, parked_issues, run_cli):
    listing = [
        {"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}},
        {"number": 2373, "title": "An issue"},
    ]
    comments = {
        2373: [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: upstream ships"}],
        2403: [],
    }

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments[int(path.split("/issues/")[1].split("/")[0])])
        return json.dumps(listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, "2403" in err) == (0, "2373\tAn issue\twaiting on upstream\tupstream ships\n", False)


def test_main_2420_still_exits_2_naming_a_parked_issue_with_no_parked_comment_listed_beside_a_parked_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [
        {"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}},
        {"number": 2373, "title": "An issue"},
    ]

    def fake_rest_list(path, *args):
        return json.dumps([] if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (2, "", "parked-issues.sh: issue #2373 has no parked comment\n")


def test_main_2420_exits_3_writing_nothing_when_only_pull_requests_carry_the_parked_label(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 2403, "title": "A pull request", "pull_request": {"url": "x"}}]

    def fake_rest_list(path, *args):
        return json.dumps([] if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (3, "")
