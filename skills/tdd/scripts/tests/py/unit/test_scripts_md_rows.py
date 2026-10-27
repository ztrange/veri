"""Every `$S/<script>.sh` bullet in skills/tdd/SCRIPTS.md is graded by an SC row."""
import re

from conftest import SCRIPTS

SKILL = SCRIPTS.parent


def test_every_scripts_md_bullet_has_an_sc_row_2486():
    catalogue = (SKILL / "SCRIPTS.md").read_text()
    requirements = (SKILL / "REQUIREMENTS.md").read_text()
    section = requirements.split("\n## skills/tdd/SCRIPTS.md\n", 1)[1]
    section = re.split(r"^## ", section, maxsplit=1, flags=re.M)[0]
    rows = [line for line in section.splitlines() if re.match(r"\| SC\d+ \|", line)]
    bullets = re.findall(r"^- `\$S/([\w.-]+\.sh)", catalogue, flags=re.M)
    missing = [b for b in bullets if not any(b in row for row in rows)]
    assert bullets and rows
    assert not missing, f"{len(bullets)} bullets, {len(rows)} SC rows; no SC row for: {missing}"
