"""Case for SKILL.md stating both VERI_REBASED_TIP_SUITE modes where the rebased tip's full run appears."""
import pathlib
import re

SKILL_MD = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

PLACES = {
    "after an exit 0 from the rebase script": (r"first\s+line\s+it\s+printed", 900),
    "after a verify-rebase PASS": (r"Only\s+on\s+a\s+verify-rebase\s+.PASS.", 600),
    "in the CI-conflict graded-only rebase": (r"conflict\s+is\s+first\s+offered\s+to", 700),
    "in the CI-conflict rebase": (r"through\s+the\s+existing\s+rebase\s+path", 700),
}


def test_skill_md_states_both_rebased_tip_suite_modes_at_each_place_the_rebased_tip_s_full_run_appears():
    text = " ".join(SKILL_MD.read_text(encoding="utf-8").split())
    missing = []
    for place, (anchor, span) in PLACES.items():
        found = re.search(anchor, text)
        window = text[found.start():found.start() + span] if found else ""
        if not (re.search(r"VERI_REBASED_TIP_SUITE=.?local", window) and re.search(r"under\s+.?ci.?\b", window)):
            missing.append(place)
    assert missing == [], f"SKILL.md does not state both modes {missing}"


CLAUDE_MD = pathlib.Path(__file__).resolve().parents[6] / "CLAUDE.md"


def test_claude_md_sentence_on_when_the_full_suite_runs_names_the_ci_mode():
    text = " ".join(CLAUDE_MD.read_text(encoding="utf-8").split())
    found = re.search(r"[^.]*`make test`, the\s+\*\*full suite\*\*, runs once per PR.*?(?<=\))[^.]*\.", text)
    sentence = found.group(0) if found else ""
    assert re.search(r"VERI_REBASED_TIP_SUITE=ci", sentence), f"CLAUDE.md full-suite sentence does not name the ci mode: {sentence!r}"
