"""In-process cases for veri/scope_check.py, the module scope-check.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def scope_check():
    return importlib.import_module("veri.scope_check")


def test_2222_a_step_with_two_criterion_tags_is_refused_with_exit_2_naming_the_step(
    tmp_path, run_cli, scope_check
):
    ledger = tmp_path / "issue-2222.md"
    ledger.write_text(
        "- [ ] fine step ⟦criterion 1⟧\n"
        "- [ ] greedy step ⟦criterion 2⟧ ⟦criterion 3⟧\n",
        encoding="utf-8",
    )

    code, _, err = run_cli(scope_check, [str(ledger), str(tmp_path)])

    assert code == 2
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
