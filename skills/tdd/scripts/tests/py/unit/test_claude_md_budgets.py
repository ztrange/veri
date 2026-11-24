"""CLAUDE.md's budgets invariant is a knob/axis/default table whose knobs and defaults match veri/tunables.py (#4516, PRD 042.3).

Only the knob set and each default are pinned; what an axis says is graded prose, never pinned here."""
import re

from conftest import ROOT
from veri.tunables import TUNABLES

BUDGETS = {
    "VERI_STUCK_RETRIES", "VERI_NO_VERDICT_RETRIES", "REVISE_BUDGET", "VERI_REFACTOR_BUDGET",
    "VERI_STEP_GROWTH_PERCENT", "VERI_SKILL_EDIT_BUDGET", "VERI_MISSING_REROUTE_BUDGET", "VERI_ADJUDICATE_BUDGET",
    "VERI_CI_FLAKE_RERUNS", "VERI_TEST_QUALITY_FIXES", "VERI_SURROUND_MUTANTS", "VERI_BRANCH_REPAIRS",
    "VERI_DEVIATION_BUDGET",
}


def budgets_rows(claude_md):
    section = claude_md.split("\n## Invariants worth not breaking\n", 1)[1]
    section = re.split(r"^## ", section, maxsplit=1, flags=re.M)[0]
    bullet = section.split("- **Thirteen budgets on thirteen axes, never merged**", 1)[1]
    bullet = re.split(r"^- \*\*", bullet, maxsplit=1, flags=re.M)[0]
    return dict(re.findall(r"^\s*\| `(\w+)` \| .* \| ([^|]+?) \|\s*$", bullet, flags=re.M))


def test_claude_md_s_budgets_invariant_tables_each_budget_with_its_tunables_default_4516():
    rows = budgets_rows((ROOT / "CLAUDE.md").read_text())

    assert set(rows) == BUDGETS
    assert {knob: rows[knob] for knob in BUDGETS} == {knob: TUNABLES[knob].default for knob in BUDGETS}
