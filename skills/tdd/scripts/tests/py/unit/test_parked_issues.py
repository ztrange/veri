"""In-process cases for veri/parked_issues.py, the reader of the parked set."""
import importlib
import json

import pytest


def first_four(out):
    return "".join("\t".join(line.split("\t")[:4]) + "\n" for line in out.splitlines())


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

    assert (code, first_four(out), "2403" in err) == (0, "2373\tAn issue\twaiting on upstream\tupstream ships\n", False)


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


def test_main_3683_prints_a_dash_fifth_field_for_a_parked_comment_with_no_blocked_by_line(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: upstream ships"}]

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\tupstream ships\t-\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_an_open_issue(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "/issues/3420" in path or "/pulls/3420" in path:
            return json.dumps([{"number": 3420, "state": "open", "merged": False}])
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        assert "3420" in path
        return json.dumps({"number": 3420, "state": "open", "merged": False})

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3420 merges\twaiting\n")


def test_main_3683_exits_2_naming_the_blocker_and_printing_nothing_when_gh_gives_no_answer_for_a_blocker(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3420" in path:
            raise parked_issues.github.NoAnswer("")
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        raise parked_issues.github.NoAnswer("")

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, "3420" in err) == (2, "", True)


def test_main_3683_prints_ready_as_the_fifth_field_when_the_blocked_by_line_names_only_closed_issues(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3420 merges\nBlocked by: #3420"}]
    closed = json.dumps({"number": 3420, "state": "closed"})

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3420" in path:
            return closed
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        assert "3420" in path
        return closed

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3420 merges\tready\n")


def test_main_3683_prints_ready_as_the_fifth_field_when_the_blocked_by_line_names_a_merged_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "closed", "merged": True})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return answer(path)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\tready\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_a_pull_request_closed_unmerged(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "closed", "merged": False})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return answer(path)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\twaiting\n")


def test_main_3683_prints_waiting_as_the_fifth_field_when_the_blocked_by_line_names_an_open_pull_request(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "open", "pull_request": {"url": "x"}})
    as_pull = json.dumps({"number": 3309, "state": "open", "merged": False})

    def answer(path):
        assert "3309" in path
        return as_pull if "/pulls/" in path else as_issue

    def fake_rest_list(path, *args):
        if "/comments" in path:
            return json.dumps(comments)
        if "3309" in path:
            return answer(path)
        return json.dumps(listing)

    def fake_api(path, *args, **kwargs):
        return answer(path)

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out) == (0, "3324\tAn issue\twaiting on upstream\t#3309 merges\twaiting\n")


def test_main_3683_exits_2_naming_the_blocker_and_printing_no_row_when_gh_gives_no_answer_to_the_merged_state_read(
        monkeypatch, parked_issues, run_cli):
    listing = [{"number": 3324, "title": "An issue"}]
    comments = [{"body": "### ⏸ Parked\n\nCause: waiting on upstream\nUnblock: #3309 merges\nBlocked by: #3309"}]
    as_issue = json.dumps({"number": 3309, "state": "closed", "pull_request": {"url": "x"}})

    def fake_rest_list(path, *args):
        return json.dumps(comments if "/comments" in path else listing)

    def fake_api(path, *args, **kwargs):
        if "/pulls/3309" in path:
            raise parked_issues.github.NoAnswer("")
        return as_issue

    monkeypatch.setattr(parked_issues.github, "gh_rest_list", fake_rest_list)
    monkeypatch.setattr(parked_issues.github, "gh_api", fake_api)

    code, out, err = run_cli(parked_issues, [])

    assert (code, out, err) == (
        2, "", "parked-issues.sh: no answer from gh to reading the merged state of #3309\n")
