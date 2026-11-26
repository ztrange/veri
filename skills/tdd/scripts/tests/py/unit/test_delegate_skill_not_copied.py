"""veri holds no copy of the installed `delegate` skill (#4095, DL4): vdev works through it where installed."""
from pathlib import Path

import pytest
from veri.git import git

import conftest

REPO = Path(__file__).resolve().parents[6]


@pytest.mark.process("git ls-files over the repository")
def test_no_tracked_file_lives_under_skills_delegate(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    tracked = git("ls-files", "--", "skills/delegate", cwd=REPO, check=True, capture_output=True, text=True).stdout

    assert tracked == "", f"veri tracks a copy of the delegate skill: {tracked.split()}"
