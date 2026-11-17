"""The smell catalogue, skills/tdd/SMELLS.md, that the refactor and structural prompts include (#4115)."""
from conftest import SCRIPTS

SMELLS = SCRIPTS.parent / "SMELLS.md"


def test_the_smell_catalogue_is_at_most_60_lines():
    assert len(SMELLS.read_bytes().splitlines()) <= 60
