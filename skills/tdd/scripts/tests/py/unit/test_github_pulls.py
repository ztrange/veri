"""In-process cases for veri/github.py's pull request reads: open_pulls, pulls_in, open_pulls_text and closed_issues."""
import importlib
import json

import pytest


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


REST_SHAPED = {"number": 7, "draft": True, "body": "Closes #3", "state": "open",
               "url": "https://api.github.com/repos/o/r/pulls/7", "html_url": "https://github.com/o/r/pull/7",
               "head": {"ref": "tdd/3-x", "sha": "abc"}, "labels": [{"name": "parked"}]}
GRAPHQL_SHAPED = {"number": 8, "isDraft": False, "body": None, "state": "OPEN",
                  "url": "https://github.com/o/r/pull/8", "headRefName": "tdd/4-y", "headRefOid": "def",
                  "labels": [{"name": "a"}, {"name": "b"}]}
REST_LIST = "gh api repos/{owner}/{repo}/pulls?state=open&per_page=100&page=%d"
FIELDS = "number,url"


def test_open_pulls_reads_the_rest_pages_and_names_both_shapes_the_same_way(github, fake_processes):
    fake = fake_processes.answers({
        REST_LIST % 1: (0, json.dumps([REST_SHAPED, {"number": 9}]) + "\n", ""),
        REST_LIST % 2: (0, "[]\n", ""),
    })
    pulls = github.open_pulls(FIELDS)
    assert fake.calls == [REST_LIST % 1, REST_LIST % 2]
    assert pulls[0] == github.Pull(number=7, url="https://api.github.com/repos/o/r/pulls/7",
                                   html_url="https://github.com/o/r/pull/7", draft=True, head_ref="tdd/3-x",
                                   head_sha="abc", body="Closes #3", state="OPEN", labels=("parked",))
    assert (pulls[1].number, pulls[1].draft, pulls[1].url, pulls[1].html_url, pulls[1].head_ref, pulls[1].head_sha,
            pulls[1].body, pulls[1].state, pulls[1].labels) == (9, None, None, None, "", None, "", "", ())


def test_open_pulls_reads_a_graphql_answer_into_the_same_record_when_the_driver_is_graphql(github, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    fake = fake_processes.answers({
        "gh pr list --state open --limit 10000 --json " + FIELDS: (0, json.dumps([GRAPHQL_SHAPED]), ""),
    })
    pulls = github.open_pulls(FIELDS)
    assert len(fake.calls) == 1
    assert pulls == [github.Pull(number=8, url="https://github.com/o/r/pull/8", html_url=None, draft=False,
                                 head_ref="tdd/4-y", head_sha="def", body="", state="OPEN", labels=("a", "b"))]


def test_open_pulls_falls_back_to_rest_when_the_driver_is_auto_and_graphql_refuses(github, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    fake = fake_processes.answers({
        "gh pr list": (1, "", "refused"),
        REST_LIST % 1: (0, json.dumps([REST_SHAPED]), ""),
        REST_LIST % 2: (0, "[]", ""),
    })
    assert [p.number for p in github.open_pulls(FIELDS)] == [7]
    assert fake.calls[0].startswith("gh pr list") and fake.calls[1:] == [REST_LIST % 1, REST_LIST % 2]


def test_open_pulls_asks_for_one_head_branch_and_leaves_gh_its_default_limit_when_limit_is_none(github, fake_processes, monkeypatch):
    fake = fake_processes.answers({"gh api": [(0, "[]", "")]})
    assert github.open_pulls(FIELDS, head="tdd/3-x") == []
    assert fake.calls == ["gh api repos/{owner}/{repo}/pulls?state=open&per_page=100&head={owner}:tdd/3-x&page=1"]
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    fake = fake_processes.answers({"gh pr list": (0, "[]", "")})
    github.open_pulls(FIELDS, head="tdd/3-x", limit=None)
    assert fake.calls == ["gh pr list --head tdd/3-x --state open --json " + FIELDS]


def test_open_pulls_asks_for_every_state_and_one_repo_when_told(github, fake_processes):
    fake = fake_processes.answers({"gh api": [(0, "[]", "")]})
    github.open_pulls(FIELDS, state="all", repo="o/r")
    assert fake.calls == ["gh api repos/o/r/pulls?state=all&per_page=100&page=1"]


def test_open_pulls_reads_prs_json_from_the_fixture_directory_and_starts_no_process(github, fake_processes, monkeypatch, tmp_path):
    (tmp_path / "prs.json").write_text(json.dumps([REST_SHAPED, GRAPHQL_SHAPED]))
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake = fake_processes.answers({})
    assert [p.number for p in github.open_pulls(FIELDS)] == [7, 8]
    assert fake.calls == []


def test_open_pulls_filters_a_fixture_by_the_head_ref_of_its_rest_shape(github, fake_processes, monkeypatch, tmp_path):
    (tmp_path / "prs.json").write_text(json.dumps([REST_SHAPED, GRAPHQL_SHAPED]))
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    assert [p.number for p in github.open_pulls(FIELDS, head="tdd/3-x")] == [7]
    assert github.open_pulls(FIELDS, head="tdd/4-y") == []


def test_open_pulls_raises_no_answer_when_the_first_page_is_refused(github, fake_processes):
    fake_processes.answers({"gh api": (1, "", "HTTP 500")})
    with pytest.raises(github.NoAnswer):
        github.open_pulls(FIELDS)


def test_open_pulls_text_carries_the_pages_read_in_the_no_answer_of_a_later_page(github, fake_processes):
    fake_processes.answers({REST_LIST % 1: (0, "[1]\n", ""), REST_LIST % 2: (1, "", "HTTP 500")})
    with pytest.raises(github.NoAnswer) as refused:
        github.open_pulls_text(FIELDS)
    assert refused.value.answer == "[1]"


def test_pulls_in_reads_back_to_back_documents_and_raises_a_value_error_on_text_that_is_not_json(github):
    assert [p.number for p in github.pulls_in('[{"number": 1}][{"number": 2}]')] == [1, 2]
    assert github.pulls_in("") == []
    with pytest.raises(ValueError):
        github.pulls_in("not json")


@pytest.mark.parametrize("body, loose, issues", [
    ("Closes #1\nCloses #22", False, ["1", "22"]),
    (None, False, []),
    ("closes #5 and discloses #6", False, []),
    ("Unclosed Closes #7", False, ["7"]),
    ("closes #5 and discloses #6 and Closes #7", True, ["5", "6", "7"]),
    ("CLOSES #8", True, []),
])
def test_closed_issues_reads_the_issue_numbers_a_body_closes_in_order(github, body, loose, issues):
    assert github.closed_issues(body, loose=loose) == issues


def test_pull_reads_one_pull_request_by_url_or_number_over_rest_into_the_same_record(github, fake_processes):
    raw = dict(REST_SHAPED, mergeable=True)
    fake = fake_processes.answers({"gh api": (0, json.dumps(raw), "")})
    by_url = github.pull("https://github.com/o/r/pull/7", "o/r")
    by_number = github.pull(7)
    assert fake.calls == ["gh api repos/o/r/pulls/7", "gh api repos/{owner}/{repo}/pulls/7"]
    assert by_url == by_number and by_url.mergeable is True
    assert (by_url.number, by_url.draft, by_url.head_sha, by_url.body) == (7, True, "abc", "Closes #3")


def test_pull_says_none_for_a_flag_the_answer_does_not_carry(github, fake_processes):
    fake_processes.answers({"gh api": (0, '{"number": 7, "head": {}}', "")})
    pull = github.pull(7)
    assert (pull.draft, pull.mergeable, pull.head_sha) == (None, None, None)
    fake_processes.answers({"gh api": (0, '{"number": 7, "head": {"sha": null}}', "")})
    assert github.pull(7).head_sha == ""


def test_pull_raises_no_answer_with_gh_s_stderr_as_its_detail_and_echoes_none_of_it(github, fake_processes, capsys):
    fake_processes.answers({"gh api": (1, "", "HTTP 404: Not Found\n")})
    with pytest.raises(github.NoAnswer) as refused:
        github.pull(7)
    assert (refused.value.detail, capsys.readouterr().err) == ("HTTP 404: Not Found\n", "")


def test_pull_raises_a_value_error_on_an_answer_that_is_not_json(github, fake_processes):
    fake_processes.answers({"gh api": (0, "<html>502</html>", "")})
    with pytest.raises(ValueError):
        github.pull(7)


@pytest.mark.parametrize("cross, expected", [(True, True), (False, False)])
def test_a_graphql_record_says_whether_its_head_is_in_another_repository_by_is_cross_repository(github, cross, expected):
    assert github.pulls_in(json.dumps([dict(GRAPHQL_SHAPED, isCrossRepository=cross)]))[0].cross_repository is expected


@pytest.mark.parametrize("head_repo, base_repo, expected", [
    ({"full_name": "o/r"}, {"full_name": "o/r"}, False),
    ({"full_name": "stranger/r"}, {"full_name": "o/r"}, True),
    (None, {"full_name": "o/r"}, True),
    ({"full_name": "o/r"}, None, True),
    ({}, {}, True),
])
def test_a_rest_record_s_head_is_in_another_repository_unless_its_head_and_base_name_the_same_one(
        github, head_repo, base_repo, expected):
    raw = dict(REST_SHAPED, head=dict(REST_SHAPED["head"], repo=head_repo), base={"ref": "main", "repo": base_repo})
    assert github.pulls_in(json.dumps([raw]))[0].cross_repository is expected


def test_joined_issues_asks_gh_pr_list_for_the_field_that_says_where_a_pr_s_head_is_3973(github, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    fake = fake_processes.answers({"gh pr list": (0, "[]", "")})
    github.joined_issues("stack")
    assert fake.calls == [
        "gh pr list --base stack --state merged --limit 10000 --json number,body,state,baseRefName,isCrossRepository"]


def test_merged_pulls_are_the_pull_requests_the_answer_says_merged_into_the_base_with_their_number_body_and_side(
        github, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")
    fake_processes.answers({"gh pr list": (0, json.dumps([
        {"number": 4, "body": "Closes #9", "state": "MERGED", "baseRefName": "stack", "isCrossRepository": False},
        {"number": 5, "body": "Closes #9", "state": "MERGED", "baseRefName": "stack", "isCrossRepository": True},
        {"number": 6, "body": "Closes #9", "state": "CLOSED", "baseRefName": "stack", "isCrossRepository": False},
        {"number": 7, "body": "Closes #9", "state": "MERGED", "baseRefName": "trunk", "isCrossRepository": False},
    ]), "")})

    found = github.merged_pulls("stack")

    assert [(pr.number, pr.body, pr.cross_repository) for pr in found] == [(4, "Closes #9", False), (5, "Closes #9", True)]


def test_pr_body_edit_patches_the_pull_requests_body_over_rest_and_a_refusal_is_no_answer(github, fake_processes):
    fake = fake_processes.answers({"gh api": (0, "{}", "")})

    github.pr_body_edit(4, "Reverted from stack by abc")

    assert fake.argvs == [["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/pulls/4", "-f",
                           "body=Reverted from stack by abc"]]
    fake_processes.answers({"gh api": (1, "", "HTTP 403")})
    with pytest.raises(github.NoAnswer):
        github.pr_body_edit(4, "x")


@pytest.mark.parametrize("raw", [{"number": 1}, {"number": 1, "isCrossRepository": None}])
def test_a_record_that_does_not_say_where_its_head_is_reads_as_another_repository(github, raw):
    assert github.pulls_in(json.dumps([raw]))[0].cross_repository is True


def test_gh_pr_create_posts_head_base_title_and_body_to_the_rest_pulls_route_and_answers_the_url_issue_4084(
        github, fake_processes):
    fake = fake_processes.answers({"gh api": (0, "https://github.com/o/r/pull/12\n", "")})

    url = github.gh_pr_create("veri-install", "main", "a title", "a body")

    assert url == "https://github.com/o/r/pull/12"
    assert fake.argvs == [["gh", "api", "-X", "POST", "repos/{owner}/{repo}/pulls", "-f", "head=veri-install",
                           "-f", "base=main", "-f", "title=a title", "-f", "body=a body", "-q", ".html_url"]]
