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
    assert "skills/tdd/SCRIPTS.md" in err
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


def test_3509_a_skill_edit_ledger_passes_when_the_spec_has_no_requirements_section(
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
        "## What happened\n\nnothing about requirements\n",
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
    assert "tighten `unit_of` wording" in err
    assert "unit: None" not in err
