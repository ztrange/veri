"""Cases for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as text."""
import importlib
import pathlib
import re

from skill_sections import LOWER, has_match as _has, plain as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
SCOPE_LOOP = SKILL.with_name("SCOPE-LOOP.md")
STOPPING_MD = SKILL.with_name("STOPPING.md")
PIN_MD = SKILL.with_name("PIN.md")

STOPPING = "## Stopping"
LAUNCHING = "## Launching a leaf — detach, then wait in the foreground"
PROCEDURE = "## Procedure"
SATISFIED = "## Already satisfied — the pin"
BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
LOOP_4 = "### Loop 4. Stop conditions"
LOOP_5 = "### Loop 5. Report"
SCRIPTS = "## The scripts (this skill's `scripts/` directory)"


def _section(heading, path=SKILL):
    section = importlib.import_module("skill_sections").section(BAIL if heading == BAILING else path, heading)
    lines = _plain(section).split("\n")[1:]
    assert "".join(lines).strip(), f"SKILL.md has no {heading} section — nothing could be checked"
    return lines


def _first(pattern, lines):
    return next((n for n, line in enumerate(lines, 1) if re.search(pattern, line)), None)


def _after(a, b):
    return bool(a and b and a > b)


def _joined(lines):
    return re.sub(" +", " ", " ".join(lines) + " ")


def _word(word):
    return rf"(^|[^a-z-]){word}([^a-z-]|$)"


def _either_order(a, b):
    return rf"{a}[^.;]*{b}|{b}[^.;]*{a}"


def _require(problems, pattern, lines, message):
    if not _has(pattern, lines):
        problems.append(message)


def _refuse(problems, pattern, lines, message):
    if _has(pattern, lines):
        problems.append(message)


def _branch(lines, start, end):
    out, inside = [], False
    for line in lines:
        if not inside and re.search(start, line):
            inside = True
        if inside:
            out.append(line)
            if re.search(end, line):
                break
    return out


def _unreadable_at_ledger(problems, what, lines):
    _require(problems, r"exit 2[^.;]*at-ledger", lines,
             f"{what} never says stop-requested.sh's exit 2 is a stop in mode at-ledger")
    _require(problems, _either_order("exit 2", "unreadable"), lines,
             f"{what} never says to narrate that the stop request was unreadable on exit 2")


def _checkpoint(problems, what, section, start, end, anchor):
    window = _branch(section, start, end)
    if not window:
        problems.append(f"{what} has no branch to read — nothing could be checked")
        return
    anchor_at = _first(anchor, window)
    stop_at = _first(r"stop-requested\.sh", window)
    if stop_at is None:
        problems.append(f"{what} is never followed by stop-requested.sh")
    elif not _after(stop_at, anchor_at):
        problems.append(f"{what} runs stop-requested.sh (line {stop_at}) before its ledger commit lands (line {anchor_at})")
    _require(problems, _either_order("(any|every|whatever)[^.;]*mode", "stopping"), [_joined(window)],
             f"{what} never says any mode stop-requested.sh prints goes to Stopping there")


def _checkpoint_exit2(problems, what, section, start, end):
    text = _joined(_branch(section, start, end))
    if "stop-requested.sh" not in text:
        problems.append(f"{what} has no stop-requested.sh checkpoint to read — nothing could be checked")
        return
    _unreadable_at_ledger(problems, what, [text.split("stop-requested.sh", 1)[1]])


GREEN_CHECKPOINT = ('git commit -m "feat: <step summary>', "continue to the refactor loop")
CLEAR_CHECKPOINT = (r"\$s/clear-refactor-pending\.sh \.tdd/issue-<n>\.md", "loop back to the top of step 3")
PIN_CHECKPOINT = ('git commit -m "test: pin', "loop back to the top of step 3")


def test_stopping_section_waits_with_wait_leaf_on_every_running_supervisor_before_it_touches_the_tree_and_reaches_only_for_git_reset_hard_head_never_git_checkout():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    wait_at = _first(r"wait-leaf\.sh", lines)
    if wait_at is None:
        problems.append("the Stopping section never calls wait-leaf.sh")
    _require(problems, r"\.tdd/<name>\.pid", lines, "the Stopping section never names .tdd/<name>.pid")
    _require(problems, r"supervise\.sh <name> ", lines, "the Stopping section never names 'supervise.sh <name> '")
    reset_at = _first(r"git reset --hard head", lines)
    if reset_at is None:
        problems.append("the Stopping section never drops the tree with git reset --hard HEAD")
    elif _after(wait_at, reset_at):
        problems.append(f"the Stopping section reaches for the tree (line {reset_at}) before it waits on the leaves (line {wait_at})")
    _refuse(problems, r"git checkout", lines, "the Stopping section reaches for git checkout")
    assert not problems, problems


def test_stopping_section_resets_nothing_and_records_at_unsettled_when_rebase_merge_rebase_apply_or_merge_head_is_present():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    for state in ("rebase-merge", "rebase-apply", "merge_head"):
        _require(problems, state, lines, f"the Stopping section never names {state}")
    _require(problems, r"at=unsettled", lines, "the Stopping section never records at=unsettled")
    guard_at = _first(r"rebase-merge", lines)
    reset_at = _first(r"git reset --hard head", lines)
    if _after(guard_at, reset_at):
        problems.append(f"the Stopping section drops the tree (line {reset_at}) before it checks for an interrupted rebase or merge (line {guard_at})")
    assert not problems, problems


def test_stopping_section_runs_push_branch_and_records_push_rejected_with_the_sha_its_stderr_names_on_exit_1_launching_no_reconcile_leaf_and_bailing_not_at_all():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    _require(problems, r"push-branch\.sh", lines, "the Stopping section never runs push-branch.sh")
    _require(problems, r"exit 1", lines, "the Stopping section says nothing about push-branch.sh exit 1")
    _require(problems, r"push=rejected", lines, "the Stopping section never records push=rejected")
    _require(problems, r"stderr", lines, "the Stopping section never names push-branch.sh's stderr")
    _require(problems, r"sha", lines, "the Stopping section never names the sha the rejected push is recorded with")
    _refuse(problems, r"detach-leaf\.sh|build-develop-prompt\.sh reconcile|develop-reconcile", lines,
            "the Stopping section launches the reconcile leaf")
    _refuse(problems, r"event\.sh bail", lines, "the Stopping section bails on the rejected push")
    assert not problems, problems


def test_stopping_section_writes_exactly_one_event_stop_mark_with_at_one_of_unplanned_planned_green_step_done_or_unsettled_and_names_classify_bail_nowhere():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    marks = sum(1 for line in lines if re.search(r"event\.sh stop", line))
    if marks == 0:
        problems.append("the Stopping section never writes an event.sh stop mark")
    elif marks != 1:
        problems.append(f"the Stopping section writes {marks} event.sh stop marks")
    _require(problems, r"event\.sh stop mode=<mode> at=<at>", lines,
             "the Stopping section never spells the mark event.sh stop mode=<mode> at=<at>")
    for at in ("unplanned", "planned", "green", "step-done", "unsettled"):
        _require(problems, f"at={at}", lines, f"the Stopping section never names at={at}")
    _refuse(problems, r"classify-bail\.sh", lines, "the Stopping section calls classify-bail.sh")
    assert not problems, problems


def test_stopping_section_renders_metrics_into_a_stopped_mode_comment_and_commits_no_metrics_file():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    _require(problems, r"metrics\.sh <n>", lines, "the Stopping section never renders metrics.sh <n>")
    _require(problems, "### ⏹️ stopped — <mode>", lines,
             "the Stopping section never posts a '### ⏹️ Stopped — <mode>' comment")
    _refuse(problems, r"git (add|commit)", lines, "the Stopping section stages or commits")
    assert not problems, problems


def test_stopping_section_ends_the_run_with_stop_requested_clear_opening_no_pr_removing_no_worktree_and_deleting_no_conductor_pid():
    lines, problems = _section(STOPPING, STOPPING_MD), []
    clear_at = _first(r"stop-requested\.sh --clear", lines)
    report_at = _first(r"metrics\.sh <n>", lines)
    if clear_at is None:
        problems.append("the Stopping section never runs stop-requested.sh --clear")
    elif _after(report_at, clear_at):
        problems.append(f"the Stopping section clears the stop request (line {clear_at}) before it reports the pause (line {report_at})")
    _refuse(problems, r"gh pr (create|ready)", lines, "the Stopping section opens or readies a PR")
    _refuse(problems, r"git worktree remove", lines, "the Stopping section removes the worktree")
    _refuse(problems, r"rm .*conductor\.pid", lines, "the Stopping section deletes .tdd/conductor.pid")
    assert not problems, problems


def test_script_reference_list_has_an_entry_for_stop_requested_saying_what_it_prints_and_which_exit_codes_it_answers_with():
    entry, in_entry, problems = [], False, []
    raw = SKILL.with_name("SCRIPTS.md").read_text().split("\n")
    for line in raw:
        if line.startswith("- `$S/"):
            in_entry = line.startswith("- `$S/stop-requested.sh")
        if in_entry:
            entry.append(_plain(line))
    if not "".join(entry).strip():
        problems.append("the script reference list has no $S/stop-requested.sh entry")
    else:
        for mode in ("at-ledger", "at-leaf", "now"):
            _require(problems, mode, entry, f"the stop-requested.sh entry never names the mode {mode}")
        sentences = _joined(entry).replace(". ", ".\n").split("\n")
        exit0 = [s for s in sentences if re.search(r"exit 0([^0-9]|$)", s)]
        _require(problems, "printed on stdout", exit0,
                 "the stop-requested.sh entry's exit 0 sentence never says the mode is printed on stdout")
        _require(problems, "--clear", entry, "the stop-requested.sh entry never names --clear")
        for code in (0, 2, 3):
            _require(problems, rf"exits? ([0-9]+[ ,/]+(or |and )?)*{code}([^0-9]|$)", entry,
                     f"the stop-requested.sh entry never names exit {code}")
    assert not problems, problems


def test_launching_a_leaf_runs_stop_requested_before_every_leaf_launch_exit_3_launches_as_normal_at_ledger_launches_the_leaf_anyway_at_leaf_and_now_launch_nothing_and_go_to_stopping():
    lines, problems = [_joined(_section(LAUNCHING))], []
    _require(problems, r"stop-requested\.sh", lines, "the Launching a leaf section never runs stop-requested.sh")
    _require(problems, _either_order(r"before[^.;]*launch", r"stop-requested\.sh"), lines,
             "the Launching a leaf section never says stop-requested.sh runs before a leaf is launched")
    _require(problems, r"exit 3[^.;]*launch", lines,
             "the Launching a leaf section never says stop-requested.sh's exit 3 launches as normal")
    _require(problems, r"at-ledger[^.;]*launch", lines,
             "the Launching a leaf section never says mode at-ledger launches the leaf anyway")
    for mode in ("at-leaf", "now"):
        _require(problems, _word(mode) + r"[^.;]*launch(es)? nothing", lines,
                 f"the Launching a leaf section never says mode {mode} launches nothing")
    _require(problems, r"launch(es)? nothing[^.;]*stopping", lines,
             "the Launching a leaf section never sends a launch-nothing mode to Stopping")
    assert not problems, problems


def test_green_pass_branch_runs_stop_requested_immediately_after_the_atomic_green_commits_push_and_any_mode_it_prints_goes_to_stopping():
    problems = []
    _checkpoint(problems, "the green PASS branch", _section(PROCEDURE), *GREEN_CHECKPOINT, r"push-branch\.sh")
    assert not problems, problems


def test_refactor_pending_clears_push_and_a_pins_test_commit_are_each_followed_by_stop_requested_and_any_mode_it_prints_goes_to_stopping():
    problems = []
    _checkpoint(problems, "the refactor-pending clear", _section(PROCEDURE), *CLEAR_CHECKPOINT, r"push-branch\.sh")
    _checkpoint(problems, "the pin's test: commit", _section(SATISFIED, PIN_MD), *PIN_CHECKPOINT, 'git commit -m "test: pin')
    assert not problems, problems


def test_launching_a_leaf_treats_stop_requested_exit_2_as_a_stop_in_mode_at_ledger_narrating_that_the_request_was_unreadable():
    problems = []
    _unreadable_at_ledger(problems, "the Launching a leaf section", [_joined(_section(LAUNCHING))])
    assert not problems, problems


def test_the_three_ledger_commit_checkpoints_send_stop_requested_exit_2_to_stopping_as_at_ledger_narrating_that_the_request_was_unreadable():
    problems, procedure = [], _section(PROCEDURE)
    _checkpoint_exit2(problems, "the green PASS branch", procedure, *GREEN_CHECKPOINT)
    _checkpoint_exit2(problems, "the refactor-pending clear", procedure, *CLEAR_CHECKPOINT)
    _checkpoint_exit2(problems, "the pin's test: commit", _section(SATISFIED, PIN_MD), *PIN_CHECKPOINT)
    assert not problems, problems


def _phase_exit2(heading, anchor):
    inside, kept = False, []
    for raw in (SKILL.read_text() + "\n" + SKILL.with_name("REVISE.md").read_text()).splitlines():
        if re.match(r"#{2,4} ", raw):
            inside = bool(re.search(heading, raw.translate(LOWER)))
            continue
        if inside:
            kept.append(_plain(raw))
    out, buf, hit = None, "", False
    for line in kept:
        if re.match(r"[ \t]*$", line) or re.match(r"[ \t]*(- |[0-9]+\. )", line):
            if hit:
                out = buf
                break
            buf = ""
        if re.match(r"[ \t]*$", line):
            continue
        buf += " " + line
        if re.search(anchor, line):
            hit = True
    else:
        if hit:
            out = buf
    return None if out is None else re.sub(" +", " ", out)


def _draft_pr_step():
    return _branch(_section(PROCEDURE), r"^### 4\. draft pr", r"^### 5\.")


def _stopped_issue_bullets():
    inside, kept = False, []
    for line in _section(LOOP_4, SCOPE_LOOP):
        if line.startswith("- "):
            inside = bool(re.match(r"- [^.]*stop", line))
        if line and line[0] not in "- ":
            inside = False
        if inside:
            kept.append(line)
    return kept


def test_launching_a_leaf_asks_stop_requested_before_reading_a_leafs_wait_leaf_exit_2_as_killed_stuck_and_a_pending_now_goes_to_stopping_instead_of_bailing():
    lines, problems = [_joined(_section(LAUNCHING))], []
    _require(problems, _either_order(r"stop-requested\.sh", r"before[^.;]*killed-stuck"), lines,
             "the Launching a leaf section never asks stop-requested.sh before reading a leaf's exit 2 as killed-stuck")
    _require(problems, rf"{_word('now')}[^.;]*stopping[^.;]*(instead of|rather than)[^.;]*bailing|{_word('now')}[^.;]*(instead of|rather than)[^.;]*bailing[^.;]*stopping", lines,
             "the Launching a leaf section never sends a leaf's exit 2 with a pending now to Stopping instead of Bailing")
    assert not problems, problems


def test_each_phases_leaf_exit_2_branch_points_back_to_launching_a_leaf_where_stop_requested_is_asked_before_the_exit_2_is_read_as_killed_stuck():
    phases = [
        ("develop-red", r"^#### red", r"exits 2 \(killed-stuck\)"),
        ("green", r"^#### green", r"exit 2 → bail"),
        ("refactor", r"^#### refactor loop", r"exit 2 → bail"),
        ("revise", r"^## revising on a reject", r"exit 2 → bail"),
    ]
    problems = []
    for phase, heading, anchor in phases:
        clause = _phase_exit2(heading, anchor)
        if not clause:
            problems.append(f"the {phase} branch has no exit-2 clause to read — nothing could be checked")
            continue
        _require(problems, "launching a leaf", [clause],
                 f"the {phase} branch reads a leaf's exit 2 without pointing back to Launching a leaf — a pending now stop there would bail")
    assert not problems, problems


def test_bailing_keeps_a_bail_reached_first_revise_budget_exhausted_or_killed_stuck_with_no_now_pending_as_a_bail_and_its_comment_says_a_stop_was_pending_when_one_was():
    lines, problems = [_joined(_section(BAILING))], []
    pending, stop = _word("pending"), _word("stop")
    _require(problems, r"stop-requested\.sh", lines,
             "the Bailing section never asks stop-requested.sh — it cannot say whether a stop was pending")
    _require(problems, _either_order("revise_budget", f"{stop}[^.;]*{pending}"), lines,
             "the Bailing section never says a REJECT exhausting REVISE_BUDGET with a stop pending still bails")
    _require(problems, _either_order("killed-stuck", f"no[^.;]*{_word('now')}[^.;]*{pending}"), lines,
             "the Bailing section never says a killed-stuck leaf with no now pending still bails")
    _require(problems, _either_order("comment", f"{stop}[^.;]*{pending}"), lines,
             "the Bailing section's comment never says a stop was pending when one was")
    assert not problems, problems


def test_the_draft_pr_step_runs_to_completion_with_a_stop_request_pending_clears_it_with_stop_requested_clear_and_its_final_done_comment_says_a_stop_arrived_after_the_last_step():
    problems = []
    draft_pr = _draft_pr_step()
    joined, stop = [_joined(draft_pr)], _word("stop")
    _require(problems, r"stop-requested\.sh --clear", joined,
             "the Draft PR step never runs stop-requested.sh --clear — a stop arriving after the last step would outlive the run and pause the next one")
    _require(problems, _either_order(f"({stop}[^.;]*pending|pending[^.;]*{stop})", "(runs? to completion|not interrupted|finish(es)?)"), joined,
             "the Draft PR step never says it runs to completion with a stop request pending")
    final = []
    for line in draft_pr:
        if not final and not re.search(r"^4\. post a final", line):
            continue
        if re.match(r"[ \t]*$", line):
            break
        final.append(line)
    final = [_joined(final)]
    _require(problems, "### ✅ done", final,
             "the Draft PR step has no sub-step posting the final ### ✅ Done comment to read")
    _require(problems, f"{stop}[^.;]*arrived[^.;]*after[^.;]*last step", final,
             "the final ### ✅ Done comment never says a stop arrived after the last step")
    assert not problems, problems


def test_the_draft_pr_step_says_both_checkpoints_apply_to_the_repair_step_a_red_full_run_appends_like_any_other_step():
    lines, problems = [_joined(_draft_pr_step())], []
    _require(problems, _either_order("repair step", "(both|the two) checkpoints"), lines,
             "the Draft PR step never says both checkpoints apply to the repair step a red full run appends — a stop requested during a repair would run on to its end")
    assert not problems, problems


def test_987_preflight_step_3_runs_stop_requested_clear_beside_the_tdd_conductor_pid_write():
    lines, problems = [_joined(_branch(_section(PROCEDURE), r"^3\. suite is green at baseline", r"^4\. "))], []
    _require(problems, r"\.tdd/conductor\.pid", lines,
             "preflight step 3 has no .tdd/conductor.pid write to read — nothing could be checked beside it")
    _require(problems, r"stop-requested\.sh --clear", lines,
             "preflight step 3 never runs stop-requested.sh --clear — a request a killed run left behind would stop the run that resumes it")
    assert not problems, problems


def test_scope_loop_md_loop_4_stop_conditions_list_an_issue_that_ended_in_a_stop_and_say_the_loop_then_reports_and_stops_without_going_back_to_loop_1_or_selecting_another_issue():
    bullets, problems = _stopped_issue_bullets(), []
    assert bullets, "SCOPE-LOOP.md's Loop 4 lists no issue that ended in a stop — a stopped issue leaves the loop carrying on to the next one"
    lines = [_joined(bullets)]
    _require(problems, r"(^|[^a-z])reports?[^.;]*stops?", lines,
             "the stopped-issue condition never says the loop reports and stops")
    _require(problems, r"(not|never)[^.;]*(go(es)? back|return)[^.;]*loop 1", lines,
             "the stopped-issue condition never says the loop does not go back to Loop 1")
    _require(problems, _either_order("(not|never|no)[^.;]*(select|pick|take|start)", "(another|next|other) issue"), lines,
             "the stopped-issue condition never says the loop does not select another issue")
    assert not problems, problems


def test_scope_loop_md_says_a_stop_unlike_a_bail_has_no_continue_past_option_no_continue_on_bail_equivalent_because_a_stop_is_the_operator_speaking():
    bullets, problems = _stopped_issue_bullets(), []
    assert bullets, "SCOPE-LOOP.md's Loop 4 lists no issue that ended in a stop — nothing could be checked"
    lines = [_joined(bullets)]
    _require(problems, _either_order("(^|[^a-z])(no|not|never|nothing)[^a-z]", "(--continue-on-bail|continue[- ]past)"), lines,
             "the stopped-issue condition never says a stop has no --continue-on-bail equivalent")
    _require(problems, r"(^|[^a-z])operator", lines,
             "the stopped-issue condition never says a stop is the operator speaking")
    assert not problems, problems


def test_scope_loop_md_loop_5_report_gives_a_stopped_issue_a_stopped_mode_per_issue_line_and_names_the_stop_and_the_stopped_issues_mode_as_what_stopped_the_loop():
    raw = importlib.import_module("skill_sections").section(SCOPE_LOOP, LOOP_5).split("\n")[1:]
    problems, fence, first, rest = [], 0, [], []
    for line in raw:
        if line.startswith("```"):
            fence += 1
            continue
        if fence == 1:
            first.append(_plain(line))
        if fence >= 2:
            rest.append(_plain(line))
    assert "".join(raw).strip(), "SCOPE-LOOP.md has no ### Loop 5 section — nothing could be checked"
    _require(problems, r"stopped: ?<mode>", first,
             "Loop 5's per-issue line has no stopped: <mode> form beside the PR url, bailed: and skipped:")
    rest = [_joined(rest)]
    _require(problems, _either_order("what stopped the loop", _word("stop")), rest,
             "Loop 5 never names the stop as what stopped the loop")
    _require(problems, _either_order("what stopped the loop", "(^|[^a-z])mode"), rest,
             "Loop 5 never names the stopped issue's mode as what stopped the loop")
    assert not problems, problems


def test_scope_loop_md_says_re_invoking_the_same_command_after_a_stop_resumes_the_stopped_issue_from_its_committed_ledger_and_then_carries_on_draining_the_scope():
    bullets, problems = _stopped_issue_bullets(), []
    assert bullets, "SCOPE-LOOP.md's Loop 4 lists no issue that ended in a stop — nothing could be checked"
    lines = [_joined(bullets)]
    _require(problems, r"re-?invok(e|es|ing)[^.;]*same command", lines,
             "the stopped-issue condition never says to re-invoke the same command")
    _require(problems, _either_order("resum", "committed ledger"), lines,
             "the stopped-issue condition never says the stopped issue resumes from its committed ledger")
    _require(problems, r"resum[^.;]*(carr(y|ies|ying) on|continu(e|es|ing)|keep(s|ing)? going)[^.;]*(drain|scope)", lines,
             "the stopped-issue condition never says the resumed run then carries on draining the scope")
    assert not problems, problems


def test_1174_skill_md_tells_the_conductor_it_signals_only_processes_it_started_by_the_pid_it_recorded_when_it_started_them_never_by_name_or_pattern_pkill_killall_kill_pgrep_and_that_experiments_carry_the_exp_prefix_no_live_run_uses():
    text = re.sub(" +", " ", _plain(SKILL.read_text()).replace("\n", " "))
    lines, problems = [text], []
    _require(problems, r"(signal|kill)s? only (the )?processes (it|you) (started|start)", lines,
             "SKILL.md never says the conductor signals only processes it started")
    _require(problems, r"pid (it|you) recorded when (it|you) started", lines,
             "SKILL.md never says it signals by the pid it recorded when it started them")
    _require(problems, r"never by name or (by )?pattern", lines, "SKILL.md never says it never signals by name or pattern")
    _require(problems, _word("pkill"), lines, "SKILL.md never names pkill")
    _require(problems, _word("killall"), lines, "SKILL.md never names killall")
    _require(problems, r"kill \$\(pgrep", lines, "SKILL.md never names kill $(pgrep …)")
    _require(problems, _either_order(_word("exp-"), "prefix"), lines,
             "SKILL.md never says an experiment's processes and leaf names carry the exp- prefix")
    _require(problems, "no live run uses", lines, "SKILL.md never says no live run uses that prefix")
    assert not problems, problems


def test_standing_bail_rule_is_stated_once_and_no_line_names_bailing_without_bail_md():
    pointer = "<base directory>/BAIL.md"
    files = [SKILL, SKILL.with_name("SCRIPTS.md"), STOPPING_MD, SKILL.with_name("RECONCILE.md")]
    texts = {path.name: path.read_text().split("\n") for path in files}
    rule = [line for line in texts["SKILL.md"] if "Whenever this procedure says **bail**" in line and pointer in line]
    assert len(rule) == 1, f"SKILL.md holds {len(rule)} standing bail rule lines, expected exactly 1"
    bare = [f"{name}:{n}" for name, lines in texts.items() for n, line in enumerate(lines, 1)
            if re.search(r"\bBailing\b", line) and pointer not in line]
    assert not bare, f"lines name Bailing without {pointer}: {bare}"


def test_bailing_section_lives_in_bail_md_and_skill_md_carries_none_of_its_lines():
    moved = [r"preserve-attempt\.sh <n> .*\bbail\b", r"event\.sh bail cause=<cause>", r"metrics: what bailing on"]
    skill = SKILL.read_text().split("\n")
    bail = BAIL.read_text().split("\n")
    assert not [line for line in skill if line == BAILING], "SKILL.md still carries the ## Bailing heading"
    assert [line for line in bail if line == BAILING], "BAIL.md carries no ## Bailing heading"
    left = [p for p in moved if _has(p, skill)]
    assert not left, f"SKILL.md still carries the moved lines {left}"
    missing = [p for p in moved if not _has(p, bail)]
    assert not missing, f"BAIL.md lacks the moved lines {missing}"
