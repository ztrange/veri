"""In-process cases for veri/scope_check.py, the module scope-check.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def scope_check():
    return importlib.import_module("veri.scope_check")


def test_2222_a_step_with_two_criterion_tags_is_refused_with_exit_1_naming_the_step(
    tmp_path, run_cli, scope_check
):
    ledger = tmp_path / "issue-2222.md"
    ledger.write_text(
        "- [ ] fine step ⟦criterion 1⟧\n"
        "- [ ] greedy step ⟦criterion 2⟧ ⟦criterion 3⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 1
    assert "greedy step" in err
    assert "more than one criterion tag" in err


def test_2222_a_ledger_with_at_most_one_criterion_tag_per_step_passes_silently(
    tmp_path, run_cli, scope_check
):
    ledger = tmp_path / "issue-2222.md"
    ledger.write_text(
        "- [ ] first step ⟦criterion 1⟧\n"
        "- [ ] second step ⟦criterion 2⟧\n"
        "- [ ] gap step with no tag\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 0
    assert err == ""


def test_2749_a_passing_check_emits_a_plan_event_with_the_step_count_and_a_repeat_emits_another(
    tmp_path, run_cli, scope_check
):
    import json
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-2749.md"
    ledger.write_text(
        "- [ ] first step ⟦criterion 1⟧\n"
        "- [ ] second step ⟦criterion 2⟧\n"
        "- [ ] gap step with no tag\n",
        encoding="utf-8",
    )

    codes = [run_cli(scope_check, [str(ledger), str(tmp_path)])[0] for _ in range(2)]

    events = [json.loads(row) for row in (tdd / "events.jsonl").read_text().splitlines()]
    plans = [(e["event"], e["issue"], e["steps"]) for e in events]
    assert (codes, plans) == ([0, 0], [("plan", "2749", "3")] * 2)


def test_3509_a_skill_edit_step_whose_unit_has_no_requirements_heading_is_refused_with_exit_2_naming_it(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3509.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/PIN.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n"
        "- [ ] regrade `skills/tdd/SCRIPTS.md` ⟦skill-edit⟧ ⟦criterion 2⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3509-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert err == "scope-check.sh: no ### heading for skill-edit unit: skills/tdd/SCRIPTS.md\n"
    assert not (tdd / "events.jsonl").exists()


def test_3509_a_ledger_whose_every_skill_edit_unit_has_its_heading_or_new_heading_passes(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3509.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/PIN.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n"
        "- [ ] add `skills/tdd/SCRIPTS.md` ⟦skill-edit⟧ ⟦criterion 2⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3509-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "### skills/tdd/SCRIPTS.md (new)\n\n| a | b |\n|---|---|\n| 3 | 4 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3509_a_skill_edit_step_backticking_a_non_unit_token_after_its_unit_is_not_refused(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3509.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/PIN.md` with `--change` and `skills/tdd/scripts/x.py` ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3509-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3509_a_skill_edit_unit_whose_heading_sits_after_the_requirements_section_ends_is_refused_with_exit_2(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3509.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/PIN.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3509-spec.md").write_text(
        "## Requirements\n\n### other\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "## Notes\n\n### skills/tdd/PIN.md\n\nnot a requirement\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert "skills/tdd/PIN.md" in err
    assert not (tdd / "events.jsonl").exists()


def test_3636_a_skill_edit_step_whose_first_backticked_token_is_not_path_shaped_is_refused_naming_the_path_not_the_token(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3636.md"
    ledger.write_text(
        "- [ ] regrade with `--change` the file `skills/tdd/PIN.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3636-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/OTHER.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert "skills/tdd/PIN.md" in err
    assert "--change" not in err


def test_3636_a_skill_edit_step_whose_first_backticked_token_is_not_path_shaped_passes_when_the_path_has_its_heading(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3636.md"
    ledger.write_text(
        "- [ ] regrade with `--change` the file `skills/tdd/PIN.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3636-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3636_a_skill_edit_step_with_no_path_shaped_backticked_token_is_refused_with_exit_2_naming_the_step(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3636.md"
    ledger.write_text(
        "- [ ] tighten `unit_of` wording ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3636-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert "tighten `unit_of` wording" in err


def test_3636_a_skill_edit_step_with_no_path_shaped_token_is_refused_on_its_own_not_as_a_missing_none_heading(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3636.md"
    ledger.write_text(
        "- [ ] tighten `unit_of` wording ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3636-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert err == ("scope-check.sh: no path-shaped unit for skill-edit step: "
                   "tighten `unit_of` wording ⟦skill-edit⟧ ⟦criterion 1⟧\n")
    assert "unit: None" not in err


def test_3710_a_step_without_the_skill_edit_tag_is_not_refused_though_its_unit_has_no_heading(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-3710.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/SCRIPTS.md` ⟦criterion 1⟧\n"
        "- [ ] tighten `unit_of` wording ⟦criterion 2⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-3710-spec.md").write_text(
        "## Requirements\n\n### skills/tdd/PIN.md\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def _signed_units_repo(tmp_path):
    """A repo whose skills/tdd/REQUIREMENTS.md lists two units, each with a GRADED line beside it."""
    tdd_skill = tmp_path / "skills" / "tdd"
    tdd_skill.mkdir(parents=True)
    (tdd_skill / "REQUIREMENTS.md").write_text(
        "## skills/tdd/PIN.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PIN1 | pins a thing | so it stays |\n\n"
        "## skills/tdd/OTHER.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| OTH1 | says another thing | so it is said |\n",
        encoding="utf-8",
    )
    (tdd_skill / "GRADED").write_text(
        "skills/tdd/PIN.md aaaa 2026-11-17 g1 p1\n"
        "skills/tdd/OTHER.md bbbb 2026-11-17 g2 p2\n",
        encoding="utf-8",
    )
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    return tdd


PLAIN_ROW_MOVE = "move row PIN1 out into `skills/tdd/scripts/x.py` ⟦criterion 1⟧"


def test_3302_a_plain_step_naming_a_row_of_a_unit_a_later_skill_edit_step_signs_is_refused_with_exit_1_naming_the_step_and_the_unit(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        f"- [ ] {PLAIN_ROW_MOVE}\n"
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/PIN.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 1
    assert PLAIN_ROW_MOVE in err
    assert "skills/tdd/PIN.md" in err
    assert not (tdd / "events.jsonl").exists()


def test_3302_a_plain_step_naming_a_row_of_a_unit_no_skill_edit_step_signs_passes_while_another_unit_is_signed(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        f"- [ ] {PLAIN_ROW_MOVE}\n"
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/OTHER.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3302_a_plain_step_naming_a_new_file_a_later_skill_edit_step_signs_as_its_unit_is_refused_with_exit_1_naming_the_step_and_the_unit(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    plain = "move the pin rows into a new `skills/tdd/NEW.md` ⟦criterion 1⟧"
    ledger.write_text(
        f"- [ ] {plain}\n"
        "- [ ] ⟦skill-edit⟧ sign `skills/tdd/NEW.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 1
    assert plain in err
    assert "skills/tdd/NEW.md" in err
    assert not (tdd / "events.jsonl").exists()


def test_3302_a_row_move_and_new_unit_file_named_only_inside_the_signing_skill_edit_steps_pass(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        "- [ ] tighten the plan check ⟦criterion 1⟧\n"
        "- [ ] ⟦skill-edit⟧ create `skills/tdd/NEW.md` holding row PIN1 moved from `skills/tdd/PIN.md` ⟦added⟧\n"
        "- [ ] ⟦skill-edit⟧ drop row PIN1 from `skills/tdd/PIN.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3302_a_plain_step_naming_a_row_of_an_unsigned_unit_a_later_skill_edit_step_regrades_passes(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    tdd_skill = tmp_path / "skills" / "tdd"
    with (tdd_skill / "REQUIREMENTS.md").open("a", encoding="utf-8") as listing:
        listing.write(
            "\n## skills/tdd/UNSIGNED.md\n\n"
            "| ID | Requirement | Why |\n|---|---|---|\n"
            "| UNS1 | says an unsigned thing | so it is said |\n"
        )
    (tdd_skill / "UNSIGNED.md").write_text("unsigned prose\n", encoding="utf-8")
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        "- [ ] move row UNS1 out into `skills/tdd/scripts/x.py` ⟦criterion 1⟧\n"
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/UNSIGNED.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3302_a_plain_step_naming_a_row_of_a_signed_unit_after_the_skill_edit_step_that_signs_it_passes(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/PIN.md` ⟦added⟧\n"
        f"- [ ] {PLAIN_ROW_MOVE}\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_3302_a_plain_step_naming_a_token_that_ends_in_a_signed_row_id_passes(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    ledger = tdd / "issue-3302.md"
    ledger.write_text(
        "- [ ] move row XPIN1 out into `skills/tdd/scripts/x.py` ⟦criterion 1⟧\n"
        "- [ ] ⟦skill-edit⟧ regrade `skills/tdd/PIN.md` ⟦added⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def _check(tmp_path, run_cli, scope_check, *steps, cwd=None):
    """Run scope-check over a ledger of steps in tmp_path's repo; return (code, err)."""
    ledger = tmp_path / ".tdd" / "issue-3302.md"
    ledger.write_text("".join(f"- [ ] {step}\n" for step in steps), encoding="utf-8")
    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)], cwd=cwd)
    return code, err


SIGN_PIN = "⟦skill-edit⟧ regrade `skills/tdd/PIN.md` ⟦added⟧"
SIGN_NEW = "⟦skill-edit⟧ sign `skills/tdd/NEW.md` ⟦added⟧"


def test_3302_a_plain_step_naming_a_longer_row_id_that_starts_with_a_signed_row_id_passes(
    tmp_path, run_cli, scope_check
):
    _signed_units_repo(tmp_path)

    result = _check(tmp_path, run_cli, scope_check, "move row PIN10 out ⟦criterion 1⟧", SIGN_PIN)

    assert result == (0, "")


def test_3302_a_row_id_is_matched_literally_not_as_a_pattern(tmp_path, run_cli, scope_check):
    _signed_units_repo(tmp_path)
    listing = tmp_path / "skills" / "tdd" / "REQUIREMENTS.md"
    listing.write_text(listing.read_text(encoding="utf-8").replace("PIN1", "P.1"), encoding="utf-8")

    result = _check(tmp_path, run_cli, scope_check, "move row PX1 out ⟦criterion 1⟧", SIGN_PIN)

    assert result == (0, "")


def test_3302_a_later_plain_step_backticking_a_signed_unit_does_not_count_as_signing_it(
    tmp_path, run_cli, scope_check
):
    _signed_units_repo(tmp_path)

    result = _check(tmp_path, run_cli, scope_check,
                    PLAIN_ROW_MOVE, "tidy `skills/tdd/PIN.md` wording ⟦criterion 2⟧")

    assert result == (0, "")


def test_3302_skill_edit_steps_with_no_unit_or_an_existing_unit_do_not_stop_a_later_one_being_checked(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    (tmp_path / "skills" / "tdd" / "OTHER.md").write_text("other prose\n", encoding="utf-8")

    result = _check(tmp_path, run_cli, scope_check,
                    "⟦skill-edit⟧ tighten `unit_of` wording ⟦added⟧",
                    "⟦skill-edit⟧ regrade `skills/tdd/OTHER.md` ⟦added⟧",
                    PLAIN_ROW_MOVE, SIGN_PIN, cwd=tdd)

    assert result == (1, "scope-check.sh: step names row PIN1 of signed unit skills/tdd/PIN.md, "
                         f"which a later skill-edit step signs: {PLAIN_ROW_MOVE}\n")


def test_3302_a_plain_step_naming_a_file_already_in_the_repo_that_a_later_skill_edit_step_regrades_passes(
    tmp_path, run_cli, scope_check
):
    tdd = _signed_units_repo(tmp_path)
    (tmp_path / "skills" / "tdd" / "EXISTING.md").write_text("prose\n", encoding="utf-8")

    result = _check(tmp_path, run_cli, scope_check,
                    "reword `skills/tdd/EXISTING.md` ⟦criterion 1⟧",
                    "⟦skill-edit⟧ regrade `skills/tdd/EXISTING.md` ⟦added⟧", cwd=tdd)

    assert result == (0, "")


@pytest.mark.parametrize("token", [
    "oldskills/tdd/NEW.md", ".skills/tdd/NEW.md", "docs/skills/tdd/NEW.md", "old-skills/tdd/NEW.md",
    "skills/tdd/NEW.mdx", "skills/tdd/NEW.md/part", "skills/tdd/NEW.md-old", "skills/tdd/NEWxmd",
])
def test_3302_a_plain_step_naming_a_longer_path_or_a_lookalike_of_a_new_unit_file_passes(
    tmp_path, run_cli, scope_check, token
):
    _signed_units_repo(tmp_path)

    result = _check(tmp_path, run_cli, scope_check, f"write `{token}` ⟦criterion 1⟧", SIGN_NEW)

    assert result == (0, "")


def test_3302_a_plain_step_creating_the_file_of_a_heading_unit_a_later_skill_edit_step_signs_is_refused(
    tmp_path, run_cli, scope_check
):
    _signed_units_repo(tmp_path)
    plain = "write `skills/tdd/NEW.md` ⟦criterion 1⟧"

    result = _check(tmp_path, run_cli, scope_check, plain, "⟦skill-edit⟧ sign `skills/tdd/NEW.md#Intro` ⟦added⟧")

    assert result == (1, "scope-check.sh: step creates skills/tdd/NEW.md, the unit skills/tdd/NEW.md#Intro "
                         f"a later skill-edit step signs: {plain}\n")


@pytest.mark.parametrize("listing", [
    None,
    "## skills/tdd/sub/DEEP.md\n\n| ID | Requirement |\n|---|---|\n| D1 | lacks its Why column |\n",
])
def test_3302_a_signed_unit_with_no_readable_rows_beside_it_refuses_no_plain_step(
    tmp_path, run_cli, scope_check, listing
):
    _signed_units_repo(tmp_path)
    sub = tmp_path / "skills" / "tdd" / "sub"
    sub.mkdir()
    (sub / "DEEP.md").write_text("deep prose\n", encoding="utf-8")
    if listing is not None:
        (sub / "REQUIREMENTS.md").write_text(listing, encoding="utf-8")
    with (tmp_path / "skills" / "tdd" / "GRADED").open("a", encoding="utf-8") as graded:
        graded.write("skills/tdd/sub/DEEP.md cccc 2026-11-17 g3 p3\n")

    result = _check(tmp_path, run_cli, scope_check,
                    "move row D1 out ⟦criterion 1⟧", "⟦skill-edit⟧ regrade `skills/tdd/sub/DEEP.md` ⟦added⟧")

    assert result == (0, "")


def test_3302_of_two_plain_steps_naming_a_signed_row_the_refusal_names_the_first(tmp_path, run_cli, scope_check):
    _signed_units_repo(tmp_path)
    second = "drop row PIN1 later ⟦criterion 2⟧"

    code, err = _check(tmp_path, run_cli, scope_check, PLAIN_ROW_MOVE, second, SIGN_PIN)

    assert (code, PLAIN_ROW_MOVE in err, second in err) == (1, True, False)


def test_3302_a_ledger_breaking_both_the_tag_and_the_row_move_rules_is_refused_for_its_tags_first(
    tmp_path, run_cli, scope_check
):
    _signed_units_repo(tmp_path)

    code, err = _check(tmp_path, run_cli, scope_check,
                       "move row PIN1 out ⟦criterion 1⟧ ⟦criterion 2⟧", SIGN_PIN)

    assert (code, "more than one criterion tag" in err, "signed unit" in err) == (1, True, False)


def test_4307_a_skill_edit_step_on_a_backticked_heading_unit_with_its_heading_is_not_refused(
    tmp_path, run_cli, scope_check
):
    unit = "skills/tdd/SKILL.md#Before the Red of a `⟦suite-repair⟧` step — is the suite still red?"
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-4307.md"
    ledger.write_text(f"- [ ] edit `{unit}` ⟦skill-edit⟧ ⟦criterion 1⟧\n", encoding="utf-8")
    (tdd / "issue-4307-spec.md").write_text(
        f"## Requirements\n\n### {unit}\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")


def test_4614_a_skill_edit_step_is_refused_with_exit_2_when_the_spec_has_no_requirements_section(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-4614.md"
    ledger.write_text(
        "- [ ] regrade `skills/tdd/SCRIPTS.md` ⟦skill-edit⟧ ⟦criterion 1⟧\n",
        encoding="utf-8",
    )
    (tdd / "issue-4614-spec.md").write_text("## What happened\n\nNo requirements here.\n", encoding="utf-8")

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
    assert err == "scope-check.sh: no ### heading for skill-edit unit: skills/tdd/SCRIPTS.md\n"
    assert not (tdd / "events.jsonl").exists()


def test_4614_a_ledger_without_a_skill_edit_step_passes_silently_when_the_spec_has_no_requirements_section(
    tmp_path, run_cli, scope_check
):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-4614.md"
    ledger.write_text("- [ ] pin the plain behaviour ⟦criterion 1⟧\n", encoding="utf-8")
    (tdd / "issue-4614-spec.md").write_text("## What happened\n\nNo requirements here.\n", encoding="utf-8")

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert (code, err) == (0, "")
