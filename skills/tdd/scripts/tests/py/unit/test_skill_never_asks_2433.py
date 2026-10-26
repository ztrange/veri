"""Case for the never-asks rule in skills/tdd/SKILL.md standing beside the two instructions to ask the user."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_2433_never_asks_rule_is_discharged_by_a_needs_user_bail_beside_both_asks():
    text = SKILL.read_text()
    flat = re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))
    rule = re.search(r"A conductor never asks the user a question.*?(?:\n\n|$)", text.replace("*", "").replace("`", ""), re.S)
    assert rule, "SKILL.md has no never-asks rule paragraph"
    para = re.sub(r"\s+", " ", rule.group(0))
    problems = [f"the rule does not name {name}" for name in ("preflight check 1", "Detecting the test command")
                if name not in para]
    if "needs-user" not in para:
        problems.append("the rule does not say an ask is discharged by a needs-user bail")
    assert not problems, f"the never-asks rule stands unqualified beside the asks: {'; '.join(problems)}: {para!r}"
