"""What skills/tdd/SKILL.md and CLAUDE.md say about which leaves run the full suite, read as text."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"
CLAUDE = pathlib.Path(__file__).resolve().parents[5] / "CLAUDE.md"

RED = "#### Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR_LOOP = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"
DIFF_CHECKED = "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"
REVISING = "## Revising on a REJECT"


def plain(text):
    return text.replace("*", "").replace("`", "").lower()


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


def claude_paragraphs(text):
    return [plain(" ".join(p.split("\n"))) for p in re.split(r"\n{2,}", text.strip("\n"))]


def idiom():
    return next((p for p in claude_paragraphs(CLAUDE.read_text()) if p.startswith("a suite whose subject is the docs pipeline")), None)


def fast_plus_affected(text, who, why):
    problems = []
    if not re.search("fast (tier|command)", text):
        problems.append(f"{who} never names the fast tier, which {why}")
    if not re.search(r"affected suites|suites affected-suites\.sh", text):
        problems.append(f"{who} never names the affected suites, which {why}")
    return problems


def full_suite_leaves(skill):
    problems = []
    red = doc_text(skill, RED)
    if not re.search(r"suite (that |which )?(holds|holding|contains|containing|carries)|case.s suite|suite the (new )?(case|test)", red):
        problems.append("SKILL.md's Red section never says the red leaf runs the suite holding its new case")
    loop = doc_text(skill, REFACTOR_LOOP)
    if not re.search(r"suites (covering|that cover|which cover|of the touched)", loop):
        problems.append("SKILL.md's Refactor loop section never says the transform leaf runs the suites covering the touched files")
    claude = CLAUDE.read_text()
    stale = [line for line in claude.splitlines() if re.search(r"every [a-z]*\s*leaf runs", line)]
    if stale:
        problems.append(f"CLAUDE.md still says every leaf runs the suite after every edit: {stale}")
    full = [p for p in claude_paragraphs(claude) if "full suite" in p]
    if not full:
        problems.append("CLAUDE.md never names the full suite at all")
    if not any(re.search("develop-green|verify-green|verifier", p) for p in full):
        problems.append("CLAUDE.md mentions the full suite without naming the leaves that run it")
    return problems


def test_skill_md_s_phase_sections_and_claude_md_say_which_leaves_run_the_full_suite():
    problems = full_suite_leaves(SKILL)
    assert not problems, "\n".join(problems)


def test_698_case_1_passes_on_a_skill_md_whose_green_section_and_refactor_loop_name_no_full_suite_run(tmp_path):
    kept, skipping = [], False
    for line in SKILL.read_text().splitlines(keepends=True):
        if re.search(r"Neither .* runs the full suite", line):
            skipping = True
        if not skipping:
            kept.append(line)
        if skipping and line.rstrip("\n").endswith("."):
            skipping = False
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("".join(kept))
    assert not re.search(r"Neither .* runs the full suite", fixture.read_text()), \
        "the fixture still carries a 'Neither … runs the full suite' sentence"
    problems = full_suite_leaves(fixture)
    assert not problems, "\n".join(problems)


def test_skill_md_s_verify_refactor_entry_says_the_verdict_is_on_the_fast_tier_plus_the_affected_suites_not_the_full_suite():
    text = before(doc_text(SKILL, REFACTOR_LOOP, r"^5\. "), "6. narrate")
    assert text.strip(), "SKILL.md has no '#### Refactor loop' section to read"
    problems = fast_plus_affected(text, "SKILL.md's verify-refactor entry", "verify-refactor.md tells the verifier to run")
    if "full suite" in text:
        problems.append("SKILL.md's verify-refactor entry still says the full suite runs in the refactor phase")
    assert not problems, "\n".join(problems)


def test_skill_md_s_sentence_on_a_break_outside_the_affected_set_points_at_the_draft_pr_step_s_full_run_and_its_repair_step_not_at_verify_refactor():
    text = doc_text(SKILL, REFACTOR_LOOP)
    assert text.strip(), "SKILL.md has no '#### Refactor loop' section to read"
    assert "break in a suite" in text, "SKILL.md's Refactor loop never says what catches a break in a suite outside the affected set"
    text = after(text, "break in a suite")
    text = re.sub(r"[0-9]\.", "#", text)
    text = before(text, ". ")
    problems = []
    if not re.search("draft pr", text):
        problems.append("the sentence never names the Draft PR step, where the one full-suite run is")
    if not re.search(r"full[- ]suite run|full run|full suite", text):
        problems.append("the sentence never names the full-suite run that catches it")
    if not re.search("repair step", text):
        problems.append("the sentence never names the repair step a red full run appends")
    if re.search(r"surfaces here|verify-refactor|verifier|reject", text):
        problems.append("the sentence still hands that break to verify-refactor")
    assert not problems, "\n".join(problems)


def test_skill_md_s_green_entry_says_develop_green_keeps_the_fast_tier_plus_the_affected_suites_green_not_the_full_suite():
    text = before(doc_text(SKILL, GREEN, r"^1\. "), "2. verify")
    assert text.strip(), "SKILL.md has no '#### Green' section to read"
    problems = fast_plus_affected(text, "SKILL.md's develop-green entry", "develop-green.md tells the leaf to run before it reports")
    if "full suite" in text:
        problems.append("SKILL.md's develop-green entry still says develop-green keeps the full suite green")
    assert not problems, "\n".join(problems)


def test_974_skill_md_s_diff_checked_section_says_develop_diff_and_verify_diff_each_run_the_fast_tier_plus_the_affected_suites():
    section = doc_text(SKILL, DIFF_CHECKED)
    assert section.strip(), "SKILL.md has no diff-checked section to read"
    problems = fast_plus_affected(before(section, "verifier"), "SKILL.md's develop-diff account", "develop-diff.md tells the leaf to run before it reports")
    problems += fast_plus_affected(after(section, "verifier"), "SKILL.md's verify-diff account", "verify-diff.md tells the verifier to run")
    assert not problems, "\n".join(problems)


def test_974_skill_md_s_diff_checked_section_s_build_develop_prompt_sh_diff_and_run_verdict_sh_diff_command_lines_pass_the_fast_command():
    text = doc_text(SKILL, DIFF_CHECKED)
    assert text.strip(), "SKILL.md has no diff-checked section to read"
    problems = []
    if not re.search(r"build-develop-prompt\.sh diff [^,]*<fast-cmd>", text):
        problems.append("the diff-checked build-develop-prompt.sh diff command line never passes '<fast-cmd>'")
    if not re.search(r"run-verdict\.sh [^,]*--fast-cmd [^,]* diff ", text):
        problems.append("the diff-checked run-verdict.sh … diff command line never passes --fast-cmd")
    assert not problems, "\n".join(problems)


def test_974_skill_md_s_revise_diff_command_line_passes_the_fast_command_and_its_diff_re_verify_passes_fast_cmd():
    section = doc_text(SKILL, REVISING, r"^[*][*]The `diff` phase")
    assert section.strip(), "SKILL.md has no '## Revising on a REJECT' section to read"
    problems = []
    text = before(after(section, "build-develop-prompt.sh revise diff"), ".prompt")
    if "'<fast-cmd>'" not in text:
        problems.append("the build-develop-prompt.sh revise diff command line never passes '<fast-cmd>'")
    text = before(after(section, "the re-verify is"), "launched as")
    if not re.search(r"run-verdict\.sh [^,]*--fast-cmd [^,]* diff ", text):
        problems.append("the diff re-verify run-verdict.sh line never passes --fast-cmd")
    assert not problems, "\n".join(problems)


def test_claude_md_s_testing_idiom_paragraph_states_what_runs_per_step_and_per_pr():
    text = idiom()
    assert text is not None, "CLAUDE.md has no paragraph opening 'a suite whose subject is the docs pipeline' to read"
    problems = fast_plus_affected(text, "CLAUDE.md's Testing idiom paragraph", "develop-green, verify-green and verify-refactor run per step")
    for leaf in ("develop-green", "verify-green", "verify-refactor"):
        if leaf not in text:
            problems.append(f"the Testing idiom paragraph never names {leaf}")
    if not re.search(r"(per|once a|each|one) pr|pr is readied|readying the pr|readies the pr", text):
        problems.append("the Testing idiom paragraph never says the full suite runs once per PR, before the PR is readied")
    if "repair step" not in text:
        problems.append("the Testing idiom paragraph never says a repair step runs the full suite again")
    if "three leaves per step" in text:
        problems.append("the Testing idiom paragraph still says three leaves per step run the full suite")
    assert not problems, "\n".join(problems)
