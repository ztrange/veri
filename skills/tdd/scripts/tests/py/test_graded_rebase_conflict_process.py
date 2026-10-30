"""A rebase whose only conflict is in a GRADED file, resolved by unit by rebase-onto-default.sh, then regraded by the SKILL.md block."""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SCRIPTS = Path(__file__).resolve().parents[2]
BASE = "The widget is blue.\nIt is round.\nIt stays silent.\n"
UPSTREAM = "The widget is deep blue.\nIt is round.\nIt stays silent.\n"
BRANCH = "The widget is blue.\nIt is round.\nIt stays quite silent.\n"
REQUIREMENTS = """## guide/unit.md

| ID | Requirement | Why |
|---|---|---|
| A1 | The widget is blue. | because |
| A2 | The widget never hums. | because |
"""
PASS_STUB = """#!/bin/sh
cat > /dev/null
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}'
"""


@pytest.mark.process("a real two-branch git repository with a bare origin, rebase-onto-default.sh, the SKILL.md regrade block and prose-owed.sh")
def test_2575_a_graded_conflict_the_rebase_resolved_by_unit_is_re_signed_by_the_regrade_block_and_leaves_prose_owed_exiting_0(tmp_path):
    skill = (SCRIPTS.parents[2] / "skills" / "tdd" / "SKILL.md").read_text()
    draft = skill[skill.index("regrades every unit the run signed"):]
    block = re.search(r"```\n(.*?)```", draft, re.S).group(1).replace("<default>", "main")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_EDITOR": "true"}
    work = tmp_path / "work"
    work.mkdir()

    def git(*argv, check=True):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=check, capture_output=True, text=True)

    def commit(text, sig, message):
        (work / "guide" / "unit.md").write_text(text)
        (work / "guide" / "GRADED").write_text(f"guide/unit.md {sig * 64} 2026-01-01 {message}\n")
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    (work / "guide").mkdir()
    (work / "guide" / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    commit(BASE, "0", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(UPSTREAM, "a", "upstream regrade")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(BRANCH, "b", "branch regrade")

    rebase = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh")], cwd=work, env=env, capture_output=True, text=True)
    claude = tmp_path / "claude"
    claude.write_text(PASS_STUB)
    claude.chmod(0o755)
    regrade = subprocess.run(["bash", "-c", block], cwd=work, capture_output=True, text=True,
                             env={**env, "S": str(SCRIPTS), "CLAUDE_BIN": str(claude)})
    owed = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(work)], env=env, capture_output=True, text=True)

    row = (work / "guide" / "GRADED").read_text()
    assert rebase.returncode == 0, rebase.stdout + rebase.stderr
    assert (regrade.returncode, "b" * 64 in row, "a" * 64 in row) == (0, False, False), regrade.stdout + regrade.stderr + row
    assert (owed.returncode, owed.stdout) == (0, ""), owed.stderr
