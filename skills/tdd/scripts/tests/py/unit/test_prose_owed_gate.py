"""The make unit gate for prose grades, read as the Makefile's text."""
import re
from pathlib import Path

MAKEFILE = Path(__file__).resolve().parents[6] / "Makefile"


def recipe(targets):
    lines, inside = [], False
    for line in MAKEFILE.read_text().split("\n"):
        if line.startswith(targets + ":"):
            inside = True
        elif inside and line.startswith("\t"):
            lines.append(line)
        elif inside and line.strip():
            break
    return "\n".join(lines).replace("\\\n", " ")


def test_make_unit_fails_naming_each_unit_prose_owed_sh_prints_when_it_prints_anything():
    text = recipe("test unit")
    assert text, "the Makefile has no 'test unit' recipe"
    run = re.search(r"skills/tdd/scripts/prose-owed\.sh \. *(?P<tail>[^;]*);", text)
    assert run, "the unit recipe never runs prose-owed.sh on the repository root"
    assert re.fullmatch(r"\|\| *fail=1 *", run["tail"]), "a non-zero prose-owed.sh exit does not fail the run, or its output is redirected: %r" % run["tail"]
    assert "SUITES FAILED" in text and "exit 1" in text, "a failed leg does not end the recipe red"
