"""What skills/tdd/SKILL.md and CLAUDE.md say about which leaves run the full suite, read as text."""
import pathlib
import re

import skill_sections
from skill_sections import plain_lower as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.with_name("REVISE.md")
CLAUDE = pathlib.Path(__file__).resolve().parents[6] / "CLAUDE.md"

GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR_LOOP = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"
DIFF_CHECKED = "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"
REVISING = "## Revising on a REJECT"
PHASES = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"


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
    text = next((p for p in claude_paragraphs(CLAUDE.read_text()) if p.startswith("a suite whose subject is the docs pipeline")), None)
    assert text is not None, "CLAUDE.md has no paragraph opening 'a suite whose subject is the docs pipeline' to read"
    return text


def fast_plus_affected(text, who, why):
    problems = []
    if not re.search("fast (tier|command)", text):
        problems.append(f"{who} never names the fast tier, which {why}")
    if not re.search(r"affected suites|suites affected-suites\.sh", text):
        problems.append(f"{who} never names the affected suites, which {why}")
    return problems


def full_suite_leaves(skill):
    problems = []
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
    section = doc_text(REVISE_MD, REVISING, r"^[*][*]The `diff` phase")
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


def test_claude_md_s_testing_idiom_paragraph_says_a_revise_leaf_runs_the_tiers_of_the_phase_it_redoes():
    text = idiom()
    problems = []
    if not re.search(r"revise[- ](leaf|leaves)|revise-(red|green|refactor)", text):
        problems.append("CLAUDE.md's Testing idiom paragraph never names the revise leaves")
    if not re.search(r"(tier|suites)[^.]*phase (it|they|the leaf) (redoes|redo|is redoing|are redoing)", text):
        problems.append("CLAUDE.md's Testing idiom paragraph never says a revise leaf runs the tiers of the phase it redoes")
    assert not problems, "\n".join(problems)


def test_skill_md_names_no_full_suite_run_inside_a_step_s_cycle():
    lines = SKILL.read_text().splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith("#### Green")), None)
    end = next((i for i, line in enumerate(lines) if line.startswith("### 4. Draft PR")), len(lines))
    assert start is not None, "SKILL.md has no text from '#### Green' to '### 4. Draft PR' to read"
    text = re.sub(r"[\n ]+", " ", plain("".join(lines[start:end])))
    for pattern in (r"(^| )(not|neither|nor|never|no)( [a-z-]+){0,5} full suite", r"full[- ]suite run (in|at) (4\. )?draft pr"):
        while (m := re.search(pattern, text)):
            text = text.replace(m.group(0), "", 1)
    m = re.search(r"[^.]{0,60}(full suite|full-suite run)[^.]{0,40}", text)
    assert not m, f"SKILL.md names a full-suite run inside a step's cycle: {m.group(0) if m else ''}"


def test_1300_skill_md_runs_suite_reported_sh_before_the_verifier_after_develop_diff_revise_diff_k_and_each_phase_leaf_and_bails_report_missing_on_its_exit_2():
    problems = []
    for label, heading, call in (
        ("diff-checked step", DIFF_CHECKED, "suite-reported.sh develop-diff"),
        ("phases step", PHASES, "suite-reported.sh develop-<phase>"),
    ):
        body = doc_text(SKILL, heading)
        if "suite-reported.sh" not in body:
            problems.append(f"{label}: never runs suite-reported.sh")
            continue
        if call not in body:
            problems.append(f"{label}: never runs {call}")
        if "report-missing" not in body:
            problems.append(f"{label}: never names the report-missing bail")
        if len(before(body, "suite-reported.sh")) > len(before(body, "verify-")):
            problems.append(f"{label}: the check comes after the verifier is launched")
    assert not problems, "\n".join(problems)


def test_1300_skill_md_runs_suite_reported_sh_only_after_a_leaf_whose_prompt_asks_for_a_suite_line_never_after_the_refactor_leaf_or_a_revise_of_red_green_or_refactor():
    problems = []
    for label, heading in (("Refactor loop", REFACTOR_LOOP), ("Revising on a REJECT", REVISING)):
        if "suite-reported.sh" in doc_text(REVISE_MD if heading == REVISING else SKILL, heading):
            problems.append(f"{label}: runs suite-reported.sh after a leaf whose prompt asks for no SUITE: line")
    if "suite-reported.sh revise-diff-<k>" not in doc_text(SKILL, DIFF_CHECKED):
        problems.append("diff-checked step: never runs suite-reported.sh revise-diff-<k>, the leaf the conductor launches")
    assert not problems, "\n".join(problems)


def test_1568_skill_md_runs_suite_reported_sh_develop_green_between_the_leaf_s_wait_and_verify_green_s_launch_and_keeps_a_looks_wrong_green_s_reject_rather_than_a_report_missing_bail():
    green = doc_text(SKILL, GREEN)
    assert "suite-reported.sh develop-green" in green, "Green section: never runs suite-reported.sh develop-green"
    problems = []
    ahead = before(green, "suite-reported.sh develop-green")
    if "wait-leaf.sh develop-green" not in ahead:
        problems.append("Green section: the check does not come after develop-green's wait")
    if "supervise.sh verdict-green" in ahead:
        problems.append("Green section: the check comes after verify-green is launched")
    behind = after(green, "suite-reported.sh develop-green")[:1200]
    if "report-missing" not in behind:
        problems.append("Green section: never names the report-missing bail for a missing SUITE: line")
    if "looks wrong" not in behind:
        problems.append("Green section: never says a green that stops because the test looks wrong is exempt")
    if "reject" not in behind:
        problems.append("Green section: never says that green keeps its verify-green REJECT outcome")
    assert not problems, "\n".join(problems)


def whole_skill():
    return plain(SKILL.read_text()).replace("\n", " ")


def test_1568_skill_md_runs_suite_reported_sh_develop_structural_between_the_transform_leaf_s_wait_and_its_transform_verifier_and_keeps_an_out_of_bounds_skip_s_reject_rather_than_a_report_missing_bail():
    whole = whole_skill()
    assert "build-develop-prompt.sh structural" in whole, "structural pass: never launches develop-structural"
    structural = after(whole, "build-develop-prompt.sh structural")[:6000]
    assert "suite-reported.sh develop-structural" in structural, "structural pass: never runs suite-reported.sh develop-structural"
    problems = []
    if "supervise.sh verdict-transform" in before(structural, "suite-reported.sh develop-structural"):
        problems.append("structural pass: the check comes after the transform verifier is launched")
    behind = after(structural, "suite-reported.sh develop-structural")[:1200]
    if "report-missing" not in behind:
        problems.append("structural pass: never names the report-missing bail for a missing SUITE: line")
    if not re.search(r"out-of-bounds|leave the tree", behind):
        problems.append("structural pass: never says an out-of-bounds skip is exempt")
    if "transform reject and the next candidate" not in behind:
        problems.append("structural pass: never says that skip keeps its transform REJECT outcome")
    assert not problems, "\n".join(problems)


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
