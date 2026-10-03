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


def test_main_writes_the_result_text_unescaped_with_its_newlines_and_quotes_and_the_last_record_winning(
        monkeypatch, capsys, extract_result):
    streams = {
        "extracts result text": (
            [{"type": "system", "subtype": "init", "session_id": "x"},
             {"type": "assistant", "message": {"content": [{"type": "text", "text": "VERDICT: PASS"}]}},
             {"type": "result", "subtype": "success", "is_error": False, "result": "VERDICT: PASS"}],
            "VERDICT: PASS\n"),
        "multiline result unescaped": (
            [{"type": "system", "subtype": "init"},
             {"type": "result", "subtype": "success",
              "result": "VERDICT: REJECT\nREASON: asserts an internal helper, not behavior."}],
            "VERDICT: REJECT\nREASON: asserts an internal helper, not behavior.\n"),
        "escaped quotes survive": (
            [{"type": "result", "result": 'VERDICT: REJECT\nREASON: the test calls slugify("a") wrongly.'}],
            'VERDICT: REJECT\nREASON: the test calls slugify("a") wrongly.\n'),
        "last result wins": (
            [{"type": "result", "result": "first"}, {"type": "result", "result": "second"}],
            "second\n"),
    }
    seen = {}
    for name, (records, _) in streams.items():
        fake_stdin(monkeypatch, "\n".join(json.dumps(r) for r in records))
        code = extract_result.main([])
        seen[name] = (code, capsys.readouterr().out)
    assert seen == {name: (0, expected) for name, (_, expected) in streams.items()}
