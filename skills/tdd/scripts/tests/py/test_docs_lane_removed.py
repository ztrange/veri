"""The generated docs page and its docs lane are gone from the tree."""
import subprocess

import pytest

import conftest
from conftest import ROOT


def test_no_path_under_the_removal_list_exists():
    walk = "walk" + "through"
    docs_owed = "docs" + "-owed.sh"
    merge_gates = "merge" + "-gates.sh"
    removed = [
        f"docs/{walk}.html",
        f"docs/build-{walk}.py",
        f"docs/check-{walk}.py",
        "docs/" + "wt",
        f"docs/{docs_owed}",
        f"docs/{merge_gates}",
        "docs/hooks",
        "docs/tests",
        "projects/docs",
        ".github/workflows/pages.yml",
        "skills/tdd/scripts/tests/py/test_docs_targets_refuse_process.py",
    ]

    assert [p for p in removed if (ROOT / p).exists()] == []


def test_make_has_none_of_the_docs_lane_targets():
    import re

    named = {"docs", "docs-test", "docs" + "-fresh", "docs" + "-check", "merge-gates", "install-hooks"}
    defined = set()
    for line in (ROOT / "Makefile").read_text().splitlines():
        if line.startswith("\t") or line.startswith("#"):
            continue
        m = re.match(r"([^:=]+?)\s*::?(?!=)", line)
        if m:
            defined.update(m.group(1).split())
        phony = re.match(r"\.PHONY\s*:(.*)", line)
        if phony:
            defined.update(phony.group(1).split())

    assert sorted(named & defined) == []


@pytest.mark.process("git: git grep -iE over the repository's tracked files")
@pytest.mark.tree_audit("every tracked file outside docs/adr/, .tdd/ and the test fixtures")
def test_no_tracked_file_outside_the_record_names_the_removed_page_or_its_lane(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    pattern = "|".join(["walk" + "through", "docs" + "-check", "docs" + "-fresh", "docs" + "-owed", "docs/" + "wt"])
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-iE", pattern, "--", ".",
         ":!docs/adr", ":!.tdd", ":!skills/tdd/scripts/tests/fixtures"],
        capture_output=True, text=True,
    )
    assert found.returncode == 1 and found.stdout == ""
