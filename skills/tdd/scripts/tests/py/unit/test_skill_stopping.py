"""Cases for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as text."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

STOPPING = "## Stopping"
LAUNCHING = "## Launching a leaf — detach, then wait in the foreground"
PROCEDURE = "## Procedure"
SATISFIED = "## Already satisfied — the pin"
SCRIPTS = "## The scripts (this skill's `scripts/` directory)"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}
_UNMARK = {ord("*"): None, ord("`"): None}


def _plain(text):
    return text.translate(_UNMARK).translate(_UPPER)


def _section(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = _plain(section).split("\n")[1:]
    assert "".join(lines).strip(), f"SKILL.md has no {heading} section — nothing could be checked"
    return lines


def _has(pattern, lines):
    return any(re.search(pattern, line) for line in lines)


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
    lines, problems = _section(STOPPING), []
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
    lines, problems = _section(STOPPING), []
    for state in ("rebase-merge", "rebase-apply", "merge_head"):
        _require(problems, state, lines, f"the Stopping section never names {state}")
    _require(problems, r"at=unsettled", lines, "the Stopping section never records at=unsettled")
    guard_at = _first(r"rebase-merge", lines)
    reset_at = _first(r"git reset --hard head", lines)
    if _after(guard_at, reset_at):
        problems.append(f"the Stopping section drops the tree (line {reset_at}) before it checks for an interrupted rebase or merge (line {guard_at})")
    assert not problems, problems


def test_stopping_section_runs_push_branch_and_records_push_rejected_with_the_sha_its_stderr_names_on_exit_1_launching_no_reconcile_leaf_and_bailing_not_at_all():
    lines, problems = _section(STOPPING), []
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
    lines, problems = _section(STOPPING), []
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
    lines, problems = _section(STOPPING), []
    _require(problems, r"metrics\.sh <n>", lines, "the Stopping section never renders metrics.sh <n>")
    _require(problems, "### ⏹️ stopped — <mode>", lines,
             "the Stopping section never posts a '### ⏹️ Stopped — <mode>' comment")
    _refuse(problems, r"git (add|commit)", lines, "the Stopping section stages or commits")
    assert not problems, problems


def test_stopping_section_ends_the_run_with_stop_requested_clear_opening_no_pr_removing_no_worktree_and_deleting_no_conductor_pid():
    lines, problems = _section(STOPPING), []
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
    for line in _section(SCRIPTS):
        if line.startswith("- $s/"):
            in_entry = line.startswith("- $s/stop-requested.sh")
        if in_entry:
            entry.append(line)
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
    _checkpoint(problems, "the pin's test: commit", _section(SATISFIED), *PIN_CHECKPOINT, 'git commit -m "test: pin')
    assert not problems, problems


def test_launching_a_leaf_treats_stop_requested_exit_2_as_a_stop_in_mode_at_ledger_narrating_that_the_request_was_unreadable():
    problems = []
    _unreadable_at_ledger(problems, "the Launching a leaf section", [_joined(_section(LAUNCHING))])
    assert not problems, problems


def test_the_three_ledger_commit_checkpoints_send_stop_requested_exit_2_to_stopping_as_at_ledger_narrating_that_the_request_was_unreadable():
    problems, procedure = [], _section(PROCEDURE)
    _checkpoint_exit2(problems, "the green PASS branch", procedure, *GREEN_CHECKPOINT)
    _checkpoint_exit2(problems, "the refactor-pending clear", procedure, *CLEAR_CHECKPOINT)
    _checkpoint_exit2(problems, "the pin's test: commit", _section(SATISFIED), *PIN_CHECKPOINT)
    assert not problems, problems
