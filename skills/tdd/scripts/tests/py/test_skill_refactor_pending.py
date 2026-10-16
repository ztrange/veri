"""Cases for how skills/tdd/SKILL.md drives the refactor-pending mark, and for CLAUDE.md's and CONTEXT.md's account of it, read as text."""
import importlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[5]
SKILL = ROOT / "skills" / "tdd" / "SKILL.md"
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
    return records_of(pathlib.Path(path).read_bytes())


def section_records(heading):
    text = importlib.import_module("skill_sections").section(SKILL, heading)
    body = text.split("\n", 1)[1] if "\n" in text else ""
    return records_of(body.encode())


def resume():
    return section_records("## Resume")


def draft_pr():
    return section_records("### 4. Draft PR")


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
    assert records, "SKILL.md has no ## Resume section to read"
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
    assert records, "SKILL.md has no ### 4. Draft PR section to read"
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
    assert records, "SKILL.md has no ## Resume section to read"
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
    assert records, "SKILL.md has no ## Resume section to read"
    ask = read(records, "runs next-pending-refactor.sh on a resume", r"next-pending-refactor\.sh")
    says(ask, VERIFY_REFACTOR + r' [^ ]+ [^ ]+ "?\$green', "Resume never runs verify.sh refactor with $green")


def test_skill_md_s_resume_resets_the_worktree_before_it_asks_next_pending_refactor_sh_so_a_resume_with_no_step_carrying_the_mark_still_discards_the_stray_work():
    records = resume()
    assert records, "SKILL.md has no ## Resume section to read"
    text = b" ".join(records)
    assert b"next-pending-refactor.sh" in text, "Resume never asks next-pending-refactor.sh"
    before_ask = text.split(b"next-pending-refactor.sh", 1)[0]
    assert re.search(RESET.encode(), before_ask), "Resume resets the worktree only after asking next-pending-refactor.sh"


def test_skill_md_s_resume_captures_the_dirty_paths_before_it_resets_and_names_them_in_the_resuming_comment():
    records = resume()
    assert records, "SKILL.md has no ## Resume section to read"
    text = b" ".join(records)
    assert DIRTY_TREE.encode() in text, "Resume never captures git status --porcelain"
    assert re.search((DIRTY_TREE + ".*" + RESET).encode(), text), "Resume captures git status --porcelain only after the reset"
    comment = read(records, "says the ### ▶️ Resuming comment names the paths the reset discarded", "▶️ resuming", "(path|file)")
    says(comment, r"(discard|threw away|thrown away|throw away|stray|reset)", "the Resuming comment mentions paths without saying the reset discarded them")


def test_skill_md_s_draft_pr_step_names_a_remedy_for_a_dirty_tree_with_no_step_pending_and_none_unchecked_and_reaches_the_pr_after_it():
    records = draft_pr()
    assert records, "SKILL.md has no ### 4. Draft PR section to read"
    gate = read(records, "asks git status --porcelain before the PR is opened", DIRTY_TREE)
    says(gate, r"(no |nothing |none |without a )[^.]{0,40}pending", "refusal names a remedy only for a step that is pending")
    says(gate, "unchecked", "refusal never says what happens when no step is unchecked either")
    says(gate, r"(come back|comes back|return here|returns here|open the pr|gh pr create)", "refusal never says the run reaches the PR after the remedy")


def test_skill_md_s_resume_says_a_leaf_killed_in_red_or_green_leaves_the_same_stray_work_a_killed_refactor_leaf_does():
    records = resume()
    assert records, "SKILL.md has no ## Resume section to read"
    killed = read(records, "says what a killed leaf leaves in a resumed worktree", "killed", "(uncommitted|stray)")
    both = r"[^a-z](red|green)[^.]{0,30}[^a-z](or|and)[^a-z][^.]{0,30}(green|red)[^a-z]"
    says(killed, both, "Resume never names Red and Green together as phases a kill leaves stray work from")
    says(killed, both + "[^.]{0,80}refactor", "Resume names Red and Green without saying they leave the same stray work a killed refactor leaf does")
