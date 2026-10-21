"""Cases for where skills/tdd/SKILL.md runs the issue's one structural pass, read as text."""
import importlib
import pathlib
import re

from skill_sections import plain_lines_cased as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
DRAFT_PR = "### 4. Draft PR"
PASS = "one structural pass"
TOUCHES = "transform-touches-tests.sh <base-sha>"
VERIFIER = "transform verifier against <base-sha>"


def draft_lines():
    text = importlib.import_module("skill_sections").section(SKILL, DRAFT_PR)
    return text.splitlines()[1:]


def before_ready():
    lines = []
    for line in draft_lines():
        if line.startswith("#") or "gh_pr_ready" in line:
            break
        lines.append(line)
    section = plain(lines)
    assert section.strip(), "SKILL.md has no '### 4. Draft PR' section before a gh pr ready to read"
    return section


def pass_text():
    section = before_ready()
    assert PASS in section, "SKILL.md's Draft PR step has no 'one structural pass' before gh pr ready"
    return section.split(PASS, 1)[1]


def pr_body():
    return "\n".join(line for line in draft_lines() if re.search(r"-X PATCH .*-f body=", line))


def tunables_parse():
    lines, inside = [], False
    for line in SKILL.read_text().splitlines():
        inside = inside or line.startswith("5. **Tunables parse.**")
        if inside and line.startswith("6. **Leaf models parse.**"):
            break
        if inside:
            lines.append(line)
    return plain(lines)


def requires(text, *phrases):
    for phrase in phrases:
        assert phrase in text, f"SKILL.md's structural pass never says {phrase!r}"


def test_skill_md_s_draft_pr_step_runs_one_structural_pass_before_gh_pr_ready_a_structural_leaf_per_refactor_owed_sh_list_candidate_bounded_by_refactor_touched_sh_issue_counted_by_refactor_budget_sh_issue():
    section = before_ready()
    requires(section, "refactor-owed.sh list", "build-develop-prompt.sh structural",
             "refactor-touched.sh --issue", "refactor-budget.sh --issue")


def test_skill_md_s_structural_pass_checks_each_transform_leaf_s_commits_with_transform_touches_tests_sh_base_sha_and_has_the_blind_transform_verifier_judge_them_against_that_base_sha_one_commit_per_transform():
    requires(pass_text(), TOUCHES, VERIFIER, "one commit per transform")


def test_skill_md_s_structural_pass_runs_transform_touches_tests_sh_before_the_blind_transform_verifier_and_both_before_the_next_candidate_s_structural_leaf_is_launched():
    text = pass_text()
    touches, verifier, nxt = (text.find(p) for p in (TOUCHES, VERIFIER, "before the next candidate"))
    assert min(touches, verifier, nxt) >= 0, f"a phrase to order is missing: touches {touches}, verifier {verifier}, next {nxt}"
    assert touches < verifier < nxt, f"checks ordered wrongly: touches {touches}, verifier {verifier}, next {nxt}"


def test_skill_md_s_structural_pass_when_refactor_owed_sh_list_exits_3_is_skipped_with_no_bail_and_marks_the_log_event_sh_structural_pass_stopped_nothing_structural():
    requires(pass_text(), "event.sh structural-pass", "stopped=nothing-structural", "with no bail")


def test_skill_md_s_structural_pass_ends_with_one_event_sh_structural_pass_mark_carrying_transforms_budget_and_stopped_and_preflight_refuses_a_veri_issue_refactor_budget_refactor_budget_sh_issue_0_cannot_read():
    requires(pass_text(), "event.sh structural-pass transforms=<count> budget=<VERI_ISSUE_REFACTOR_BUDGET> stopped=<reason>")
    preflight = tunables_parse()
    assert preflight.strip(), "SKILL.md has no '5. Tunables parse.' preflight step to read"
    requires(preflight, "refactor-budget.sh --issue 0", "VERI_ISSUE_REFACTOR_BUDGET")


def test_skill_md_s_structural_pass_takes_the_candidates_in_the_order_refactor_owed_sh_list_prints_them_and_names_that_order_as_most_valuable_first():
    requires(pass_text(), "in the order refactor-owed.sh list prints them", "most valuable first")


def test_skill_md_s_draft_pr_body_still_carries_refactor_owed_sh_render_s_refactor_owed_section_after_the_structural_pass_has_run():
    step = plain(draft_lines())
    assert PASS in step, "SKILL.md's Draft PR step has no 'one structural pass'"
    assert "refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md" in step.split(PASS, 1)[1], \
        "never runs refactor-owed.sh render after its structural pass"
    assert "that render's output" in pr_body(), "SKILL.md's Draft PR body never carries that render's output"


def squeezed():
    return re.sub(" +", " ", pass_text())


def after(text, marker):
    assert marker in text, f"SKILL.md's structural pass has no {marker!r} to read from"
    return text.split(marker, 1)[1]


def until(text, marker):
    return text.split(marker, 1)[0]


APPLIED = "refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md"


def test_596_skill_md_s_structural_pass_runs_whenever_refactor_owed_sh_list_prints_a_candidate_never_skips_or_shortens_it_for_cost_spends_less_only_by_a_lower_veri_issue_refactor_budget_set_before_launch_and_files_candidates_past_the_budget_by_refactor_overflow_sh():
    requires(squeezed(), "whenever refactor-owed.sh list prints a candidate",
             "never skips or shortens it for cost",
             "set a lower VERI_ISSUE_REFACTOR_BUDGET before launch")


def test_596_skill_md_s_structural_pass_says_stopped_takes_only_candidates_done_budget_spent_or_nothing_structural_and_budget_spent_is_marked_only_when_refactor_budget_sh_issue_exited_3_i_e_transforms_equals_the_budget():
    requires(squeezed(), "stopped= takes only candidates-done, budget-spent or nothing-structural",
             "budget-spent is marked only when refactor-budget.sh --issue exited 3",
             "transforms equals the budget")


def test_691_skill_md_s_structural_pass_takes_each_candidate_s_predicate_from_a_build_develop_prompt_sh_predicate_leaf_checked_by_structural_predicate_sh_whose_record_is_the_test_path_the_transform_verifier_runs_and_skips_a_candidate_with_no_predicate_for_refactor_overflow_sh_to_file():
    requires(squeezed(), "build-develop-prompt.sh predicate",
             "structural-predicate.sh .tdd/issue-<n>-predicate",
             "the test path the transform verifier runs",
             "refactor-owed.sh not-done", "no-predicate")


def test_726_skill_md_s_structural_pass_says_a_missing_tdd_issue_n_refactor_owed_md_is_the_refactor_owed_sh_list_exit_3_case_marked_stopped_nothing_structural_before_the_pr_is_readied():
    requires(squeezed(), "a missing .tdd/issue-<n>-refactor-owed.md is the list exit-3 case",
             "marked stopped=nothing-structural before the PR is readied")


def test_952_skill_md_s_structural_pass_runs_refactor_owed_sh_applied_on_the_run_s_owed_file_with_the_candidate_and_the_commit_after_each_transform_verifier_pass_before_the_pr_body_is_rendered():
    text = pass_text()
    applied, verifier = text.find(APPLIED), text.find(VERIFIER)
    assert applied >= 0, f"SKILL.md's structural pass never runs {APPLIED} before gh pr ready"
    assert verifier < applied, f"SKILL.md's structural pass runs {APPLIED} at {VERIFIER}'s offset {verifier} or before ({applied})"
    assert "PASS" in text, "SKILL.md's structural pass never ties refactor-owed.sh applied to a transform verifier PASS"


def test_980_skill_md_s_structural_pass_stages_and_commits_tdd_issue_n_refactor_owed_md_after_refactor_owed_sh_applied_records_a_transform_before_the_pr_is_readied():
    text = pass_text()
    stage = "git add .tdd/issue-<n>-refactor-owed.md"
    applied, staged = text.find(APPLIED), text.find(stage)
    assert applied >= 0 and staged >= 0, f"a phrase to order is missing: {APPLIED} at {applied}, {stage} at {staged}"
    assert staged > applied, f"stages the owed file at {staged}, not after {APPLIED} at {applied}"
    assert "git commit" in text[staged:], "stages the owed file but never runs git commit after it before gh pr ready"


def test_1058_skill_md_s_structural_pass_records_a_candidate_whose_predicate_already_holds_structural_predicate_sh_exit_1_as_applied_with_refactor_owed_sh_applied_at_the_current_head_not_in_skipped_file_only_exit_3_appends_to_skipped_file():
    bound = "Once the pass ends"
    rest = after(squeezed(), "structural-predicate.sh .tdd/issue-<n>-predicate")
    assert bound in rest, f"never says {bound!r} after structural-predicate.sh"
    handling = until(rest, bound)
    requires(handling, APPLIED, "git rev-parse HEAD", "only exit 3")
    assert "1 or 3 ⇒ skip" not in handling, "still says structural-predicate.sh exit 1 or 3 ⇒ skip"


def test_skill_md_s_structural_pass_names_neither_refactor_overflow_sh_nor_refactor_owed_sh_out_of_scope_and_files_no_refactor_owed_by_issue():
    text = pass_text()
    for phrase in ("refactor-overflow.sh", "refactor-owed.sh out-of-scope", "Refactor owed by #"):
        assert phrase not in text, f"SKILL.md's structural pass still names {phrase!r}"


def test_skill_md_s_structural_pass_runs_a_develop_cover_leaf_read_through_cover_outcome_sh_before_each_transform_leaf_and_cover_no_launches_no_transform_records_uncovered_under_not_done_and_neither_bails_nor_files():
    text = squeezed()
    requires(text, "build-develop-prompt.sh cover", "develop-cover", "cover-outcome.sh")
    cover, outcome, transform = (text.find(p) for p in ("develop-cover", "cover-outcome.sh", "as develop-structural"))
    assert 0 <= cover < outcome < transform, f"cover leaf not ordered before the transform: cover {cover}, outcome {outcome}, transform {transform}"
    no = after(text, "COVERED: no")
    requires(until(no, "predicate leaf"), "launches no transform", "refactor-owed.sh not-done .tdd/issue-<n>-refactor-owed.md '<candidate>' uncovered",
             "neither bails nor files anything")


def test_refactor_overflow_script_and_module_no_longer_exist():
    scripts = SKILL.parent / "scripts"
    leftovers = [p for p in ("refactor-overflow.sh", "veri/refactor_overflow.py") if (scripts / p).exists()]
    assert leftovers == []


def test_skill_md_s_structural_pass_checks_each_transform_s_commits_with_transform_touches_tests_sh_base_sha_bound():
    requires(pass_text(), "transform-touches-tests.sh <base-sha> <bound>")


def test_skill_md_s_structural_pass_computes_each_candidate_s_bound_with_refactor_touched_sh_issue_issue_base_candidate_candidate():
    requires(pass_text(), "refactor-touched.sh --issue <issue-base> --candidate '<candidate>'")


def test_skill_md_s_structural_pass_records_a_candidate_the_budget_stops_with_refactor_owed_sh_not_done_and_reason_budget_spent():
    requires(pass_text(), "refactor-owed.sh not-done .tdd/issue-<n>-refactor-owed.md '<candidate>' budget-spent")


def test_skill_md_s_structural_pass_records_a_candidate_whose_transform_was_rejected_with_refactor_owed_sh_not_done_and_reason_transform_rejected():
    requires(pass_text(), "candidate transform-rejected with refactor-owed.sh not-done")


def test_skill_md_s_structural_pass_passes_the_commit_subject_git_log_1_format_s_as_the_last_argument_of_every_refactor_owed_sh_applied_call():
    calls = re.findall(r"refactor-owed\.sh applied .*?(?= {2}|$)", pass_text())
    assert calls, "SKILL.md's structural pass never calls refactor-owed.sh applied"
    for call in calls:
        assert call.endswith('"$(git log -1 --format=%s)"'), \
            f"SKILL.md's structural pass calls refactor-owed.sh applied without the commit subject last: {call}"
