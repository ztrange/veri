"""In-process cases for veri/github.py's workflow_runs, stack-red.sh's read (PRD 034.3a): the newest 100 workflow runs
GitHub lists for one branch; gh is faked at the process boundary."""
import importlib
import json

import pytest


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


LIST = "gh api repos/{owner}/{repo}/actions/runs?branch=stack&per_page=100"


def run(n, status="completed", conclusion="failure", created="2026-11-16T10:00:%02dZ", head_repo="o/r", attempt=1):
    return {"id": n, "run_attempt": attempt, "workflow_id": 900 + n % 2, "head_sha": "%040x" % n, "html_url": "https://github.com/o/r/actions/runs/%d" % n,
            "status": status, "conclusion": conclusion, "created_at": created % n if "%" in created else created,
            "head_branch": "stack", "repository": {"full_name": "o/r"},
            "head_repository": {"full_name": head_repo} if head_repo else None}


def answer(*runs):
    return json.dumps({"total_count": len(runs), "workflow_runs": list(runs)})


def test_workflow_runs_reads_one_page_of_100_for_the_branch_keeping_only_this_repositorys_runs(github, fake_processes):
    fake = fake_processes.answers({LIST: (0, answer(run(1), run(2, "in_progress", None, attempt=2), run(3, head_repo="evil/r"),
                                                     run(4, head_repo=None)), "")})

    got = github.workflow_runs("stack")

    assert (got, fake.calls) == ([("%040x" % 1, "https://github.com/o/r/actions/runs/1", "completed", "failure",
                                   "2026-11-16T10:00:01Z", 1, 901),
                                  ("%040x" % 2, "https://github.com/o/r/actions/runs/2", "in_progress", None,
                                   "2026-11-16T10:00:02Z", 2, 900)], [LIST])


@pytest.mark.parametrize("given", [
    (1, "", "HTTP 502\n"), (0, "<html>", ""), (0, "[]", ""), (0, '{"workflow_runs": {}}', ""),
    (0, answer(dict(run(1), head_sha="not a sha")), ""), (0, answer(dict(run(1), status=None)), ""),
    (0, answer(dict(run(1), conclusion=7)), ""), (0, answer(dict(run(1), created_at="yesterday")), ""),
    (0, answer(dict(run(1), html_url="https://evil.example/1")), ""), (0, json.dumps({"workflow_runs": ["x"]}), ""),
    (0, answer(dict(run(1), run_attempt=0)), ""), (0, answer(dict(run(1), run_attempt="2")), ""),
    (0, answer(dict(run(1), run_attempt=True)), ""), (0, answer(dict(run(1), workflow_id="ci")), ""),
    (0, answer({k: v for k, v in run(1).items() if k != "workflow_id"}), ""),
    (0, answer({k: v for k, v in run(1).items() if k != "run_attempt"}), ""),
])
def test_workflow_runs_is_no_answer_for_a_failed_read_or_an_answer_not_of_the_workflow_runs_shape(
        github, fake_processes, given):
    fake_processes.answers({LIST: given})

    with pytest.raises(github.NoAnswer):
        github.workflow_runs("stack")


LOG = "gh run view 42 --log-failed"


def test_run_failed_log_reads_the_failed_job_log_of_one_workflow_run(github, fake_processes):
    fake = fake_processes.answers({LOG: (0, "job\tstep\t2026-11-16T10:00:00Z FAILED a.py::t - x\n", "")})

    got = github.run_failed_log("42")

    assert (got, fake.calls) == ("job\tstep\t2026-11-16T10:00:00Z FAILED a.py::t - x\n", [LOG])


@pytest.mark.parametrize("run_id", ["42", "4x"])
def test_run_failed_log_is_no_answer_when_gh_gives_none_or_the_run_id_is_not_a_number(github, fake_processes, run_id):
    fake = fake_processes.answers({LOG: (1, "", "HTTP 502\n")})

    with pytest.raises(github.NoAnswer):
        github.run_failed_log(run_id)
    assert len(fake.calls) == (run_id == "42")


ATTEMPT = "gh api repos/{owner}/{repo}/actions/runs/42/attempts/1"


def test_run_attempt_reads_one_attempt_of_a_workflow_run_as_status_and_conclusion(github, fake_processes):
    fake = fake_processes.answers({ATTEMPT: (0, json.dumps(dict(run(42), run_attempt=1)), "")})

    got = github.run_attempt("42", 1)

    assert (got, fake.calls) == (("completed", "failure"), [ATTEMPT])


@pytest.mark.parametrize("run_id, attempt, given", [
    ("42", 1, (1, "", "HTTP 404\n")), ("42", 1, (0, "<html>", "")), ("42", 1, (0, "[]", "")),
    ("42", 1, (0, json.dumps(dict(run(42), status=None)), "")), ("42", 1, (0, json.dumps(dict(run(42), conclusion=7)), "")),
    ("42", 1, (0, json.dumps(dict(run(42), run_attempt=2)), "")), ("4x", 1, (0, "{}", "")), ("42", 0, (0, "{}", "")),
])
def test_run_attempt_is_no_answer_for_a_failed_read_a_garbled_answer_or_a_bad_run_id_or_attempt(
        github, fake_processes, run_id, attempt, given):
    fake_processes.answers({ATTEMPT: given})

    with pytest.raises(github.NoAnswer):
        github.run_attempt(run_id, attempt)
