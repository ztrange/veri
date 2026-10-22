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


def test_1866_skill_and_resume_say_a_resumes_missing_opt_in_label_is_expected():
    problems = []
    for doc in (SKILL.with_name("RESUME.md"),):
        plain = _plain(doc.read_text())
        found = re.search(r"on a resume[^.]*missing opt-in label is expected[^.]*"
                          r"(?:\.[^.]*)?never (?:stop|ask)[^.]*(?:stop|ask)", plain)
        if not found:
            problems.append(f"{doc.name} does not say a resume's missing opt-in label is expected and never a reason to stop or ask")
    assert not problems, "; ".join(problems)


def test_2112_bail_md_no_verdict_entry_names_the_script_of_every_no_verdict_bail_site():
    root = SKILL.parent
    known = ("verify.sh", "grade-prose.sh", "skill-edit-step.sh")
    bail = (root / "BAIL.md").read_text()
    start = bail.index("- `no-verdict`")
    entry = bail[start:bail.index("\n- `", start + 1)]
    unnamed = []
    for doc in (root / "SKILL.md", root / "SKILL-EDIT.md"):
        text = doc.read_text()
        for site in re.finditer("no-verdict", text):
            before = text[:site.start()]
            script = max(known, key=before.rfind)
            if before.rfind(script) >= 0 and script not in entry:
                line = text.count("\n", 0, site.start()) + 1
                unnamed.append(f"{doc.name}:{line} ({script})")
    assert not unnamed, "BAIL.md's no-verdict entry does not name the script of: " + ", ".join(unnamed)
