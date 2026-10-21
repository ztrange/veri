"""SKILL.md's Scope & plan paragraph on the guard-subject marker."""
import re

from conftest import SCRIPTS


def test_skill_md_guard_subject_paragraph_names_a_pytest_guard_suite_and_conftest_and_says_the_path_is_matched_exactly_1775():
    text = (SCRIPTS.parent / "SKILL.md").read_text()
    paragraph = next(p for p in re.split(r"\n\s*\n", text) if "⟦guard-subject: <path>⟧" in p)
    flat = " ".join(paragraph.split())
    suite = re.search(r"skills/tdd/scripts/tests/py/test_\w+\.py", flat)
    assert suite, flat
    assert "skills/tdd/scripts/tests/py/conftest.py" in flat, flat
    repo = SCRIPTS.parent.parent.parent
    for path in (suite.group(), "skills/tdd/scripts/tests/py/conftest.py"):
        assert (repo / path).is_file(), path
    assert re.search(r"full repo-relative path, matched exactly", flat), flat
    assert re.search(r"directory or a glob", flat), flat
