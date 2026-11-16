"""In-process cases for veri/github.py's check_runs (PRD 034.2b): a sha's check runs read by sha, page by page within a
bound, a garbled answer being no answer; gh is faked at the process boundary."""
import importlib
import json

import pytest


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


SHA = "a" * 40
PAGE = "gh api repos/{owner}/{repo}/commits/%s/check-runs?filter=latest&per_page=100&page=%%d" % SHA


def run(conclusion="success", status="completed"):
    return {"name": "x", "status": status, "conclusion": conclusion}


def test_check_runs_reads_the_latest_attempt_of_each_check_by_sha_every_page_until_the_total_is_read(github, fake_processes):
    first = [run()] * 100
    fake = fake_processes.answers({
        PAGE % 1: (0, json.dumps({"total_count": 101, "check_runs": first}), ""),
        PAGE % 2: (0, json.dumps({"total_count": 101, "check_runs": [run(None, "in_progress")]}), ""),
    })

    got = github.check_runs(SHA)

    assert (len(got), got[-1], fake.calls) == (101, ("in_progress", None), [PAGE % 1, PAGE % 2])


@pytest.mark.parametrize("answer", [
    (1, "", "HTTP 502\n"), (0, "garbage", ""), (0, "[]", ""), (0, '{"check_runs": []}', ""),
    (0, '{"total_count": "1", "check_runs": []}', ""), (0, '{"total_count": 1, "check_runs": {}}', ""),
    (0, '{"total_count": 1, "check_runs": ["x"]}', ""), (0, '{"total_count": 1, "check_runs": [{"status": 1}]}', ""),
    (0, '{"total_count": 1, "check_runs": [{"status": "completed", "conclusion": 5}]}', ""),
    (0, '{"total_count": 2, "check_runs": [{"status": "completed", "conclusion": "success"}]}', ""),
    (0, '{"total_count": 100000, "check_runs": []}', ""),
])
def test_check_runs_is_no_answer_for_a_failed_read_a_garbled_or_short_answer_or_more_runs_than_its_bound(
        github, fake_processes, answer):
    fake_processes.answers({"gh api": [answer, (0, json.dumps({"total_count": 2, "check_runs": []}), "")]})

    with pytest.raises(github.NoAnswer):
        github.check_runs(SHA)


def test_check_runs_refuses_a_sha_that_is_not_hex_before_any_read(github, fake_processes):
    fake = fake_processes.answers({})

    with pytest.raises(ValueError):
        github.check_runs("main; rm")
    assert fake.calls == []
