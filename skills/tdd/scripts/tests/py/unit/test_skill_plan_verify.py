"""Cases for where skills/tdd/SKILL.md verifies the plan and how its plan section orders and words the steps."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
SCRIPTS_MD = SKILL.with_name("SCRIPTS.md")

SCOPE = "### 2. Scope & plan → the ledger"
COMMIT_RE = r'git commit -m "plan: scope'
LOOP_RE = r"^### 3[.] The cycle loop"
PLAN_LAUNCH_RE = r"(run-verdict|verify)[.]sh.* plan "
EXIT2_RE = r"[(]exit 2[)]"
WANT_PHASES = ["red", "green", "refactor", "pin", "plan"]
ALTERNATION_RE = r"<([a-z|]*red[a-z|]*)>"


def skill_lines():
    return SKILL.read_text().splitlines()


def line_of(pattern):
    return next((n for n, line in enumerate(skill_lines(), 1) if re.search(pattern, line)), 0)


def span_lines(a, b):
    return [(n, line) for n, line in enumerate(skill_lines(), 1) if a < n < b]


def span_text(a, b):
    return " ".join(line for _, line in span_lines(a, b)).lower() + " "


def line_in_span(a, b, pattern):
    return next((n for n, line in span_lines(a, b) if re.search(pattern, line)), 0)


def bullet_text(a, b, pattern):
    out, inside = [], False
    for _, line in span_lines(a, b):
        if not inside and re.search(pattern, line):
            inside = True
            out.append(line)
            continue
        if inside and (line.strip() == "" or line.startswith("- ")):
            inside = False
        if inside:
            out.append(line)
    return " ".join(out).lower() + " "


def scope_paragraphs():
    text = importlib.import_module("skill_sections").section(SKILL, SCOPE)
    paragraphs, current = [], []
    for line in text.splitlines()[1:]:
        if line.strip() == "":
            paragraphs.append(" ".join(current).lower())
            current = []
        else:
            current.append(line)
    paragraphs.append(" ".join(current).lower())
    return paragraphs


def scope_paragraph_with_all(words):
    return any(all(word in paragraph for word in words.split("|")) for paragraph in scope_paragraphs())


def test_skill_md_verifies_the_plan_between_the_ledger_commit_and_the_first_step_and_a_reject_rewrites_it_and_re_verifies():
    commit_line, loop_line = line_of(COMMIT_RE), line_of(LOOP_RE)
    assert commit_line, f"no instruction committing the ledger (/{COMMIT_RE}/)"
    assert loop_line, f"no cycle-loop heading (/{LOOP_RE}/)"
    launch_line = line_of(PLAN_LAUNCH_RE)
    assert launch_line, f"never launches the plan verifier: no line matching /{PLAN_LAUNCH_RE}/"
    assert commit_line < launch_line < loop_line, (
        f"launches the plan verifier at line {launch_line}, outside lines {commit_line}..{loop_line}")
    span = span_text(commit_line, loop_line)
    for want in ("reject", "rewrit", "re-verif"):
        assert want in span, f"says nothing matching '{want}' between lines {commit_line} and {loop_line}"


def test_skill_md_bails_as_a_system_failure_when_the_plan_verification_rendered_no_verdict():
    commit_line, loop_line = line_of(COMMIT_RE), line_of(LOOP_RE)
    assert commit_line and loop_line, f"landmark missing (commit {commit_line}, loop {loop_line})"
    exit2_line = line_in_span(commit_line, loop_line, EXIT2_RE)
    assert exit2_line, f"says nothing about /{EXIT2_RE}/ between lines {commit_line} and {loop_line}"
    bullet = bullet_text(commit_line, loop_line, EXIT2_RE)
    for want in ("bail", "system"):
        assert want in bullet, f"exit-2 outcome (line {exit2_line}) says nothing matching '{want}': {bullet}"


def test_skill_md_script_entries_for_the_verifier_scripts_name_the_plan_phase_beside_the_four_cycle_phases():
    for script in ("build-verify-prompt.sh", "verify.sh", "run-verdict.sh"):
        entry_re = r"^- .[$]S/" + script.replace(".", "[.]") + " "
        catalogue = SCRIPTS_MD.read_text().splitlines()
        entry_line = next((n for n, text in enumerate(catalogue, 1) if re.search(entry_re, text)), 0)
        assert entry_line, f"no script-inventory entry for {script} (/{entry_re}/)"
        line = catalogue[entry_line - 1]
        match = re.search(ALTERNATION_RE, line)
        assert match, f"line {entry_line}, the entry for {script}, spells no phase alternation: {line}"
        alternation = f"|{match.group(1)}|"
        for phase in WANT_PHASES:
            assert f"|{phase}|" in alternation, (
                f"line {entry_line}, the entry for {script}, spells <{match.group(1)}>, which does not name '{phase}'")


def test_skill_md_plan_section_orders_a_step_bringing_in_code_after_the_steps_pinning_its_branches_or_has_it_bring_in_only_the_branches_its_own_test_requires():
    assert scope_paragraph_with_all("branch|pin|after|its own test requires|module")


def test_skill_md_plan_section_plans_an_interface_change_that_also_asks_for_a_test_case_as_the_phased_step_plus_a_separate_red_green_step_tagged_with_the_same_criterion():
    assert scope_paragraph_with_all("interface change|test case|separate|red/green|same")


def test_skill_md_plan_section_requires_each_steps_text_to_carry_every_constraint_the_issue_attaches_to_its_cases():
    assert scope_paragraph_with_all("constraint|medium|no production change|end-to-end")


def test_skill_md_plan_section_plans_a_step_that_can_be_satisfied_only_by_editing_a_test_as_a_test_only_step_never_as_red_green():
    assert scope_paragraph_with_all("only by editing|test-only step|diff-checked|never as red/green")


def test_skill_md_names_reorder_ledger_steps_sh_as_the_one_sanctioned_reorder_of_unchecked_steps_and_the_hand_edit_guardrail_points_at_it():
    script = "reorder-ledger-steps.sh"
    lines = skill_lines() + SCRIPTS_MD.read_text().splitlines()
    assert script in "\n".join(lines).lower(), f"never names {script}"
    mention = " ".join(line for line in lines if script in line).lower()
    for word in ("unchecked", "plan:", "operator"):
        assert word in mention, f"no line naming {script} mentions '{word}'"
    guard = next((line for line in lines if "Never hand-edit the ledger" in line), "")
    assert script in guard and "tick-ledger.sh" in guard, guard
