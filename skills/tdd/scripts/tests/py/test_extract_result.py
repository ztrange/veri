"""In-process cases for veri/extract_result.py, the module extract-result.sh is a shim over."""
import importlib
import io
import json
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def extract_result():
    return importlib.import_module("veri.extract_result")


def fake_stdin(monkeypatch, text):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(text.encode())))


def test_main_on_a_stream_whose_result_record_carries_verdict_pass_writes_it_with_a_newline_and_returns_0(
        monkeypatch, capsys, extract_result):
    fake_stdin(monkeypatch, json.dumps({"type": "system", "subtype": "init"}) + "\n"
               + json.dumps({"type": "result", "subtype": "success", "result": "VERDICT: PASS"}) + "\n")
    code = extract_result.main([])
    assert (code, capsys.readouterr().out) == (0, "VERDICT: PASS\n")
