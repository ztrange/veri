"""In-process cases for veri/criterion_finished.py, the module criterion-finished.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: criterion-finished.sh <k> < .tdd/issue-<n>.md\n"


@pytest.fixture
def criterion_finished():
    return importlib.import_module("veri.criterion_finished")


def fake_stdin(monkeypatch, data):
    stdin = io.TextIOWrapper(io.BytesIO(data))
    monkeypatch.setattr(sys, "stdin", stdin)
    return stdin


def test_main_refuses_a_missing_or_empty_argument_with_its_usage_and_answers_0_or_3_for_one_step(
    monkeypatch, capsys, criterion_finished
):
    for argv in ([], [""]):
        ledger = b"- [x] a \xe2\x9f\xa6criterion 1\xe2\x9f\xa7\n"
        stdin = fake_stdin(monkeypatch, ledger)
        code = criterion_finished.main(argv)
        assert (argv, code, capsys.readouterr()) == (argv, 2, ("", USAGE))
        assert stdin.buffer.read() == ledger

    answers = {}
    for name, ledger in {
        "ticked": "- [x] a ⟦criterion 1⟧\n",
        "unticked": "- [ ] a ⟦criterion 1⟧\n",
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main(["1"])
    assert answers == {"ticked": 0, "unticked": 3}
    assert all(code in range(4) for code in answers.values())


def test_main_answers_for_criterion_k_alone(monkeypatch, criterion_finished):
    answers = {}
    for name, (k, ledger) in {
        "2 over a ticked criterion-1 step": ("2", "- [x] a ⟦criterion 1⟧\n"),
        "1 beside an open criterion-2 step": (
            "1",
            "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n",
        ),
        "1 over a refactor-pending criterion-1 step": (
            "1",
            "- [x] a ⟦criterion 1⟧ ⟂ refactor pending\n",
        ),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main([k])
    assert answers == {
        "2 over a ticked criterion-1 step": 3,
        "1 beside an open criterion-2 step": 0,
        "1 over a refactor-pending criterion-1 step": 3,
    }


def test_main_compares_k_to_each_criterion_as_a_string_and_ignores_extra_arguments(
    monkeypatch, criterion_finished
):
    answers = {}
    for name, (argv, ledger) in {
        "01 over criterion 1": (["01"], "- [x] a ⟦criterion 1⟧\n"),
        "01 over criterion 01": (["01"], "- [x] a ⟦criterion 01⟧\n"),
        "1 over criterion 01": (["1"], "- [x] a ⟦criterion 01⟧\n"),
        "'1 ' over criterion 1": (["1 "], "- [x] a ⟦criterion 1⟧\n"),
        "* over criterion 1": (["*"], "- [x] a ⟦criterion 1⟧\n"),
        "1 over full-width criterion": (["1"], "- [x] a ⟦criterion １⟧\n"),
        "full-width over full-width criterion": (["１"], "- [x] a ⟦criterion １⟧\n"),
        "1 junk over ticked criterion 1": (["1", "junk"], "- [x] a ⟦criterion 1⟧\n"),
        "1 junk over open criterion 1": (["1", "junk"], "- [ ] a ⟦criterion 1⟧\n"),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main(argv)
    assert answers == {
        "01 over criterion 1": 3,
        "01 over criterion 01": 0,
        "1 over criterion 01": 3,
        "'1 ' over criterion 1": 3,
        "* over criterion 1": 3,
        "1 over full-width criterion": 3,
        "full-width over full-width criterion": 3,
        "1 junk over ticked criterion 1": 0,
        "1 junk over open criterion 1": 3,
    }
