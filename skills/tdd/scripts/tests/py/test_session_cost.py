"""In-process cases for veri/session_cost.py, the module session-cost.sh is a shim over."""
import importlib
import pathlib
import sys
import time

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]\n"


@pytest.fixture
def session_cost():
    return importlib.import_module("veri.session_cost")


def test_main_returns_2_with_the_usage_line_alone_when_since_has_no_value_or_is_absent(capsys, session_cost):
    for argv in (["--since"], []):
        code = session_cost.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)


def test_main_prints_the_days_total_cost_split_into_cache_read_cache_write_and_output(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    transcript = tmp_path / "2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4.jsonl"
    transcript.write_text(
        '{"type":"summary","summary":"A cost report read from the session transcripts","leafUuid":"0b1f8c22-4a67-4f30-91da-6c2d3e5b7a19"}\n'
        '{"type":"user","timestamp":"2026-09-14T12:04:28.331Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"total the day"}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T12:04:31.807Z","requestId":"req_011CS4kQn7XdF2vHbJ9tLm3p","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":3,"cache_creation_input_tokens":200000,"cache_creation":{"ephemeral_5m_input_tokens":200000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":800000,"output_tokens":15000}}}\n'
        '{"type":"user","timestamp":"2026-09-14T15:37:09.115Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"and the split"}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T15:37:12.244Z","requestId":"req_011CS5rB8xWgT6nPqK4vZy7d","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":128000,"cache_creation":{"ephemeral_5m_input_tokens":128000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":440000,"output_tokens":8600}}}\n'
    )
    want = [
        "  cache read          1240000 tokens   $1.86",
        "  cache write          328000 tokens   $6.15",
        "  output                23600 tokens   $1.77",
        "  total                                $9.78",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(transcript)])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])
