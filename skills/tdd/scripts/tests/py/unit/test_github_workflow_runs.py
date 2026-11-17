"""In-process cases for veri/github.py's workflow_runs, stack-red.sh's read (PRD 034.3a): the newest 100 workflow runs
GitHub lists for one branch; gh is faked at the process boundary."""
import importlib
import json

import pytest


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


LIST = "gh api repos/{owner}/{repo}/actions/runs?branch=stack&per_page=100"


def run(n, status="completed", conclusion="failure", created="2026-11-16T10:00:%02dZ", head_repo="o/r"):
    return {"id": n, "head_sha": "%040x" % n, "html_url": "https://github.com/o/r/actions/runs/%d" % n,
            "status": status, "conclusion": conclusion, "created_at": created % n if "%" in created else created,
            "head_branch": "stack", "repository": {"full_name": "o/r"},
            "head_repository": {"full_name": head_repo} if head_repo else None}


def answer(*runs):
    return json.dumps({"total_count": len(runs), "workflow_runs": list(runs)})


def test_workflow_runs_reads_one_page_of_100_for_the_branch_keeping_only_this_repositorys_runs(github, fake_processes):
    fake = fake_processes.answers({LIST: (0, answer(run(1), run(2, "in_progress", None), run(3, head_repo="evil/r"),
                                                     run(4, head_repo=None)), "")})

    got = github.workflow_runs("stack")

    assert (got, fake.calls) == ([("%040x" % 1, "https://github.com/o/r/actions/runs/1", "completed", "failure",
                                   "2026-11-16T10:00:01Z"),
                                  ("%040x" % 2, "https://github.com/o/r/actions/runs/2", "in_progress", None,
                                   "2026-11-16T10:00:02Z")], [LIST])


@pytest.mark.parametrize("given", [
    (1, "", "HTTP 502\n"), (0, "<html>", ""), (0, "[]", ""), (0, '{"workflow_runs": {}}', ""),
    (0, answer(dict(run(1), head_sha="not a sha")), ""), (0, answer(dict(run(1), status=None)), ""),
    (0, answer(dict(run(1), conclusion=7)), ""), (0, answer(dict(run(1), created_at="yesterday")), ""),
    (0, answer(dict(run(1), html_url="https://evil.example/1")), ""), (0, json.dumps({"workflow_runs": ["x"]}), ""),
])
def test_workflow_runs_is_no_answer_for_a_failed_read_or_an_answer_not_of_the_workflow_runs_shape(
        github, fake_processes, given):
    fake_processes.answers({LIST: given})

    with pytest.raises(github.NoAnswer):
        github.workflow_runs("stack")
