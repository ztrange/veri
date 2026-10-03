"""In-process cases for veri/session_cost.py, the module session-cost.sh is a shim over."""
import importlib
import json
import pathlib
import subprocess
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


def test_main_sums_every_project_directory_prefixed_by_the_repo_roots_slug_and_not_an_unrelated_one(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    root = tmp_path.resolve() / "repo"
    root.mkdir()
    home = tmp_path / "home"
    projects = home / ".claude" / "projects"
    slug = str(root).replace("/", "-")
    transcripts = {
        slug: '{"type":"assistant","timestamp":"2026-09-14T09:12:44.512Z","requestId":"req_011CS6aM2pQrX8dTvB1nHk5w","sessionId":"8c1d2e4f-7a93-4b05-8e61-2d7f9a0c3b48","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":2,"cache_creation_input_tokens":100000,"cache_creation":{"ephemeral_5m_input_tokens":100000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":600000,"output_tokens":10000}}}\n',
        slug + "--tdd-wt-999": '{"type":"assistant","timestamp":"2026-09-14T11:48:02.907Z","requestId":"req_011CS7bN3qRsY9eUwC2pJl6x","sessionId":"4e90b7c1-35da-4f27-a0b8-6c19d2e84f3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":60000,"cache_creation":{"ephemeral_5m_input_tokens":60000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":300000,"output_tokens":5600}}}\n',
        "-Users-someone-else-anotherrepo": '{"type":"assistant","timestamp":"2026-09-14T13:20:55.104Z","requestId":"req_011CS8cP4rStZ0fVxD3qKm7y","sessionId":"1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":900000,"cache_creation_input_tokens":900000,"cache_creation":{"ephemeral_5m_input_tokens":900000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":900000,"output_tokens":900000}}}\n',
    }
    for directory, record in transcripts.items():
        (projects / directory).mkdir(parents=True)
        session = json.loads(record)["sessionId"]
        (projects / directory / (session + ".jsonl")).write_text(record)
    monkeypatch.setenv("HOME", str(home))

    def git(argv, **kwargs):
        assert argv == ["git", "rev-parse", "--show-toplevel"]
        return subprocess.CompletedProcess(argv, 0, stdout=str(root) + "\n", stderr="")

    monkeypatch.setattr(subprocess, "run", git)
    want = [
        "  cache read           900000 tokens   $1.35",
        "  cache write          160000 tokens   $3.00",
        "  output                15600 tokens   $1.17",
        "  total                                $5.52",
    ]

    code = session_cost.main(["--since", "2026-09-14"])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])


def test_main_counts_a_repeated_request_id_once_and_a_distinct_one_still(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    transcript = tmp_path / "6b3e02f7-d914-4c85-a27e-8f01c6b45d3a.jsonl"
    a_usage = '{"input_tokens":3,"cache_creation_input_tokens":160000,"cache_creation":{"ephemeral_5m_input_tokens":160000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":900000,"output_tokens":12400}'
    contents = [
        '{"type":"thinking","thinking":"work out the plan"}',
        '{"type":"tool_use","name":"Bash","input":{"command":"ls"}}',
        '{"type":"tool_use","name":"Bash","input":{"command":"cat a"}}',
        '{"type":"tool_use","name":"Bash","input":{"command":"cat b"}}',
        '{"type":"tool_use","name":"Bash","input":{"command":"cat c"}}',
        '{"type":"tool_use","name":"Bash","input":{"command":"cat d"}}',
    ]
    transcript.write_text(
        "".join(
            '{"type":"assistant","timestamp":"2026-09-14T10:02:11.004Z","requestId":"req_011CS9dQ5sTuA1gWyE4rLn8z","sessionId":"6b3e02f7-d914-4c85-a27e-8f01c6b45d3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","content":['
            + content
            + '],"usage":'
            + a_usage
            + "}}\n"
            for content in contents
        )
        + '{"type":"assistant","timestamp":"2026-09-14T10:09:47.663Z","requestId":"req_011CSAeR6tUvB2hXzF5sMo9a","sessionId":"6b3e02f7-d914-4c85-a27e-8f01c6b45d3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","content":[{"type":"text","text":"done"}],"usage":{"input_tokens":1,"cache_creation_input_tokens":40000,"cache_creation":{"ephemeral_5m_input_tokens":40000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":500000,"output_tokens":7600}}}\n'
    )
    want = [
        "  cache read          1400000 tokens   $2.10",
        "  cache write          200000 tokens   $3.75",
        "  output                20000 tokens   $1.50",
        "  total                                $7.35",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(transcript)])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])


def test_main_prices_1h_and_5m_cache_writes_apart_and_a_bare_cache_creation_count_at_5m(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    transcript = tmp_path / "9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5.jsonl"
    transcript.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T08:15:03.221Z","requestId":"req_011CSBfS7uVwC3iYaG6tNp0b","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":400000,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":400000},"cache_read_input_tokens":200000,"output_tokens":4000}}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T08:41:19.508Z","requestId":"req_011CSCgT8vWxD4jZbH7uOq1c","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":400000,"cache_creation":{"ephemeral_5m_input_tokens":400000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":100000,"output_tokens":2000}}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T09:03:55.740Z","requestId":"req_011CSDhU9wXyE5kAcI8vPr2d","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":200000,"cache_read_input_tokens":60000,"output_tokens":2000}}}\n'
    )
    want = [
        "  cache read           360000 tokens   $0.54",
        "  cache write         1000000 tokens   $23.25",
        "  output                 8000 tokens   $0.60",
        "  total                                $24.39",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(transcript)])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])
