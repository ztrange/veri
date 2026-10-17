"""Cases for what skills/tdd/SKILL.md tells a refactor-kind run, read as text."""
import importlib
import pathlib
import re

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

PLAN = "### 2. Scope & plan → the ledger"
DRAFT_PR = "### 4. Draft PR"
LOOP = "### 3. The cycle loop"
PHASED = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"
GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def plain(raw):
    return raw.translate(None, b"*`").lower().replace(b"\n", b" ")


def section(heading):
    text = importlib.import_module("skill_sections").section(SKILL, heading)
    return plain(text.encode())


def skill_text():
    return plain(SKILL.read_bytes())


def has(text, pattern):
    return any(re.search(pattern.encode(), line) for line in text.split(b"\n"))


def windows(text, pattern, radius=250):
    found = []
    for line in text.split(b"\n"):
        for match in re.finditer(pattern.encode(), line):
            found.append(line[max(match.start() - radius, 0):match.end() + radius])
    return found


def window(text, pattern, radius=250):
    return next(iter(windows(text, pattern, radius)), b"")


def test_skill_md_tells_a_refactor_kind_run_to_plan_each_step_as_one_named_refactoring_whose_criterion_is_a_shell_predicate_false_before_the_step_and_true_after_it():
    text = section(PLAN)
    assert text.strip(), "SKILL.md has no Scope & plan section to read"
    assert has(text, r"refactor[- ]kind|## refactor section|label(l)?ed refactor"), "never names the refactor run kind"
    assert has(text, r"predicate"), "never says a refactor step's criterion is a shell predicate"
    near = window(text, r"predicate")
    assert has(near, r"(one|named) refactoring"), "names a predicate without saying each step is one named refactoring"
    assert has(near, r"false before"), "never says the predicate is false before the step"
    assert has(near, r"true after"), "never says the predicate is true after the step"


def test_the_develop_cover_prompt_tells_the_leaf_to_mutate_run_the_suite_expect_red_restore_and_prove_the_tree_unchanged_ending_in_covered_and_caught_by_and_skill_md_refuses_to_continue_past_cover_on_a_non_empty_git_status_porcelain(
    tmp_path, run_cli, build_develop_prompt
):
    spec = tmp_path / "spec"
    spec.write_text("QWIXTLE spec\n")
    code, out, _ = run_cli(build_develop_prompt, ["cover", str(spec), "Extract Function QWIXTLE", "make test"])
    raw = out.encode()
    assert raw.strip(), "build-develop-prompt.sh cover printed no prompt to read"
    cover = plain(raw)
    assert has(cover, r"mutat|break"), "never tells the leaf to mutate"
    assert has(cover, r"run the suite|run the (affected )?suites"), "never tells the leaf to run the suite"
    assert has(cover, r"expect red"), "never tells the leaf to expect red"
    assert has(cover, r"restore"), "never tells the leaf to restore"
    assert has(cover, r"git diff[^.]{0,120}before[^.]{0,40}mutat|git status --porcelain"), "never proves the tree unchanged"
    tail = b"\n".join([line for line in raw.split(b"\n") if line.strip()][-3:])
    assert has(tail, r"^COVERED:"), "closing lines carry no COVERED: line"
    assert has(tail, r"^CAUGHT_BY:"), "closing lines carry no CAUGHT_BY: line"
    near = window(skill_text(), r"(develop-cover|cover (phase|step|leaf))")
    assert has(near, r"git status --porcelain") and has(near, r"refus|stop|bail|(not|never) (go on|continue)"), (
        "SKILL.md never refuses to continue past Cover on a non-empty git status --porcelain"
    )


def test_skill_md_s_cover_step_on_covered_no_bails_with_cause_uncovered_narrates_the_remedy_find_a_seam_surround_the_behaviour_and_runs_coverage_blocker():
    near = window(skill_text(), r"covered: no")
    assert near, "SKILL.md never says what a run does when Cover answers COVERED: no"
    assert has(near, r"bail[^.]*cause uncovered|cause uncovered"), "never bails with cause uncovered"
    assert has(near, r"seam"), "never narrates finding a seam"
    assert has(near, r"surround"), "never narrates surrounding the behaviour"
    assert has(near, r"coverage-blocker\.sh"), "never runs coverage-blocker.sh"


def test_skill_md_s_refactor_kind_cycle_runs_cover_transform_verify_rejects_a_transform_whose_commits_touch_a_test_file_via_transform_touches_tests_and_abandons_a_step_by_resetting_to_its_base_sha():
    text = skill_text()
    assert has(text, r"cover (→|->|, then|then) transform (→|->|, then|then) verify"), "never states Cover → Transform → Verify"
    near = window(text, r"transform-touches-tests\.sh")
    assert near, "never runs transform-touches-tests.sh"
    assert has(near, r"reject|refus"), "runs transform-touches-tests.sh without saying a touching transform is rejected"
    assert has(text, r"git reset --hard <base-sha>|reset(ting)? (it )?to (its|the step.s) base sha"), (
        "never abandons a step by resetting to its base sha"
    )


def test_skill_md_s_draft_pr_step_titles_a_run_on_an_issue_labelled_refactor_with_the_refactor_prefix_beside_fix_and_feat():
    text = section(DRAFT_PR)
    assert text.strip(), "SKILL.md has no Draft PR section to read"
    assert b"refactor:" in text, "never names the refactor: prefix"
    near = window(text, r"refactor:")
    assert has(near, r"label"), "names the refactor: prefix without tying it to the refactor label"
    assert has(near, r"fix") and has(near, r"feat"), "names the prefix away from fix: and feat:"


def test_679_skill_md_s_cover_step_reads_the_cover_report_through_cover_outcome_exit_3_goes_on_to_transform_posting_the_proof_in_the_cover_comment_without_bailing_or_running_coverage_blocker_exit_2_bails_as_no_verdict():
    near = window(skill_text(), r"cover-outcome\.sh")
    assert near, "never reads the cover report through cover-outcome.sh"
    exit3 = window(near, r"exit 3")
    assert exit3, "runs cover-outcome.sh without saying what its exit 3 does"
    assert has(exit3, r"transform"), "exit 3 never goes on to Transform"
    assert has(exit3, r"proof") and has(exit3, r"cover comment|comment"), "exit 3 never posts the proof in the Cover comment"
    assert has(exit3, r"(without|not|never|no) [^.]{0,60}(bail|coverage-blocker\.sh)"), "exit 3 never says it neither bails nor runs coverage-blocker.sh"
    assert has(near, r"exit 2[^.]{0,120}no-verdict"), "exit 2 never bails as no-verdict"


def test_679_skill_md_reruns_a_type_only_step_s_proof_command_after_its_transform_commits_a_non_zero_exit_rejecting_the_transform_as_transform_touches_tests_exit_1_does():
    near = window(skill_text(), r"(rerun|re-run|runs? again)[^.]{0,80}proof")
    assert near, "never reruns a type-only step's proof command after its transform"
    assert has(near, r"type-only"), "reruns a proof command without tying it to a type-only step"
    assert has(near, r"after[^.]{0,60}transform[^.]{0,40}commit|transform[^.]{0,40}commit[^.]{0,60}(then|after)"), "never says it reruns after the transform commits"
    assert has(near, r"(non-zero|nonzero)[^.]{0,80}reject"), "never says a non-zero exit rejects the transform"
    assert has(near, r"transform-touches-tests\.sh[^.]{0,40}exit 1"), "never ties the rejection to transform-touches-tests.sh exit 1"


def test_679_skill_md_keeps_a_type_only_step_s_proof_command_the_text_cover_outcome_printed_after_type_only_in_a_run_file_between_cover_and_transform_and_the_conductor_itself_reruns_that_saved_command():
    text = skill_text()
    near = window(text, r"type-only: ")
    assert near, "never names the text cover-outcome.sh prints after 'type-only: '"
    assert has(near, r"cover-outcome\.sh"), "names 'type-only: ' without saying cover-outcome.sh printed it"
    assert has(near, r"(save|write|keep|store)[^.]{0,80}\.tdd/[a-z0-9<>_.-]+"), "never says the proof command is saved to a run file under .tdd/"
    assert has(text, r"conductor[^.]{0,40}(rerun|re-run|runs? again)[^.]{0,80}(saved|\.tdd/)"), "never says the conductor reruns the saved proof command"


def test_679_skill_md_s_scope_and_plan_tells_a_refactor_kind_planner_to_fold_a_deletion_into_the_step_that_makes_the_code_dead_never_leaving_a_no_op_in_place_for_a_later_step_to_delete():
    near = window(section(PLAN), r"no-op")
    assert near, "Scope & plan never names a no-op"
    assert has(near, r"refactor[- ]kind|refactor (plan|step)"), "names a no-op without tying it to a refactor-kind plan"
    assert has(near, r"(fold|same step|one step)[^.]{0,120}delet|delet[^.]{0,120}(fold|same step|one step)"), "never tells the planner to fold the deletion into the same step"
    assert has(near, r"dead"), "never names the step that makes the code dead"
    assert has(near, r"(never|not|no)[^.]{0,80}no-op[^.]{0,80}later step|later step[^.]{0,80}delet"), "never forbids leaving a no-op for a later step to delete"


def test_skill_md_plans_an_interface_change_as_one_step_listing_its_phases_and_runs_them_in_order_each_as_a_developer_leaf_then_a_blind_verifier_ticking_the_phase_s_mark_with_tick_ledger_sh_phase_in_its_commit():
    plan = section(PLAN)
    assert has(plan, r"interface change"), "Scope & plan never names an interface change"
    assert "⟦phases:".encode() in window(plan, r"interface change", 400), "names an interface change without planning it as one step listing the phases"
    loop = section(LOOP)
    assert b"tick-ledger.sh --phase" in loop, "The cycle loop never ticks a phase with tick-ledger.sh --phase"
    near = window(loop, r"tick-ledger\.sh --phase", 900)
    assert "⟦phases".encode() in near, "ticks a phase without naming the phased step"
    assert has(near, r"in order|ledger-steps\.sh next-phase"), "never runs a phased step's phases in order"
    assert b"build-develop-prompt.sh" in near, "never builds a phase's developer leaf"
    assert b"run-verdict.sh" in near, "never follows a phase with a blind verifier"
    assert has(near, r"commit"), "never ties a phase's tick to its commit"
    assert b"the run loop calls neither yet" not in skill_text(), "still says the run loop calls neither"


def test_skill_md_rejects_an_expand_migrate_or_contract_b_phase_s_commit_that_transform_touches_tests_sh_exits_1_on_and_a_contract_a_phase_s_commit_that_production_frozen_sh_exits_1_on():
    phased = section(PHASED)
    assert phased.strip(), "SKILL.md has no phased step subsection to read"
    assert b"transform-touches-tests.sh" in phased, "phased step never runs transform-touches-tests.sh"
    near = window(phased, r"transform-touches-tests\.sh")
    for phase in (b"expand", b"migrate", b"contract-b"):
        assert phase in near, f"runs transform-touches-tests.sh without naming {phase.decode()}"
    assert has(near, r"exit 1") and has(near, r"reject"), "never says exit 1 rejects the commit"
    assert b"production-frozen.sh" in phased, "phased step never runs production-frozen.sh"
    near = window(phased, r"production-frozen\.sh")
    assert b"contract-a" in near, "runs production-frozen.sh without naming contract-a"
    assert has(near, r"exit 1") and has(near, r"reject"), "never says production-frozen.sh exit 1 rejects the commit"


def test_skill_md_starts_a_phased_step_s_contract_only_once_no_product_caller_sh_on_the_old_interface_exits_0():
    phased = section(PHASED)
    assert phased.strip(), "SKILL.md has no phased step subsection to read"
    assert b"no-product-caller.sh" in phased, "phased step never runs no-product-caller.sh"
    near = window(phased, r"no-product-caller\.sh")
    assert b"contract" in near, "no tie to the contract phase"
    assert has(near, r"old interface"), "never says it is run on the old interface"
    assert has(near, r"exit(s)? 0") and has(near, r"only once|until|before"), "never says the contract starts only once it exits 0"
    flat_near = window(phased, r"no-product-caller\.sh", 600)
    assert b"contract-b" in flat_near, "does not name contract-b as the phase it gates"
    assert b"before it launches contract-a or contract-b" not in flat_near, "still runs it before contract-a"
    assert has(flat_near, r"contract-a starts on the migrate phase's pass without the scan"), "never says contract-a starts without the scan"


def test_skill_md_spends_one_refactor_of_the_budget_for_a_whole_phased_step_not_one_per_phase():
    phased = section(PHASED)
    assert phased.strip(), "SKILL.md has no phased step subsection to read"
    budget = r"refactor-budget\.sh|veri_(issue_)?refactor_budget|refactor budget"
    assert has(phased, budget), "phased step never says what it spends of the refactor budget"
    near = window(phased, budget)
    assert has(near, r"one refactor"), "never says the step spends one refactor"
    assert has(near, r"whole step|not one per phase"), "never says it is for the whole step"


def test_skill_md_resets_a_phased_step_s_contract_phase_that_exhausts_revise_budget_to_its_own_base_sha_keeps_the_expand_and_migrate_commits_and_files_the_contract_under_owed_steps():
    phased = section(PHASED)
    assert phased.strip(), "SKILL.md has no phased step subsection to read"
    assert b"revise_budget" in phased and has(phased, r"exhaust"), "never says what an exhausted REVISE_BUDGET does"
    near = window(phased, r"exhaust")
    assert b"contract" in near, "not tied to the contract phase"
    assert has(near, r"reset") and has(near, r"(its own|that phase.s|the contract.s) base"), "never resets to its own base sha"
    assert b"expand" in near and b"migrate" in near and has(near, r"kept|keep"), "never keeps the expand and migrate commits"
    assert b"## owed steps" in near, "never files the contract under ## Owed steps"


def test_skill_md_accepts_a_replaces_case_group_step_s_green_only_once_the_conductor_s_own_run_of_mutation_parity_sh_on_that_step_s_pairs_table_exits_0():
    green = section(GREEN)
    assert green.strip(), "SKILL.md has no Green subsection to read"
    assert b"mutation-parity.sh" in green, "Green never runs mutation-parity.sh"
    near = window(green, r"mutation-parity\.sh")
    assert b"replaces-case" in near, "not tied to a replaces-case step"
    assert b"pairs table" in near, "not run on the pairs table"
    assert has(near, r"exit(s)? 0") and has(near, r"only once|until|before"), "never says accepted only once it exits 0"


def test_skill_md_accepts_a_phased_step_s_contract_a_phase_only_once_the_conductor_s_own_run_of_mutation_parity_sh_on_that_phase_s_pairs_table_exits_0():
    phased = section(PHASED)
    assert phased.strip(), "SKILL.md has no phased step subsection to read"
    assert b"mutation-parity.sh" in phased, "phased step never runs mutation-parity.sh"
    near = window(phased, r"mutation-parity\.sh")
    assert b"contract-a" in near, "not tied to contract-a"
    assert b"pairs table" in near, "not run on the phase's pairs table"
    assert has(near, r"exit(s)? 0") and has(near, r"only once|until|before"), "never says accepted only once it exits 0"


def test_skill_md_puts_mutation_parity_sh_s_report_into_the_pr_body_as_the_pairs_table_and_each_row_it_reports_owed_under_owed_by_a_human():
    near = b"\n".join(w for w in windows(skill_text(), r"mutation-parity\.sh", 400) if b"pr body" in w)
    assert near, "never puts mutation-parity.sh's report into the PR body"
    assert b"pairs table" in near, "does not say it is the pairs table"
    assert has(near, r"rows? (it|mutation-parity\.sh) reports? owed") and b"## owed by a human" in near, (
        "never puts a row reported owed under ## Owed by a human"
    )


def test_skill_md_s_draft_pr_step_puts_the_conductor_s_mutation_parity_sh_report_into_the_pr_body_template_as_the_pairs_table_and_its_owed_rows_under_owed_by_a_human_and_the_replaces_case_green_gate_says_the_same_of_its_run_s_report():
    pr = section(DRAFT_PR)
    templates = [m.group(0) for m in re.finditer(rb'gh api -x patch [^"]*-f title="[^"]*" -f body="[^"]*"', pr)]
    body_template = b"\n".join(templates)
    assert body_template, "Draft PR step has no gh api -X PATCH template to read"
    assert b"mutation-parity.sh" in body_template, "Draft PR body template never includes mutation-parity.sh's report"
    near = window(body_template, r"mutation-parity\.sh")
    assert b"pairs table" in near, "template does not say it is the pairs table"
    assert has(near, r"owed") and b"## owed by a human" in near, "template never puts owed rows under ## Owed by a human"
    green_near = b"\n".join(w for w in windows(section(GREEN), r"mutation-parity\.sh", 400) if b"pr body" in w)
    assert green_near, "Green gate never says its report goes into the PR body"
    assert b"pairs table" in green_near, "Green gate does not say it is the pairs table"
    assert has(green_near, r"owed") and b"## owed by a human" in green_near, "Green gate never puts owed rows under ## Owed by a human"


def test_skill_md_marks_an_exhausted_contract_phase_owed_with_tick_ledger_sh_phase_owed_phase_before_committing_the_ledger_so_next_phase_never_hands_the_owed_contract_back():
    near = window(section(PHASED), r"exhaust", 700)
    assert near.strip(), "phased step has no exhausted-contract paragraph to read"
    assert b"tick-ledger.sh --phase-owed <phase>" in near, "never marks the contract phase owed with tick-ledger.sh --phase-owed <phase>"
    before_commit, sep, _ = near.partition(b"commit the ledger")
    assert sep and b"tick-ledger.sh --phase-owed" in before_commit, "marks the phase owed only after committing the ledger"


def test_issue_1527_skill_md_says_an_issue_whose_work_changes_only_tests_is_not_refactor_kind_and_is_planned_as_diff_checked_steps():
    text = section(PLAN)
    assert text.strip(), "SKILL.md has no Scope & plan section to read"
    assert has(text, r"changes only tests"), "never names an issue whose work changes only tests"
    near = window(text, r"changes only tests")
    assert has(near, r"not refactor-kind"), "never says a tests-only issue is not refactor-kind"
    assert has(near, r"⟦diff-checked⟧ steps"), "never says a tests-only issue is planned as ⟦diff-checked⟧ steps"
