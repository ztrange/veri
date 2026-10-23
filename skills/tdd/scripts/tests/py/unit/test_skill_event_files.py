"""SKILL.md hands Stopping and the reconcile leaf to STOPPING.md and RECONCILE.md, read as text (#1716)."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


EVENT_FILES = {
    "BAIL.md": r"\*\*bail\*\*|\bbails with\b|→ bail",
    "PIN.md": r"\bthe pin path\b|\bcontinue at the pin\b",
    "REVISE.md": r"enter the \*\*revise loop|^\s*\*\*revise loop\*\* for red|revise under|bounded revise loop|goes round the revise loop|a revise of the",
    "RECONCILE.md": r"reconcile leaf",
    "STOPPING.md": r"\bgo(es)? to \*Stopping\*",
    "RESUME.md": r"\bresum(e|ing) (the run|at)\b",
    "SKILL-EDIT.md": r"⟦skill-edit⟧ step",
}


def unpointed_sends(text):
    lines = text.splitlines()
    found = []
    for event_file, trigger in EVENT_FILES.items():
        pointer = f"`<base directory>/{event_file}`"
        for i, line in enumerate(lines):
            nearby = line + " " + (lines[i + 1] if i + 1 < len(lines) else "")
            if re.search(trigger, line) and pointer not in nearby:
                found.append((event_file, i + 1))
    return found


def _lines():
    return SKILL.read_text().splitlines()


def _lines_with_pin():
    return _lines() + SKILL.with_name("PIN.md").read_text().splitlines()


def _outside_red(lines):
    inside, kept = False, []
    for line in lines:
        if line.startswith("#### "):
            inside = line.startswith("#### Red")
        if not inside:
            kept.append(line)
    return kept


def _outside_green(lines):
    inside, kept = False, []
    for line in lines:
        if line.startswith("#### "):
            inside = line.startswith("#### Green")
        if not inside:
            kept.append(line)
    return kept


def test_every_line_sending_the_run_to_stopping_points_at_stopping_md_1716():
    """Subject is source text: each line of SKILL.md that sends the run to *Stopping* names the file to read."""
    sends = [line for line in _outside_green(_lines_with_pin()) if re.search(EVENT_FILES["STOPPING.md"], line)]

    assert len(sends) == 4
    assert [line for line in sends if "`<base directory>/STOPPING.md`" not in line] == []


def test_every_line_launching_the_reconcile_leaf_points_at_reconcile_md_1716():
    """Subject is source text: each line of SKILL.md naming the reconcile leaf names the file to read."""
    launches = [line for line in _outside_green(_lines()) if "reconcile leaf" in line]

    assert len(launches) >= 1
    assert [line for line in launches if "`<base directory>/RECONCILE.md`" not in line] == []


def test_skill_md_no_longer_carries_the_stopping_or_reconciling_sections_1716():
    """Subject is source text: the moved sections and their distinctive lines are gone from SKILL.md."""
    text = SKILL.read_text()

    assert [line for line in _lines() if line in ("## Stopping", "## Reconciling a rejected push")] == []
    assert [marker for marker in ("event.sh stop mode=", "reconcile-ledger.before") if marker in text] == []


def test_every_line_sending_the_run_into_the_pin_points_at_pin_md_1852():
    """Subject is source text: each SKILL.md line sending a run into the pin names PIN.md, to Read, on PASSES."""
    sends = [line for line in _outside_red(_lines()) if re.search(EVENT_FILES["PIN.md"], line)]

    assert len(sends) >= 1
    missing = [
        line for line in sends
        if not ("`<base directory>/PIN.md`" in line and "`Read`" in line and "`AGAINST_UNMODIFIED: PASSES`" in line)
    ]
    assert missing == []


def test_the_pin_section_lives_in_pin_md_not_skill_md_1852():
    """Subject is source text: the pin heading and its two distinctive lines are in PIN.md and gone from SKILL.md."""
    heading = "## Already satisfied — the pin"
    markers = ("git commit -m \"test: pin", "VERI_PHASE=pin $S/event.sh pin")
    skill = SKILL.read_text()
    pin = SKILL.with_name("PIN.md").read_text()

    assert [line for line in _lines() if line == heading] == []
    assert [marker for marker in markers if marker in skill] == []
    assert heading in pin.splitlines()
    assert [marker for marker in markers if marker not in pin] == []


def test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855():
    """Subject is source text: each site entering the revise loop names REVISE.md to Read; the budget default stays."""
    sites = EVENT_FILES["REVISE.md"]
    lines = _outside_green(_outside_red(_lines_with_pin()))
    entering = [i for i, line in enumerate(lines) if re.search(sites, line)]

    assert len(entering) >= 6
    missing = [
        lines[i] for i in entering
        if not ("`<base directory>/REVISE.md`" in lines[i] + " " + lines[i + 1] and "`Read`" in lines[i] + " " + lines[i + 1])
    ]
    assert missing == []
    assert re.search(r"`REVISE_BUDGET`[^.]*?\*\*default (\d+)\*\*", SKILL.read_text()).group(1) == "2"


def test_the_revise_section_lives_in_revise_md_not_skill_md_1855():
    """Subject is source text: the revise heading and its three distinctive lines are in REVISE.md, gone from SKILL.md."""
    heading = "## Revising on a REJECT"
    markers = (
        "$S/event.sh revise budget=",
        "build-develop-prompt.sh exhausted",
        "exhausted-outcome.sh < .tdd/develop-exhausted.out",
    )
    skill = SKILL.read_text()
    revise = SKILL.with_name("REVISE.md").read_text()

    assert [line for line in _lines() if line == heading] == []
    assert [marker for marker in markers if marker in skill] == []
    assert [line for line in revise.splitlines() if line == heading] == [heading]
    assert [marker for marker in markers if marker not in revise] == []


def test_the_guard_reports_no_unpointed_send_in_the_real_skill_md_2075():
    """Subject is source text: the event-pointer guard run over SKILL.md reports no place, for every row of its table."""
    assert unpointed_sends(SKILL.read_text()) == []
