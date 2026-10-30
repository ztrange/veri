"""SKILL.md hands Stopping and the reconcile leaf to STOPPING.md and RECONCILE.md, read as text (#1716)."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


EVENT_FILES = {
    "BAIL.md": r"\*\*bails?\*\*|\bbails (with|as)\b|\bbail with\b|→ bail|\bis a bail\b|(?<=: )bail\b(?![-.]\w)",
    "PIN.md": r"\bthe pin path\b|\bcontinue at the pin\b",
    "REVISE.md": r"enter the \*\*revise loop|^\s*\*\*revise loop\*\* for red|revise under|bounded revise loop|goes round the revise loop|a revise of the",
    "RECONCILE.md": r"reconcile leaf",
    "STOPPING.md": r"\bgo(es)? to \*Stopping\*",
    "RESUME.md": r"\bresum(e|ing) (the run|at)\b",
    "SKILL-EDIT.md": r"⟦skill-edit⟧ step",
    "REFACTOR-KIND.md": r"the `## Refactor` section `capture-spec\.sh` writes",
    "PHASED.md": r"hands over a step listing `⟦phases: …⟧`",
    "STRUCTURAL.md": r"\bone structural pass\b",
}


PLACED = r"\)?[.:](\s|\Z)"


def unpointed_sends(text):
    ends = [m.end() for m in re.finditer(r"\.(?=\s|\Z)", text)] + [len(text)]
    found = []
    for event_file, trigger in EVENT_FILES.items():
        pointer = f"`<base directory>/{event_file}`"
        start = 0
        for end in ends:
            sentence = text[start:end]
            match = re.search(trigger, sentence)
            if match:
                line = text.count("\n", 0, start + match.start())
                if pointer not in sentence:
                    found.append((event_file, line + 1))
            start = end
    return found


def misplaced_pointers(text):
    found = []
    for event_file in EVENT_FILES:
        for m in re.finditer(re.escape(f"`<base directory>/{event_file}`"), text):
            if not re.match(PLACED, text[m.end():]):
                found.append((event_file, text.count("\n", 0, m.start()) + 1))
    return found


def misplaced_send_pointers(text):
    ends = [m.end() for m in re.finditer(r"\.(?=\s|\Z)", text)] + [len(text)]
    found = []
    for event_file, trigger in EVENT_FILES.items():
        pointer = f"`<base directory>/{event_file}`"
        start = 0
        for end in ends:
            sentence = text[start:end]
            if re.search(trigger, sentence):
                for m in re.finditer(re.escape(pointer), sentence):
                    if not re.match(PLACED, sentence[m.end():]):
                        found.append((event_file, text.count("\n", 0, start + m.start()) + 1))
            start = end
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

    assert len(sends) == 2
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
    """Subject is source text: each site entering the revise loop, in SKILL.md, PIN.md or PHASED.md, names REVISE.md to Read; the budget default stays."""
    sites = EVENT_FILES["REVISE.md"]
    lines = _outside_green(_outside_red(_lines_with_pin())) + SKILL.with_name("PHASED.md").read_text().splitlines()
    entering = [i for i, line in enumerate(lines) if re.search(sites, line)]

    assert len(entering) >= 6
    missing = [
        lines[i] for i in entering
        if not ("`<base directory>/REVISE.md`" in lines[i] + " " + lines[i + 1] and "`Read`" in lines[i] + " " + lines[i + 1])
    ]
    assert missing == []
    assert re.search(r"`REVISE_BUDGET`[^.]*?\*\*default (\d+)\*\*", SKILL.read_text()).group(1) == "2"


def test_the_revise_section_lives_in_revise_md_not_skill_md_1855():
    """Subject is source text: the revise heading and its three distinctive lines are gone from SKILL.md."""
    heading = "## Revising on a REJECT"
    markers = (
        "$S/event.sh revise budget=",
        "build-develop-prompt.sh exhausted",
        "exhausted-outcome.sh < .tdd/develop-exhausted.out",
    )
    skill = SKILL.read_text()

    assert [line for line in _lines() if line == heading] == []
    assert [marker for marker in markers if marker in skill] == []


def test_the_guard_reports_no_unpointed_send_in_the_real_skill_md_2075():
    """Subject is source text: the event-pointer guard run over SKILL.md reports no place, for every row of its table."""
    assert unpointed_sends(SKILL.read_text()) == []


def test_the_guard_reports_a_bolded_bails_and_a_bolded_bail_with_cause_without_a_pointer_2075():
    """Subject is the guard: '**bails**' and '**bail with cause …**' with no colon before them each name BAIL.md and their line."""
    text = "\n".join([
        "The step **bails** once the budget is spent.",
        "Exit 1 again: then **bail with cause `x`** and stop.",
    ])

    assert [line for event_file, line in unpointed_sends(text) if event_file == "BAIL.md"] == [1, 2]


def test_the_guard_ignores_a_bail_script_or_hyphenated_name_after_a_colon_2075():
    """Subject is the guard: a name such as 'bail.sh' or 'bail-cause' after a colon is not a bare bail instruction."""
    text = "\n".join([
        "The helper is named: bail.sh in the scripts.",
        "The label it prints: bail-stuck for that case.",
    ])

    assert unpointed_sends(text) == []


def test_the_guard_reports_no_misplaced_bail_pointer_in_the_real_skill_md_2075():
    """Subject is source text: the pointer-placement check run over SKILL.md reports no pointer that fails to end its sentence."""
    assert [place for place in misplaced_pointers(SKILL.read_text()) if place[0] == "BAIL.md"] == []


def test_the_send_scoped_placement_check_finds_no_misplaced_pointer_in_skill_md_or_any_event_file_2339():
    """Subject is source text: the send-scoped placement check over SKILL.md and every file a pointer names reports no misplaced pointer."""
    files = [SKILL] + [SKILL.parent / name for name in EVENT_FILES]
    assert {f.name: misplaced_send_pointers(f.read_text()) for f in files} == {f.name: [] for f in files}


def test_the_moved_sections_distinctive_lines_are_absent_from_skill_md_and_present_in_their_files_2218():
    """Subject is source text: each moved section's distinctive lines sit in STRUCTURAL.md, PHASED.md and REFACTOR-KIND.md, not in SKILL.md."""
    moved = {
        "STRUCTURAL.md": ["$S/transform-touches-tests.sh <base-sha> <bound>", "event.sh structural-pass transforms="],
        "PHASED.md": ["tick-ledger.sh --phase-owed", "no-product-caller.sh <old-interface>"],
        "REFACTOR-KIND.md": ["coverage-blocker.sh <n>", ".tdd/issue-<n>-proof"],
    }
    skill = SKILL.read_text()
    in_skill = [line for lines in moved.values() for line in lines if line in skill]
    missing = [(name, line) for name, lines in moved.items() for line in lines if line not in (SKILL.parent / name).read_text()]
    assert (in_skill, missing) == ([], [])


def test_the_structural_phased_and_refactor_kind_files_exist_and_skill_md_tells_the_run_to_read_each_2218():
    """Subject is source text: each of the three files exists, and SKILL.md holds a sentence naming it under <base directory>/ that says to Read it."""
    text = SKILL.read_text()
    sentences = re.split(r"\.(?=\s|\Z)", text)
    missing = []
    for name in ("STRUCTURAL.md", "PHASED.md", "REFACTOR-KIND.md"):
        pointer = f"`<base directory>/{name}`"
        reads = any(pointer in s and "`Read`" in s for s in sentences)
        if not ((SKILL.parent / name).is_file() and reads):
            missing.append(name)
    assert missing == []
