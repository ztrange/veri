"""Mechanical facts about ADR-0034."""
import pytest

from conftest import SCRIPTS

ADR_DIR = SCRIPTS.parents[2] / "docs" / "adr"


@pytest.mark.tree_audit("reads the repository's docs/adr")
def test_adr_0034_exists_and_names_adr_0031():
    adr = ADR_DIR / "0034-a-run-files-one-candidates-issue-for-what-it-leaves.md"
    assert adr.is_file()
    assert "0031" in adr.read_text()
