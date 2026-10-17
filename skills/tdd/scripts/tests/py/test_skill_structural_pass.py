"""Cases for where skills/tdd/SKILL.md runs the issue's one structural pass, read as text."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"
DRAFT_PR = "### 4. Draft PR"
PASS = "one structural pass"
TOUCHES = "transform-touches-tests.sh <base-sha>"
VERIFIER = "transform verifier against <base-sha>"


def plain(lines):
    return " ".join(line.translate({ord("*"): None, ord("`"): None}) for line in lines) + " "


def draft_lines():
    text = importlib.import_module("skill_sections").section(SKILL, DRAFT_PR)
    return text.splitlines()[1:]


def before_ready():
    lines = []
    for line in draft_lines():
        if line.startswith("#") or "gh_pr_ready" in line:
            break
        lines.append(line)
    return plain(lines)


def pass_text():
    section = before_ready()
    assert section.strip(), "SKILL.md has no '### 4. Draft PR' section before a gh pr ready to read"
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
    assert section.strip(), "SKILL.md has no '### 4. Draft PR' section before a gh pr ready to read"
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


def test_skill_md_s_structural_pass_stopped_budget_spent_runs_refactor_overflow_sh_with_the_candidates_it_took_up_and_puts_the_filed_issue_s_url_in_the_pr_body_candidates_done_or_nothing_structural_files_nothing():
    requires(pass_text(), "refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md <taken>",
             "<taken> being the candidates the pass took up", "stopped=budget-spent",
             "candidates-done or nothing-structural files nothing")
    assert "refactor-overflow.sh" in pr_body(), "SKILL.md's Draft PR body never carries the issue refactor-overflow.sh filed"


def test_skill_md_s_draft_pr_body_still_carries_refactor_owed_sh_render_s_refactor_owed_section_after_the_structural_pass_has_run():
    step = plain(draft_lines())
    assert PASS in step, "SKILL.md's Draft PR step has no 'one structural pass'"
    assert "refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md" in step.split(PASS, 1)[1], \
        "never runs refactor-owed.sh render after its structural pass"
    assert "that render's output" in pr_body(), "SKILL.md's Draft PR body never carries that render's output"


def test_skill_md_s_structural_pass_says_its_overflow_filing_applies_no_label_to_this_issue_and_commits_no_debt_file():
    requires(pass_text(), "applies no label to this issue", "commits no debt file")
