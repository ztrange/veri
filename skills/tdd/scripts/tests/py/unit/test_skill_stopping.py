"""Cases for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as text."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_standing_bail_rule_is_stated_once_and_no_line_names_bailing_without_bail_md():
    pointer = "<base directory>/BAIL.md"
    files = [SKILL, SKILL.with_name("SCRIPTS.md"), SKILL.with_name("RECONCILE.md")]
    texts = {path.name: path.read_text().split("\n") for path in files}
    bare = [f"{name}:{n}" for name, lines in texts.items() for n, line in enumerate(lines, 1)
            if re.search(r"\bBailing\b", line) and pointer not in line]
    assert not bare, f"lines name Bailing without {pointer}: {bare}"
