"""In-process cases for veri/parse_verdict.py, the module parse-verdict.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def parse_verdict():
    return importlib.import_module("veri.parse_verdict")


def test_main_returns_2_naming_an_unrecognised_verdict_word_with_nothing_on_stdout(monkeypatch, capsys, parse_verdict):
    monkeypatch.setattr(sys, "stdin", io.StringIO("VERDICT: MAYBE\nREASON: unsure"))

    code = parse_verdict.main([])
    out, err = capsys.readouterr()

    assert (code, out, err) == (2, "", "parse-verdict: unrecognised verdict word 'MAYBE'\n")
