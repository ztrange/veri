"""Cases for veri/blocked_by.py that start a real process."""
import json
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

ISSUES = [
    {"number": 5, "title": "takeable", "state": "OPEN", "labels": [{"name": "ready-for-agent"}],
     "body": "## Blocked by\n\nNone.\n"},
    {"number": 99, "title": "the planted blocker", "state": "OPEN", "labels": [],
     "body": "## Blocked by\n\nNone.\n"},
]


@pytest.mark.process("solvable-issues.sh run from a copied scripts tree whose blocked_by.blockers answers [99]")
@pytest.mark.tree_audit("copies the scripts, lib and veri directories")
def test_solvable_issues_takes_its_blocker_parsing_from_the_blocked_by_module(tmp_path):
    tree = tmp_path / "scripts"
    tree.mkdir()
    shutil.copy(SCRIPTS / "solvable-issues.sh", tree)
    for directory in ("lib", "veri"):
        shutil.copytree(SCRIPTS / directory, tree / directory, ignore=shutil.ignore_patterns("__pycache__"))
    (tree / "veri" / "blocked_by.py").write_text("def blockers(*args, **kwargs):\n    return [99]\n")
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "prs.json").write_text("[]\n")
    (gh / "issues.json").write_text(json.dumps(ISSUES))
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    ran = subprocess.run([str(tree / "solvable-issues.sh")], cwd=cwd, capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "VERI_GH_JSON": str(gh),
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout) == (3, "")
