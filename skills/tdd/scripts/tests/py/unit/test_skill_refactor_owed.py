"""Cases for how skills/tdd/SKILL.md carries a step's structural leftovers out of its refactor loop, read as text."""
import importlib
import pathlib
import re

from skill_sections import plain_folded as plain, window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

REFACTOR = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"
DRAFT_PR = "### 4. Draft PR"


def section(heading):
    text = importlib.import_module("skill_sections").section(SKILL, heading)
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return plain(body.encode())


def refactor_section():
    text = importlib.import_module("skill_sections").section(SKILL, REFACTOR)
    lines = []
    for line in text.split("\n")[1:]:
        if line.startswith("#"):
            break
        lines.append(line)
    return plain("\n".join(lines).encode())


def narration_of(text):
    narration = text.split(b"6. narrate + branch.", 1)[-1]
    return narration.split(b"mark the same three figures in the log", 1)[0], b"6. narrate + branch." in text


def class_clauses(rest, cls, others):
    clauses = []
    while cls in rest:
        rest = rest.split(cls, 1)[1]
        clause = rest.split(b". ", 1)[0]
        cut = re.search(others, clause)
        clauses.append(clause[:cut.start()] if cut else clause)
    return clauses


def test_skill_md_s_refactor_section_appends_the_step_s_structural_leftovers_to_the_run_s_owed_file_and_commits_that_file_with_the_step_s_refactor_pending_clear():
    text = refactor_section()
    assert text.strip(), "SKILL.md has no Refactor section to read"
    append = window(text, r"refactor-owed\.sh append")
    assert append, "never runs refactor-owed.sh append"
    assert re.search(rb"issue-[^ ]*refactor-owed\.md", append), "append never names the run's .tdd/issue-<n>-refactor-owed.md file"
    assert re.search(rb"develop-refactor\.out", append), "append is not fed the refactor leaf's report"
    assert re.search(rb"<step>", append), "append is not given the step"
    cleared = window(text, r"clear-refactor-pending\.sh")
    assert cleared, "never clears the refactor-pending mark"
    assert re.search(rb"refactor-owed", cleared), "commits the cleared ledger without the owed file"
    assert re.search(rb"commit", cleared), "clears the refactor-pending mark without committing"


def test_756_skill_md_s_refactor_loop_passes_the_step_s_refactor_bounds_to_refactor_owed_sh_append_and_records_an_all_test_file_step_s_structural_candidate_test_only_which_the_structural_pass_never_lists_and_so_launches_no_predicate_or_transform_leaf_for():
    text = refactor_section()
    append = window(text, r"refactor-owed\.sh append")
    assert append, "never runs refactor-owed.sh append"
    assert re.search(rb'refactor-owed\.sh append .*<step>"? +"?(\$touched|<touched-files>)', append), "append lacks the step's refactor bounds ($touched) after the step"
    assert b"test-only" in append, "never says append records an all-test-file step's candidate as test-only"
    draft_pr = section(DRAFT_PR)
    assert b"one structural pass" in draft_pr, "the Draft PR step has no 'one structural pass'"
    pass_text = draft_pr.split(b"one structural pass", 1)[1]
    test_only = window(pass_text, r"test-only")
    assert test_only, "the structural pass never says a test-only candidate is not listed"
    for word in (b"never listed", b"predicate", b"transform leaf"):
        assert word in test_only, f"{word!r} is missing near test-only in the structural pass"


def test_1163_skill_md_s_refactor_step_6_narrate_branch_narration_names_all_four_candidate_classes_structural_cosmetic_test_only_and_out_of_scope():
    text = refactor_section()
    narration, found = narration_of(text)
    assert found, "the Refactor section has no '6. Narrate + branch.' sub-step"
    for cls in (b"structural", b"cosmetic", b"test-only", b"out-of-scope"):
        assert cls in narration, f"the step-6 narration never names the {cls.decode()} class"


def test_1163_skill_md_s_refactor_step_6_narration_says_where_each_class_goes_structural_narrated_and_owed_by_a_follow_up_cosmetic_narrated_and_owed_by_nobody_test_only_and_out_of_scope_recorded_through_refactor_owed_sh_and_not_narrated_as_a_backlog():
    text = refactor_section()
    narration, found = narration_of(text)
    assert found, "the Refactor section has no '6. Narrate + branch.' sub-step"
    goes = {
        b"structural": ([b"follow-up owes"], rb"cosmetic|test-only|out-of-scope"),
        b"cosmetic": ([b"nobody owes"], rb"structural|test-only|out-of-scope"),
        b"test-only": ([b"refactor-owed.sh", b"not narrated as a backlog"], rb"structural|cosmetic"),
        b"out-of-scope": ([b"refactor-owed.sh", b"not narrated as a backlog"], rb"structural|cosmetic"),
    }
    for cls, (phrases, others) in goes.items():
        assert any(all(p in clause for p in phrases) for clause in class_clauses(narration, cls, others)), (
            f"the step-6 narration never says, of the {cls.decode()} class, {phrases!r}"
        )
