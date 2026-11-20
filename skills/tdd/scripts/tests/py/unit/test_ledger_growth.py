"""In-process cases for veri/ledger_growth.py, the module ledger-growth.sh is a shim over."""
import importlib
import json

import pytest


# A cap no case below reaches: three ⟦added⟧ steps over a one-step plan.
ROOMY = {"VERI_STEP_GROWTH_PERCENT": "300"}


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


def test_4075_added_lines_are_capped_at_the_percent_of_the_plan_steps_rounded_up_and_a_refused_percent_exits_2(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    planned = ["- [ ] a cog exists ⟦criterion 1⟧", "- [ ] a gear turns ⟦criterion 1⟧", "- [ ] a lamp glows ⟦criterion 1⟧"]
    plan.write_text("# Plan for #42\n\n" + "\n".join(planned) + "\n")
    added = ["- [ ] inserted step %d ⟦added⟧ ⟦criterion 1⟧" % i for i in (1, 2, 3)]
    (tmp_path / "issue-42-added.md").write_text("\n".join(added) + "\n")

    def check(count, env=None):
        ledger.write_text("# Plan for #42\n\n" + "\n".join(planned + added[:count]) + "\n")
        return run_cli(ledger_growth, [str(plan), str(ledger)], env=env)

    at_cap, past = check(2), check(3)
    refused = [check(2, {"VERI_STEP_GROWTH_PERCENT": value})[0] for value in ("many", "-1", "")]
    doubled = check(3, {"VERI_STEP_GROWTH_PERCENT": "100"})

    assert (at_cap, past[0], "VERI_STEP_GROWTH_PERCENT" in past[2], refused, doubled) == (
        (0, "", ""), 1, True, [2, 2, 2], (0, "", ""))


def test_4075_a_set_retired_veri_step_growth_exits_2_naming_veri_step_growth_percent(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n")

    got = [run_cli(ledger_growth, [str(plan), str(ledger)], env={"VERI_STEP_GROWTH": value}) for value in ("5", "")]

    assert [(code, out, "VERI_STEP_GROWTH_PERCENT" in err) for code, out, err in got] == [(2, "", True)] * 2


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
    assert run_cli(ledger_growth, [str(plan), str(ledger)], env=ROOMY) == (0, "", "")
    ledger.write_text(ledger.read_text() + "- [ ] a hand step ⟦added⟧ ⟦criterion 1⟧\n")
    assert run_cli(ledger_growth, [str(plan), str(ledger)], env=ROOMY) == (
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


def test_3427_reopen_with_a_needle_matching_two_steps_exits_2_naming_both_and_changes_nothing(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    text = ("# Plan for #42\n\n"
            "- [x] ⟦skill-edit⟧ regrade the doc ⟦criterion 1⟧ ⟂ refactor pending\n"
            "- [x] ⟦skill-edit⟧ regrade the scripts ⟦criterion 2⟧ ⟂ refactor pending\n")
    ledger.write_text(text)
    code, out, err = run_cli(ledger_growth, ["reopen", str(ledger), "regrade", "a change"])
    assert (code, "regrade the doc" in err, "regrade the scripts" in err, ledger.read_text(),
            (tmp_path / "issue-42-added.md").exists()) == (2, True, True, text, False)


def test_3427_reopen_of_an_unticked_skill_edit_step_exits_3_and_appends_no_added_record(
        tmp_path, run_cli, ledger_growth):
    ledger = tmp_path / "issue-42.md"
    text = "# Plan for #42\n\n- [ ] ⟦skill-edit⟧ regrade the doc ⟦criterion 1⟧\n"
    ledger.write_text(text)
    code = run_cli(ledger_growth, ["reopen", str(ledger), "regrade", "a change"])[0]
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


def reworded_lines(run):
    """The `step-reworded` lines of the event log under <run>/.tdd, as (from, to, issue)."""
    log = run / ".tdd" / "events.jsonl"
    lines = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return [(line["from"], line["to"], line["issue"]) for line in lines if line["event"] == "step-reworded"]


def test_4226_record_rewrite_writes_one_step_reworded_per_position_whose_step_text_differs_when_the_counts_match(
        tmp_path, run_cli, ledger_growth):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    pre = tmp_path / "pre-rewrite.md"
    ledger = run / ".tdd" / "issue-42.md"
    pre.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [ ] a broad step ⟦criterion 2⟧\n"
                   "- [ ] kept as is ⟦criterion 2⟧\n- [ ] another broad step ⟦criterion 3⟧\n")
    ledger.write_text("# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [ ] a narrow step ⟦criterion 2⟧\n"
                      "- [ ] kept as is ⟦criterion 2⟧\n- [ ] another narrow step ⟦criterion 3⟧\n")

    code = run_cli(ledger_growth, ["record-rewrite", str(pre), str(ledger)])[0]

    assert (code, reworded_lines(run)) == (0, [
        ("a broad step ⟦criterion 2⟧", "a narrow step ⟦criterion 2⟧", "42"),
        ("another broad step ⟦criterion 3⟧", "another narrow step ⟦criterion 3⟧", "42")])


def test_4226_record_rewrite_writes_no_step_reworded_when_the_step_counts_differ_and_exits_as_before(
        tmp_path, run_cli, ledger_growth):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    pre = tmp_path / "pre-rewrite.md"
    ledger = run / ".tdd" / "issue-42.md"
    pre.write_text("# Plan for #42\n\n- [ ] a broad step ⟦criterion 1⟧\n- [ ] kept as is ⟦criterion 2⟧\n")
    ledger.write_text("# Plan for #42\n\n- [ ] a narrow step ⟦criterion 1⟧\n- [ ] its twin ⟦criterion 1⟧\n"
                      "- [ ] kept as is ⟦criterion 2⟧\n")

    code = run_cli(ledger_growth, ["record-rewrite", str(pre), str(ledger)])

    assert (code, reworded_lines(run)) == ((0, "", ""), [])


SCOPED = "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"


def split_history(fake_processes, scoped=SCOPED):
    """git answers for `split`: the ledger's history holds two `plan: scope` commits and a rewrite; only the oldest
    scope commit's ledger may be read."""
    log = ("bbb plan: rewrite #42 after verify-plan (#42)\nddd green: a cog (#42)\n"
           "eee plan: scope #42 into 9 steps (#42)\nccc plan: scope #42 into 2 steps (#42)\n")
    return fake_processes.answers({"git log": (0, log, ""), "git show ccc:./issue-42.md": (0, scoped, "")})


def test_4251_split_exits_0_naming_the_growth_past_the_bound_counted_from_the_oldest_scope_commit(
        tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a wheel turns, rewritten ⟦criterion 2⟧\n- [ ] a gear meshes ⟦added⟧ ⟦criterion 2⟧\n"
        "- [ ] a third part ⟦criterion 2⟧\n"
        "- [ ] fix the full-suite failure: x — FAIL - y ⟦suite-repair⟧\n- [ ] fix the CI failure: z ⟦ci-repair⟧\n")

    code, out, err = run_cli(ledger_growth, ["split", str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "50"})

    assert (code, out.split("\n")[0], err) == (
        0, "plan grew from 2 to 4 steps, past the growth bound of 1 (VERI_STEP_GROWTH_PERCENT 50% of 2, rounded up)", "")


def test_4251_split_exits_3_printing_nothing_when_the_growth_equals_the_bound(
        tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
        "- [ ] a gear meshes ⟦added⟧ ⟦criterion 2⟧\n- [ ] fix the CI failure: z ⟦ci-repair⟧\n")

    assert run_cli(ledger_growth, ["split", str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "50"}) == (3, "", "")


def test_4472_split_exits_3_when_a_branch_repair_step_is_the_only_step_past_the_bound(
        tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n"
        "- [ ] a gear meshes ⟦added⟧ ⟦criterion 2⟧\n- [ ] fix the branch: z ⟦diff-checked⟧ ⟦branch-repair⟧ ⟦criterion 2⟧\n")

    assert run_cli(ledger_growth, ["split", str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "50"}) == (3, "", "")


def split_second_line(directory, run_cli, ledger_growth, criteria):
    """The second stdout line of `split` over a ledger holding one step per entry of criteria (None: untagged), and a
    repair line that serves criterion 1; the case answers git with split_history."""
    directory.mkdir(exist_ok=True)
    ledger = directory / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n" + "".join(
        f"- [ ] step {i}" + (f" ⟦criterion {k}⟧" if k else "") + "\n" for i, k in enumerate(criteria))
        + "- [ ] fix the full-suite failure: x ⟦suite-repair⟧ ⟦criterion 1⟧\n")
    code, out, err = run_cli(ledger_growth, ["split", str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "0"})
    assert (code, err, len(out.split("\n"))) == (0, "", 3)
    return out.split("\n")[1]


def test_4251_split_suggests_the_criterion_boundary_leaving_the_two_sides_closest(
        tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)

    line = split_second_line(tmp_path, run_cli, ledger_growth, [1, 3, 3, 5, 5, 5, None, None])

    assert line == ("split suggested after criterion 3: criteria 1–3 (3 steps) here,"
                    " criteria 5–5 (3 steps) in a follow-up issue")


def test_4251_split_takes_the_earlier_boundary_on_a_tie(tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)

    line = split_second_line(tmp_path, run_cli, ledger_growth, [1, 1, 2, 3, 3])

    assert line == ("split suggested after criterion 1: criteria 1–1 (2 steps) here,"
                    " criteria 2–3 (3 steps) in a follow-up issue")


def test_4251_split_names_no_split_point_with_one_criterion_or_none(tmp_path, run_cli, ledger_growth, fake_processes):
    split_history(fake_processes)

    one = split_second_line(tmp_path / "one", run_cli, ledger_growth, [2, 2, None])
    none = split_second_line(tmp_path / "none", run_cli, ledger_growth, [None, None, None])

    assert (one, none) == ("no split point: every counted step serves criterion 2", "no split point: no criterion tag")


GROWN = "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n- [ ] a wheel turns ⟦criterion 2⟧\n- [ ] a gear ⟦criterion 2⟧\n"


@pytest.mark.parametrize("argv, env, git_answers, names", [
    (["split"], {}, {}, "usage"),
    (["split", "{ledger}", "extra"], {}, {}, "usage"),
    (["split", "{missing}"], {}, {}, "missing.md"),
    (["split", "{ledger}"], {}, {"git log": (0, "bbb plan: rewrite #42 (#42)\nddd green: a cog (#42)\n", "")},
     "no plan: scope commit"),
    (["split", "{ledger}"], {}, {"git log": (128, "", "fatal: not a git repository\n")}, "not a git repository"),
    (["split", "{ledger}"], {}, {"git log": (0, "ccc plan: scope #42 (#42)\n", ""),
                                 "git show": (128, "", "fatal: path not in ccc\n")}, "path not in ccc"),
    (["split", "{ledger}"], {"VERI_STEP_GROWTH_PERCENT": "half"}, {}, "VERI_STEP_GROWTH_PERCENT"),
    (["split", "{ledger}"], {"VERI_STEP_GROWTH_PERCENT": "-1"}, {}, "VERI_STEP_GROWTH_PERCENT"),
    (["split", "{ledger}"], {"VERI_STEP_GROWTH": "3"}, {}, "VERI_STEP_GROWTH_PERCENT"),
])
def test_4251_split_exits_2_with_nothing_on_stdout_and_one_stderr_line_when_no_answer_can_be_had(
        tmp_path, run_cli, ledger_growth, fake_processes, argv, env, git_answers, names):
    fake = fake_processes.answers(git_answers)
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(GROWN)
    paths = {"ledger": str(ledger), "missing": str(tmp_path / "missing.md")}

    code, out, err = run_cli(ledger_growth, [arg.format(**paths) for arg in argv], env=env)

    assert (code, out, err.count("\n"), err.endswith("\n"), names in err) == (2, "", 1, True, True), (err, fake.calls)
