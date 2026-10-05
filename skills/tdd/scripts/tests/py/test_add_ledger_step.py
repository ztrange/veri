"""In-process cases for veri/add_ledger_step.py, the module add-ledger-step.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

USAGE = (
    "usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]\n"
)

LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] a one ⟦criterion 1⟧\n"
    "- [ ] b two ⟦criterion 2⟧\n"
    "- [ ] c three ⟦criterion 3⟧\n"
).encode()


@pytest.fixture
def add_ledger_step():
    return importlib.import_module("veri.add_ledger_step")


def test_main_refuses_bad_arguments_with_exit_2_and_inserts_after_the_anchor(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    for argv in ([], ["l.md", "after", "anchor"], ["l.md", "after", "", "t"]):
        code = add_ledger_step.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)

    code = add_ledger_step.main([str(ledger), "sideways", "b two", "t"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        2, "", "add-ledger-step.sh: position must be after, before or instead-of: sideways\n"
    )
    assert ledger.read_bytes() == LEDGER

    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    captured = capsys.readouterr()
    assert code == 0
    assert ledger.read_bytes().decode().split("\n")[3:5] == [
        "- [ ] b two ⟦criterion 2⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 2⟧",
    ]
