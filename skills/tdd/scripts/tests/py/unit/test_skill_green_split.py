"""Cases for what skills/tdd/SKILL.md's Green section says to do with a SPLIT: report, a repair step's CI verdict and a replaces-case green."""
import pathlib
import re

from skill_sections import plain_lines as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def skill_lines():
    return SKILL.read_text().splitlines() + SKILL.with_name("REVISE.md").read_text().splitlines()


def numbered(pattern):
    return [(n, line) for n, line in enumerate(skill_lines(), 1) if re.search(pattern, line)]


def in_skill_md(call):
    return (call[0] if isinstance(call, tuple) else call) <= len(SKILL.read_text().splitlines())


def outside_cost_check(calls):
    lines = skill_lines()
    start = next(n for n, line in enumerate(lines, 1) if line == "#### The step's cost check")
    end = next(n for n, line in enumerate(lines, 1) if n > start and line.startswith("#### "))
    return [call for call in calls if not start < (call[0] if isinstance(call, tuple) else call) < end]


def split_calls():
    return outside_cost_check(numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)'))


def test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2(tmp_path, monkeypatch, fake_processes):
    from veri import add_ledger_step

    splits = [(n, line) for n, line in numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)') if in_skill_md(n)]
    positions = {re.search(r"\.md (instead-of|before) ", line).group(1): line.strip() for _n, line in splits}
    assert sorted(positions) == ["before", "instead-of"], f"SKILL.md's split add-ledger-step.sh calls: {positions}"
    fake_processes.answers({"git log --format=%H %s": (0, "beef plan: scope #42 into 3 steps (#42)\n", ""),
                            "git show beef:./": (0, "- [ ] planned step\n" * 3, "")})
    monkeypatch.setenv("VERI_STEP_GROWTH_PERCENT", "100")
    kept = {}
    for where, line in positions.items():
        assert "--criterion" not in line, f"SKILL.md's split call passes --criterion: {line}"
        ledger = tmp_path / where / ".tdd" / "issue-42.md"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("# Plan for #42\n\n- [ ] anchor ⟦criterion 7⟧\n")
        assert add_ledger_step.main([str(ledger), where, "anchor", "smaller"]) == 0
        kept[where] = re.search(r"smaller.*⟦criterion (\d+)⟧", ledger.read_text()).group(1)
    assert kept == {"instead-of": "7", "before": "7"}

    uncovered = [(n, line) for n, line in numbered(r'\$S/add-ledger-step\.sh .*after "\$\(\$S/next-pending-refactor\.sh') if in_skill_md(n)]
    assert len(uncovered) == 1, f"SKILL.md's uncovered-spec add-ledger-step.sh calls: {uncovered}"
    at, call = uncovered[0]
    assert "$S/add-ledger-step.sh --criterion <k> .tdd/issue-<n>.md after" in call, f"SKILL.md's uncovered-spec call: {call.strip()}"
    near = plain(skill_lines()[at - 1:at + 30])
    assert re.search(r"add-ledger-step\.sh exit 2.*step-add-refused", near), f"SKILL.md:{at} never bails step-add-refused on exit 2"


def first_line(needle):
    return next((n for n, line in enumerate(skill_lines(), 1) if needle in line), None)


def run_lines(pattern):
    return [n for n, _ in numbered(pattern)]


def test_1558_skill_md_runs_every_replaces_case_survivors_sh_occurrence_before_the_verify_green_launch_it_gates_on_the_green_path_and_the_pin_path_alike():
    green_launch = first_line("detach-leaf.sh $S/supervise.sh verdict-green")
    occurrences = [n for n, line in enumerate(skill_lines(), 1) if 'replaces-case-survivors.sh "' in line]
    assert green_launch and occurrences, f"SKILL.md lacks a survivors run or a launch marker (green launch={green_launch})"
    assert occurrences[0] < green_launch, f"SKILL.md:{occurrences[0]} runs replaces-case-survivors.sh after the verify-green launch at line {green_launch}"


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
        assert "step-add-refused" in near, f"SKILL.md:{call} calls add-ledger-step.sh with no step-add-refused cause within 30 lines"
