"""Cases for what skills/tdd/SKILL.md's Green section says to do with a SPLIT: report, a repair step's CI verdict and a replaces-case green."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"
BAILING = "## Bailing"
ADD_LEDGER_STEP = r"\$s/add-ledger-step\.sh"


def _lines(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def plain(lines):
    return " ".join(line.replace("*", "").replace("`", "").lower() for line in lines) + " "


def green():
    return plain(_lines(GREEN))


def bailing_causes():
    lines = _lines(BAILING)
    start = next(i for i, line in enumerate(lines) if "killed-stuck" in line.lower())
    return plain(lines[start:])


def grep(text, pattern, flags=0):
    return any(re.search(pattern, line, flags) for line in text.split("\n"))


def says(text, pattern, message, flags=0):
    assert grep(text, pattern, flags), message


def window(text, pattern, radius=250):
    for line in text.split("\n"):
        match = re.search(pattern, line)
        if match:
            return line[max(match.start() - radius, 0):match.end() + radius]
    return ""


def skill_lines():
    return SKILL.read_text().splitlines()


def numbered(pattern):
    return [(n, line) for n, line in enumerate(skill_lines(), 1) if re.search(pattern, line)]


def neighbourhood(at):
    return plain(line for n, line in enumerate(skill_lines(), 1) if at - 20 <= n <= at + 20)


def split_calls():
    return numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)')


def uncovered_spec_calls():
    return numbered(r'\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*after "\$\(\$S/next-pending-refactor\.sh')


def add_ledger_step_entry():
    out, inside = [], False
    for line in skill_lines():
        if inside and (line.startswith("- ") or line == ""):
            break
        if line.startswith("- `$S/add-ledger-step.sh"):
            inside = True
        if inside:
            out.append(line)
    return plain(out)


def repair_call_neighbourhood(tag):
    at = max((n for n, line in enumerate(skill_lines(), 1) if "$S/add-ledger-step.sh" in line and tag in line), default=0)
    if not at:
        return ""
    return plain(line for n, line in enumerate(skill_lines(), 1) if at - 20 <= n <= at + 20)


def step_too_big_cause():
    lines = _lines(BAILING)
    out, inside = [], False
    for line in lines:
        if inside and (line.startswith("- ") or line == ""):
            break
        if line.startswith("- `step-too-big`"):
            inside = True
        if inside:
            out.append(line)
    return plain(out)


def one_line(lines):
    return re.sub(r" +", " ", " ".join(line.replace("*", "").replace("`", "") for line in lines) + " ")


def green_paragraph():
    out, inside = [], False
    for line in skill_lines():
        if "On a `⟦replaces-case⟧` step, a PASS is accepted" in line:
            inside = True
        if inside and re.match(r"3\. ", line):
            break
        if inside:
            out.append(line)
    return one_line(out)


def test_skill_md_s_green_section_on_split_restores_the_tree_to_head_adds_the_split_steps_before_step_in_one_add_ledger_step_call_commits_the_ledger_emits_step_split_and_returns_to_next_unchecked():
    section = green()
    says(section, r"split", "SKILL.md's Green section never branches on the leaf's SPLIT: report")
    says(section, r"git (restore|checkout|reset)[^.]{0,60}head|restore[^.]{0,60}(the tree|to) head",
         "SKILL.md's Green section never restores the tree to HEAD on a SPLIT:")
    calls = len(re.findall(ADD_LEDGER_STEP, section))
    assert calls != 0, "SKILL.md's Green section never runs add-ledger-step.sh on a SPLIT:"
    assert calls <= 1, f"SKILL.md's Green section runs add-ledger-step.sh {calls} times"
    added = window(section, ADD_LEDGER_STEP)
    says(added, r"before ['\"]?(<step>|\$\(\$s/next-unchecked\.sh)",
         "SKILL.md's Green section runs add-ledger-step.sh without anchoring the insertion before the step being split")
    says(added, r"commit", "SKILL.md's Green section grows the ledger on a SPLIT: without committing it")
    says(section, r"step-split", "SKILL.md's Green section never emits step-split")
    says(section, r"next-unchecked", "SKILL.md's Green section never loops back to next-unchecked.sh after a split")


def test_skill_md_s_green_section_bails_with_cause_step_too_big_when_add_ledger_step_exits_1_on_a_split_and_its_bailing_section_lists_that_cause_as_a_process_failure():
    section = green()
    says(section, r"step-too-big", "SKILL.md's Green section never names the step-too-big cause")
    over = window(section, r"step-too-big")
    says(over, r"exits? 1", "SKILL.md's Green section names step-too-big without saying it is add-ledger-step.sh's exit 1")
    says(over, r"bail", "SKILL.md's Green section names step-too-big without bailing on it")
    says(bailing_causes(), r"step-too-big[^.]{0,220}process",
         "SKILL.md's Bailing causes list never classifies step-too-big as a process failure")


def test_skill_md_s_bailing_entry_for_step_too_big_names_all_three_splits_that_lead_to_it_a_green_leaf_s_split_the_revise_exhausted_split_and_the_over_budget_split():
    bullet = step_too_big_cause()
    assert bullet.strip(), "SKILL.md's Bailing causes list has no step-too-big bullet"
    says(bullet, r"green[^.]*split:|split:[^.]*green", "SKILL.md's step-too-big entry does not name a Green leaf's SPLIT:")
    says(bullet, r"exhausted", "SKILL.md's step-too-big entry does not name the revise-exhausted split")
    says(bullet, r"over-budget", "SKILL.md's step-too-big entry does not name the over-budget split")


def test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2():
    splits = split_calls()
    assert sum("instead-of" in line for _, line in splits) >= 2, \
        "SKILL.md has fewer than two instead-of add-ledger-step.sh calls"
    assert any('before "$($S/next-unchecked.sh' in line for _, line in splits), \
        "SKILL.md has no add-ledger-step.sh call anchored before next-unchecked.sh"
    for n, line in splits:
        assert "--criterion" not in line.strip(), f"SKILL.md's split call passes --criterion: {line.strip()}"
        assert "anchor's criterion" in neighbourhood(n), \
            f"SKILL.md never says beside this split call that the split keeps its anchor's criterion: {line.strip()}"
    uncovered = uncovered_spec_calls()
    assert uncovered, "SKILL.md has no add-ledger-step.sh call anchored after next-pending-refactor.sh"
    assert any("--criterion <k>" in line for _, line in uncovered), \
        "SKILL.md's uncovered-spec add-ledger-step.sh call passes no --criterion <k>"
    around = neighbourhood(uncovered[0][0])
    says(around, r"numbered acceptance criteri", "SKILL.md never says k is read from the issue's numbered acceptance criteria")
    says(around, r"one (add-ledger-step\.sh )?call per criterion", "SKILL.md never says one call per criterion")
    says(around, r"exits? 2[^.]{0,200}bail", "SKILL.md never says add-ledger-step.sh exit 2 bails")
    assert "--criterion" in add_ledger_step_entry(), "SKILL.md's add-ledger-step.sh entry never documents --criterion"


def test_1281_the_suite_repair_and_ci_repair_add_ledger_step_calls_say_they_pass_no_criterion_because_the_repair_step_serves_its_anchor_s_criterion():
    for tag in ("⟦suite-repair⟧", "⟦ci-repair⟧"):
        around = repair_call_neighbourhood(tag)
        assert around.strip(), f"SKILL.md has no add-ledger-step.sh call adding a {tag} step"
        assert "--criterion" in around, f"SKILL.md never says beside its {tag} call that it passes no --criterion"
        assert "anchor's criterion" in around, f"SKILL.md never says beside its {tag} call that the step serves its anchor's criterion"


def test_1292_skill_md_s_add_ledger_step_entry_under_the_scripts_says_criterion_k_tags_the_added_steps_with_criterion_k_for_any_whole_number_k_1_carried_or_not_and_lists_a_k_that_is_not_a_whole_number_1_among_its_exit_2_cases():
    entry = add_ledger_step_entry()
    assert entry.strip(), "SKILL.md has no add-ledger-step.sh entry under The scripts"
    says(entry, r"whole number[^.]{0,20}(≥|>=|at least) ?1", "SKILL.md's entry never says --criterion <k> takes any whole number k ≥ 1")
    says(entry, r"whether or not[^.]{0,80}carr|carried or not|(no|not yet)[^.]{0,30}step[^.]{0,20}carr",
         "SKILL.md's entry never says --criterion <k> tags the steps whether or not a step carries k")
    exit2 = "\n".join(re.findall(r"exit 2[^.]*", entry))
    says(exit2, r"not a whole number", f"SKILL.md's entry never lists a k that is not a whole number ≥ 1 among its exit 2 cases: {exit2!r}")


def test_1431_skill_md_s_green_section_judges_a_ci_repair_step_s_green_against_a_fresh_ci_run_on_the_pushed_fix_wait_ci_on_the_pushed_sha_not_only_a_local_make_test_and_a_red_ci_there_bails_ci_red():
    section = green()
    assert "⟦ci-repair⟧" in section, "SKILL.md's Green section never names a ⟦ci-repair⟧ step"
    rule = section.split("⟦ci-repair⟧", 1)[1][:700]
    assert "wait-ci.sh" in rule, "SKILL.md's ⟦ci-repair⟧ green rule never runs wait-ci.sh on the fix"
    says(rule, r"push[^.]{0,60}sha|sha[^.]{0,60}push", "SKILL.md's ⟦ci-repair⟧ green rule never waits on the pushed sha")
    says(rule, r"not only[^.]{0,60}make test", "SKILL.md's ⟦ci-repair⟧ green rule never says a local make test alone does not judge it")
    assert "ci-red" in rule, "SKILL.md's ⟦ci-repair⟧ green rule never bails ci-red on a red CI there"


def _sentences(text):
    return text.replace(". ", ".\n")


def test_1473_skill_md_s_green_section_names_the_ci_repair_verify_green_variant_and_says_its_evidence_is_ci_the_failing_job_s_log_before_the_fix_and_a_green_ci_run_on_the_pushed_fix_not_a_local_revert_goes_red_check():
    variant = "\n".join(line for line in _sentences(green()).split("\n")
                        if "⟦ci-repair⟧" in line and "verify-green" in line)
    assert variant, "SKILL.md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant"
    says(variant, r"variant", "SKILL.md's ⟦ci-repair⟧ verify-green sentence never calls it a variant")
    says(variant, r"failing job's log|log of the failing job", "SKILL.md's sentence never names the failing job's log as evidence")
    says(variant, r"green ci run", "SKILL.md's sentence never names a green CI run on the pushed fix as evidence")
    says(variant, r"not[^.]{0,80}(local )?revert", "SKILL.md's sentence never says the local revert-goes-red check does not judge it")


def test_1473_skill_md_s_green_section_says_the_ci_repair_verify_green_variant_judges_only_evidence_that_exists_before_the_push_and_never_requires_a_ci_run_on_the_fix_whose_ci_verdict_is_the_post_push_wait_ci_wait_where_red_bails_ci_red():
    lines = _sentences(green()).split("\n")
    start = next((i for i, line in enumerate(lines) if "⟦ci-repair⟧" in line and "verify-green" in line), None)
    assert start is not None, "SKILL.md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant"
    tail = "\n".join(lines[start:])
    says(tail, r"judges only[^.]{0,120}(before|prior to) the push", "SKILL.md's variant never says it judges only evidence that exists before the push")
    says(tail, r"never requires?[^.]{0,60}ci run", "SKILL.md's variant never says it does not require a CI run on the fix")
    says(tail, r"wait-ci\.sh", "SKILL.md's variant never leaves the CI verdict on the fix to the post-push wait-ci.sh wait")
    assert "ci-red" in tail, "SKILL.md's variant never says a red CI on the pushed fix bails ci-red"
    assert not grep(tail, r"(requires?|evidence is)[^.]{0,120}green ci run[^.]{0,40}(on|for) the (pushed )?fix"), \
        "SKILL.md's variant requires a green CI run on the pushed fix, which does not exist until after its PASS"


def test_skill_md_s_replaces_case_green_paragraph_runs_replaces_case_survivors_before_verify_green_and_on_survivors_relaunches_the_green_leaf_naming_them_records_an_event_and_launches_no_verifier():
    section = green_paragraph()
    assert section.strip(), "SKILL.md has no replaces-case paragraph in the Green step's Verify (blind)"
    assert "replaces-case-survivors.sh" in section, "SKILL.md's replaces-case Green paragraph never runs replaces-case-survivors.sh"
    assert "relaunch" in section, "SKILL.md's replaces-case Green paragraph never relaunches the green leaf on survivors"
    assert "event" in section, "SKILL.md's replaces-case Green paragraph never records the relaunch as an event"
    assert "no verifier" in section, "SKILL.md's replaces-case Green paragraph never says no verifier is launched"
