"""Cases for the conductor's own preservation of a troubled step's attempt, as skills/tdd/SKILL.md prescribes it."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
PRESERVE_RE = r"\$s/preserve-attempt\.sh"
MARK_RE = r"event\.sh\s+prediction-diverged([^a-z0-9-]|$)"


def bail_lines():
    section = importlib.import_module("skill_sections").section(BAIL, BAILING)
    return section.lower().splitlines()[1:]


def first_line(lines, pattern):
    return next((i for i, line in enumerate(lines) if re.search(pattern, line)), None)


def instructions():
    records, rec = [], ""
    for line in SKILL.read_text().splitlines():
        if re.match(r"[0-9]+\. ", line) or re.match(r"\s*- ", line):
            if rec:
                records.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                records.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        records.append(rec)
    return [re.sub(r"\s+", " ", r).lower() for r in records]


def test_skill_md_preserves_the_attempt_on_a_bail_before_the_bails_reset_and_beside_every_prediction_diverged_mark():
    lines = bail_lines()
    preserve = first_line(lines, PRESERVE_RE)
    reset = first_line(lines, r"git reset --hard head")
    assert preserve is not None, "Bailing section prescribes no `$S/preserve-attempt.sh` call"
    assert reset is not None, "Bailing section no longer prescribes `git reset --hard HEAD`"
    assert preserve < reset, f"bails by preserving at line {preserve}, after the reset at line {reset}"

    marks = [r for r in instructions() if re.search(MARK_RE, r)]
    assert marks, "SKILL.md prescribes no `event.sh prediction-diverged` call"
    for record in marks:
        assert re.search(PRESERVE_RE, record), f"prediction-diverged mark with no preserve-attempt.sh beside it: {record[:130]}"
