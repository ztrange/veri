"""Cases for what skills/tdd/SKILL.md's Green section says to do with a SPLIT: report, a repair step's CI verdict and a replaces-case green."""
import importlib
import pathlib
import re

from skill_sections import plain_lines as plain, window_text as window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"
BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
ADD_LEDGER_STEP = r"\$s/add-ledger-step\.sh"


def _lines(heading):
    section = importlib.import_module("skill_sections").section(BAIL if heading == BAILING else SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def green():
    return plain(_lines(GREEN))


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


def uncovered_spec_calls():
    return numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*after "\$\(\$S/next-pending-refactor\.sh')


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


def green_paragraph():
    return _paragraph(lambda line: "On a `⟦replaces-case⟧` step, a PASS is accepted" in line,
                      lambda line: re.match(r"3\. ", line))


def test_skill_md_s_green_section_on_split_restores_the_tree_to_head_adds_the_split_steps_before_step_in_one_add_ledger_step_call_commits_the_ledger_emits_step_split_and_returns_to_next_unchecked():
    section = green()
    says(section, r"split", "SKILL.md's Green section never branches on the leaf's SPLIT: report")
    says(section, r"git (restore|checkout|reset)[^.]{0,60}head|restore[^.]{0,60}(the tree|to) head",
         "SKILL.md's Green section never restores the tree to HEAD on a SPLIT:")
    calls = len(re.findall(ADD_LEDGER_STEP, section))
    assert calls != 0, "SKILL.md's Green section never runs add-ledger-step.sh on a SPLIT:"
    assert calls <= 1, f"SKILL.md's Green section runs add-ledger-step.sh {calls} times"
    added = window(section, ADD_LEDGER_STEP)
    says(added, r"before ['\"]?(<step>|\$\(\$s/next-unchecked\.sh)",
         "SKILL.md's Green section runs add-ledger-step.sh without anchoring the insertion before the step being split")
    says(added, r"commit", "SKILL.md's Green section grows the ledger on a SPLIT: without committing it")
    says(section, r"step-split", "SKILL.md's Green section never emits step-split")
    says(section, r"next-unchecked", "SKILL.md's Green section never loops back to next-unchecked.sh after a split")


def test_skill_md_s_green_section_bails_with_cause_step_too_big_when_add_ledger_step_exits_1_on_a_split_and_its_bailing_section_lists_that_cause_as_a_process_failure():
    section = green()
    says(section, r"step-too-big", "SKILL.md's Green section never names the step-too-big cause")
    over = window(section, r"step-too-big")
    says(over, r"exits? 1", "SKILL.md's Green section names step-too-big without saying it is add-ledger-step.sh's exit 1")
    says(over, r"bail", "SKILL.md's Green section names step-too-big without bailing on it")
    says(bailing_causes(), r"step-too-big[^.]{0,220}process",
         "SKILL.md's Bailing causes list never classifies step-too-big as a process failure")


def test_skill_md_s_bailing_entry_for_step_too_big_names_all_three_splits_that_lead_to_it_a_green_leaf_s_split_the_revise_exhausted_split_and_the_over_budget_split():
    bullet = step_too_big_cause()
    assert bullet.strip(), "SKILL.md's Bailing causes list has no step-too-big bullet"
    says(bullet, r"green[^.]*split:|split:[^.]*green", "SKILL.md's step-too-big entry does not name a Green leaf's SPLIT:")
    says(bullet, r"exhausted", "SKILL.md's step-too-big entry does not name the revise-exhausted split")
    says(bullet, r"over-budget", "SKILL.md's step-too-big entry does not name the over-budget split")


def test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2():
    splits = split_calls()
    assert sum("instead-of" in line for _, line in splits) >= 1, \
        "SKILL.md has no instead-of add-ledger-step.sh call"
    assert any('before "$($S/next-unchecked.sh' in line for _, line in splits), \
        "SKILL.md has no add-ledger-step.sh call anchored before next-unchecked.sh"
    for n, line in splits:
        assert "--criterion" not in line.strip(), f"SKILL.md's split call passes --criterion: {line.strip()}"
        assert "anchor's criterion" in neighbourhood(n), \
            f"SKILL.md never says beside this split call that the split keeps its anchor's criterion: {line.strip()}"
    uncovered = uncovered_spec_calls()
    assert uncovered, "SKILL.md has no add-ledger-step.sh call anchored after next-pending-refactor.sh"
    assert any("--criterion <k>" in line for _, line in uncovered), \
        "SKILL.md's uncovered-spec add-ledger-step.sh call passes no --criterion <k>"
    around = neighbourhood(uncovered[0][0])
    says(around, r"numbered acceptance criteri", "SKILL.md never says k is read from the issue's numbered acceptance criteria")
    says(around, r"one (add-ledger-step\.sh )?call per criterion", "SKILL.md never says one call per criterion")
    says(around, r"exits? 2[^.]{0,200}bail", "SKILL.md never says add-ledger-step.sh exit 2 bails")
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


def test_1431_skill_md_s_green_section_judges_a_ci_repair_step_s_green_against_a_fresh_ci_run_on_the_pushed_fix_wait_ci_on_the_pushed_sha_not_only_a_local_make_test_and_a_red_ci_there_bails_ci_red():
    section = green()
    assert "⟦ci-repair⟧" in section, "SKILL.md's Green section never names a ⟦ci-repair⟧ step"
    rule = section.split("⟦ci-repair⟧", 1)[1][:700]
    assert "wait-ci.sh" in rule, "SKILL.md's ⟦ci-repair⟧ green rule never runs wait-ci.sh on the fix"
    says(rule, r"push[^.]{0,60}sha|sha[^.]{0,60}push", "SKILL.md's ⟦ci-repair⟧ green rule never waits on the pushed sha")
    says(rule, r"not only[^.]{0,60}make test", "SKILL.md's ⟦ci-repair⟧ green rule never says a local make test alone does not judge it")
    assert "ci-red" in rule, "SKILL.md's ⟦ci-repair⟧ green rule never bails ci-red on a red CI there"


def _sentences(text):
    return text.replace(". ", ".\n")


def test_1473_skill_md_s_green_section_names_the_ci_repair_verify_green_variant_and_says_its_evidence_is_ci_the_failing_job_s_log_before_the_fix_and_a_green_ci_run_on_the_pushed_fix_not_a_local_revert_goes_red_check():
    variant = "\n".join(line for line in _sentences(green()).split("\n")
                        if "⟦ci-repair⟧" in line and "verify-green" in line)
    assert variant, "SKILL.md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant"
    says(variant, r"variant", "SKILL.md's ⟦ci-repair⟧ verify-green sentence never calls it a variant")
    says(variant, r"failing job's log|log of the failing job", "SKILL.md's sentence never names the failing job's log as evidence")
    says(variant, r"green ci run", "SKILL.md's sentence never names a green CI run on the pushed fix as evidence")
    says(variant, r"not[^.]{0,80}(local )?revert", "SKILL.md's sentence never says the local revert-goes-red check does not judge it")


def test_1473_skill_md_s_green_section_says_the_ci_repair_verify_green_variant_judges_only_evidence_that_exists_before_the_push_and_never_requires_a_ci_run_on_the_fix_whose_ci_verdict_is_the_post_push_wait_ci_wait_where_red_bails_ci_red():
    lines = _sentences(green()).split("\n")
    start = next((i for i, line in enumerate(lines) if "⟦ci-repair⟧" in line and "verify-green" in line), None)
    assert start is not None, "SKILL.md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant"
    tail = "\n".join(lines[start:])
    says(tail, r"judges only[^.]{0,120}(before|prior to) the push", "SKILL.md's variant never says it judges only evidence that exists before the push")
    says(tail, r"never requires?[^.]{0,60}ci run", "SKILL.md's variant never says it does not require a CI run on the fix")
    says(tail, r"wait-ci\.sh", "SKILL.md's variant never leaves the CI verdict on the fix to the post-push wait-ci.sh wait")
    assert "ci-red" in tail, "SKILL.md's variant never says a red CI on the pushed fix bails ci-red"
    assert not grep(tail, r"(requires?|evidence is)[^.]{0,120}green ci run[^.]{0,40}(on|for) the (pushed )?fix"), \
        "SKILL.md's variant requires a green CI run on the pushed fix, which does not exist until after its PASS"


def test_skill_md_s_replaces_case_green_paragraph_runs_replaces_case_survivors_before_verify_green_and_on_survivors_relaunches_the_green_leaf_naming_them_records_an_event_and_launches_no_verifier():
    section = green_paragraph()
    assert section.strip(), "SKILL.md has no replaces-case paragraph in the Green step's Verify (blind)"
    assert "replaces-case-survivors.sh" in section, "SKILL.md's replaces-case Green paragraph never runs replaces-case-survivors.sh"
    assert "relaunch" in section, "SKILL.md's replaces-case Green paragraph never relaunches the green leaf on survivors"
    assert "event" in section, "SKILL.md's replaces-case Green paragraph never records the relaunch as an event"
    assert "no verifier" in section, "SKILL.md's replaces-case Green paragraph never says no verifier is launched"


def first_line(needle):
    return next((n for n, line in enumerate(skill_lines(), 1) if needle in line), None)


def run_lines(pattern):
    return [n for n, _ in numbered(pattern)]


UNREPLACED_RUN = r"\$S/unreplaced-cases\.sh|[Rr]un [^.]*unreplaced-cases\.sh"


def test_1406_skill_md_runs_replaces_case_survivors_sh_before_the_verify_green_launch_command_not_after_it():
    survivors = first_line('replaces-case-survivors.sh "')
    launch = first_line("supervise.sh verdict-green")
    assert survivors and launch, f"SKILL.md lacks a replaces-case-survivors.sh run or a verdict-green launch line (survivors={survivors}, launch={launch})"
    assert survivors <= launch, f"SKILL.md:{survivors} runs replaces-case-survivors.sh after the verify-green launch at line {launch}"


def test_1558_skill_md_runs_every_replaces_case_survivors_sh_occurrence_before_the_verify_green_launch_it_gates_on_the_green_path_and_the_pin_path_alike():
    green_launch = first_line("supervise.sh verdict-green")
    pin_start = first_line("A `⟦replaces-case⟧` step whose Red reports")
    pin_launch = first_line("Judge it by the replaces-case verify-green")
    occurrences = [n for n, line in enumerate(skill_lines(), 1) if 'replaces-case-survivors.sh "' in line]
    assert green_launch and pin_start and pin_launch and occurrences, \
        f"SKILL.md lacks a survivors run or a launch marker (green launch={green_launch}, pin path={pin_start}, pin launch={pin_launch})"
    lines = skill_lines()
    for at in occurrences:
        if at < pin_start:
            context = one_line(lines[max(at - 2, 0):at])
            assert not (at > green_launch and "Before that verify-green" not in context), \
                f"SKILL.md:{at} runs replaces-case-survivors.sh after the Green verify-green launch at line {green_launch}"
        else:
            assert at <= pin_launch, f"SKILL.md:{at} runs replaces-case-survivors.sh after the pin-path verify-green launch at line {pin_launch}"


def test_1406_skill_md_orders_the_unreplaced_cases_sh_check_before_the_replaces_case_survivors_sh_check_and_both_before_the_verify_green_launch_command():
    unreplaced = first_line('unreplaced-cases.sh "')
    survivors = first_line('replaces-case-survivors.sh "')
    launch = first_line("supervise.sh verdict-green")
    assert unreplaced and survivors and launch, \
        f"SKILL.md lacks an unreplaced-cases.sh run, a replaces-case-survivors.sh run or a verdict-green launch line (unreplaced={unreplaced}, survivors={survivors}, launch={launch})"
    assert unreplaced <= survivors <= launch, \
        f"SKILL.md gates are out of order: unreplaced-cases.sh at line {unreplaced}, replaces-case-survivors.sh at line {survivors}, verify-green launch at line {launch}"


def test_1406_skill_md_s_replaces_case_green_paragraph_says_each_survivors_relaunch_spends_one_revise_budget_attempt_and_a_spent_budget_bails_with_a_cause_classify_bail_sh_classifies(capsys):
    section = green_paragraph()
    assert section.strip(), "SKILL.md has no replaces-case paragraph in the Green step's Verify (blind) to read"
    assert "REVISE_BUDGET" in section, "SKILL.md's replaces-case Green paragraph never says the survivors relaunch spends a REVISE_BUDGET attempt"
    found = re.search(r"cause=([a-z-]+)", section)
    assert found, "SKILL.md's replaces-case Green paragraph names no cause= to bail with when the REVISE_BUDGET is spent on survivors"
    code = importlib.import_module("veri.classify_bail").main([found.group(1)])
    capsys.readouterr()
    assert code == 0, f"SKILL.md's replaces-case Green paragraph bails with cause={found.group(1)}, which classify-bail.sh does not classify"


def test_1406_skill_md_documents_build_develop_prompt_sh_green_s_8th_argument_the_cases_still_owed_for_deletion_at_the_green_build_command_and_in_the_script_reference_entry():
    green_build = next((line for line in skill_lines() if "build-develop-prompt.sh green " in line), None)
    assert green_build, "SKILL.md has no 'build-develop-prompt.sh green ' command line to read"
    assert "owed" in green_build, f"SKILL.md's green build command passes no argument for the cases still owed for deletion: {green_build}"
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


def test_1546_skill_md_runs_unreplaced_cases_sh_at_every_place_it_names_it_as_a_run_before_the_verify_red_launch_command():
    red_launch = first_line("supervise.sh verdict-red")
    runs = run_lines(UNREPLACED_RUN)
    assert red_launch and runs, f"SKILL.md lacks an unreplaced-cases.sh run or a verdict-red launch line (runs={runs}, launch={red_launch})"
    for run in runs:
        assert run <= red_launch, f"SKILL.md:{run} runs unreplaced-cases.sh after the verify-red launch at line {red_launch}"


def unreplaced_paragraph():
    return _paragraph(lambda line: 'Run `$S/unreplaced-cases.sh "<step line>"' in line, lambda line: not line.strip())


def test_1625_skill_md_s_unreplaced_cases_exit_1_launches_one_develop_replaces_report_leaf_through_the_supervisor_spending_no_revise_budget_and_reruns_unreplaced_cases_sh_before_verify_red():
    section = unreplaced_paragraph()
    assert section.strip(), "SKILL.md has no unreplaced-cases.sh paragraph in the Red step to read"
    exit_1 = section[section.index("Exit 1"):]
    for needle, message in (
        ("build-develop-prompt.sh replaces-report", "never builds the correction prompt with build-develop-prompt.sh replaces-report"),
        ("develop-replaces-report", "never launches a develop-replaces-report leaf"),
        ("supervise.sh", "never launches that leaf through supervise.sh"),
    ):
        assert needle in exit_1, f"SKILL.md's unreplaced-cases.sh exit 1 {message}: {exit_1}"
    assert re.search(r"(no|not|never)[^.]{0,80}REVISE_BUDGET|REVISE_BUDGET[^.]{0,80}(no|not|never)", exit_1), \
        f"SKILL.md's unreplaced-cases.sh exit 1 never says the correction leaf spends no REVISE_BUDGET attempt: {exit_1}"
    assert re.search(r"(no|not|never)[^.]{0,60}revise[^.]{0,20}mark", exit_1), \
        f"SKILL.md's unreplaced-cases.sh exit 1 never says the correction leaf writes no revise mark: {exit_1}"
    assert re.search(r"(again|re-?run)[^.]{0,120}unreplaced-cases\.sh|unreplaced-cases\.sh[^.]{0,120}(again|re-?run)", exit_1), \
        f"SKILL.md's unreplaced-cases.sh exit 1 never runs unreplaced-cases.sh again on the corrected report: {exit_1}"


def test_1625_skill_md_s_unreplaced_cases_exit_1_on_the_corrected_report_bails_with_cause_unreplaced_cases_naming_each_printed_case_and_launches_no_second_correction_leaf_and_no_verifier():
    section = unreplaced_paragraph()
    assert section.strip(), "SKILL.md has no unreplaced-cases.sh paragraph in the Red step to read"
    assert "Exit 1 again" in section, f"SKILL.md's unreplaced-cases.sh paragraph never says what exit 1 on the corrected report does: {section}"
    again = section[section.index("Exit 1 again"):]
    again = again[:again.index("Exit 2")] if "Exit 2" in again else again
    assert "bail with cause=unreplaced-cases" in again, f"SKILL.md's second unreplaced-cases.sh exit 1 never bails with cause=unreplaced-cases: {again}"
    assert re.search(r"naming each case", again), f"SKILL.md's second unreplaced-cases.sh exit 1 never names each printed case: {again}"
    assert re.search(r"(no|not|never)[^.]{0,60}(second|another|further|more)[^.]{0,60}(correction|replaces-report)", again), \
        f"SKILL.md's second unreplaced-cases.sh exit 1 never says no second correction leaf launches: {again}"
    assert re.search(r"(no|not|never)[^.]{0,30}verifier", again), f"SKILL.md's second unreplaced-cases.sh exit 1 never says no verifier launches: {again}"


def test_1625_skill_md_s_develop_replaces_report_wait_leaf_exit_1_or_2_bails_with_cause_replaces_report_failed_launching_no_verifier_runs_step_cost_after_the_wait_and_the_bail_table_lists_the_cause_as_a_system_failure():
    section = unreplaced_paragraph()
    assert section.strip(), "SKILL.md has no unreplaced-cases.sh paragraph in the Red step to read"
    wait = section.index("wait-leaf.sh develop-replaces-report")
    after_wait = section[wait:]
    assert re.search(r"exit(s)? 1 or 2|exit 2 or 1|exits? [12][^.]{0,40}(or|and) [12]", after_wait), \
        f"SKILL.md never says what wait-leaf.sh develop-replaces-report exit 1 or 2 does: {after_wait}"
    assert "bail with cause=replaces-report-failed" in section, f"SKILL.md never bails with cause=replaces-report-failed: {section}"
    assert "step-cost.sh" in after_wait, f"SKILL.md never runs step-cost.sh after the develop-replaces-report wait: {after_wait}"
    row = next((line for line in BAIL.read_text().splitlines() if line.startswith("- `replaces-report-failed`")), "")
    assert row, "SKILL.md's bail-cause table has no replaces-report-failed entry"
    assert "system" in row.lower(), f"SKILL.md's bail-cause table never lists replaces-report-failed as a system failure: {row}"


def test_1546_skill_md_never_runs_replaces_case_survivors_sh_at_any_place_it_names_it_as_a_run_before_the_last_place_it_runs_unreplaced_cases_sh():
    unreplaced = run_lines(UNREPLACED_RUN)
    survivors = run_lines(r"\$S/replaces-case-survivors\.sh|[Rr]uns? [^.]*replaces-case-survivors\.sh")
    assert unreplaced and survivors, f"SKILL.md lacks an unreplaced-cases.sh run or a replaces-case-survivors.sh run (unreplaced={unreplaced}, survivors={survivors})"
    for run in survivors:
        assert run >= max(unreplaced), f"SKILL.md:{run} runs replaces-case-survivors.sh before the unreplaced-cases.sh run at line {max(unreplaced)}"


def test_1558_skill_md_s_green_verify_line_that_runs_replaces_case_survivors_sh_before_the_launch_carries_a_replaces_case_qualifier_so_an_ordinary_step_runs_nothing():
    run = next((line for line in skill_lines()
                if 'Run `$S/replaces-case-survivors.sh "<step text>"` before the launch below' in line), None)
    assert run, "SKILL.md has no Green Verify line running replaces-case-survivors.sh before the launch below"
    assert "⟦replaces-case⟧" in run, "SKILL.md runs replaces-case-survivors.sh with no ⟦replaces-case⟧ qualifier"


def test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused_and_bailing_lists_that_cause_as_a_system_failure():
    calls = outside_cost_check(run_lines(r"\$S/add-ledger-step\.sh [^ ]*\.tdd/issue-<n>\.md|\$S/add-ledger-step\.sh --criterion <k> \.tdd/issue-<n>\.md"))
    assert calls, "SKILL.md has no add-ledger-step.sh call site"
    lines = skill_lines()
    for call in calls:
        near = plain(lines[call - 1:call + 30])
        says(near, r"exits? 2[^.]{0,120}step-add-refused|step-add-refused[^.]{0,120}exits? 2",
             f"SKILL.md:{call} calls add-ledger-step.sh and never says its exit 2 bails with cause step-add-refused")
    says(bailing_causes(), r"step-add-refused[^.]{0,220}system", "SKILL.md's Bailing causes list never classifies step-add-refused as a system failure")


def test_1625_skill_md_s_second_unreplaced_cases_sh_check_reads_both_the_red_report_and_the_correction_leaf_s_develop_replaces_report_out_so_a_case_the_first_report_replaced_still_counts():
    section = unreplaced_paragraph()
    assert section.strip(), "SKILL.md has no unreplaced-cases.sh paragraph in the Red step to read"
    exit_1 = section[section.index("Exit 1"):]
    rerun = exit_1[:exit_1.index("Exit 1 again")] if "Exit 1 again" in exit_1 else exit_1
    # The command itself, not the prose after it: a parenthetical naming the Red report must not
    # satisfy a command that reads only the correction output.
    commands = re.findall(r"unreplaced-cases\.sh \"<step line>\"((?:\s+\.tdd/[^\s()]+\.out)+)", rerun)
    assert commands, f"SKILL.md's unreplaced-cases.sh exit 1 never runs unreplaced-cases.sh again on a report: {rerun}"
    command = commands[-1]
    assert ".tdd/develop-replaces-report.out" in command, \
        f"SKILL.md's second unreplaced-cases.sh run never names .tdd/develop-replaces-report.out as a report it reads: {command}"
    assert re.search(r"\.tdd/(develop-red|revise-red-<k>)\.out", command), \
        f"SKILL.md's second unreplaced-cases.sh run never also names the Red report it read first: {command}"


def test_1625_skill_md_allows_one_red_report_at_most_one_develop_replaces_report_leaf_launching_it_once_and_granting_no_second_or_third_correction_before_the_bail():
    text = "\n".join(skill_lines())
    launches = re.findall(r"detach-leaf\.sh \$S/supervise\.sh develop-replaces-report\b", text)
    assert len(launches) == 1, f"SKILL.md launches a develop-replaces-report leaf {len(launches)} times, not once"
    section = unreplaced_paragraph()
    assert section.strip(), "SKILL.md has no unreplaced-cases.sh paragraph in the Red step to read"
    for grant in re.finditer(r"(second|third|another|further|additional|two|three|up to \d+)[^.\n]{0,40}(correction|develop-replaces-report)", section, re.I):
        before = section[max(0, grant.start() - 40):grant.start()]
        assert re.search(r"\b(no|not|never|without)\b[^.]{0,30}$", before, re.I), \
            f"SKILL.md's unreplaced-cases.sh paragraph allows more than one correction: {section[max(0, grant.start() - 80):grant.end() + 80]}"
    assert re.search(r"(at most one|one chance|exactly one|only one|one correction)", section, re.I), \
        f"SKILL.md's unreplaced-cases.sh paragraph never limits the Red to one correction: {section}"


def test_1625_skill_md_s_bail_cause_table_describes_unreplaced_cases_as_a_second_exit_1_after_the_one_correction_or_an_exit_2_at_once_not_as_any_exit_1():
    entry = re.search(r"- `unreplaced-cases`.*?(?=\n- `)", "\n".join(_lines(BAILING)), re.S)
    assert entry, "SKILL.md's Bailing causes list has no unreplaced-cases entry"
    text = plain(entry.group(0).splitlines())
    assert re.search(r"(second|again|after the one correction)", text), \
        f"SKILL.md's unreplaced-cases bail cause never says exit 1 is the second one, after the one correction: {text}"
    assert re.search(r"exit(s|ed)? \**2\**[^.]{0,80}(at once|immediately|no correction)|(at once|immediately)[^.]{0,80}exit(s|ed)? \**2", text), \
        f"SKILL.md's unreplaced-cases bail cause never says an exit 2 bails at once: {text}"
