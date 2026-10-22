"""Cases for what skills/tdd/SKILL.md tells the conductor to do when a step's revise budget runs out, and where its step-cost check runs."""
import importlib
import pathlib
import re

from skill_sections import plain_lines as plain, window_text as window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.with_name("REVISE.md")

REVISE = "## Revising on a REJECT"
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
    for leaf in ("revise-<phase>-<k>",):
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
    assert not problems, "\n".join(problems)


def revise_prose_sentences():
    prose, fenced = [], False
    for line in _lines(REVISE):
        if re.match(r"\s*```", line):
            fenced = not fenced
            continue
        if not fenced:
            prose.append(line)
    return sentences(plain(prose))


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
