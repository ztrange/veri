"""Cases for what skills/tdd/SKILL.md tells a refactor-kind run, read as text."""
import importlib
import pathlib
import re

import pytest
from skill_sections import has, plain_folded as plain, window, windows

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"


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


def test_skill_md_says_a_diff_checked_step_in_a_refactor_kind_run_runs_develop_diff_then_verify_diff_and_never_cover_or_transform_1915():
    near = window(b" ".join(skill_text().split()), r"unless it is ⟦diff-checked⟧", 400)
    assert near, "never says what a diff-checked step runs in a refactor-kind run"
    assert has(near, r"develop-diff then verify-diff"), "does not say it runs develop-diff then verify-diff"
    assert has(near, r"never cover or transform"), "does not say it never runs Cover or Transform"
