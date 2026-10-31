"""Medium case: the run-state rule ensure-run-state-ignored.sh writes lets `git add -A` stage a mutations record."""
import subprocess
from pathlib import Path

import pytest

ENSURE = Path(__file__).resolve().parents[2] / "ensure-run-state-ignored.sh"


@pytest.mark.process("git and ensure-run-state-ignored.sh against a throwaway repository")
def test_git_add_all_stages_the_mutations_record_under_the_run_state_rule_2506(tmp_path):
    def git(*words):
        return subprocess.run(["git", *words], cwd=tmp_path, capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    subprocess.run([str(ENSURE), str(tmp_path)], capture_output=True, text=True, timeout=20, check=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7-mutations.md").write_text("record\n")
    git("add", "-A")
    assert ".tdd/issue-7-mutations.md" in git("diff", "--cached", "--name-only").splitlines()
