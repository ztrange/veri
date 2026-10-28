"""Case for the never-asks rule in skills/tdd/SKILL.md standing beside the two instructions to ask the user."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
PREFLIGHT = SKILL.with_name("PREFLIGHT.md")


def _flat(text):
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))


def test_2433_never_asks_rule_is_discharged_by_a_needs_user_bail_beside_both_asks():
    text = SKILL.read_text().replace("*", "").replace("`", "")
    rule = re.search(r"A conductor never asks the user a question.*?(?:\n\n|$)", text, re.S)
    preflight = re.search(r"\n1\. Git repo & clean tree\..*?(?=\n\d+\. )",
                          "\n" + PREFLIGHT.read_text().replace("*", "").replace("`", ""), re.S)
    detecting = re.search(r"\n## Detecting the test command\n.*?(?=\n## )", text, re.S)
    assert rule, "SKILL.md has no never-asks rule paragraph"
    assert preflight, "PREFLIGHT.md has no preflight check 1"
    assert detecting, "SKILL.md has no Detecting the test command section"
    para = _flat(rule.group(0))
    problems = [f"the rule does not name {name}" for name in ("preflight check 1", "Detecting the test command")
                if name not in para]
    if "needs-user" not in para:
        problems.append("the rule does not say an ask is discharged by a needs-user bail")
    for name, site in (("preflight check 1", preflight), ("Detecting the test command", detecting)):
        ask = _flat(site.group(0))
        if "ask" not in ask:
            problems.append(f"{name} no longer asks the user")
        elif "needs-user" not in ask:
            problems.append(f"{name} asks the user without bailing needs-user: {ask!r}")
    assert not problems, f"the never-asks rule stands unqualified beside the asks: {'; '.join(problems)}: {para!r}"
