"""No file under skills/tdd/ but a REQUIREMENTS.md names a retired pin name (#4770).

The names are built from pieces, so this file does not match its own grep.
"""
import subprocess

import pytest

import conftest
from conftest import ROOT

UNPIN = "unpin" + "nable"
RETIRED = ("pin-reject" + "-route", "retired " + UNPIN, UNPIN + "-missing", UNPIN + "-step", "--" + UNPIN)


@pytest.mark.process("git: git grep -nF over the repository's tracked files under skills/tdd/")
@pytest.mark.tree_audit("every tracked file under skills/tdd/ but a REQUIREMENTS.md")
def test_no_file_under_skills_tdd_but_a_requirements_md_names_a_retired_pin_name(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    patterns = [arg for name in RETIRED for arg in ("-e", name)]
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-nF", *patterns, "--", "skills/tdd", ":(exclude,glob)**/REQUIREMENTS.md"],
        capture_output=True, text=True,
    )
    hits = [":".join(line.split(":", 2)[:2]) for line in found.stdout.splitlines()]

    assert (found.returncode, hits) == (1, []), "named at: " + ", ".join(hits)
