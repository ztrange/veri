"""In-process cases for the three root documents' record of the selection order."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
CONTEXT_MD = "CONTEXT.md"
SKILL_MD = "skills/tdd/SKILL.md"
CLAUDE_MD = "CLAUDE.md"
LOWER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}

PRIORITY_BAND = "priority"
BUG_BAND = "bug"
ASCENDING = "ascending|by number|lowest number|increasing|numeric"
ORDERED = "first|before|then|band|ahead"
TUNABLE = "veri_priority_label"
NOT_ENLARGE = "enlarge|reorder|re-order|only.*order|never.*solvable|not.*solvable|still.*not printed"


def plain(text):
    return text.replace("*", "").replace("`", "").translate(LOWER)


def lines_of(path):
    lines = Path(path).read_text().split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def joined(lines):
    return plain("".join(line + " " for line in lines))


def entry(path, name):
    want = rf"^\*\*{name}\*\*:"
    inside, body = False, []
    for line in lines_of(path):
        if re.search(want, line):
            inside = True
            continue
        if inside and re.search(r"^_Avoid_|^\*\*|^## ", line):
            break
        if inside:
            body.append(line)
    return joined(body)


def bullet(path, want):
    inside, body = False, []
    for line in lines_of(path):
        if re.search(want, line):
            inside = True
            body.append(line)
            continue
        if inside and re.search(r"^([-*] |#)", line):
            break
        if inside:
            body.append(line)
    return joined(body)


def records(path):
    out, rec = [], ""
    for line in lines_of(path):
        if re.match(r"[-*] ", line):
            if rec != "":
                out.append(rec)
            rec = line
        elif re.match(r"\s*$", line):
            if rec != "":
                out.append(rec)
            rec = ""
        elif rec == "":
            rec = line
        else:
            rec = rec + " " + line
    if rec != "":
        out.append(rec)
    return [plain(r) for r in out]


def says(problems, passage_from, passage_lines, fact, *regexes):
    for line in passage_lines:
        if all(re.search(r, line) for r in regexes):
            return
    problems.append(f"{passage_from} does not say {fact}")


def need_passage(problems, passage_from, text, missing):
    if text.replace(" ", "") != "":
        return True
    problems.append(missing)
    return False


def need_entry(problems, name):
    text = entry(ROOT / CONTEXT_MD, name)
    passage_from = f"{CONTEXT_MD}'s {name} entry"
    if need_passage(problems, passage_from, text,
                    f"{CONTEXT_MD} has no '{name}' glossary entry to read, so the order is unstated where every other document defers to it"):
        return passage_from, [text]
    return None


def states_the_order(problems, passage_from, lines):
    says(problems, passage_from, lines, "states the three-band order — priority, then bug, then the rest, each band ascending by number",
         PRIORITY_BAND, BUG_BAND, ORDERED, ASCENDING)


def order_problems():
    problems = []
    found = need_entry(problems, "Selection layer")
    if found:
        states_the_order(problems, *found)
    found = need_entry(problems, "Solvable")
    if found:
        says(problems, *found,
             "that the order runs over the solvable set and never enlarges it — a priority or bug issue still has to pass the four conditions",
             PRIORITY_BAND, BUG_BAND, NOT_ENLARGE)
    text = bullet(ROOT / SKILL_MD, r"^[-*] .*solvable-issues\.sh")
    passage_from = f"{SKILL_MD}'s solvable-issues.sh bullet"
    if need_passage(problems, passage_from, text,
                    f"{SKILL_MD} has no top-level 'solvable-issues.sh' bullet to read, so the order and the tunable an operator looks up beside VERI_GH_JSON could not be found"):
        states_the_order(problems, passage_from, [text])
        says(problems, passage_from, [text], "which tunable names the priority label — VERI_PRIORITY_LABEL", TUNABLE)
    recs = records(ROOT / CLAUDE_MD)
    if need_passage(problems, CLAUDE_MD, "".join(recs),
                    f"{CLAUDE_MD} could not be read, so nothing could be asked of what it records"):
        says(problems, CLAUDE_MD, recs,
             "the three-band order and the tunable that names the priority label — VERI_PRIORITY_LABEL",
             TUNABLE, PRIORITY_BAND, BUG_BAND, ORDERED, ASCENDING)
        says(problems, CLAUDE_MD, recs, "that priority reorders the solvable set and does not enlarge it",
             PRIORITY_BAND, NOT_ENLARGE)
    return problems


def test_context_mds_selection_layer_and_solvable_entries_skill_mds_solvable_issues_sh_bullet_and_claude_md_record_the_three_band_order_and_veri_priority_label_and_say_priority_reorders_the_solvable_set_without_enlarging_it():
    assert order_problems() == []


def test_1037_entry_given_run_dot_sh_starts_at_the_entry_where_run_sh_stands_not_the_one_where_runxsh_does(tmp_path):
    fixture = tmp_path / "CONTEXT.md"
    fixture.write_text("**runXsh**:\nwrong\n**run.sh**:\nright\n")
    assert entry(fixture, r"run\.sh") == "right "
