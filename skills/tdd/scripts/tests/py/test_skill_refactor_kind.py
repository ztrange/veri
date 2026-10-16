"""Cases for what skills/tdd/SKILL.md tells a refactor-kind run, read as text."""
import importlib
import pathlib
import re

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

PLAN = "### 2. Scope & plan → the ledger"
DRAFT_PR = "### 4. Draft PR"


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


def window(text, pattern, radius=250):
    for line in text.split(b"\n"):
        match = re.search(pattern.encode(), line)
        if match:
            return line[max(match.start() - radius, 0):match.end() + radius]
    return b""


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
