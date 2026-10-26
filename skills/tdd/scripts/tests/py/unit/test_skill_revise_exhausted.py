"""Cases for what skills/tdd/SKILL.md tells the conductor to do when a step's revise budget runs out, and where its step-cost check runs."""
import pathlib

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.with_name("REVISE.md")

STEP_COST = "step-cost.sh"


def _both():
    return SKILL.read_text() + "\n" + REVISE_MD.read_text()


def after_wait(leaf):
    marker = f"wait-leaf.sh {leaf}"
    inside, out = False, []
    for line in _both().splitlines():
        if not inside:
            inside = marker in line
            continue
        if "detach-leaf.sh" in line or "tick-ledger.sh" in line:
            break
        out.append(line)
    return out


def test_skill_md_checks_step_cost_sh_after_neither_develop_refactor_nor_verify_refactor_and_the_cost_heading_says_why_no_check_follows_the_green_commit():
    problems = []
    text = _both()
    for leaf in ("develop-refactor", "verdict-refactor"):
        if f"wait-leaf.sh {leaf}" not in text:
            problems.append(f"never waits on {leaf}")
        elif any(STEP_COST in line for line in after_wait(leaf)):
            problems.append(f"runs {STEP_COST} after {leaf}, which runs after the step's green commit")
    assert not problems, "\n".join(problems)
