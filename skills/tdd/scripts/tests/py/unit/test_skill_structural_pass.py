"""Cases for where skills/tdd/SKILL.md runs the issue's one structural pass, read as text."""
import pathlib

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_refactor_overflow_script_and_module_no_longer_exist():
    scripts = SKILL.parent / "scripts"
    leftovers = [p for p in ("refactor-overflow.sh", "veri/refactor_overflow.py") if (scripts / p).exists()]
    assert leftovers == []
