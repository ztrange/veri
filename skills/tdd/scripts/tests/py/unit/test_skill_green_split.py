"""Cases for what skills/tdd/SKILL.md's Green section says to do with a SPLIT: report, a repair step's CI verdict and a replaces-case green."""
import pathlib
import re

from skill_sections import plain_lines as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def grep(text, pattern, flags=0):
    return any(re.search(pattern, line, flags) for line in text.split("\n"))


def says(text, pattern, message, flags=0):
    assert grep(text, pattern, flags), message


def skill_lines():
    return SKILL.read_text().splitlines() + SKILL.with_name("REVISE.md").read_text().splitlines()


def numbered(pattern):
    return [(n, line) for n, line in enumerate(skill_lines(), 1) if re.search(pattern, line)]


def in_skill_md(call):
    return (call[0] if isinstance(call, tuple) else call) <= len(SKILL.read_text().splitlines())


def neighbourhood(at):
    return plain(line for n, line in enumerate(skill_lines(), 1) if at - 20 <= n <= at + 20)


def outside_cost_check(calls):
    lines = skill_lines()
    start = next(n for n, line in enumerate(lines, 1) if line == "#### The step's cost check")
    end = next(n for n, line in enumerate(lines, 1) if n > start and line.startswith("#### "))
    return [call for call in calls if not start < (call[0] if isinstance(call, tuple) else call) < end]


def split_calls():
    return outside_cost_check(numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)'))


def _bullet(lines, prefix):
    out, inside = [], False
    for line in lines:
        if inside and (line.startswith("- ") or line == ""):
            break
        if line.startswith(prefix):
            inside = True
        if inside:
            out.append(line)
    return plain(out)


def _bullet_body(lines, prefix):
    out, inside = [], False
    for line in lines:
        if inside and line.startswith("- `"):
            break
        if inside:
            out.append(line)
        if line.startswith(prefix):
            inside = True
    return plain(out)


def catalogue_lines():
    return SKILL.with_name("SCRIPTS.md").read_text().splitlines()


def add_ledger_step_entry():
    return _bullet(catalogue_lines(), "- `$S/add-ledger-step.sh")


def test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2():
    splits = [(n, line) for n, line in split_calls() if "instead-of" in line and in_skill_md(n)]
    for n, line in splits:
        assert "--criterion" not in line.strip(), f"SKILL.md's split call passes --criterion: {line.strip()}"
        assert "anchor's criterion" in neighbourhood(n), \
            f"SKILL.md never says beside this split call that the split keeps its anchor's criterion: {line.strip()}"
    assert "--criterion" in add_ledger_step_entry(), "SKILL.md's add-ledger-step.sh entry never documents --criterion"


def test_1292_skill_md_s_add_ledger_step_entry_under_the_scripts_says_criterion_k_tags_the_added_steps_with_criterion_k_for_any_whole_number_k_1_carried_or_not_and_lists_a_k_that_is_not_a_whole_number_1_among_its_exit_2_cases():
    entry = add_ledger_step_entry()
    assert entry.strip(), "SKILL.md has no add-ledger-step.sh entry under The scripts"
    says(entry, r"whole number[^.]{0,20}(≥|>=|at least) ?1", "SKILL.md's entry never says --criterion <k> takes any whole number k ≥ 1")
    says(entry, r"whether or not[^.]{0,80}carr|carried or not|(no|not yet)[^.]{0,30}step[^.]{0,20}carr",
         "SKILL.md's entry never says --criterion <k> tags the steps whether or not a step carries k")
    exit2 = "\n".join(re.findall(r"exit 2[^.]*", entry))
    says(exit2, r"not a whole number", f"SKILL.md's entry never lists a k that is not a whole number ≥ 1 among its exit 2 cases: {exit2!r}")


def first_line(needle):
    return next((n for n, line in enumerate(skill_lines(), 1) if needle in line), None)


def run_lines(pattern):
    return [n for n, _ in numbered(pattern)]


def test_1558_skill_md_runs_every_replaces_case_survivors_sh_occurrence_before_the_verify_green_launch_it_gates_on_the_green_path_and_the_pin_path_alike():
    green_launch = first_line("detach-leaf.sh $S/supervise.sh verdict-green")
    occurrences = [n for n, line in enumerate(skill_lines(), 1) if 'replaces-case-survivors.sh "' in line]
    assert green_launch and occurrences, f"SKILL.md lacks a survivors run or a launch marker (green launch={green_launch})"
    assert occurrences[0] < green_launch, f"SKILL.md:{occurrences[0]} runs replaces-case-survivors.sh after the verify-green launch at line {green_launch}"


def test_1406_skill_md_documents_build_develop_prompt_sh_green_s_8th_argument_the_cases_still_owed_for_deletion_at_the_green_build_command_and_in_the_script_reference_entry():
    reference = _bullet_body(catalogue_lines(), "- `$S/build-develop-prompt.sh <red")
    assert re.search(r"<fast-cmd>.*owed", reference) or re.search(r"green <spec-file>.*owed.*refactor <spec-file>", reference), \
        "SKILL.md's build-develop-prompt.sh reference entry never lists an owed-cases argument in green's synopsis"


def test_1546_skill_md_never_runs_replaces_case_survivors_sh_at_any_place_it_names_it_as_a_run_before_the_last_place_it_runs_unreplaced_cases_sh():
    survivors = run_lines(r"\$S/replaces-case-survivors\.sh|[Rr]uns? [^.]*replaces-case-survivors\.sh")
    assert survivors, "SKILL.md lacks a replaces-case-survivors.sh run"


def test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused():
    calls = [call for call in outside_cost_check(run_lines(r"\$S/add-ledger-step\.sh [^ ]*\.tdd/issue-<n>\.md|\$S/add-ledger-step\.sh --criterion <k> \.tdd/issue-<n>\.md"))
             if in_skill_md(call) and "<SPLIT: value>" not in skill_lines()[call - 1]
             and not re.search("⟦(suite|ci)-repair⟧", skill_lines()[call - 1])]
    assert calls, "SKILL.md has no add-ledger-step.sh call site"
    lines = skill_lines()
    for call in calls:
        near = plain(lines[call - 1:call + 30])
        says(near, r"exits? 2[^.]{0,120}step-add-refused|step-add-refused[^.]{0,120}exits? 2",
             f"SKILL.md:{call} calls add-ledger-step.sh and never says its exit 2 bails with cause step-add-refused")
