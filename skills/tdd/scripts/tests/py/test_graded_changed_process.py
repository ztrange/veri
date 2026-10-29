"""graded-changed.sh <base-sha>: names the files listed in a GRADED file that differ between <base-sha> and HEAD."""
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("a real git repository and graded-changed.sh")
def test_2653_exits_0_and_prints_nothing_when_no_graded_file_differs_between_the_base_and_head(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "skills" / "tdd").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    git("init", "-q", "-b", "main")
    (work / "skills" / "tdd" / "unit.md").write_text("graded prose\n")
    (work / "skills" / "tdd" / "GRADED").write_text("skills/tdd/unit.md " + "0" * 64 + " 2026-01-01 sig\n")
    (work / "other.txt").write_text("one\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (work / "other.txt").write_text("two\n")
    git("commit", "-q", "-am", "ungraded change")

    result = subprocess.run(["sh", str(SCRIPTS / "graded-changed.sh"), base], cwd=work, env=env, capture_output=True, text=True)

    assert (result.returncode, result.stdout) == (0, ""), result.stderr
