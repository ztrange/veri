"""In-process cases for parallel_conductors._outcome, the finished run's report line read from the open PRs."""
import importlib
import json

import pytest


@pytest.fixture
def parallel_conductors(tmp_path, monkeypatch):
    module = importlib.import_module("veri.parallel_conductors")
    monkeypatch.setattr(module, "toplevel", lambda: str(tmp_path))
    monkeypatch.setattr(module, "_parked", lambda n: False)
    return module


@pytest.mark.parametrize("where, said", [
    ({"isCrossRepository": True}, ""),
    ({"head": {"repo": None}, "base": {"repo": {"full_name": "o/r"}}}, ""),
    ({"isCrossRepository": False}, "done https://github.com/o/r/pull/70"),
])
def test_a_ready_pr_closing_the_issue_reports_the_run_done_only_when_its_head_is_in_this_repository_3977(
        parallel_conductors, where, said):
    # A stranger's ready fork PR saying Closes #7 must not turn a run's empty outcome into `done <fork url>`.
    prs = json.dumps([dict({"body": "Closes #7", "isDraft": False, "url": "https://github.com/o/r/pull/70"}, **where)])

    assert parallel_conductors._outcome("7", 0, prs) == said
