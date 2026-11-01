"""The walkthrough and its docs lane are gone from the tree."""
from conftest import ROOT


def test_no_path_under_the_removal_list_exists():
    walk = "walk" + "through"
    docs_owed = "docs" + "-owed.sh"
    merge_gates = "merge" + "-gates.sh"
    removed = [
        f"docs/{walk}.html",
        f"docs/build-{walk}.py",
        f"docs/check-{walk}.py",
        "docs/wt",
        f"docs/{docs_owed}",
        f"docs/{merge_gates}",
        "docs/hooks",
        "docs/tests",
        "projects/docs",
        ".github/workflows/pages.yml",
        "skills/tdd/scripts/tests/py/test_docs_targets_refuse_process.py",
    ]

    assert [p for p in removed if (ROOT / p).exists()] == []
