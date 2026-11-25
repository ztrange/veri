"""The repository's .gitignore admits exactly the .tdd/ kinds veri commits (PRD 025.10)."""
import subprocess

import pytest

from conftest import SCRIPTS

GITIGNORE = SCRIPTS.parents[2] / ".gitignore"
IGNORED = (".tdd/issue-1-pr-body.md", ".tdd/issue-1-spec.md", ".tdd/issue-1-pairs.md", ".tdd/issue-1-mutations.md",
           ".tdd/events.jsonl")
COMMITTED = (".tdd/issue-1.md", ".tdd/issue-1-added.md", ".tdd/issue-1-refactor-owed.md", ".tdd/issue-1-metrics.md")


@pytest.mark.process("git")
def test_4048_check_ignore_ignores_run_state_and_admits_the_four_committed_kinds(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    (tmp_path / ".gitignore").write_bytes(GITIGNORE.read_bytes())
    answer = subprocess.run(["git", "-C", str(tmp_path), "check-ignore", "--no-index", *IGNORED, *COMMITTED],
                            stdout=subprocess.PIPE, text=True)

    assert answer.stdout.splitlines() == list(IGNORED)
