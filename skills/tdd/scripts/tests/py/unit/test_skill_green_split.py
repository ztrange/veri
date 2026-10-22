"""Cases for what skills/tdd/SKILL.md's Green section says to do with a SPLIT: report, a repair step's CI verdict and a replaces-case green."""
import importlib
import pathlib
import re

from skill_sections import plain_lines as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")


def _lines(heading):
    section = importlib.import_module("skill_sections").section(BAIL if heading == BAILING else SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def bailing_causes():
    lines = _lines(BAILING)
    start = next(i for i, line in enumerate(lines) if "killed-stuck" in line.lower())
    return plain(lines[start:])


def grep(text, pattern, flags=0):
    return any(re.search(pattern, line, flags) for line in text.split("\n"))


def says(text, pattern, message, flags=0):
    assert grep(text, pattern, flags), message


def skill_lines():
    return SKILL.read_text().splitlines() + SKILL.with_name("PIN.md").read_text().splitlines() + SKILL.with_name("REVISE.md").read_text().splitlines()


def numbered(pattern):
    return [(n, line) for n, line in enumerate(skill_lines(), 1) if re.search(pattern, line)]


def neighbourhood(at):
    return plain(line for n, line in enumerate(skill_lines(), 1) if at - 20 <= n <= at + 20)


def outside_cost_check(calls):
    lines = skill_lines()
    start = next(n for n, line in enumerate(lines, 1) if line == "#### The step's cost check")
    end = next(n for n, line in enumerate(lines, 1) if n > start and line.startswith("#### "))
    return [call for call in calls if not start < (call[0] if isinstance(call, tuple) else call) < end]


def split_calls():
    return outside_cost_check(numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)'))


def _bullet(lines, prefix):
    out, inside = [], False
    for line in lines:
        if inside and (line.startswith("- ") or line == ""):
            break
        if line.startswith(prefix):
            inside = True
        if inside:
            out.append(line)
    return plain(out)


def _bullet_body(lines, prefix):
    out, inside = [], False
    for line in lines:
        if inside and line.startswith("- `"):
            break
        if inside:
            out.append(line)
        if line.startswith(prefix):
            inside = True
    return plain(out)


def catalogue_lines():
    return SKILL.with_name("SCRIPTS.md").read_text().splitlines()


def add_ledger_step_entry():
    return _bullet(catalogue_lines(), "- `$S/add-ledger-step.sh")


def repair_call_neighbourhood(tag):
    at = max((n for n, line in enumerate(skill_lines(), 1) if "$S/add-ledger-step.sh" in line and tag in line), default=0)
    if not at:
        return ""
    return neighbourhood(at)


def step_too_big_cause():
    return _bullet(_lines(BAILING), "- `step-too-big`")


def one_line(lines):
    return re.sub(r" +", " ", " ".join(line.replace("*", "").replace("`", "") for line in lines) + " ")


def _paragraph(starts, stops):
    out, inside = [], False
    for line in skill_lines():
        if starts(line):
            inside = True
        if inside and stops(line):
            break
        if inside:
            out.append(line)
    return one_line(out)


def test_skill_md_s_green_section_bails_with_cause_step_too_big_when_add_ledger_step_exits_1_on_a_split_and_its_bailing_section_lists_that_cause_as_a_process_failure():
    says(bailing_causes(), r"step-too-big[^.]{0,220}process",
         "SKILL.md's Bailing causes list never classifies step-too-big as a process failure")


def test_skill_md_s_bailing_entry_for_step_too_big_names_all_three_splits_that_lead_to_it_a_green_leaf_s_split_the_revise_exhausted_split_and_the_over_budget_split():
    bullet = step_too_big_cause()
    assert bullet.strip(), "SKILL.md's Bailing causes list has no step-too-big bullet"
    says(bullet, r"green[^.]*split:|split:[^.]*green", "SKILL.md's step-too-big entry does not name a Green leaf's SPLIT:")
    says(bullet, r"exhausted", "SKILL.md's step-too-big entry does not name the revise-exhausted split")
    says(bullet, r"over-budget", "SKILL.md's step-too-big entry does not name the over-budget split")


def test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2():
    splits = [(n, line) for n, line in split_calls() if "instead-of" in line]
    assert splits, "SKILL.md has no instead-of add-ledger-step.sh call"
    for n, line in splits:
        assert "--criterion" not in line.strip(), f"SKILL.md's split call passes --criterion: {line.strip()}"
        assert "anchor's criterion" in neighbourhood(n), \
            f"SKILL.md never says beside this split call that the split keeps its anchor's criterion: {line.strip()}"
    assert "--criterion" in add_ledger_step_entry(), "SKILL.md's add-ledger-step.sh entry never documents --criterion"


def test_1281_the_suite_repair_and_ci_repair_add_ledger_step_calls_say_they_pass_no_criterion_because_the_repair_step_serves_its_anchor_s_criterion():
    for tag in ("⟦suite-repair⟧", "⟦ci-repair⟧"):
        around = repair_call_neighbourhood(tag)
        assert around.strip(), f"SKILL.md has no add-ledger-step.sh call adding a {tag} step"
        assert "--criterion" in around, f"SKILL.md never says beside its {tag} call that it passes no --criterion"
        assert "anchor's criterion" in around, f"SKILL.md never says beside its {tag} call that the step serves its anchor's criterion"


def test_1292_skill_md_s_add_ledger_step_entry_under_the_scripts_says_criterion_k_tags_the_added_steps_with_criterion_k_for_any_whole_number_k_1_carried_or_not_and_lists_a_k_that_is_not_a_whole_number_1_among_its_exit_2_cases():
    entry = add_ledger_step_entry()
    assert entry.strip(), "SKILL.md has no add-ledger-step.sh entry under The scripts"
    says(entry, r"whole number[^.]{0,20}(≥|>=|at least) ?1", "SKILL.md's entry never says --criterion <k> takes any whole number k ≥ 1")
    says(entry, r"whether or not[^.]{0,80}carr|carried or not|(no|not yet)[^.]{0,30}step[^.]{0,20}carr",
         "SKILL.md's entry never says --criterion <k> tags the steps whether or not a step carries k")
    exit2 = "\n".join(re.findall(r"exit 2[^.]*", entry))
    says(exit2, r"not a whole number", f"SKILL.md's entry never lists a k that is not a whole number ≥ 1 among its exit 2 cases: {exit2!r}")


def first_line(needle):
    return next((n for n, line in enumerate(skill_lines(), 1) if needle in line), None)


def run_lines(pattern):
    return [n for n, _ in numbered(pattern)]


def test_1558_skill_md_runs_every_replaces_case_survivors_sh_occurrence_before_the_verify_green_launch_it_gates_on_the_green_path_and_the_pin_path_alike():
    pin_start = first_line("A `⟦replaces-case⟧` step whose Red reports")
    pin_launch = first_line("Judge it by the replaces-case verify-green")
    occurrences = [n for n, line in enumerate(skill_lines(), 1) if 'replaces-case-survivors.sh "' in line]
    assert pin_start and pin_launch and occurrences, \
        f"SKILL.md lacks a survivors run or a launch marker (pin path={pin_start}, pin launch={pin_launch})"
    for at in occurrences:
        if at >= pin_start:
            assert at <= pin_launch, f"SKILL.md:{at} runs replaces-case-survivors.sh after the pin-path verify-green launch at line {pin_launch}"


def test_1406_skill_md_documents_build_develop_prompt_sh_green_s_8th_argument_the_cases_still_owed_for_deletion_at_the_green_build_command_and_in_the_script_reference_entry():
    reference = _bullet_body(catalogue_lines(), "- `$S/build-develop-prompt.sh <red")
    assert re.search(r"<fast-cmd>.*owed", reference) or re.search(r"green <spec-file>.*owed.*refactor <spec-file>", reference), \
        "SKILL.md's build-develop-prompt.sh reference entry never lists an owed-cases argument in green's synopsis"


def pin_paragraph():
    return _paragraph(lambda line: line.startswith("A `⟦replaces-case⟧` step whose Red reports"),
                      lambda line: "Every other step takes the verdict" in line)


def test_1546_skill_md_s_replaces_case_pin_path_paragraph_runs_replaces_case_survivors_sh_after_the_deletion_green_and_on_survivors_relaunches_it_bounded_by_revise_budget_before_verify_green():
    section = pin_paragraph()
    assert section.strip(), "SKILL.md has no replaces-case pin-path paragraph to read"
    for needle, message in (
        ("replaces-case-survivors.sh", "never runs replaces-case-survivors.sh"),
        ("relaunch", "never relaunches the green leaf on survivors"),
        ("REVISE_BUDGET", "never says a survivors relaunch spends a REVISE_BUDGET attempt"),
        ("revise-exhausted", "never bails cause=revise-exhausted when the budget is spent"),
        ("no verifier", "never says no verifier is launched while a named case survives"),
    ):
        assert needle in section, f"SKILL.md's replaces-case pin-path paragraph {message}"


def test_1625_skill_md_s_develop_replaces_report_wait_leaf_exit_1_or_2_bails_with_cause_replaces_report_failed_launching_no_verifier_runs_step_cost_after_the_wait_and_the_bail_table_lists_the_cause_as_a_system_failure():
    row = next((line for line in BAIL.read_text().splitlines() if line.startswith("- `replaces-report-failed`")), "")
    assert row, "SKILL.md's bail-cause table has no replaces-report-failed entry"
    assert "system" in row.lower(), f"SKILL.md's bail-cause table never lists replaces-report-failed as a system failure: {row}"


def test_1546_skill_md_never_runs_replaces_case_survivors_sh_at_any_place_it_names_it_as_a_run_before_the_last_place_it_runs_unreplaced_cases_sh():
    survivors = run_lines(r"\$S/replaces-case-survivors\.sh|[Rr]uns? [^.]*replaces-case-survivors\.sh")
    assert survivors, "SKILL.md lacks a replaces-case-survivors.sh run"


def test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused_and_bailing_lists_that_cause_as_a_system_failure():
    calls = [call for call in outside_cost_check(run_lines(r"\$S/add-ledger-step\.sh [^ ]*\.tdd/issue-<n>\.md|\$S/add-ledger-step\.sh --criterion <k> \.tdd/issue-<n>\.md"))
             if "<SPLIT: value>" not in skill_lines()[call - 1]]
    assert calls, "SKILL.md has no add-ledger-step.sh call site"
    lines = skill_lines()
    for call in calls:
        near = plain(lines[call - 1:call + 30])
        says(near, r"exits? 2[^.]{0,120}step-add-refused|step-add-refused[^.]{0,120}exits? 2",
             f"SKILL.md:{call} calls add-ledger-step.sh and never says its exit 2 bails with cause step-add-refused")
    says(bailing_causes(), r"step-add-refused[^.]{0,220}system", "SKILL.md's Bailing causes list never classifies step-add-refused as a system failure")


def test_1625_skill_md_s_bail_cause_table_describes_unreplaced_cases_as_a_second_exit_1_after_the_one_correction_or_an_exit_2_at_once_not_as_any_exit_1():
    entry = re.search(r"- `unreplaced-cases`.*?(?=\n- `)", "\n".join(_lines(BAILING)), re.S)
    assert entry, "SKILL.md's Bailing causes list has no unreplaced-cases entry"
    text = plain(entry.group(0).splitlines())
    assert re.search(r"(second|again|after the one correction)", text), \
        f"SKILL.md's unreplaced-cases bail cause never says exit 1 is the second one, after the one correction: {text}"
    assert re.search(r"exit(s|ed)? \**2\**[^.]{0,80}(at once|immediately|no correction)|(at once|immediately)[^.]{0,80}exit(s|ed)? \**2", text), \
        f"SKILL.md's unreplaced-cases bail cause never says an exit 2 bails at once: {text}"
