"""Cases for the shape of the refactor phase skills/tdd/SKILL.md prescribes, read as text."""
import importlib
import pathlib
import re
import sys

import pytest
from skill_sections import has, plain_bytes as plain, window, windows

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
ROOT = pathlib.Path(__file__).resolve().parents[6]
CONTEXT = ROOT / "CONTEXT.md"
CLAUDE = ROOT / "CLAUDE.md"

REFACTOR = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

ONE_LEAF = r"(one|a single) (refactor |developer |transform )?leaf"
REFUSAL = r"refus|do(es)? not (go on|continue|proceed)|don.t (go on|continue)|not continue|bail"
ADD_LEDGER_STEP = r"\$s/add-ledger-step\.sh"
DENIAL_WORD = "no|never|neither|without|not"
DENIAL = f"({DENIAL_WORD})[^.]{{0,80}}"
AMENDMENT = r"amend|ledger (step|line)|add-ledger-step|grow"


def section(document=None):
    sections = importlib.import_module("skill_sections")
    if document is None:
        text = sections.section(SKILL, REFACTOR)
    else:
        text = sections.section_of(document, REFACTOR)
    lines = []
    for line in text.split("\n")[1:]:
        if line.startswith("#"):
            break
        lines.append(line)
    return plain("\n".join(lines).encode()).replace(b"\n", b" ")


def wins(text, pattern):
    return b" ".join(windows(text, pattern))


def either_order(first, second, between):
    return f"(({first}){between}({second})|({second}){between}({first}))"


def records_of(path):
    records = []
    rec = None

    def flush():
        if rec:
            records.append(plain(re.sub(rb"\s+", b" ", rec)))

    for line in pathlib.Path(path).read_bytes().split(b"\n"):
        if re.match(rb"[0-9]+\. ", line) or re.match(rb"\s*- ", line):
            flush()
            rec = line
        elif not line.strip():
            flush()
            rec = None
        elif not rec:
            rec = line
        else:
            rec += b" " + line
    flush()
    return records


def record(path, *patterns):
    return next((r for r in records_of(path) if all(re.search(p.encode(), r) for p in patterns)), b"")


def adr_pointer(text):
    return any(int(re.search(rb"[0-9]+$", ref).group()) != 10 for ref in re.findall(rb"adr[- ]?[0-9]+", text))


def test_skill_md_s_refactor_section_launches_one_leaf_per_step_and_refuses_verify_refactor_over_a_dirty_tree_or_a_non_refactor_commit_since_the_green_commit_narrating_the_count_against_the_budget():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    assert has(text, ONE_LEAF), "never says one leaf applies the step's transforms"
    relaunch = re.search(rb"repeatedly|(each|every|the next) iteration", text)
    assert relaunch is None, f"still launches a leaf per transform: {relaunch and relaunch.group()!r}"

    dirty = window(text, r"git status --porcelain")
    assert dirty, "never asks git status --porcelain"
    assert has(dirty, REFUSAL), "asks git status --porcelain without saying a non-empty answer stops it"

    subjects = window(text, r"(--(format|pretty)=%s|subject)")
    assert subjects, "never reads the subjects of the commits since the green commit"
    assert has(subjects, r"refactor:"), "reads commit subjects without saying they must be refactor:"
    assert has(subjects, REFUSAL), "never says a non-refactor: commit since the green commit stops it"

    counted = window(text, r"rev-list --count")
    assert counted, "never counts the refactor: commits with git rev-list --count"
    assert has(counted, r"budget|refactor [0-9k]+/"), "counts the refactor: commits without narrating them against the budget"

    assert has(text, r"overrun|over the budget|above the budget|exceed"), "never says a count above the budget is narrated as an overrun"


def test_context_md_s_cycle_entry_and_claude_md_s_budget_invariant_describe_one_refactor_leaf_per_step_and_point_at_the_adr_that_records_it():
    cycle = record(CONTEXT, r"^cycle:")
    invariant = record(CLAUDE, r"veri_stuck_retries", r"revise_budget", r"veri_refactor_budget")

    assert cycle, "CONTEXT.md has no Cycle glossary entry to read"
    assert has(cycle, ONE_LEAF), "the Cycle entry never says the refactor step is one leaf"
    stale_cycle = re.search(rb"per leaf|until none remain|per leaf invocation", cycle)
    assert stale_cycle is None, f"the Cycle entry still says {stale_cycle and stale_cycle.group()!r}"

    assert invariant, "CLAUDE.md has no invariant naming all three budgets to read"
    assert has(invariant, ONE_LEAF), "the budget invariant never says one leaf spends the step's refactor budget"
    stale_invariant = re.search(rb"asked for one always finds one|one transform per leaf|a transform per leaf", invariant)
    assert stale_invariant is None, f"the budget invariant still explains the budget by {stale_invariant and stale_invariant.group()!r}"

    assert adr_pointer(cycle + b" " + invariant), "neither entry names an ADR other than the superseded 0010"


def test_skill_md_s_refactor_section_passes_the_flags_behaviours_to_one_add_ledger_step_sh_call_after_the_step_and_commits_the_grown_ledger_with_the_refactor_pending_clear():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    calls = len(re.findall(ADD_LEDGER_STEP.encode(), text))
    assert calls != 0, "never runs add-ledger-step.sh"
    assert calls == 1, f"runs add-ledger-step.sh {calls} times"
    added = window(text, ADD_LEDGER_STEP)
    assert has(added, r"'<[^>]*behaviou?r>'"), "runs add-ledger-step.sh without saying the texts are the flags' behaviours"
    assert has(added, r"after ['\"]?(<step>|\$\(\$s/next-pending-refactor\.sh)"), "runs add-ledger-step.sh without anchoring the insertion after the step"

    cleared = window(text, r"clear-refactor-pending\.sh")
    assert cleared, "never clears the refactor-pending mark"
    assert has(cleared, r"add-ledger-step"), "commits the cleared ledger without the steps add-ledger-step.sh inserted into it"


def test_skill_md_s_refactor_section_narrates_add_ledger_step_sh_exit_1_as_owed_steps_and_does_not_bail_on_it():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    owed_claim = either_order("exit 1", "owed", ".{0,120}")
    assert has(text, owed_claim), "never says what add-ledger-step.sh exit 1 means"
    clause = window(text, owed_claim, 150)
    bailed = re.search(rb"bail|abort", clause)
    assert bailed is None, f"says {bailed and bailed.group()!r} where it narrates add-ledger-step.sh exit 1"


def test_skill_md_s_refactor_section_passes_the_passing_verify_refactor_verdict_s_uncovered_spec_flags_to_the_same_add_ledger_step_sh_call_as_the_leaf_s():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    added = window(text, ADD_LEDGER_STEP)
    assert added, "never runs add-ledger-step.sh"
    assert has(added, r"verif|verdict"), "runs add-ledger-step.sh over the leaf's values alone"


def test_skill_md_s_refactor_section_answers_an_overfit_flag_with_one_triangulating_red_green_pair_inside_the_step_adding_no_ledger_step_and_no_second_step_done_and_resumes_that_step_s_refactor_loop_with_the_budget_it_had_left():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    flagged = wins(text, r"overfit")
    assert flagged, "never names the overfit class"
    assert has(flagged, either_order(r"triangulat[a-z]*", r"verify-(red|green)", r"[^.]{0,200}")), (
        "never says an overfit flag is answered by a triangulating red and green pair"
    )
    assert has(flagged, f"{DENIAL}({AMENDMENT})"), "answers an overfit flag without saying the plan does not grow for it"
    assert has(flagged, f"{DENIAL}(second )?step.done"), "answers an overfit flag without saying the step is not mirrored done a second time"
    assert has(flagged, either_order(r"(resum|return|back)", r"budget", r"[^.]{0,160}")), (
        "never says the step resumes its own refactor loop with the budget it had left"
    )


GUARD_CASES = (
    "test_beyond_spec_narration_guard_",
    "test_flag_class_amendment_guard_",
    "test_one_call_per_criterion_case_passes_over_",
)


def cases_failing_over(document, tmp_path, monkeypatch):
    planted = tmp_path / "SKILL.md"
    planted.write_text(document)
    module = sys.modules[__name__]
    failing = []
    # A context, not monkeypatch.undo(): undo() would also revert the conftest autouse guards.
    with monkeypatch.context() as patch:
        patch.setattr(module, "SKILL", planted)
        for name, case in sorted(vars(module).items()):
            if not name.startswith("test_") or name.startswith(GUARD_CASES):
                continue
            try:
                case()
            except (AssertionError, pytest.fail.Exception):
                failing.append(name)
    return failing


def assert_one_case_fails_naming(document, planted, cls, tmp_path, monkeypatch):
    unplanted_failing = cases_failing_over(document, tmp_path, monkeypatch)
    assert unplanted_failing == [], f"the suite is not green over the document as committed: {unplanted_failing}"
    failing = cases_failing_over(planted, tmp_path, monkeypatch)
    assert len(failing) == 1, f"want exactly 1 case to fail over the planted document, the others untouched by the plant; {len(failing)} failed: {failing}"
    assert cls.replace("-", "_") in failing[0], f"the one case that failed does not name the {cls} class: {failing[0]}"


def assert_fails_naming(case, planted, cls, planted_description):
    try:
        case(planted)
    except AssertionError as failure:
        assert cls in str(failure), f"failed without naming the {cls} class: {failure}"
    else:
        raise AssertionError(f"the case passed over {planted_description}")


CLASS = "beyond-spec"
DENIAL_CLAUSE = "is not planned and not built in this run"
GRANT_CLAUSE = "is planned and built in this run"


def beyond_spec_narration(document):
    text = section(document)
    problems = []
    if not text.strip():
        problems.append(f"SKILL.md has no Refactor section to read — where a {CLASS} flag goes could not be established")
    else:
        beyond = wins(text, CLASS)
        if not beyond:
            problems.append(f"the Refactor section never names the {CLASS} class")
        else:
            if not has(beyond, either_order(r"follow.?up", r"(🛠️ )?refactor comment|narrat|post", "[^.]{0,200}")):
                problems.append(f"never says a {CLASS} flag is narrated as a follow-up in the Refactor comment")
            if not has(beyond, r"pr body|body of the (draft )?pr|pull request body"):
                problems.append(f"never carries a {CLASS} flag into the PR body")
            if not has(beyond, f"({DENIAL_WORD}) (planned|plan|built|build)"):
                problems.append(f"narrates a {CLASS} flag without saying it is neither planned nor built in this run")
    assert not problems, "; ".join(problems)


def test_skill_md_s_refactor_section_narrates_a_beyond_spec_flag_as_a_follow_up_in_the_refactor_comment_and_in_the_pr_body_planning_and_building_neither():
    beyond_spec_narration(SKILL.read_text())


def test_beyond_spec_narration_guard_fails_naming_the_class_over_a_skill_md_that_plans_and_builds_a_beyond_spec_flag_and_passes_as_committed(tmp_path, monkeypatch):
    committed = SKILL.read_text()
    assert GRANT_CLAUSE not in committed, "SKILL.md already grants the clause the plant is about"
    assert DENIAL_CLAUSE in committed, "SKILL.md no longer carries the clause the plant replaces"
    beyond_spec_narration(committed)

    planted = committed.replace(DENIAL_CLAUSE, GRANT_CLAUSE)
    assert planted != committed
    assert_fails_naming(beyond_spec_narration, planted, CLASS, f"a SKILL.md whose Refactor section says a {CLASS} flag {GRANT_CLAUSE}")
    assert_one_case_fails_naming(committed, planted, CLASS, tmp_path, monkeypatch)


UNCOVERED = "uncovered-spec"
OTHER_CLASS = "off-spec"
SUBSTEP_OPENING = b"flag is the one class that grows the plan"
SUBSTEP_CLOSING = b"a beyond-spec flag is narrated"


def uncovered_spec_amendment(document):
    text = section(document)
    problems = []
    if not text.strip():
        problems.append("SKILL.md has no Refactor section to read — which flag class grows the plan could not be established")
    else:
        uncovered = wins(text, UNCOVERED)
        if not uncovered:
            problems.append(f"the Refactor section never names the {UNCOVERED} class the leaf's FLAGS: line carries, so no flag is routed to a plan amendment by its class")
        else:
            if not has(uncovered, AMENDMENT):
                problems.append(f"the Refactor section names the {UNCOVERED} class without saying it is what amends the plan")
            if not has(uncovered, r"(only|alone|no other|the one (flag|class))"):
                problems.append(f"the Refactor section amends the plan from an {UNCOVERED} flag without saying that no other flag class does")
        grown = window(text, ADD_LEDGER_STEP)
        if grown and UNCOVERED.encode() not in grown:
            problems.append(f"the Refactor section runs add-ledger-step.sh without saying its texts are the {UNCOVERED} flags' behaviours")
    assert not problems, "; ".join(problems)


def one_call_per_criterion(document):
    text = section(document)
    problems = []
    if not text.strip():
        problems.append("SKILL.md has no Refactor section to read — which add-ledger-step.sh call an uncovered-spec flag's behaviour goes into could not be established")
    else:
        substep = b""
        if SUBSTEP_OPENING in text:
            substep = SUBSTEP_OPENING + text.split(SUBSTEP_OPENING, 1)[1]
            substep = substep.split(SUBSTEP_CLOSING, 1)[0]
        if not substep:
            problems.append("the Refactor section has no sub-step 4 opening '<class> flag is the one class that grows the plan'")
        else:
            shared = re.search(rb"the same[^.]{0,80}add-ledger-step\.sh[^.]{0,80}call", substep)
            if shared:
                problems.append(f"sub-step 4 still sends every uncovered-spec behaviour into one shared call — it says {shared.group()!r}")
            if not has(substep, r"one call per criterion|call for the criterion (it|the behaviour) serves"):
                problems.append("sub-step 4 never says a behaviour goes into the add-ledger-step.sh call for the criterion it serves, one call per criterion")
    assert not problems, "; ".join(problems)


def test_skill_md_s_refactor_section_amends_the_plan_from_an_uncovered_spec_flag_and_from_no_other_flag_class():
    uncovered_spec_amendment(SKILL.read_text())


def test_skill_md_s_refactor_sub_step_4_sends_each_uncovered_spec_behaviour_into_the_add_ledger_step_sh_call_for_the_criterion_it_serves_one_call_per_criterion_not_into_one_shared_call():
    one_call_per_criterion(SKILL.read_text())


def planted_with_other_class():
    committed = SKILL.read_text()
    assert OTHER_CLASS not in committed, f"SKILL.md already names {OTHER_CLASS}, so the rename leaves the two classes indistinguishable"
    assert UNCOVERED in committed
    return committed.replace(UNCOVERED, OTHER_CLASS)


def test_flag_class_amendment_guard_fails_naming_the_class_over_a_skill_md_whose_refactor_section_amends_the_plan_from_another_class_and_passes_as_committed(tmp_path, monkeypatch):
    uncovered_spec_amendment(SKILL.read_text())
    assert_fails_naming(uncovered_spec_amendment, planted_with_other_class(), UNCOVERED, f"a SKILL.md whose plan-growing flag class is {OTHER_CLASS}")
    assert_one_case_fails_naming(SKILL.read_text(), planted_with_other_class(), UNCOVERED, tmp_path, monkeypatch)


def test_one_call_per_criterion_case_passes_over_a_skill_md_whose_plan_growing_flag_class_is_named_off_spec_since_it_asks_how_many_calls_not_which_class():
    one_call_per_criterion(planted_with_other_class())


def whole_document():
    return plain(SKILL.read_bytes()).replace(b"\n", b" ")


def test_skill_md_s_refactor_section_runs_a_step_s_triangulation_at_most_once_narrating_a_flag_raised_inside_that_triangulation_s_own_refactor_loop_about_the_same_code_rather_than_triangulating_it_again():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read — whether a step's triangulation runs more than once could not be established"
    triangulation = wins(text, "triangulat")
    assert triangulation, "the Refactor section never mentions triangulation at all, so there is no ceiling on it to read"
    ceiling = rf"at most once|only once|once (per|a) step|({DENIAL_WORD}) ((a )?(second|further|another) (triangulat[a-z]*|time)|triangulat[a-z]* (it |them )?(again|a second time))"
    assert has(triangulation, ceiling), "the Refactor section puts no ceiling on a step's triangulation"
    narrated = either_order("narrat", "(again|a second (time|triangulation)|same code)", "[^.]{0,200}")
    assert has(triangulation, narrated), "never says a flag raised inside a triangulation's own refactor loop about the same code is narrated"


def test_skill_md_grows_the_plan_from_the_refactor_leaf_s_flags_classes_alone_reading_no_new_step_or_candidates_line_of_the_leaf_s_into_it():
    text = section()
    whole = whole_document()
    assert text.strip(), "SKILL.md has no Refactor section to read — what the plan is grown from could not be established"
    grown = window(text, ADD_LEDGER_STEP)
    assert grown, "the Refactor section never runs add-ledger-step.sh, so no flag is ever planned"
    assert has(grown, r"'<[^>]*leaf[^>]* [a-z]+-[a-z]+ behaviou?r>'"), "runs add-ledger-step.sh without saying its texts come from the leaf's FLAGS: lines"
    leaf_new_step = re.search(either_order("leaf's", "new_step", "[^.]{0,30}").encode(), whole)
    assert leaf_new_step is None, f"still reads a NEW_STEP: line from the refactor leaf: {leaf_new_step and leaf_new_step.group()!r}"
    candidate_growth = re.search(either_order("candidates:", f"({AMENDMENT})", "[^.]{0,80}").encode(), whole)
    assert candidate_growth is None, f"grows the plan from the leaf's CANDIDATES: lines: {candidate_growth and candidate_growth.group()!r}"


def test_skill_md_s_refactor_section_does_not_bail_when_no_ledger_step_carries_criterion_k_yet_since_add_ledger_step_sh_criterion_accepts_it_1292():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read — what the conductor does with a criterion no ledger step carries could not be established"
    uncarried_bail = re.search(either_order("bail", "carr[a-z]* criterion", "[^.]{0,200}").encode(), text)
    assert uncarried_bail is None, f"still bails on a criterion no ledger step carries: {uncarried_bail and uncarried_bail.group()!r}"


def test_skill_md_s_refactor_section_says_each_per_criterion_add_ledger_step_sh_call_emits_its_own_step_added_event_anchored_on_the_step_and_carrying_added_that_call_s_count_1292():
    text = section()
    assert text.strip(), "SKILL.md has no Refactor section to read — which step-added event each per-criterion add-ledger-step.sh call emits could not be established"
    per_call = r"(each|every)( per-criterion)? (add-ledger-step\.sh )?call[^.]{0,120}(its own|a|one) step-added|one step-added[^.]{0,80}(per|for each|for every) (add-ledger-step\.sh )?(call|criterion)"
    assert re.search(per_call.encode(), text), "never says each per-criterion add-ledger-step.sh call emits its own step-added event"
    emitted = window(text, per_call)
    assert has(emitted, r"anchor(ed)?( on|=)[^.]{0,40}step"), f"emits its own step-added event without saying it is anchored on the step: {emitted!r}"
    assert has(emitted, r"added=<[^>]*call[^>]*>"), f"emits its own step-added event without saying it carries added=<that call's count>: {emitted!r}"
