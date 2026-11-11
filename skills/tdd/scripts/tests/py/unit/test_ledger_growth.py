"""In-process cases for veri/ledger_growth.py, the module ledger-growth.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def ledger_growth():
    return importlib.import_module("veri.ledger_growth")


def test_2130_a_hand_added_step_line_without_the_added_mark_exits_1_naming_the_line(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n"
        "- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a sneaked in step ⟦criterion 1⟧\n"
    )
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "a sneaked in step" in err) == (1, "", True)


def test_2130_ticks_refactor_pending_and_phase_marks_on_planned_lines_exit_0_and_a_missing_argument_or_file_exits_2(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text(
        "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n"
        "- [ ] a wheel turns ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a wheel turns ⟦phases: expand, migrate⟧ ⟦criterion 2⟧ ⟂ expand done\n")
    unchanged = run_cli(ledger_growth, [str(plan), str(ledger)])
    no_arguments = run_cli(ledger_growth, [])
    unreadable = run_cli(ledger_growth, [str(plan), str(tmp_path / "missing.md")])
    assert (unchanged, no_arguments[0], "usage" in no_arguments[2], unreadable[0]) == (
        (0, "", ""), 2, True, 2)


def test_2130_a_hand_added_step_line_with_the_added_mark_but_no_add_ledger_step_record_exits_1_naming_the_line(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n"
        "- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a hand written step ⟦added⟧ ⟦criterion 1⟧\n"
    )
    (tmp_path / "events.jsonl").write_text(
        '{"ts": 1, "issue": "42", "event": "step-added", "anchor": "a hand written step", "added": "1"}\n')
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "a hand written step" in err) == (1, "", True)


def test_2130_an_added_step_line_with_its_add_ledger_step_record_exits_0_silently(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    line = "- [ ] a inserted step ⟦added⟧ ⟦criterion 1⟧"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + line + "\n")
    (tmp_path / "events.jsonl").write_text(
        '{"event": "step-added", "actor": "add-ledger-step", "step": "' + line + '"}\n')
    assert run_cli(ledger_growth, [str(plan), str(ledger)]) == (0, "", "")


def test_2130_an_unmarked_repair_step_line_is_accepted_with_its_add_ledger_step_record_and_refused_without(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    line = "- [ ] repair the suite ⟦suite-repair⟧ ⟦criterion 1⟧"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + line + "\n")
    missing = run_cli(ledger_growth, [str(plan), str(ledger)])
    (tmp_path / "events.jsonl").write_text(
        '{"event": "step-added", "actor": "add-ledger-step", "step": "' + line + '"}\n')
    recorded = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (missing[0], "repair the suite" in missing[2], recorded) == (1, True, (0, "", ""))


def test_2130_recorded_added_lines_past_veri_step_growth_exit_1_and_a_malformed_veri_step_growth_exits_2(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    lines = ["- [ ] first inserted step ⟦added⟧ ⟦criterion 1⟧", "- [ ] second inserted step ⟦added⟧ ⟦criterion 1⟧"]
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + "\n".join(lines) + "\n")
    (tmp_path / "events.jsonl").write_text("".join(
        '{"event": "step-added", "actor": "add-ledger-step", "step": "' + line + '"}\n' for line in lines))
    args = [str(plan), str(ledger)]
    within = run_cli(ledger_growth, args, env={"VERI_STEP_GROWTH": "2"})
    past = run_cli(ledger_growth, args, env={"VERI_STEP_GROWTH": "1"})
    malformed = [run_cli(ledger_growth, args, env={"VERI_STEP_GROWTH": value})[0] for value in ("many", "-1", "")]
    assert (within, past[0], malformed) == ((0, "", ""), 1, [2, 2, 2])


def test_2130_a_record_covers_a_ledger_line_only_by_equal_step_text_never_by_substring(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    recorded = "- [ ] fix the suite: x ⟦suite-repair⟧ ⟦criterion 1⟧"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] fix the suite\n- [ ] x ⟦suite-repair⟧ ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").write_text(
        '{"event": "step-added", "actor": "add-ledger-step", "step": "' + recorded + '"}\n')
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    named = [line for line in err.splitlines()
             if line.endswith(": fix the suite") or line.endswith(": x ⟦suite-repair⟧ ⟦criterion 1⟧")]
    assert (code, out, len(named)) == (1, "", 2)


def test_2130_an_added_line_recorded_in_the_tracked_added_file_still_exits_0_with_events_jsonl_deleted(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    line = "- [ ] a inserted step ⟦added⟧ ⟦criterion 1⟧"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + line + "\n")
    (tmp_path / "issue-42-added.md").write_text(line + "\n")
    assert not (tmp_path / "events.jsonl").exists()
    assert run_cli(ledger_growth, [str(plan), str(ledger)]) == (0, "", "")


def test_2130_plan_sha_prints_the_newest_plan_scope_or_rewrite_commit_and_exits_2_when_there_is_none(run_cli, ledger_growth):
    log = (
        f"{'e' * 40} plan: replace step 2\n"
        f"{'d' * 40} plan: split step 1\n"
        f"{'c' * 40} plan: rewrite after verify-plan REJECT\n"
        f"{'b' * 40} plan: scope #42\n"
        f"{'a' * 40} chore: unrelated\n"
    )
    newest = run_cli(ledger_growth, ["plan-sha"], stdin=log)
    none = run_cli(ledger_growth, ["plan-sha"], stdin=f"{'a' * 40} plan: split step 1\n")
    assert (newest, none[0]) == ((0, "c" * 40 + "\n", ""), 2)


def test_2130_an_unreadable_ledger_exits_2_naming_the_file_on_stderr(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    missing = tmp_path / "issue-42.md"
    code, out, err = run_cli(ledger_growth, [str(plan), str(missing)])
    assert (code, out, str(missing) in err) == (2, "", True)


def test_2130_an_unreadable_plan_ledger_file_exits_2_naming_it_never_exit_1(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    plan.mkdir()
    ledger = tmp_path / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, str(plan) in err) == (2, "", True)


def test_2209_a_directory_in_the_place_of_the_added_record_file_exits_2_naming_it_never_exit_1(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a inserted step ⟦added⟧ ⟦criterion 1⟧\n")
    (tmp_path / "issue-42-added.md").mkdir()
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "issue-42-added.md" in err) == (2, "", True)


def test_2209_a_directory_in_the_place_of_events_jsonl_exits_2_naming_it_never_exit_1(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a inserted step ⟦added⟧ ⟦criterion 1⟧\n")
    (tmp_path / "events.jsonl").mkdir()
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "events.jsonl" in err) == (2, "", True)


def test_2209_with_neither_the_added_record_file_nor_events_jsonl_present_a_new_step_without_added_exits_1_naming_it_never_2(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a sneaked in step ⟦criterion 1⟧\n")
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "a sneaked in step" in err) == (1, "", True)


def test_2209_no_arguments_exits_2_and_the_usage_line_names_the_plan_sha_subcommand(run_cli, ledger_growth):
    code, out, err = run_cli(ledger_growth, [])
    assert (code, out, "plan-sha" in err) == (2, "", True)


def test_2351_a_step_reworded_in_a_plan_rewrite_commit_is_the_baseline_and_passes_the_growth_check(
        tmp_path, run_cli, ledger_growth):
    log = (
        f"{'c' * 40} plan: rewrite step 2 on the coordinator's ruling (#42)\n"
        f"{'b' * 40} plan: scope #42\n"
    )
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    reworded = "- [ ] step 2's red cases leak through mkdir, so every guard is pinned ⟦criterion 2⟧"
    plan.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n" + reworded + "\n")
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + reworded + "\n")
    baseline = run_cli(ledger_growth, ["plan-sha"], stdin=log)
    growth = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (baseline, growth) == ((0, "c" * 40 + "\n", ""), (0, "", ""))


def test_3439_steps_a_verify_plan_rewrite_added_are_recorded_by_record_rewrite_and_a_later_hand_step_still_exits_1(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    pre = tmp_path / "pre-rewrite.md"
    ledger = tmp_path / "issue-42.md"
    head = "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    pre.write_text(head + "- [ ] one broad step ⟦added⟧ ⟦criterion 1⟧\n")
    (tmp_path / "issue-42-added.md").write_text("- [ ] one broad step ⟦added⟧ ⟦criterion 1⟧\n")
    ledger.write_text(
        head + "- [ ] landed lines ⟦added⟧ ⟦criterion 1⟧\n- [ ] waiting bail lines ⟦added⟧ ⟦criterion 1⟧\n")
    run_cli(ledger_growth, ["record-rewrite", str(pre), str(ledger)])
    assert run_cli(ledger_growth, [str(plan), str(ledger)]) == (0, "", "")
    ledger.write_text(ledger.read_text() + "- [ ] a hand step ⟦added⟧ ⟦criterion 1⟧\n")
    assert run_cli(ledger_growth, [str(plan), str(ledger)]) == (
        1, "", "ledger-growth.sh: step added without an add-ledger-step.sh record: a hand step ⟦added⟧ ⟦criterion 1⟧\n")


def test_3439_record_rewrite_keeps_earlier_records_adds_only_steps_the_pre_rewrite_file_lacked_and_exits_2_when_the_records_file_cannot_be_written(
        tmp_path, run_cli, ledger_growth):
    pre = tmp_path / "pre-rewrite.md"
    ledger = tmp_path / "issue-42.md"
    records = tmp_path / "issue-42-added.md"
    pre.write_text("# Plan for #42\n\n- [ ] kept step ⟦added⟧ ⟦criterion 1⟧\n")
    records.write_text("- [ ] earlier record ⟦added⟧ ⟦criterion 1⟧\n")
    ledger.write_text("# Plan for #42\n\n- [ ] kept step ⟦added⟧ ⟦criterion 1⟧\n"
                      "- [ ] fresh step ⟦added⟧ ⟦criterion 1⟧\n")
    code = run_cli(ledger_growth, ["record-rewrite", str(pre), str(ledger)])[0]
    assert (code, records.read_text()) == (0, "- [ ] earlier record ⟦added⟧ ⟦criterion 1⟧\n"
                                              "- [ ] fresh step ⟦added⟧ ⟦criterion 1⟧\n")
    blocked = tmp_path / "blocked"
    (blocked / "issue-43-added.md").mkdir(parents=True)
    (blocked / "issue-43.md").write_text("# Plan for #43\n\n- [ ] fresh step ⟦added⟧ ⟦criterion 1⟧\n")
    code, out, err = run_cli(ledger_growth, ["record-rewrite", str(pre), str(blocked / "issue-43.md")])
    assert (code, out, err.startswith(f"ledger-growth.sh: {blocked / 'issue-43-added.md'}: ")) == (2, "", True)


def test_3439_record_rewrite_appends_no_line_for_a_step_an_existing_record_covers_and_records_the_new_step(
        tmp_path, run_cli, ledger_growth):
    pre = tmp_path / "pre-rewrite.md"
    ledger = tmp_path / "issue-42.md"
    records = tmp_path / "issue-42-added.md"
    pre.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    records.write_text("- [ ] covered step ⟦added⟧ ⟦criterion 1⟧\n")
    ledger.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n"
                      "- [ ] covered step ⟦added⟧ ⟦criterion 1⟧\n- [ ] new step ⟦added⟧ ⟦criterion 1⟧\n")
    code = run_cli(ledger_growth, ["record-rewrite", str(pre), str(ledger)])[0]
    assert (code, records.read_text()) == (0, "- [ ] covered step ⟦added⟧ ⟦criterion 1⟧\n"
                                              "- [ ] new step ⟦added⟧ ⟦criterion 1⟧\n")


def test_3427_reopen_unticks_a_passed_skill_edit_step_with_the_change_and_added_mark_and_records_it(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [x] ⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 ⟦criterion 2⟧ ⟂ refactor pending\n")
    code, out, err = run_cli(ledger_growth, [
        "reopen", str(ledger), "regrade `skills/tdd/SCRIPTS.md`", "extend it with the reopen"])
    step = ("⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 change: extend it with the reopen"
            " ⟦added⟧ ⟦criterion 2⟧")
    added = tmp_path / "issue-42-added.md"
    assert (code, ledger.read_text(), added.read_text() if added.exists() else None) == (
        0,
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n- [ ] " + step + "\n",
        "- [ ] " + step + "\n")


def test_3427_reopen_on_an_unreadable_ledger_exits_2_naming_the_ledger_file_on_stderr(
        tmp_path, run_cli, ledger_growth):
    missing = tmp_path / "issue-42.md"
    code, out, err = run_cli(ledger_growth, ["reopen", str(missing), "regrade", "a change"])
    assert (code, out, str(missing) in err, (tmp_path / "issue-42-added.md").exists()) == (2, "", True, False)


def test_3427_reopen_skips_header_and_prose_lines_holding_the_needle_and_reopens_the_step_line(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42: regrade the scripts doc\n\nWe regrade it after review.\n"
        "- [x] ⟦skill-edit⟧ regrade the doc ⟦criterion 1⟧ ⟂ refactor pending\n")
    code = run_cli(ledger_growth, ["reopen", str(ledger), "regrade", "a change"])[0]
    assert (code, ledger.read_text()) == (
        0,
        "# Plan for #42: regrade the scripts doc\n\nWe regrade it after review.\n"
        "- [ ] ⟦skill-edit⟧ regrade the doc change: a change ⟦added⟧ ⟦criterion 1⟧\n")


def test_3427_reopen_of_a_passed_skill_edit_step_already_marked_added_keeps_exactly_one_added_mark(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42\n\n"
        "- [x] ⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 ⟦added⟧ ⟦criterion 2⟧ ⟂ refactor pending\n")
    code = run_cli(ledger_growth, ["reopen", str(ledger), "regrade", "extend it"])[0]
    step = "⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 change: extend it ⟦added⟧ ⟦criterion 2⟧"
    added = tmp_path / "issue-42-added.md"
    assert (code, ledger.read_text(), added.read_text() if added.exists() else None) == (
        0, "# Plan for #42\n\n- [ ] " + step + "\n", "- [ ] " + step + "\n")


def test_3427_reopen_of_a_passed_plain_step_exits_2_naming_the_step_and_leaves_the_ledger_untouched(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    text = "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
    ledger.write_text(text)
    code, out, err = run_cli(ledger_growth, ["reopen", str(ledger), "a cog exists", "a change"])
    assert (code, "a cog exists" in err, ledger.read_text(), (tmp_path / "issue-42-added.md").exists()) == (
        2, True, text, False)


def test_3427_reopen_with_no_step_matching_the_needle_exits_3_leaving_the_ledger_and_the_record_untouched(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    text = "# Plan for #42\n\n- [x] ⟦skill-edit⟧ regrade the doc ⟦criterion 1⟧ ⟂ refactor pending\n"
    ledger.write_text(text)
    code = run_cli(ledger_growth, ["reopen", str(ledger), "no such step", "a change"])[0]
    assert (code, ledger.read_text(), (tmp_path / "issue-42-added.md").exists()) == (3, text, False)


def test_3427_after_a_reopen_of_a_passed_skill_edit_step_the_growth_check_against_the_original_plan_exits_0_silently(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text(
        "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n"
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 ⟦criterion 2⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [x] ⟦skill-edit⟧ regrade `skills/tdd/SCRIPTS.md` against A1 ⟦criterion 2⟧ ⟂ refactor pending\n")
    reopened = run_cli(ledger_growth, ["reopen", str(ledger), "regrade", "extend it with the reopen"])[0]
    assert (reopened, run_cli(ledger_growth, [str(plan), str(ledger)])) == (0, (0, "", ""))
