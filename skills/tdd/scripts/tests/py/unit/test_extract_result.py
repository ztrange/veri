"""In-process cases for veri/extract_result.py, the module extract-result.sh is a shim over."""
import importlib
import io
import json
import sys

import pytest


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


def test_main_prefers_the_newest_record_carrying_a_report_line_and_with_none_the_last_record_wins(
        monkeypatch, capsys, extract_result):
    later = {"type": "result", "result": "That is the second monitor expiring."}
    streams = {
        "a developer report beats a later turn with no report line": (
            [{"type": "result", "result": "Done.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed"}, later],
            "Done.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed\n"),
        "a SPLIT: report beats a later turn with no report line": (
            [{"type": "result", "result": "Too big.\nSPLIT: the first behaviour\nSPLIT: the second behaviour"}, later],
            "Too big.\nSPLIT: the first behaviour\nSPLIT: the second behaviour\n"),
        "a TEST_PATH: report beats a later turn with no report line": (
            [{"type": "result", "result": "Red.\nTEST_PATH: tests/a.test.sh\nAGAINST_UNMODIFIED: FAILS"}, later],
            "Red.\nTEST_PATH: tests/a.test.sh\nAGAINST_UNMODIFIED: FAILS\n"),
        "a SUITE:-only report beats a later turn with no report line": (
            [{"type": "result", "result": "Tidied.\nSUITE: GREEN — 19 passed, 0 failed"}, later],
            "Tidied.\nSUITE: GREEN — 19 passed, 0 failed\n"),
        "of two records that both carry a report line, the later one wins": (
            [{"type": "result", "result": "First.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed"},
             {"type": "result", "result": "Second.\nIMPL_PATH: b.sh\nSUITE: GREEN — 20 passed, 0 failed"}],
            "Second.\nIMPL_PATH: b.sh\nSUITE: GREEN — 20 passed, 0 failed\n"),
        "with no report or VERDICT: line in any record, the last record wins": (
            [{"type": "result", "result": "First turn."},
             {"type": "result", "result": "Second turn.\nNothing to report."},
             {"type": "result", "result": "Third turn.\nStill no report."}],
            "Third turn.\nStill no report.\n"),
        "a VERDICT: record still beats a later record without one": (
            [{"type": "result", "result": "VERDICT: PASS\nREASON: the case pins the behaviour."}, later],
            "VERDICT: PASS\nREASON: the case pins the behaviour.\n"),
    }
    seen = {}
    for name, (records, _) in streams.items():
        fake_stdin(monkeypatch, "\n".join(json.dumps(r) for r in records))
        code = extract_result.main([])
        seen[name] = (code, capsys.readouterr().out)
    assert seen == {name: (0, expected) for name, (_, expected) in streams.items()}


def test_main_writes_stdin_back_unchanged_when_no_record_carries_a_result(monkeypatch, capsys, extract_result):
    streams = {
        "#624 a developer report with no result record passes through unchanged": (
            '{"type":"system","subtype":"init"}\n'
            '{"type":"assistant","message":{"content":[{"type":"text","text":"IMPL_PATH: a.sh"}]}}\n'
            "Done.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed"),
        "passthrough non-stream": "VERDICT: PASS\nREASON: plain text, no stream-json here.",
        "json but no result event": (
            '{"type":"system","subtype":"init"}\n'
            '{"type":"assistant","message":{"content":[]}}'),
    }
    seen = {}
    for name, text in streams.items():
        fake_stdin(monkeypatch, text)
        code = extract_result.main([])
        seen[name] = (code, capsys.readouterr().out)
    assert seen == {name: (0, text) for name, text in streams.items()}


def test_main_ports_the_null_result_non_string_report_case_newline_empty_stdin_and_argument_quirks(
        monkeypatch, capsys, extract_result):
    streams = {
        "a null result and a record with no result key pass through unchanged": (
            [], '{"type":"result","result":null}\n{"type":"result","subtype":"success"}\n'),
        "a lowercase report line indented by spaces beats a later record": (
            [], "\n".join(json.dumps(r) for r in [
                {"type": "result", "result": "Done.\n  verdict: x"},
                {"type": "result", "result": "later"}])),
        "a report line indented by a tab counts as a report": (
            [], "\n".join(json.dumps(r) for r in [
                {"type": "result", "result": "Done.\n\tImpl_Path: a.sh"},
                {"type": "result", "result": "later"}])),
        "a result already ending in a newline gets none added": (
            [], json.dumps({"type": "result", "result": "VERDICT: PASS\n"})),
        "empty stdin": ([], ""),
        "arguments are ignored": (
            ["--bogus", "extra"], json.dumps({"type": "result", "result": "VERDICT: PASS"})),
    }
    seen = {}
    for name, (argv, text) in streams.items():
        fake_stdin(monkeypatch, text)
        code = extract_result.main(argv)
        seen[name] = (code, capsys.readouterr().out)
    fake_stdin(monkeypatch, json.dumps({"type": "result", "result": 7}))
    with pytest.raises(AttributeError):
        extract_result.main([])
    assert seen == {
        "a null result and a record with no result key pass through unchanged": (
            0, '{"type":"result","result":null}\n{"type":"result","subtype":"success"}\n'),
        "a lowercase report line indented by spaces beats a later record": (0, "Done.\n  verdict: x\n"),
        "a report line indented by a tab counts as a report": (0, "Done.\n\tImpl_Path: a.sh\n"),
        "a result already ending in a newline gets none added": (0, "VERDICT: PASS\n"),
        "empty stdin": (0, ""),
        "arguments are ignored": (0, "VERDICT: PASS\n"),
    }
