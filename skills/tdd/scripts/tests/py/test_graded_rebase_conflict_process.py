"""A rebase whose only conflict is in a GRADED file, resolved with the branch side, then regraded by the SKILL.md block."""
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


@pytest.mark.process("a real two-branch git repository with a bare origin, rebase-onto-default.sh, the DRAFT-PR.md regrade block and prose-owed.sh")
def test_2575_a_graded_conflict_resolved_with_the_branch_side_is_re_signed_by_the_regrade_block_and_leaves_prose_owed_exiting_0(tmp_path):
    skill = (SCRIPTS.parents[2] / "skills" / "tdd" / "DRAFT-PR.md").read_text()
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
    git("rebase", "-q", "origin/main", check=False)
    git("checkout", "--theirs", "--", "guide/GRADED")
    git("add", "guide/GRADED")
    git("rebase", "--continue")
    claude = tmp_path / "claude"
    claude.write_text(PASS_STUB)
    claude.chmod(0o755)
    regrade = subprocess.run(["bash", "-c", block], cwd=work, capture_output=True, text=True,
                             env={**env, "S": str(SCRIPTS), "CLAUDE_BIN": str(claude)})
    owed = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(work)], env=env, capture_output=True, text=True)

    row = (work / "guide" / "GRADED").read_text()
    assert (rebase.returncode, rebase.stdout.split()) == (1, ["guide/GRADED"]), rebase.stderr
    assert (regrade.returncode, "b" * 64 in row, "a" * 64 in row) == (0, False, False), regrade.stdout + regrade.stderr + row
    assert (owed.returncode, owed.stdout) == (0, ""), owed.stderr


HEADED = "# Guide\n\n## Two words\n\nThe widget is blue.\n\n## 100% sure\n\nIt stays silent.\n"
HEADED_REQUIREMENTS = "".join("## skills/tdd/SKILL.md#%s\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                              "| A1 | The widget is blue. | because |\n| A2 | The widget never hums. | because |\n\n" % h
                              for h in ("Two words", "100% sure"))


@pytest.mark.process("a real git repository with an origin, the DRAFT-PR.md regrade block, grade-prose.sh and a stub grader")
def test_4429_the_regrade_block_regrades_branch_signed_heading_units_decoded_and_not_a_line_the_merge_base_holds(tmp_path):
    skill = (SCRIPTS.parents[2] / "skills" / "tdd" / "DRAFT-PR.md").read_text()
    draft = skill[skill.index("regrades every unit the run signed"):]
    block = re.search(r"```\n(.*?)```", draft, re.S).group(1).replace("<default>", "main")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "skills" / "tdd").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True)

    main_line = "skills/tdd/SKILL.md#Main%20only " + "e" * 64 + " 2026-01-01 id prefix\n"
    (work / "skills" / "tdd" / "SKILL.md").write_text(HEADED)
    (work / "skills" / "tdd" / "REQUIREMENTS.md").write_text(HEADED_REQUIREMENTS)
    (work / "skills" / "tdd" / "GRADED").write_text(main_line)
    git("init", "-q", "-b", "main")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env,
                   check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work")
    (work / "skills" / "tdd" / "GRADED").write_text(
        main_line + "skills/tdd/SKILL.md#Two%20words " + "a" * 64 + " 2026-01-01 id prefix\n"
        + "skills/tdd/SKILL.md#100%25%20sure " + "b" * 64 + " 2026-01-01 id prefix\n" + main_line)
    git("commit", "-q", "-am", "branch signs two heading units, and a resolution duplicates main's line")
    claude = tmp_path / "claude"
    claude.write_text(PASS_STUB)
    claude.chmod(0o755)

    regrade = subprocess.run(["bash", "-c", block], cwd=work, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                             env={**env, "S": str(SCRIPTS), "CLAUDE_BIN": str(claude)})

    graded = (work / "skills" / "tdd" / "GRADED").read_text().splitlines()
    units = [line.split(" ")[0] for line in graded]
    assert regrade.returncode == 0, regrade.stdout + regrade.stderr
    assert sorted(units) == ["skills/tdd/SKILL.md#100%25%20sure", "skills/tdd/SKILL.md#Main%20only",
                             "skills/tdd/SKILL.md#Main%20only", "skills/tdd/SKILL.md#Two%20words"], graded
    assert ["a" * 64 in line or "b" * 64 in line for line in graded] == [False] * 4, graded
