"""In-process cases for veri/session_cost.py, the module session-cost.sh is a shim over."""
import importlib
import json
import re
import subprocess
import time

import pytest

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


def test_main_since_excludes_a_record_before_the_window_and_counts_one_inside_it(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    transcript = tmp_path / "c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7.jsonl"
    transcript.write_text(
        '{"type":"assistant","timestamp":"2026-09-13T16:22:40.118Z","requestId":"req_011CSEiV0xYzF6lBdJ9wQs3e","sessionId":"c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":2,"cache_creation_input_tokens":80000,"cache_creation":{"ephemeral_5m_input_tokens":80000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":300000,"output_tokens":6800}}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T14:07:33.902Z","requestId":"req_011CSFjW1yZaG7mCeK0xRt4f","sessionId":"c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":2,"cache_creation_input_tokens":120000,"cache_creation":{"ephemeral_5m_input_tokens":120000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":700000,"output_tokens":9200}}}\n'
    )
    want = [
        "  cache read           700000 tokens   $1.05",
        "  cache write          120000 tokens   $2.25",
        "  output                 9200 tokens   $0.69",
        "  total                                $3.99",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(transcript)])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])


def test_main_attributes_an_sdk_cli_session_and_an_interactive_session_to_their_own_rows(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    leaf = tmp_path / "3f6d9a71-0c58-4e29-b7a3-1d4e8f2c50b6.jsonl"
    human = tmp_path / "7a1c4e82-6b30-4d95-8f16-2e9b0a5d3c74.jsonl"
    leaf.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T10:31:07.442Z","requestId":"req_011CSGkX2zAbH8nDfL1ySu5g","sessionId":"3f6d9a71-0c58-4e29-b7a3-1d4e8f2c50b6","entrypoint":"sdk-cli","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":80000,"cache_creation":{"ephemeral_5m_input_tokens":80000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":400000,"output_tokens":4000}}}\n'
    )
    human.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T10:52:26.019Z","requestId":"req_011CSHlY3aBcI9oEgM2zTv6h","sessionId":"7a1c4e82-6b30-4d95-8f16-2e9b0a5d3c74","entrypoint":"claude-desktop","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":40000,"cache_creation":{"ephemeral_5m_input_tokens":40000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":200000,"output_tokens":6800}}}\n'
    )
    want = [
        "  sdk-cli (leaf)                       $2.40",
        "  interactive                          $1.56",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(leaf), str(human)])
    lines = capsys.readouterr().out.splitlines()

    assert (code, [line for line in want if line not in lines]) == (0, [])


def test_main_prints_per_session_rows_with_preamble_final_and_total_context_and_names_an_uncleared_ramp_in_words(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    ramp = tmp_path / "a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5.jsonl"
    flat = tmp_path / "5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e.jsonl"

    def record(stamp, request, session, usage_in, read, write, output):
        return (
            '{"type":"assistant","timestamp":"%s","requestId":"%s","sessionId":"%s","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":%d,"cache_creation_input_tokens":%d,"cache_creation":{"ephemeral_5m_input_tokens":%d,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":%d,"output_tokens":%d}}}\n'
            % (stamp, request, session, usage_in, write, write, read, output)
        )

    ramp.write_text(
        record("2026-09-14T07:02:18.443Z", "req_011CSJmZ4bCdJ0pFhN3aUw7i", "a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5", 4, 0, 60000, 900)
        + record("2026-09-14T09:26:51.207Z", "req_011CSKnA5cDeK1qGiO4bVx8j", "a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5", 2, 60000, 120000, 700)
        + record("2026-09-14T13:44:05.912Z", "req_011CSLoB6dEfL2rHjP5cWy9k", "a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5", 2, 180000, 220000, 800)
    )
    flat.write_text(
        record("2026-09-14T08:11:32.605Z", "req_011CSMpC7eFgM3sIkQ6dXz0l", "5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e", 1, 0, 52000, 600)
        + record("2026-09-14T08:39:14.881Z", "req_011CSNqD8fGhN4tJlR7eYa1m", "5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e", 1, 52000, 0, 500)
    )
    want = {
        "a8f3d1c6": (60004, 400002, 640008),
        "5c72e0b4": (52001, 52001, 104002),
    }
    ramp_words = re.compile(r"un-?cleared|never cleared|not cleared|ramp", re.IGNORECASE)

    code = session_cost.main(["--since", "2026-09-14", str(ramp), str(flat)])
    out = capsys.readouterr().out

    problems = []
    for session, figures in want.items():
        rows = "\n".join(line for line in out.splitlines() if session in line)
        for figure in figures:
            if not re.search(r"(^|[^0-9])%d([^0-9]|$)" % figure, rows, re.MULTILINE):
                problems.append("session %s: want %d on a line naming it, not found" % (session, figure))
    if not ramp_words.search("\n".join(line for line in out.splitlines() if "a8f3d1c6" in line)):
        problems.append("the ramping session: want its row to name it as un-cleared in words, not found")
    if ramp_words.search("\n".join(line for line in out.splitlines() if "5c72e0b4" in line)):
        problems.append("the flat session: named as un-cleared, but its context read is its preamble x its requests")

    assert (code, problems) == (0, []), out


def test_main_reports_an_unknown_models_tokens_with_no_cost_and_names_it_in_a_footer(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    known = tmp_path / "1d8b6f40-2a93-4c17-8e65-3b07d9a4f2e1.jsonl"
    unknown = tmp_path / "9e4a2c58-7f61-4b0d-a392-5c81e6b70d43.jsonl"
    model = "claude-quasar-9-20260901"
    known.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T09:12:44.518Z","requestId":"req_011CSJmZ4bCdJ0pFhN3aUw7i","sessionId":"1d8b6f40-2a93-4c17-8e65-3b07d9a4f2e1","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":2,"cache_creation_input_tokens":40000,"cache_creation":{"ephemeral_5m_input_tokens":40000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":600000,"output_tokens":4400}}}\n'
    )
    unknown.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T09:48:02.907Z","requestId":"req_011CSKnA5cDeK1qGiO4bVx8j","sessionId":"9e4a2c58-7f61-4b0d-a392-5c81e6b70d43","message":{"role":"assistant","model":"%s","usage":{"input_tokens":0,"cache_creation_input_tokens":24680,"cache_creation":{"ephemeral_5m_input_tokens":24680,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":512345,"output_tokens":3107}}}\n'
        % model
    )
    want = [
        "  cache read           600000 tokens   $0.90",
        "  cache write           40000 tokens   $0.75",
        "  output                 4400 tokens   $0.33",
        "  total                                $1.98",
    ]

    code = session_cost.main(["--since", "2026-09-14", str(known), str(unknown)])
    lines = capsys.readouterr().out.splitlines()
    footer = [line for line in lines if model in line]

    problems = [line for line in want if line not in lines]
    if not footer:
        problems.append("the unknown model: want a line naming %s, the report names it nowhere" % model)
    if not any(re.search(r"(^|[^0-9])540132([^0-9]|$)", line) for line in footer):
        problems.append("the unknown model's tokens: want 540132 on a line naming %s, got %r" % (model, footer))
    if any(re.search(r"\$[0-9]", line) for line in footer):
        problems.append("the unknown model: want no money on the line naming it, got %r" % footer)
    assert (code, problems) == (0, []), "\n".join(lines)


def test_main_json_states_the_same_four_totals_as_the_text_report(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    transcript = tmp_path / "6b19d4e7-3c05-42af-9d71-8e260a5fb3c7.jsonl"
    transcript.write_text(
        '{"type":"assistant","timestamp":"2026-09-14T10:21:07.412Z","requestId":"req_011CSPrE9gHiO5uKmS8fZb2n","sessionId":"6b19d4e7-3c05-42af-9d71-8e260a5fb3c7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":3,"cache_creation_input_tokens":160000,"cache_creation":{"ephemeral_5m_input_tokens":160000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":700000,"output_tokens":12000}}}\n'
        '{"type":"assistant","timestamp":"2026-09-14T11:58:33.276Z","requestId":"req_011CSQsF0hIjP6vLnT9gAc3o","sessionId":"6b19d4e7-3c05-42af-9d71-8e260a5fb3c7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":96000,"cache_creation":{"ephemeral_5m_input_tokens":96000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":340000,"output_tokens":7600}}}\n'
    )
    want_text = [
        "  cache read          1040000 tokens   $1.56",
        "  cache write          256000 tokens   $4.80",
        "  output                19600 tokens   $1.47",
        "  total                                $7.83",
    ]
    want_json = {
        r"cache.*read": "1.56",
        r"cache.*(write|creat)": "4.80",
        r"output": "1.47",
        r"total": "7.83",
    }

    code = session_cost.main(["--since", "2026-09-14", str(transcript)])
    lines = capsys.readouterr().out.splitlines()
    json_code = session_cost.main(["--since", "2026-09-14", "--json", str(transcript)])
    out_json = capsys.readouterr().out

    flat = []

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, (path + "." + str(key)) if path else str(key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, "%s[%d]" % (path, index))
        elif isinstance(node, bool):
            pass
        elif isinstance(node, (int, float)):
            flat.append("%s %.2f" % (path, node))

    problems = ["text report: want %r, not found" % line for line in want_text if line not in lines]
    try:
        walk(json.loads(out_json), "")
    except ValueError:
        problems.append("--json: want stdout to parse as one JSON document, it does not")
    for pattern, figure in want_json.items():
        named = [entry for entry in flat if re.search(pattern, entry, re.IGNORECASE)]
        if not any(re.search(r"(^|[^0-9])%s([^0-9]|$)" % re.escape(figure), entry) for entry in named):
            problems.append("the JSON %s total: want %s, got %r" % (pattern, figure, named))
    assert (code, json_code, problems) == (0, 0, []), out_json


def test_main_names_each_session_rows_entrypoint_and_bands_min_median_max_per_harness(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    desktop = [
        ("b2061c86-0d47-4e9a-8153-6fa2c70e91db", 597, 68000),
        ("c93172d5-1e58-4f0b-9264-7ab3d81fa2ec", 535, 69000),
        ("da4283e6-2f69-40c1-a375-8bc4e92b03fd", 436, 70000),
    ]
    leaf = [
        ("eb5394f7-3a70-41d2-b486-9cd5fa3c14ae", 321, 28000),
        ("fc64a508-4b81-42e3-c597-ade60b4d25bf", 1000, 30000),
        ("0d75b619-5c92-43f4-d6a8-bef71c5e36c0", 155, 33000),
    ]
    want_bands = {
        "claude-desktop": (68597, 69535, 70436),
        "sdk-cli": (28321, 31000, 33155),
    }

    transcripts = []

    def write_session(session, entrypoint, usage_in, write, stamp, output):
        path = tmp_path / (session + ".jsonl")
        path.write_text(
            '{"type":"assistant","timestamp":"%s","requestId":"req_%s","sessionId":"%s","entrypoint":"%s","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":%d,"cache_creation_input_tokens":%d,"cache_creation":{"ephemeral_5m_input_tokens":%d,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":0,"output_tokens":%d}}}\n'
            % (stamp, session, session, entrypoint, usage_in, write, write, output)
        )
        transcripts.append(str(path))

    for i in range(3):
        write_session(desktop[i][0], "claude-desktop", desktop[i][1], desktop[i][2], "2026-09-14T1%d:04:31.807Z" % i, 1100 + i)
        write_session(leaf[i][0], "sdk-cli", leaf[i][1], leaf[i][2], "2026-09-14T1%d:37:12.204Z" % i, 2200 + i)

    code = session_cost.main(["--since", "2026-09-14"] + transcripts)
    out = capsys.readouterr().out
    lines = out.splitlines()

    def anchored(figure):
        return r"(^|[^0-9])%d([^0-9]|$)" % figure

    problems = []
    for entrypoint, sessions in (("claude-desktop", desktop), ("sdk-cli", leaf)):
        for session, _, _ in sessions:
            if not any(entrypoint in line for line in lines if session[:8] in line):
                problems.append("session %s: want its row to name the entrypoint %s, it does not" % (session[:8], entrypoint))
    for harness, figures in want_bands.items():
        if not any(harness in line and all(re.search(anchored(figure), line) for figure in figures) for line in lines):
            problems.append(
                "the %s band: want one line naming %s and stating min %d, median %d and max %d together, no line states all three"
                % ((harness, harness) + figures)
            )
    assert (code, problems) == (0, []), out


def test_main_names_an_absent_entrypoints_rows_and_band_conductor_apart_from_clis(tmp_path, monkeypatch, capsys, session_cost):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    conductor = [
        ("1a842fb0-6d03-4e51-b7c2-8ef1a940d25e", 986, 51000),
        ("2b953ec1-7e14-4f62-c8d3-9fa2b051e36f", 438, 53000),
        ("3ca64fd2-8f25-4073-d9e4-0ab3c162f470", 994, 55000),
    ]
    cli = [
        ("4db75063-9036-4184-e0f5-1bc4d273058a", 500, 52000),
        ("5ec86174-0147-4295-f106-2cd5e384169b", 786, 53000),
        ("6fd97285-1258-43a6-028f-3de6f495270c", 800, 54000),
    ]
    want_bands = {
        "conductor": (51986, 53438, 55994),
        "cli": (52500, 53786, 54800),
    }

    transcripts = []

    def write_keyed_session(session, entrypoint_field, usage_in, write, stamp, output):
        path = tmp_path / (session + ".jsonl")
        path.write_text(
            '{"type":"assistant","timestamp":"%s","requestId":"req_%s","sessionId":"%s",%s"userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":%d,"cache_creation_input_tokens":%d,"cache_creation":{"ephemeral_5m_input_tokens":%d,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":0,"output_tokens":%d}}}\n'
            % (stamp, session, session, entrypoint_field, usage_in, write, write, output)
        )
        transcripts.append(str(path))

    for i in range(3):
        write_keyed_session(conductor[i][0], "", conductor[i][1], conductor[i][2], "2026-09-14T0%d:11:45.310Z" % i, 3300 + i)
        write_keyed_session(cli[i][0], '"entrypoint":"cli",', cli[i][1], cli[i][2], "2026-09-14T0%d:48:02.915Z" % i, 4400 + i)

    code = session_cost.main(["--since", "2026-09-14"] + transcripts)
    out = capsys.readouterr().out
    lines = out.splitlines()

    def anchored(figure):
        return r"(^|[^0-9])%d([^0-9]|$)" % figure

    problems = []
    for session, _, _ in conductor:
        if not any("conductor" in line for line in lines if session[:8] in line):
            problems.append("session %s: no entrypoint key, want its row to name it a conductor, it does not" % session[:8])
    for session, _, _ in cli:
        if not any("cli" in line for line in lines if session[:8] in line):
            problems.append("session %s: want its row to name the entrypoint cli, it does not" % session[:8])
    for harness, figures in want_bands.items():
        if not any(harness in line and all(re.search(anchored(figure), line) for figure in figures) for line in lines):
            problems.append(
                "the %s band: want one line naming %s and stating min %d, median %d and max %d together, no line states all three"
                % ((harness, harness) + figures)
            )
    assert (code, problems) == (0, []), out
