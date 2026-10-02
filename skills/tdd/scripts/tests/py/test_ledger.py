"""In-process cases for veri/ledger.py, the ledger reader lib/ledger.sh's ledger_steps defines in bash."""
import importlib
import pathlib
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_ledger_steps_returns_the_records_lib_ledger_sh_prints():
    text = (
        "# Plan for #9 — cogs mesh\n"
        "\n"
        "- [x] a cog exists ⟦criterion 1⟧\n"
        "- [X] two cogs mesh ⟦criterion 2⟧ ⟂ refactor pending\n"
        "- [ ] a cog turns ⟦full-suite⟧ ⟦criterion 2⟧\n"
        "  - [ ] a gear slips ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending\n"
        "not a step - [ ] at all\n"
        "- [ ] the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 4⟧\n"
        "- [ ] a note with no criterion"
    )

    ledger = importlib.import_module("veri.ledger")

    assert [tuple(record) for record in ledger.ledger_steps(text)] == [
        ("1", "done", "step", "0", "0", "1", "a cog exists ⟦criterion 1⟧"),
        ("2", "done", "step", "1", "0", "2", "two cogs mesh ⟦criterion 2⟧"),
        ("3", "open", "full-suite", "0", "0", "2", "a cog turns ⟦full-suite⟧ ⟦criterion 2⟧"),
        ("4", "open", "step", "0", "1", "3", "a gear slips ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending"),
        ("5", "open", "human-owed", "0", "0", "4", "the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 4⟧"),
        ("6", "open", "step", "0", "0", "", "a note with no criterion"),
    ]
