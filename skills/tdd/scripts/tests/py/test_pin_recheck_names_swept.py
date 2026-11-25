"""No file under skills/tdd/ but a REQUIREMENTS.md or a test_*.py names pin-recheck or the mutation record (#4741)."""
import subprocess

import pytest

import conftest
from conftest import ROOT

NAMES = r"pin-recheck|pin-recheck-ok|repin-failed|--recheck|mutation-record|issue-[^/ ]*-mutations\.md"


@pytest.mark.process("git: git grep -nE over the repository's tracked files under skills/tdd/")
@pytest.mark.tree_audit("every tracked file under skills/tdd/ but a REQUIREMENTS.md or a test_*.py")
def test_4741_no_file_under_skills_tdd_but_requirements_or_a_test_names_pin_recheck_or_the_mutation_record(
        monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-nE", "-e", NAMES, "--", "skills/tdd",
         ":(exclude,glob)**/REQUIREMENTS.md", ":(exclude,glob)**/test_*.py"],
        capture_output=True, text=True,
    )
    hits = [":".join(line.split(":", 2)[:2]) for line in found.stdout.splitlines()]

    assert (found.returncode, hits) == (1, []), "named at: " + ", ".join(hits)
