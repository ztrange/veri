"""Audit of the tree itself: only ledger.py spells the ledger file name."""
import re

import pytest

LEDGER_NAME = re.compile(r"issue-(?:%s|%d|\{[^}]*\})\.md")


@pytest.mark.tree_audit("every module under skills/tdd/scripts/veri/")
def test_no_module_but_ledger_spells_the_ledger_file_name(veri_modules_index):
    spelling = sorted(f"{name}.py" for name in veri_modules_index.names
                      if name != "ledger" and LEDGER_NAME.search(veri_modules_index.text(name)))

    assert spelling == []
