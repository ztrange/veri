"""Cases for what skills/tdd/SKILL.md tells a refactor-kind run, read as text."""
import importlib
import pathlib
import re

import pytest
from skill_sections import has, plain_folded as plain, window, windows

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
LOOP = "### 3. The cycle loop"
PHASED = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"


@pytest.fixture
def build_develop_prompt():
    return importlib.import_module("veri.build_develop_prompt")


def section(heading):
    text = importlib.import_module("skill_sections").section(SKILL, heading)
    return plain(text.encode())


def skill_text():
    return plain(SKILL.read_bytes())


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


def test_skill_md_s_draft_pr_step_titles_a_run_on_an_issue_labelled_refactor_with_the_refactor_prefix_beside_fix_and_feat():
    text = section(DRAFT_PR)
    assert text.strip(), "SKILL.md has no Draft PR section to read"
    assert b"refactor:" in text, "never names the refactor: prefix"
    near = window(text, r"refactor:")
    assert has(near, r"label"), "names the refactor: prefix without tying it to the refactor label"
    assert has(near, r"fix") and has(near, r"feat"), "names the prefix away from fix: and feat:"


def test_skill_md_plans_an_interface_change_as_one_step_listing_its_phases_and_runs_them_in_order_each_as_a_developer_leaf_then_a_blind_verifier_ticking_the_phase_s_mark_with_tick_ledger_sh_phase_in_its_commit():
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


def test_skill_md_marks_an_exhausted_contract_phase_owed_with_tick_ledger_sh_phase_owed_phase_before_committing_the_ledger_so_next_phase_never_hands_the_owed_contract_back():
    near = window(section(PHASED), r"exhaust", 700)
    assert near.strip(), "phased step has no exhausted-contract paragraph to read"
    assert b"tick-ledger.sh --phase-owed <phase>" in near, "never marks the contract phase owed with tick-ledger.sh --phase-owed <phase>"
    before_commit, sep, _ = near.partition(b"commit the ledger")
    assert sep and b"tick-ledger.sh --phase-owed" in before_commit, "marks the phase owed only after committing the ledger"
