"""The fence-opening rule has one home: veri/markdown_sections.py."""
import re

import pytest

from conftest import SCRIPTS


@pytest.mark.tree_audit("every module under skills/tdd/scripts, to find affected_suites and skill_sections")
def test_no_module_other_than_markdown_sections_holds_a_fence_opening_rule_for_affected_suites_or_skill_sections():
    opener = re.compile(r"""["'](?:`{3}|~{3})""")
    readers = [path for path in SCRIPTS.rglob("*.py") if path.name in ("affected_suites.py", "skill_sections.py")]
    holders = sorted(str(path.relative_to(SCRIPTS)) for path in readers if opener.search(path.read_text(encoding="utf-8")))
    assert len(readers) == 2
    assert holders == []
