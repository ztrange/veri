"""Cases for what skills/tdd/SKILL.md tells a conductor that would ask the user a question, read as text."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def _plain(text):
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).lower()


def test_1866_skill_bails_needs_user_instead_of_asking_the_user():
    text = _plain(SKILL.read_text())
    paragraph = next((p for p in re.split("\n\n", SKILL.read_text())
                      if "needs-user" in p and "bail" in p.lower()), "")
    plain = _plain(paragraph)
    problems = []
    if not re.search(r"\b(ask|asks|asking)\b[^.]*\b(question|user)\b|\bnever asks\b", plain):
        problems.append("no instruction covers a conductor that would ask the user a question")
    if not re.search(r"\bdecline", plain):
        problems.append("no instruction covers a conductor that would decline the next instruction")
    if not re.search(r"bail[^.]*cause needs-user", plain):
        problems.append("the instruction does not bail with cause needs-user")
    if not re.search(r"question[^.]*in full[^.]*bail comment|in full[^.]*question[^.]*bail comment", plain):
        problems.append("the question is not written in full into the bail comment")
    assert "needs-user" in text and not problems, "; ".join(problems) or "SKILL.md never names needs-user"
