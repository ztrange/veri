"""Cases for what skills/tdd/SKILL.md tells the conductor to do when a step's revise budget runs out, and where its step-cost check runs."""
import importlib
import pathlib
import re

from skill_sections import plain_lines as plain, window_text as window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.with_name("REVISE.md")

REVISE = "## Revising on a REJECT"
COST = "#### The step's cost check"
STEP_COST = "step-cost.sh"


def _doc(heading):
    return REVISE_MD if heading == REVISE else SKILL


def _both():
    return SKILL.read_text() + "\n" + REVISE_MD.read_text()


def _lines(heading):
    section = importlib.import_module("skill_sections").section(_doc(heading), heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def sentences(text):
    return re.split(r"[.!?] ", text)


def grep(text, pattern):
    return any(re.search(pattern, line) for line in text.split("\n"))


def revise_section():
    return plain(_lines(REVISE))


def cost_lines():
    return _lines(COST)


def cost_sentences():
    return sentences(plain(cost_lines()))


def any_sentence(sents, *patterns):
    return any(all(re.search(p, s) for p in patterns) for s in sents)


def after_wait(leaf):
    marker = f"wait-leaf.sh {leaf}"
    inside, out = False, []
    for line in _both().splitlines():
        if not inside:
            inside = marker in line
            continue
        if "detach-leaf.sh" in line or "tick-ledger.sh" in line:
            break
        out.append(line)
    return out


def test_skill_md_s_exhausted_budget_branch_launches_the_exhausted_leaf_and_acts_on_exhausted_outcome_sh_s_three_answers_replace_the_step_on_a_split_park_it_on_needs_user_bail_revise_exhausted_on_neither():
    section = revise_section()
    problems = []
    assert section.strip(), f"{REVISE_MD} has no '{REVISE}' section to read"
    outcome_reader = r"\$s/exhausted-outcome\.sh"
    add_ledger_step = r"\$s/add-ledger-step\.sh"
    needs_user = "needs_user|needs-user|needs the user"
    bail_cause = "revise-exhausted"

    if not grep(section, r"\$s/build-develop-prompt\.sh exhausted"):
        problems.append("the revise section never builds an exhausted-phase prompt")
    if not grep(section, outcome_reader):
        problems.append("the revise section never runs exhausted-outcome.sh on the exhausted leaf's report")
    else:
        outcome = window(section, outcome_reader)
        for code, what in (("0", "the split"), ("1", "the needs-user answer"), ("3", "neither answer")):
            if not grep(outcome, rf"exit {code}|exits? {code}"):
                problems.append(f"exhausted-outcome.sh is run without saying exit {code} is {what}")

    if not grep(section, add_ledger_step):
        problems.append("the revise section never runs add-ledger-step.sh on a split at exhaustion")
    else:
        added = window(section, add_ledger_step)
        if not grep(added, "instead-of"):
            problems.append("the exhausted split grows the ledger with a placement other than instead-of")
        if not grep(added, "commit"):
            problems.append("the exhausted split grows the ledger without committing it")
        if not grep(section, "next-unchecked"):
            problems.append("the revise section never returns to next-unchecked.sh after replacing the step")

    if not grep(section, needs_user):
        problems.append("the revise section never names the needs-user answer")
    elif not grep(window(section, needs_user), "park"):
        problems.append("the revise section names the needs-user answer without parking the step on it")

    if not grep(section, bail_cause):
        problems.append("the revise section no longer names the revise-exhausted cause")
    elif not grep(window(section, bail_cause), "bail"):
        problems.append("the revise section names revise-exhausted without bailing on it")

    assert not problems, "\n".join(problems)


def test_skill_md_s_needs_user_branch_mirrors_the_parked_step_to_the_issue_thread_carrying_the_leaf_s_answer_and_the_verifier_s_last_rejection_reason():
    assert plain(_lines(REVISE)).strip(), f"{REVISE_MD} has no '{REVISE}' section to read"
    opening = "exit 1 — the step needs the user"
    closing = "exit 3"
    inside, branch_lines = False, []
    for line in _both().splitlines():
        if not inside and opening in line:
            inside = True
        if inside and closing in line and opening not in line:
            break
        if inside:
            branch_lines.append(line)
    branch = plain(branch_lines)
    assert branch.strip(), f"no '{opening}' branch to read"
    issue_mirror = r"gh issue comment|post a [^.]{0,120}comment"
    problems = []
    if not grep(branch, f"({issue_mirror})"):
        problems.append("the needs-user branch parks the step without posting anything to the issue thread")
    else:
        posted = window(branch, f"({issue_mirror})")
        if not grep(posted, "exhausted-answer"):
            problems.append("the post does not carry .tdd/exhausted-answer.txt")
        if not grep(posted, "reason"):
            problems.append("the post does not carry the verifier's last rejection reason")
    assert not problems, "\n".join(problems)


def test_skill_md_checks_step_cost_sh_after_develop_red_verify_red_each_revise_attempt_develop_green_and_verify_green_before_the_next_leaf_launches_or_the_green_commit_ticks():
    problems = []
    for leaf in ("develop-red", "verdict-red", "revise-<phase>-<k>", "develop-green", "verdict-green"):
        window_lines = after_wait(leaf)
        if not "".join(window_lines).strip():
            problems.append(f"never waits on {leaf}, or launches the next leaf straight after it")
        elif not any(STEP_COST in line for line in window_lines):
            problems.append(f"runs no {STEP_COST} between {leaf} exiting and the next leaf's launch or the green commit")
    assert not problems, "\n".join(problems)


def test_skill_md_says_in_the_prose_of_the_revise_heading_not_only_in_an_inline_comment_that_the_revise_block_runs_step_cost_sh_only_when_the_phase_is_red_or_green_never_for_a_refactor_phase_revise():
    assert any_sentence(
        revise_prose_sentences(),
        re.escape(STEP_COST),
        "refactor",
        r"(^|[^a-z])(never|not|no)([^a-z]|$)|n't",
        "red or green|red or the green|red and green",
    ), "no sentence of the revise section outside its fenced commands names step-cost.sh and refactor together, negates it, and states red or green"


def test_skill_md_checks_step_cost_sh_after_neither_develop_refactor_nor_verify_refactor_and_the_cost_heading_says_why_no_check_follows_the_green_commit():
    problems = []
    text = _both()
    for leaf in ("develop-refactor", "verdict-refactor"):
        if f"wait-leaf.sh {leaf}" not in text:
            problems.append(f"never waits on {leaf}")
        elif any(STEP_COST in line for line in after_wait(leaf)):
            problems.append(f"runs {STEP_COST} after {leaf}, which runs after the step's green commit")
    if not any_sentence(
        cost_sentences(),
        "after the green commit",
        r"(^|[^a-z])(none|no|never|not)([^a-z]|$)",
        "refactor",
        r"(^|[^a-z])(because|since|so|by then)([^a-z]|$)",
    ):
        problems.append("no sentence of the cost check says that no check follows a leaf after the green commit, names the refactor loop, and gives the reason")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_says_the_check_runs_only_once_the_leaf_has_exited_and_its_usage_event_has_been_harvested():
    assert any_sentence(
        cost_sentences(),
        "harvest",
        "usage",
        r"(^|[^a-z])exited([^a-z]|$)",
        r"(^|[^a-z])(once|only|after)([^a-z]|$)",
    ), "no sentence of the cost check says it runs only once the leaf has exited and its usage event has been harvested"


def test_the_cost_heading_says_the_check_fires_at_most_once_per_step_and_is_not_re_armed():
    sents = cost_sentences()
    problems = []
    if not any_sentence(sents, "at most once per step"):
        problems.append("no sentence says the check fires at most once per step")
    if not any_sentence(sents, "re-arm", r"(^|[^a-z])(not|never|no|nothing)([^a-z]|$)"):
        problems.append("no sentence says the check is not re-armed")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_says_step_cost_sh_exit_3_no_leaf_of_the_step_has_reported_yet_is_not_a_crossing():
    exit_3 = [s for s in cost_sentences() if "exit 3" in s]
    problems = []
    if not any("not a crossing" in s for s in exit_3):
        problems.append("no sentence says step-cost.sh exit 3 is not a crossing")
    if not any(re.search(r"no leaf .*(reported|usage)", s) for s in exit_3):
        problems.append("no sentence says exit 3 means no leaf of the step has reported yet")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_builds_the_over_budget_prompt_launches_its_leaf_through_supervise_sh_and_reads_its_answer_with_exhausted_outcome_sh_never_by_eye():
    lines = cost_lines()
    problems = []
    if not any("build-develop-prompt.sh over-budget" in line for line in lines):
        problems.append("never builds an over-budget prompt")
    launch = [line for line in lines if "detach-leaf.sh $S/supervise.sh" in line and "over-budget" in line]
    if not launch:
        problems.append("never launches an over-budget leaf through detach-leaf.sh $S/supervise.sh")
    else:
        match = re.match(r".*supervise\.sh ([^ ]+)", launch[0])
        leaf = match.group(1) if match else launch[0]
        if not any(f"wait-leaf.sh {leaf}" in line for line in lines):
            problems.append(f"launches {leaf} but never waits on it with wait-leaf.sh")
        if not any(f"exhausted-outcome.sh < .tdd/{leaf}.out" in line for line in lines):
            problems.append(f"never reads {leaf}'s answer with exhausted-outcome.sh < .tdd/{leaf}.out")
    if any("run-leaf.sh" in line and "supervise.sh" not in line for line in lines):
        problems.append("launches a leaf with run-leaf.sh outside supervise.sh")
    if not any_sentence(cost_sentences(), "by eye", r"(^|[^a-z])(never|not)([^a-z]|$)"):
        problems.append("no sentence says the over-budget leaf's answer is read with the script, never by eye")
    assert not problems, "\n".join(problems)


def first_line(lines, needle):
    return next((i + 1 for i, line in enumerate(lines) if needle in line), None)


def over_budget_exit(code):
    out, inside = [], False
    for line in cost_lines():
        if re.match(rf"- \*\*exit {code}", line):
            inside = True
            out.append(line)
            continue
        if inside and not line.startswith("  "):
            break
        if inside:
            out.append(line)
    return plain(out)


def supervisor_exit_2():
    paragraphs = re.split(r"\n\n+", "\n".join(cost_lines()).strip("\n"))
    return " ".join(
        plain(p.split("\n")) for p in paragraphs if "supervisor exit 2" in p.replace("*", "").replace("`", "").lower()
    )


def revise_prose_sentences():
    prose, fenced = [], False
    for line in _lines(REVISE):
        if re.match(r"\s*```", line):
            fenced = not fenced
            continue
        if not fenced:
            prose.append(line)
    return sentences(plain(prose))


def test_the_cost_heading_on_the_over_budget_split_restores_the_tree_git_reset_hard_head_git_clean_f_test_path_then_grows_the_plan_in_one_add_ledger_step_sh_instead_of_call_then_commits_it_before_the_run_goes_on():
    lines = cost_lines()
    problems = []
    reset_at = first_line(lines, "git reset --hard HEAD")
    clean_at = first_line(lines, "git clean -f -- <test-path>")
    grow_lines = [i + 1 for i, line in enumerate(lines) if "$S/add-ledger-step.sh" in line and "instead-of" in line]
    grow_at = grow_lines[0] if grow_lines else None
    commit_at = first_line(lines, "git commit")
    if reset_at is None:
        problems.append("the cost check never runs git reset --hard HEAD, so the over-budget split grows the plan on top of the step's uncommitted work")
    if clean_at is None:
        problems.append("the cost check never runs git clean -f -- <test-path>, so the untracked test file Red created survives the over-budget split")
    if len(grow_lines) != 1:
        problems.append(f"the cost check runs add-ledger-step.sh instead-of {len(grow_lines)} times, not once, so the over-budget split does not replace the step in one call")
    else:
        if not (reset_at and clean_at and reset_at < grow_at and clean_at < grow_at):
            problems.append(f"the cost check grows the plan before restoring the tree (reset at line {reset_at}, clean at {clean_at}, add-ledger-step.sh at {grow_at})")
        if not (commit_at and commit_at > grow_at):
            problems.append(f"the cost check never commits the plan after add-ledger-step.sh instead-of (commit at line {commit_at}, add-ledger-step.sh at {grow_at})")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_says_that_add_ledger_step_sh_exit_1_on_the_over_budget_split_is_a_bail_with_cause_step_too_big():
    assert any_sentence(
        cost_sentences(),
        re.escape("add-ledger-step.sh exit 1"),
        re.escape("step-too-big"),
        r"(^|[^a-z])bail",
    ), "no sentence of the cost check names add-ledger-step.sh exit 1 and a step-too-big bail together"


def test_the_cost_heading_parks_the_step_on_the_over_budget_leaf_s_exit_1_carrying_the_leaf_s_answer_and_the_spent_and_budget_figures_and_leaves_the_plan_unchanged():
    bullet = over_budget_exit(1)
    assert bullet.strip(), "the cost check has no **exit 1** bullet"
    problems = []
    if not re.search(r"(^|[^a-z])park", bullet):
        problems.append("the exit 1 bullet never parks the step")
    if not re.search(r"over-budget-answer\.txt|leaf's answer", bullet):
        problems.append("the exit 1 bullet does not carry the leaf's answer (.tdd/over-budget-answer.txt)")
    if not re.search(r"(^|[^a-z])spent", bullet):
        problems.append("the exit 1 bullet does not carry what the step has spent")
    if not re.search(r"step[- ]budget", bullet):
        problems.append("the exit 1 bullet does not carry the step budget")
    if not re.search(r"plan[^.]*(as it is|unchanged)", bullet):
        problems.append("the exit 1 bullet does not say the plan is left as it is")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_records_the_crossing_and_continues_the_step_on_the_over_budget_leaf_s_exit_3_and_says_it_is_not_a_bail_because_nothing_has_failed():
    bullet = over_budget_exit(3)
    assert bullet.strip(), "the cost check has no **exit 3** bullet"
    problems = []
    if not re.search(r"record[a-z]* the crossing", bullet):
        problems.append("the exit 3 bullet does not record the crossing")
    if not re.search(r"(carr(y|ies) on|continues?|goes on|finish(es)?)[^.]*step|step[^.]*(carr(y|ies) on|continues|goes on|finishes)", bullet):
        problems.append("the exit 3 bullet does not say the step continues")
    if not re.search(r"not a bail", bullet):
        problems.append("the exit 3 bullet does not say in so many words that it is not a bail")
    if not re.search(r"nothing has failed|not a failure", bullet):
        problems.append("the exit 3 bullet does not say why it is not a bail: nothing has failed")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_states_once_why_a_crossing_is_not_a_failure_and_that_no_exit_code_changes_meaning():
    problems = []
    not_failure = [
        s for s in cost_sentences()
        if "crossing" in s and "not a failure" in s and re.search(r"(^|[^a-z])(because|since)([^a-z]|$)", s)
    ]
    if not not_failure:
        problems.append("no sentence of the cost check says a crossing is not a failure and gives the reason")
    elif len(not_failure) > 1:
        problems.append(f"the cost check says why a crossing is not a failure in {len(not_failure)} sentences, not once")
    if not any_sentence(
        cost_sentences(), "exit code", r"(^|[^a-z])(no|none|nor|never|not)([^a-z]|$)", "mean"
    ):
        problems.append("no sentence of the cost check says that no exit code changes meaning")
    assert not problems, "\n".join(problems)


def test_the_cost_heading_says_a_supervisor_exit_2_on_the_over_budget_leaf_is_a_killed_stuck_bail_and_the_step_s_budget_stays_crossed_rather_than_re_arming():
    paragraph = supervisor_exit_2()
    assert paragraph.strip(), "the cost check has no paragraph naming a supervisor exit 2"
    problems = []
    if "killed-stuck" not in paragraph:
        problems.append("the supervisor exit 2 paragraph does not name the killed-stuck cause")
    if not re.search(r"(^|[^a-z])bail", paragraph):
        problems.append("the supervisor exit 2 paragraph does not say the step is bailed")
    if not re.search(r"(stays|remains) crossed|(not|never|no|nothing)[^.]*re-arm", paragraph):
        problems.append("the supervisor exit 2 paragraph does not say the step's budget stays crossed rather than re-arming")
    assert not problems, "\n".join(problems)


def test_880_skill_md_s_revise_heading_covers_the_diff_phase_the_revise_leaf_is_built_with_revise_diff_the_re_verify_is_the_blind_diff_verifier_against_the_same_base_sha_as_the_original_verify_diff_verdict_and_its_pass_is_ticked_as_the_diff_checked_pass_bullet_describes():
    section = revise_section()
    assert section.strip(), f"{REVISE_MD} has no '{REVISE}' section to read"
    problems = []
    if "$s/build-develop-prompt.sh revise diff" not in section:
        problems.append("the revise section never builds the revise leaf with build-develop-prompt.sh revise diff")
    if not re.search(r"run-verdict\.sh [^|]* diff [^|]*<base-sha>", section):
        problems.append("the revise section never re-verifies a diff revise with run-verdict.sh ... diff ... <base-sha>")
    sents = revise_prose_sentences()
    if not any_sentence(sents, r"verify-diff|verdict-diff", "same", "base"):
        problems.append("no sentence of the revise section says the diff re-verify runs against the same base sha as the original verify-diff verdict")
    if not any_sentence(sents, "⟦diff-checked⟧", "pass", "tick"):
        problems.append("no sentence of the revise section says a recovered diff PASS is ticked as the ⟦diff-checked⟧ PASS bullet describes")
    assert not problems, "\n".join(problems)


def test_880_skill_md_s_revise_heading_re_verifies_a_diff_revise_with_both_base_shas_the_original_verify_diff_verdict_ran_against_run_verdict_sh_step_step_diff_spec_file_branch_base_sha_step_base_sha_the_step_base_sha_the_one_recorded_before_the_step_s_develop_diff_leaf():
    section = revise_section()
    assert section.strip(), f"{REVISE_MD} has no '{REVISE}' section to read"
    problems = []
    if not re.search(
        r'run-verdict\.sh --step "<step>" (--fast-cmd [^ ]+ )?diff <spec-file> <branch-base-sha> <step-base-sha>', section
    ):
        problems.append('the revise section never re-verifies a diff revise with run-verdict.sh --step "<STEP>" diff <spec-file> <branch-base-sha> <step-base-sha>')
    if not any_sentence(revise_prose_sentences(), "step base sha", "develop-diff", "record|before"):
        problems.append("no sentence of the revise section says the step base sha is the one recorded before the step's develop-diff leaf")
    assert not problems, "\n".join(problems)
