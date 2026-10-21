"""Cases for how skills/tdd/SKILL.md drives the refactor-pending mark, and for CLAUDE.md's and CONTEXT.md's account of it, read as text."""
import importlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
SKILL = ROOT / "skills" / "tdd" / "SKILL.md"
RESUME_MD = SKILL.with_name("RESUME.md")
CLAUDE = ROOT / "CLAUDE.md"
CONTEXT = ROOT / "CONTEXT.md"

MARK = "⟂ refactor pending"
VERIFY_REFACTOR = r'(verify|run-verdict)\.sh (--step ("[^"]*"|[^ ]+) )?(--fast-cmd [^ ]+ )?refactor'
RESET = r"git (reset|checkout|restore|clean)"
DIRTY_TREE = "git status --porcelain"


def records_of(raw):
    records, rec = [], b""
    for line in raw.splitlines():
        if re.match(rb"[0-9]+\. ", line) or re.match(rb"\s*- ", line):
            records.append(rec)
            rec = line
        elif not line.strip():
            records.append(rec)
            rec = b""
        elif rec == b"":
            rec = line
        else:
            rec += b" " + line
    records.append(rec)
    return [re.sub(rb"\s+", b" ", r).lower() for r in records if r != b""]


def file_records(path):
    raw = pathlib.Path(path).read_bytes()
    if pathlib.Path(path) == SKILL:
        raw += b"\n" + SKILL.with_name("PIN.md").read_bytes()
    return records_of(raw)


def body_of(text):
    return text.split("\n", 1)[1] if "\n" in text else ""


def section_records(heading):
    source = RESUME_MD if heading == "## Resume" else SKILL
    return records_of(body_of(importlib.import_module("skill_sections").section(source, heading)).encode())


def resume():
    records = section_records("## Resume")
    assert records, "SKILL.md has no ## Resume section to read"
    return records


def draft_pr():
    records = section_records("### 4. Draft PR")
    assert records, "SKILL.md has no ### 4. Draft PR section to read"
    return records


def first(records, *patterns):
    return next((r for r in records if all(re.search(p.encode(), r) for p in patterns)), None)


def read(records, what, *patterns):
    found = first(records, *patterns)
    assert found is not None, f"SKILL.md has no instruction that {what}"
    return found


def says(text, pattern, message):
    assert re.search(pattern.encode(), text), message


def test_skill_md_ticks_green_with_refactor_pending_pins_without_it_and_clears_the_mark_before_mirroring_the_step_done():
    records = file_records(SKILL)
    assert records, "SKILL.md has no instructions to read"
    green = read(records, "ticks the ledger and commits the code with a feat: commit", r"tick-ledger\.sh", "feat:")
    says(green, r"tick-ledger\.sh\s+--refactor-pending", "the green PASS ticks with plain tick-ledger.sh")
    pin = read(records, "ticks the ledger and commits the pin with a test: pin commit", r"tick-ledger\.sh", "test: pin")
    assert b"--refactor-pending" not in pin, "the pin path ticks with --refactor-pending"
    done = read(records, "ends the cycle by posting the step done comment", "step done")
    assert b"clear-refactor-pending.sh" in done, "never runs clear-refactor-pending.sh where a step's cycle completes"
    rest = done.split(b"clear-refactor-pending.sh", 1)[1]
    assert re.search(rb"git\s.*commit", rest), "clears the mark but commits nothing after it"
    assert b"tick-issue-criterion.sh" in rest.split(b"commit", 1)[1], "mirrors the step to the issue before the cleared ledger is committed"


def test_skill_md_s_resume_asks_next_pending_refactor_sh_before_next_unchecked_sh_re_enters_the_pending_step_s_refactor_loop_and_reaches_the_draft_pr_only_when_both_exit_3():
    records = resume()
    pending = next((i for i, r in enumerate(records, 1) if re.search(rb"next-pending-refactor\.sh", r)), 0)
    unchecked = next((i for i, r in enumerate(records, 1) if re.search(rb"next-unchecked\.sh", r)), 0)
    assert pending, "Resume never asks next-pending-refactor.sh"
    assert unchecked, "Resume no longer asks next-unchecked.sh"
    assert pending <= unchecked, "Resume asks next-unchecked.sh before next-pending-refactor.sh"
    ask = read(records, "runs next-pending-refactor.sh on a resume", r"next-pending-refactor\.sh")
    anchor = b"git diff --name-only"
    assert anchor in ask, "Resume computes no files of the pending step's green commit"
    before, after = ask.split(anchor, 1)
    assert re.search(rb"git (checkout|restore|reset|stash|clean)", before), "Resume re-enters the refactor loop without first resetting the worktree"
    assert re.search(rb"git log.*issue-<n>\.md", ask), "Resume never identifies the green commit as the last commit that changed the ledger"
    assert b"refactor:" in ask, "Resume hands the refactor loop no count of refactor: commits"
    assert re.search(rb"verify-refactor|verify\.sh refactor", after), "Resume never runs verify-refactor after re-entering the loop"
    reaches = read(records, "sends a resumed run to the draft pr", "draft pr")
    says(reaches, r"next-pending-refactor\.sh", "Resume sends a resumed run to the draft PR without next-pending-refactor.sh")
    says(reaches, r"next-unchecked\.sh", "Resume sends a resumed run to the draft PR without next-unchecked.sh having exited 3")


def test_skill_md_s_draft_pr_step_refuses_to_open_the_pr_while_git_status_porcelain_is_non_empty_or_next_pending_refactor_sh_finds_a_pending_step():
    records = draft_pr()
    status = next((i for i, r in enumerate(records, 1) if re.search(DIRTY_TREE.encode(), r)), 0)
    opens = next((i for i, r in enumerate(records, 1) if re.search(rb"pr-creating `gh api`", r)), 0)
    assert status, "Draft PR step never checks git status --porcelain"
    assert opens, "Draft PR step no longer opens the PR"
    assert status <= opens, "Draft PR step checks the tree only after the PR-creating gh api call"
    gate = read(records, "asks git status --porcelain before the PR is opened", DIRTY_TREE)
    says(gate, r"next-pending-refactor\.sh", "Draft PR step checks only that the tree is clean")
    says(gate, r"refuse|do not open|does not open|stop|bail|must not|never", "Draft PR step never says the checks can stop it")


def test_claude_md_s_ledger_invariant_and_context_md_s_ledger_entry_say_a_ticked_step_carries_the_refactor_pending_mark_until_its_verify_refactor_passes():
    claude = file_records(CLAUDE)
    assert claude, "CLAUDE.md has no records to read"
    invariant = read(claude, "CLAUDE.md's ledger invariant", "committed ledger", "source of truth")
    says(invariant, MARK, "CLAUDE.md's ledger invariant never spells the mark")
    says(invariant, "verify-refactor", "CLAUDE.md's ledger invariant never names verify-refactor")
    context = file_records(CONTEXT)
    assert context, "CONTEXT.md has no records to read"
    entry = read(context, "CONTEXT.md's Ledger glossary entry", r"^\*\*ledger\*\*:")
    says(entry, MARK, "CONTEXT.md's Ledger entry never spells the mark")
    says(entry, "verify-refactor", "CONTEXT.md's Ledger entry never names verify-refactor")


def test_skill_md_s_resume_resets_the_uncommitted_work_and_relaunches_the_refactor_leaf_with_veri_refactor_budget_reduced_by_the_step_s_existing_refactor_commits():
    records = resume()
    ask = read(records, "runs next-pending-refactor.sh on a resume", r"next-pending-refactor\.sh")
    says(ask, RESET, "Resume relaunches the refactor leaf without first resetting the worktree")
    says(ask, "veri_refactor_budget", "Resume never names VERI_REFACTOR_BUDGET on the pending branch")
    says(ask, r"reduc|minus|subtract|net of|what is left|left of|remaining|\$\(\(", "Resume never says the budget is reduced by the refactor: commits")


def test_skill_md_passes_the_step_s_green_commit_sha_to_verify_sh_refactor_in_the_cycle_loop_and_in_resume_s_pending_branch():
    records = file_records(SKILL)
    assert records, "SKILL.md has no instructions to read"
    loop = read(records, "runs verify.sh refactor in the cycle loop", VERIFY_REFACTOR)
    says(loop, VERIFY_REFACTOR + " [^ ]+ [^ ]+ <green-sha>", "the cycle loop runs verify.sh refactor without <green-sha>")
    records = resume()
    ask = read(records, "runs next-pending-refactor.sh on a resume", r"next-pending-refactor\.sh")
    says(ask, VERIFY_REFACTOR + r' [^ ]+ [^ ]+ "?\$green', "Resume never runs verify.sh refactor with $green")


def test_skill_md_s_resume_resets_the_worktree_before_it_asks_next_pending_refactor_sh_so_a_resume_with_no_step_carrying_the_mark_still_discards_the_stray_work():
    records = resume()
    text = b" ".join(records)
    assert b"next-pending-refactor.sh" in text, "Resume never asks next-pending-refactor.sh"
    before_ask = text.split(b"next-pending-refactor.sh", 1)[0]
    assert re.search(RESET.encode(), before_ask), "Resume resets the worktree only after asking next-pending-refactor.sh"


def test_skill_md_s_resume_captures_the_dirty_paths_before_it_resets_and_names_them_in_the_resuming_comment():
    records = resume()
    text = b" ".join(records)
    assert DIRTY_TREE.encode() in text, "Resume never captures git status --porcelain"
    assert re.search((DIRTY_TREE + ".*" + RESET).encode(), text), "Resume captures git status --porcelain only after the reset"
    comment = read(records, "says the ### ▶️ Resuming comment names the paths the reset discarded", "▶️ resuming", "(path|file)")
    says(comment, r"(discard|threw away|thrown away|throw away|stray|reset)", "the Resuming comment mentions paths without saying the reset discarded them")


def test_skill_md_s_draft_pr_step_names_a_remedy_for_a_dirty_tree_with_no_step_pending_and_none_unchecked_and_reaches_the_pr_after_it():
    records = draft_pr()
    gate = read(records, "asks git status --porcelain before the PR is opened", DIRTY_TREE)
    says(gate, r"(no |nothing |none |without a )[^.]{0,40}pending", "refusal names a remedy only for a step that is pending")
    says(gate, "unchecked", "refusal never says what happens when no step is unchecked either")
    says(gate, r"(come back|comes back|return here|returns here|open the pr|gh pr create)", "refusal never says the run reaches the PR after the remedy")


def test_skill_md_s_resume_says_a_leaf_killed_in_red_or_green_leaves_the_same_stray_work_a_killed_refactor_leaf_does():
    records = resume()
    killed = read(records, "says what a killed leaf leaves in a resumed worktree", "killed", "(uncommitted|stray)")
    both = r"[^a-z](red|green)[^.]{0,30}[^a-z](or|and)[^a-z][^.]{0,30}(green|red)[^a-z]"
    says(killed, both, "Resume never names Red and Green together as phases a kill leaves stray work from")
    says(killed, both + "[^.]{0,80}refactor", "Resume names Red and Green without saying they leave the same stray work a killed refactor leaf does")


SCRIPTS_HEADING = "## The scripts (this skill's `scripts/` directory)"
SKILL_MD = "skills/tdd/SKILL.md"
REMOVAL_VERB = r"strip|remove|drop|clear|delete"


def scripts_records():
    records = file_records(SKILL.with_name("SCRIPTS.md"))
    assert records, "SCRIPTS.md has no entries to read"
    return records


def planted_records(text):
    records = records_of(body_of(importlib.import_module("skill_sections").section_of(text, SCRIPTS_HEADING)).encode())
    assert records, "the planted ## The scripts section could not be read"
    return records


def entry_of(records, script, problems):
    found = first(records, r"^- .\$s/" + re.escape(script))
    if found is None:
        problems.append(f"{SKILL_MD} has no instruction that documents {script} in the script reference list")
    return found


def entry_says(problems, entry, script, pattern, message):
    if not re.search(pattern.encode(), entry):
        problems.append(f"{SKILL_MD}'s entry for {script} {message}")


def says_removal_verb(problems, entry, script):
    entry_says(problems, entry.replace(script.encode(), b""), script, REMOVAL_VERB,
               "never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name")


def says_exit_codes(problems, entry, script):
    entry_says(problems, entry, script, r"exits? 0",
               "never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty")
    entry_says(problems, entry, script, r"exits? 3",
               "never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken")


def removal_verb_probe(records):
    problems = []
    entry = entry_of(records, "clear-refactor-pending.sh", problems)
    if entry is not None:
        says_removal_verb(problems, entry, "clear-refactor-pending.sh")
    return problems


def reference_list_probes(records):
    problems = []
    script = "tick-ledger.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, r"--refactor-pending",
                   "never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick")
        entry_says(problems, entry, script, re.escape(MARK),
                   f"never spells the mark the flag appends, so nothing connects that write to the `{MARK}` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing")
        entry_says(problems, entry, script, r"exits? 3",
                   "never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick")
    script = "next-pending-refactor.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, r"prints?[^.]*step",
                   "never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on")
        says_exit_codes(problems, entry, script)
    script = "clear-refactor-pending.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, re.escape(MARK),
                   "never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark")
        says_removal_verb(problems, entry, script)
        says_exit_codes(problems, entry, script)
    return problems


def resume_text():
    body = body_of(importlib.import_module("skill_sections").section(RESUME_MD, "## Resume"))
    assert body.strip(), "SKILL.md has no ## Resume section to read"
    return re.sub(" +", " ", body.replace("\n", " "))


def test_skill_md_s_script_reference_list_documents_tick_ledger_sh_refactor_pending_next_pending_refactor_sh_and_clear_refactor_pending_sh_each_with_what_it_prints_and_its_exit_codes():
    problems = reference_list_probes(scripts_records())
    assert not problems, problems


def test_1420_skill_md_s_resume_sub_step_2_uses_the_stray_preflight_step_3_captured_and_never_re_captures_git_status_porcelain_after_that_reset():
    sub2 = read(resume(), "is Resume sub-step 2", r"^2\. ")
    assert not re.search(rb'stray="?\$\(git status --porcelain', sub2), "Resume sub-step 2 tells the conductor to run stray=\"$(git status --porcelain)\" itself, but preflight step 3 has already reset the tree"
    says(sub2, "preflight", "Resume sub-step 2 never says the stray capture already happened in preflight step 3")


PLANTED_CLEAR_ONLY_BY_FILENAME = """## The scripts (this skill's `scripts/` directory)

- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of
  `tick-ledger.sh --refactor-pending`: the first ticked step matching the substring no longer
  carries the ` ⟂ refactor pending` mark afterwards, once that step's refactor has been
  verified. Nothing on stdout. **Exit 0** when it did its work; **exit 3** when no ticked step
  both matched and carried the mark.
"""

PLANTED_BARE_ENTRIES = """## The scripts (this skill's `scripts/` directory)

- `$S/tick-ledger.sh .tdd/issue-<n>.md '<substring>'` — the ledger is rewritten so the first
  unchecked step matching the substring is ticked.
- `$S/next-pending-refactor.sh .tdd/issue-<n>.md` — reads the ledger and answers about the
  first ticked step whose tidying is still owed.
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of the
  tick above, run once that step's refactor has been verified. Nothing on stdout.
"""


def test_case_4_s_removal_verb_probe_reports_a_problem_naming_the_clear_refactor_pending_sh_entry_when_only_the_filename_that_opens_it_supplies_a_removal_verb():
    problems = removal_verb_probe(planted_records(PLANTED_CLEAR_ONLY_BY_FILENAME))
    assert problems, "the removal-verb probe reported nothing against an entry whose only removal verb is the clear-refactor-pending.sh filename that opens it"
    assert "clear-refactor-pending.sh" in " ".join(problems), "the removal-verb probe reported a problem that never names the clear-refactor-pending.sh entry"


def test_skill_md_s_clear_refactor_pending_sh_entry_names_a_removal_verb_in_its_own_prose_so_case_4_s_removal_verb_probe_reports_nothing_against_the_document_as_committed():
    problems = removal_verb_probe(scripts_records())
    assert not problems, problems


def test_case_4_s_other_nine_probes_each_report_a_problem_under_the_entry_they_were_asked_of_against_reference_list_entries_that_carry_none_of_what_they_ask_for():
    problems = reference_list_probes(planted_records(PLANTED_BARE_ENTRIES))
    wanted = [
        ("tick-ledger.sh", "never mentions --refactor-pending"),
        ("tick-ledger.sh", "never spells the mark the flag appends"),
        ("tick-ledger.sh", "never names exit 3, so a green commit"),
        ("next-pending-refactor.sh", "never says it prints the pending step"),
        ("next-pending-refactor.sh", "never names exit 0"),
        ("next-pending-refactor.sh", "never names exit 3, so the one code"),
        ("clear-refactor-pending.sh", "never spells the mark it removes"),
        ("clear-refactor-pending.sh", "never names exit 0"),
        ("clear-refactor-pending.sh", "never names exit 3, so the one code"),
    ]
    silent = [w for w in wanted if not any(f"entry for {w[0]}" in p and w[1] in p for p in problems)]
    assert not silent, f"no probe reported these, though the planted entries carry none of it: {silent}"


def test_1579_skill_md_s_resume_plans_each_unticked_criterion_no_ledger_step_serves_with_add_ledger_step_sh_planned_criterion_k_one_call_per_criterion_as_a_plan_commit_before_the_cycle_loop_and_leaves_every_other_insertion_counting():
    text = resume_text()
    assert "add-ledger-step.sh --planned --criterion" in text, "Resume never names add-ledger-step.sh --planned --criterion k"
    assert "unticked" in text and "⟦criterion k⟧" in text, "Resume never limits --planned to an unticked criterion no ⟦criterion k⟧ step serves"
    assert re.search(r"one call per criterion", text), "Resume never says one call per criterion"
    assert "`plan:` commit" in text, "Resume never says the planned steps are committed as a plan: commit"
    assert "⟦added⟧" in text and re.search(r"omits? --planned", text), "Resume never says every other insertion omits --planned and stays ⟦added⟧ growth"


def test_1579_skill_md_s_resume_sub_step_1_says_the_ledger_is_not_re_planned_except_that_the_amended_criteria_are_planned_with_planned_in_sub_step_3_not_an_unqualified_do_not_re_plan():
    text = resume_text()
    sub1 = text.split(" 1. ", 1)[1] if " 1. " in text else text
    sub1 = sub1.split(" 2. ", 1)[0]
    assert "re-plan" in sub1, "could not find Resume sub-step 1's re-plan sentence"
    assert "--planned" in sub1, "Resume sub-step 1 never names --planned"
    assert "sub-step 3" in sub1, "Resume sub-step 1 never points at sub-step 3"
    assert re.search(r"except", sub1), "Resume sub-step 1 never states the exception to not re-planning"


def test_1579_skill_md_states_that_a_conductor_never_sets_or_raises_veri_step_growth_revise_budget_veri_refactor_budget_veri_stuck_retries_or_veri_no_verdict_retries_mid_run_and_that_a_budget_it_cannot_fit_inside_is_a_bail():
    text = re.sub(" +", " ", (SKILL.read_text() + RESUME_MD.read_text()).replace("*", "").replace("`", "").lower().replace("\n", " "))
    sentences = re.sub(r"\. ", ".\n", text).split("\n")
    never = "\n".join(s for s in sentences if "never" in s and "mid-run" in s and "raise" in s)
    for var in ("VERI_STEP_GROWTH", "REVISE_BUDGET", "VERI_REFACTOR_BUDGET", "VERI_STUCK_RETRIES", "VERI_NO_VERDICT_RETRIES"):
        assert var.lower() in never, f"no sentence says a conductor never sets or raises {var} mid-run"
    assert any("budget" in s and "cannot fit" in s and "bail" in s for s in sentences), "no sentence says a budget the conductor cannot fit inside is a bail"
