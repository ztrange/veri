"""What skills/tdd/SKILL.md and CLAUDE.md say about which leaves run the full suite, read as text."""
import pathlib
import re

import skill_sections
from skill_sections import plain_lower as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

REFACTOR_LOOP = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"


def doc_text(skill, heading, start=None):
    lines = skill_sections.section(skill, heading).splitlines()[1:]
    if start is not None:
        at = next((i for i, line in enumerate(lines) if re.search(start, line)), len(lines))
        lines = lines[at:]
    return "".join(plain(line) + " " for line in lines)


def before(text, sep):
    return text.split(sep, 1)[0]


def after(text, sep):
    return text.split(sep, 1)[1] if sep in text else text


def test_skill_md_names_no_full_suite_run_inside_a_step_s_cycle():
    lines = SKILL.read_text().splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith("#### Refactor loop")), None)
    end = next((i for i, line in enumerate(lines) if line.startswith("### 4. Draft PR")), len(lines))
    assert start is not None, "SKILL.md has no text from '#### Refactor loop' to '### 4. Draft PR' to read"
    text = re.sub(r"[\n ]+", " ", plain("".join(lines[start:end])))
    for pattern in (r"(^| )(not|neither|nor|never|no)( [a-z-]+){0,5} full suite", r"full[- ]suite run (in|at) (4\. )?draft pr"):
        while (m := re.search(pattern, text)):
            text = text.replace(m.group(0), "", 1)
    m = re.search(r"[^.]{0,60}(full suite|full-suite run)[^.]{0,40}", text)
    assert not m, f"SKILL.md names a full-suite run inside a step's cycle: {m.group(0) if m else ''}"


def test_1300_skill_md_runs_suite_reported_sh_only_after_a_leaf_whose_prompt_asks_for_a_suite_line_never_after_the_refactor_leaf_or_a_revise_of_red_green_or_refactor():
    assert "suite-reported.sh" not in doc_text(SKILL, REFACTOR_LOOP), (
        "Refactor loop: runs suite-reported.sh after a leaf whose prompt asks for no SUITE: line")


def whole_skill():
    return plain(SKILL.with_name("REFACTOR-KIND.md").read_text()).replace("\n", " ")


def test_1568_skill_md_runs_suite_reported_sh_develop_transform_after_the_refactor_kind_transform_leaf_and_before_its_blind_transform_verifier():
    whole = whole_skill()
    assert "refactor-kind step therefore runs" in whole, "Cover → Transform → Verify: the refactor-kind step's passage is missing"
    passage = after(whole, "refactor-kind step therefore runs")[:2500]
    assert "suite-reported.sh develop-transform" in passage, "Cover → Transform → Verify: never runs suite-reported.sh develop-transform"
    ahead = before(passage, "suite-reported.sh develop-transform")
    problems = []
    if not re.search(r"transform +leaf +applies", ahead):
        problems.append("Cover → Transform → Verify: the check does not come after the transform leaf")
    if re.search(r"blind +transform +verifier", ahead):
        problems.append("Cover → Transform → Verify: the check comes after the transform verifier")
    assert not problems, "\n".join(problems)


def test_991_doc_text_given_the_from_regex_5_starts_at_the_line_5_y_not_at_5x_y(tmp_path):
    fixture = tmp_path / "doc.md"
    fixture.write_text("## Section\n5x y\n5. y\n")
    assert doc_text(fixture, "## Section", r"^5\. ") == "5. y "


