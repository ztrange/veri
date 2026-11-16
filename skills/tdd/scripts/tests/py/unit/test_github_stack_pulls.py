"""In-process cases for veri/github.py's tracking pull request calls (PRD 034.2a): stack_pulls reads the open pull
requests from one head branch to one base, pr_open opens one, ready; gh is faked at the process boundary."""
import importlib
import json

import pytest


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


LIST = "gh api repos/{owner}/{repo}/pulls?state=open&head={owner}:stack&base=trunk&per_page=100&page=%d"
CREATE = "gh api -X POST repos/{owner}/{repo}/pulls"


def pull(number, head="stack", base="trunk", draft=False):
    return {"number": number, "html_url": "https://github.com/o/r/pull/%d" % number, "draft": draft,
            "head": {"ref": head, "sha": "abc"}, "base": {"ref": base}, "state": "open"}


def test_stack_pulls_keeps_only_pull_requests_the_answer_itself_names_from_head_to_base_reading_every_full_page(
        github, fake_processes):
    full = [pull(n) for n in range(1, 100)] + [pull(100, base="main")]
    fake = fake_processes.answers({
        LIST % 1: (0, json.dumps(full), ""),
        LIST % 2: (0, json.dumps([pull(200, head="other"), pull(201)]), ""),
    })

    got = github.stack_pulls("stack", "trunk")

    assert ([p.number for p in got], fake.calls) == (list(range(1, 100)) + [201], [LIST % 1, LIST % 2])


@pytest.mark.parametrize("answer", [(1, "", "HTTP 502\n"), (0, "not json", ""), (0, '{"message": "x"}', ""),
                                    (0, '["a string"]', ""), (0, json.dumps([{"head": "stack", "base": {}}]), "")])
def test_stack_pulls_is_no_answer_for_a_failed_read_or_an_answer_that_is_not_a_list_of_pull_request_objects(
        github, fake_processes, answer):
    fake_processes.answers({LIST % 1: answer})

    with pytest.raises(github.NoAnswer):
        github.stack_pulls("stack", "trunk")


def test_stack_pulls_is_no_answer_past_its_page_bound_rather_than_reading_without_end(github, fake_processes):
    fake = fake_processes.answers({"gh api": (0, json.dumps([pull(n) for n in range(100)]), "")})

    with pytest.raises(github.NoAnswer):
        github.stack_pulls("stack", "trunk")
    assert len(fake.calls) == github.PULL_PAGES


def test_pr_open_posts_a_ready_pull_request_from_head_to_base_and_returns_its_url(github, fake_processes):
    fake = fake_processes.answers({CREATE: (0, json.dumps(pull(9)), "")})

    url = github.pr_open("stack", "trunk", "the title", "the body")

    assert url == "https://github.com/o/r/pull/9"
    assert fake.argvs == [["gh", "api", "-X", "POST", "repos/{owner}/{repo}/pulls", "-f", "head=stack", "-f", "base=trunk",
                           "-f", "title=the title", "-f", "body=the body", "-F", "draft=false"]]


@pytest.mark.parametrize("answer", [(1, "", "HTTP 422: Validation Failed\n"), (0, "garbage", ""), (0, "[]", ""),
                                    (0, '{"html_url": 7}', ""), (0, '{"html_url": "https://evil.example/x"}', "")])
def test_pr_open_is_no_answer_for_a_refused_call_or_an_answer_naming_no_pull_request_url(github, fake_processes, answer):
    fake_processes.answers({CREATE: answer})

    with pytest.raises(github.NoAnswer):
        github.pr_open("stack", "trunk", "t", "b")
