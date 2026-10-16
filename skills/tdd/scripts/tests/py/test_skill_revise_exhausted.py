"""Cases for what skills/tdd/SKILL.md tells the conductor to do when a step's revise budget runs out, and where its step-cost check runs."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

REVISE = "## Revising on a REJECT"
COST = "#### The step's cost check"
STEP_COST = "step-cost.sh"


def _lines(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def plain(lines):
    return " ".join(line.replace("*", "").replace("`", "").lower() for line in lines) + " "


def sentences(text):
    return re.split(r"[.!?] ", text)


def window(text, pattern, radius=250):
    for line in text.split("\n"):
        match = re.search(pattern, line)
        if match:
            return line[max(match.start() - radius, 0):match.end() + radius]
    return ""


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
    for line in SKILL.read_text().splitlines():
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
    assert section.strip(), f"{SKILL} has no '{REVISE}' section to read"
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
    assert plain(_lines(REVISE)).strip(), f"{SKILL} has no '{REVISE}' section to read"
    opening = "exit 1 — the step needs the user"
    closing = "exit 3"
    inside, branch_lines = False, []
    for line in SKILL.read_text().splitlines():
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
    prose, fenced = [], False
    for line in _lines(REVISE):
        if re.match(r"\s*```", line):
            fenced = not fenced
            continue
        if not fenced:
            prose.append(line)
    assert any_sentence(
        sentences(plain(prose)),
        re.escape(STEP_COST),
        "refactor",
        r"(^|[^a-z])(never|not|no)([^a-z]|$)|n't",
        "red or green|red or the green|red and green",
    ), "no sentence of the revise section outside its fenced commands names step-cost.sh and refactor together, negates it, and states red or green"


def test_skill_md_checks_step_cost_sh_after_neither_develop_refactor_nor_verify_refactor_and_the_cost_heading_says_why_no_check_follows_the_green_commit():
    problems = []
    text = SKILL.read_text()
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
