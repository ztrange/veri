"""Audit of the tree itself: only ledger.py spells the ledger file name."""
import re

import pytest

from conftest import ROOT

VERI = ROOT / "skills" / "tdd" / "scripts" / "veri"
LEDGER_NAME = re.compile(r"issue-(?:%s|%d|\{[^}]*\})\.md")


@pytest.mark.tree_audit("every module under skills/tdd/scripts/veri/")
def test_no_module_but_ledger_spells_the_ledger_file_name():
    spelling = sorted(p.name for p in VERI.glob("*.py") if p.name != "ledger.py" and LEDGER_NAME.search(p.read_text()))

    assert spelling == []
