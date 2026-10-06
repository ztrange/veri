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
