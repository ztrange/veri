"""PRD 014.1: the old pages and their helpers are gone."""
import subprocess

import pytest

import conftest
from conftest import ROOT, SCRIPTS

DASH = "dash" + "board"
RLOG = "render" + "-leaf-" + "log"
RLOG_PY = "render" + "_leaf_" + "log"
SCOST = "session" + "-cost"
SSCOST_PY = "session" + "_cost"


def test_no_path_under_the_prd_014_1_remove_list_exists():
    removed = [
        f"{DASH}.sh",
        f"{DASH}.html",
        f"veri/{DASH}.py",
        f"{RLOG}.sh",
        f"veri/{RLOG_PY}.py",
        f"tests/fixtures/{RLOG}",
        f"{SCOST}.sh",
        f"veri/{SSCOST_PY}.py",
        f"tests/py/test_{DASH}.py",
        f"tests/py/test_{RLOG_PY}.py",
        f"tests/py/test_{SSCOST_PY}.py",
    ]
    assert [p for p in removed if (SCRIPTS / p).exists()] == []


@pytest.mark.process("git: git grep -iE over the repository's tracked files")
@pytest.mark.tree_audit("every tracked file outside docs/, projects/, specs/ and .tdd/")
def test_no_tracked_file_outside_the_record_names_the_removed_scripts(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    pattern = "|".join([DASH, "session" + ".cost", "render" + ".leaf." + "log"])
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-iE", pattern, "--", ".",
         ":!docs", ":!projects", ":!specs", ":!.tdd"],
        capture_output=True, text=True,
    )
    assert found.returncode == 1 and found.stdout == ""


def test_invisible_work_suite_samples_never_use_the_removed_page_name():
    text = (SCRIPTS / "tests/py/test_invisible_work.py").read_text()
    assert DASH not in text.lower()
