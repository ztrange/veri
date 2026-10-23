"""In-process cases for veri/run_leaf.py, the module run-leaf.sh is a shim over."""
import importlib
import io
import os
import pathlib
import pytest
import select
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

from conftest import SCRIPTS


def _write_prompt(work, text):
    (work / "prompt.txt").write_text(text)


def _workspace(tmp_path, monkeypatch, *extra_dirs):
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp, *(work / name for name in extra_dirs)):
        path.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    monkeypatch.delenv("CLAUDE_BIN", raising=False)
    monkeypatch.delenv("VERI_LEAF_MODEL", raising=False)
    return work, tmp


def test_main_without_a_prompt_argument_refuses_with_the_usage_line_before_any_temp_file_or_launch(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    launches = []
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: launches.append((args, kwargs)))

    answers = []
    for argv in ([], [""]):
        code = run_leaf.main(argv)
        captured = capfd.readouterr()
        answers.append((code, captured.out, captured.err))

    usage = "usage: run-leaf.sh <prompt-file|-> [claude args...]\n"
    assert (answers, launches, sorted(tmp.iterdir()), sorted(work.iterdir())) == (
        [(2, "", usage), (2, "", usage)], [], [], [])


class _FakeLeaf:
    def __init__(self, launches, argv, stream=b"", **kwargs):
        launches.append(list(argv))
        read_end, write_end = os.pipe()
        os.write(write_end, stream)
        os.close(write_end)
        self.stdout = open(read_end, "rb", buffering=0)
        self.returncode = 0
        self.pid = 0

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stdout.close()
        return False


def test_main_launches_one_leaf_with_the_prompt_the_model_only_when_non_empty_and_the_callers_arguments_in_order(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    head = ["-p", "do the step", "--output-format", "stream-json", "--verbose"]

    launched = []
    for claude_bin, model, extra, want in (
            (None, None, [], ["claude", *head]),
            ("", "", ["--x"], ["claude", *head, "--x"]),
            ("/stub/claude", "a model", ["--a", "", "b"],
             ["/stub/claude", *head, "--model", "a model", "--a", "", "b"])):
        for name, value in (("CLAUDE_BIN", claude_bin), ("VERI_LEAF_MODEL", model)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        launches = []
        monkeypatch.setattr(subprocess, "Popen",
                            lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))
        run_leaf.main(["prompt.txt", *extra])
        capfd.readouterr()
        tail = want[len(head) + 1:]
        launched.append(([[a[:len(head) + 1], a[len(a) - len(tail):]] for a in launches],
                         [[want[:len(head) + 1], tail]]))

    assert [got for got, _ in launched] == [want for _, want in launched]


def test_main_launch_limits_what_the_harness_loads_and_keeps_the_callers_arguments_unchanged_and_in_order_1705(
        tmp_path, monkeypatch, capfd):
    import json
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.setenv("VERI_LEAF_MODEL", "sonnet")
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))
    extra = ["--permission-mode", "bypassPermissions", "--model", "haiku", "--allowed-tools", "Read,Bash"]

    run_leaf.main(["prompt.txt", *extra])
    capfd.readouterr()

    argv = launches[0]
    value = lambda flag: argv[argv.index(flag) + 1] if flag in argv else "null"
    home = os.environ["HOME"]
    assert (argv[-len(extra):], "--disable-slash-commands" in argv, "--strict-mcp-config" in argv,
            json.loads(value("--mcp-config")), json.loads(value("--settings")),
            "--bare" in argv, "--model" in argv[:-len(extra)]) == (
        extra, True, True, {"mcpServers": {}},
        {"autoMemoryEnabled": False, "claudeMdExcludes": [os.path.join(home, ".claude", "CLAUDE.md")]},
        False, False)


def test_main_launches_claude_with_background_tasks_disabled_whatever_the_callers_environment_holds_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.setenv("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS", "0")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        seen.append(kwargs["env"].get("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == ["1"]


def test_main_launches_claude_with_the_bash_tool_timeouts_at_the_default_hard_cap_in_milliseconds_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    for name in ("VERI_TIMEOUT", "BASH_DEFAULT_TIMEOUT_MS", "BASH_MAX_TIMEOUT_MS"):
        monkeypatch.delenv(name, raising=False)
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("900000", "900000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_at_the_supervisors_hard_cap_in_milliseconds_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.delenv("BASH_DEFAULT_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("BASH_MAX_TIMEOUT_MS", raising=False)
    monkeypatch.setenv("VERI_TIMEOUT", "120")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("120000", "120000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_at_the_runs_timeout_file_in_milliseconds_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch, ".tdd")
    _write_prompt(work, "do the step\n")
    (work / ".tdd" / "issue-7-timeout").write_text("3570\n")
    monkeypatch.delenv("BASH_DEFAULT_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("BASH_MAX_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setenv("VERI_ISSUE", "7")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("3570000", "3570000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_at_veri_timeout_over_the_runs_timeout_file_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch, ".tdd")
    _write_prompt(work, "do the step\n")
    (work / ".tdd" / "issue-7-timeout").write_text("3570\n")
    monkeypatch.delenv("BASH_DEFAULT_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("BASH_MAX_TIMEOUT_MS", raising=False)
    monkeypatch.setenv("VERI_TIMEOUT", "120")
    monkeypatch.setenv("VERI_ISSUE", "7")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("120000", "120000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_at_the_default_hard_cap_when_the_run_wrote_no_timeout_file_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch, ".tdd")
    _write_prompt(work, "do the step\n")
    monkeypatch.delenv("BASH_DEFAULT_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("BASH_MAX_TIMEOUT_MS", raising=False)
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setenv("VERI_ISSUE", "7")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("900000", "900000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_the_caller_set_unchanged_whatever_veri_timeout_says_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.setenv("BASH_DEFAULT_TIMEOUT_MS", "45000")
    monkeypatch.setenv("BASH_MAX_TIMEOUT_MS", "60000")
    monkeypatch.setenv("VERI_TIMEOUT", "120")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("45000", "60000")]


def test_main_launches_claude_with_the_bash_tool_timeouts_the_caller_set_unchanged_whatever_the_runs_timeout_file_holds_1939(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch, ".tdd")
    _write_prompt(work, "do the step\n")
    (work / ".tdd" / "issue-7-timeout").write_text("3570\n")
    monkeypatch.setenv("BASH_DEFAULT_TIMEOUT_MS", "45000")
    monkeypatch.setenv("BASH_MAX_TIMEOUT_MS", "60000")
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setenv("VERI_ISSUE", "7")
    seen = []
    launches = []

    def fake_popen(argv, *args, **kwargs):
        env = kwargs["env"]
        seen.append((env.get("BASH_DEFAULT_TIMEOUT_MS"), env.get("BASH_MAX_TIMEOUT_MS")))
        return _FakeLeaf(launches, argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert seen == [("45000", "60000")]


def _stream_of_what_the_real_claude_loads(argv, home, repo):
    """A stream shaped by the 2026-10-18 observation of the real binary under each flag."""
    import json
    flag = lambda name: argv[argv.index(name) + 1] if name in argv else None
    if "--bare" in argv:
        return [{"type": "result", "subtype": "error", "is_error": True, "result": "Not logged in"}]
    settings = json.loads(flag("--settings") or "{}")
    excluded = settings.get("claudeMdExcludes", [])
    servers = ["claude.ai Gmail", "claude.ai Slack", "claude.ai ClickUp"]
    if "--strict-mcp-config" in argv:
        servers = list(json.loads(flag("--mcp-config") or "{}").get("mcpServers", {}))
    docs = [str(home / ".claude" / "CLAUDE.md"), str(repo / "CLAUDE.md")]
    if settings.get("autoMemoryEnabled", True):
        docs.append(str(home / ".claude" / "projects" / "MEMORY.md"))
    loaded = [path for path in docs if path not in excluded]
    skills = [] if "--disable-slash-commands" in argv else ["tdd", "merge"]
    return [{"type": "system", "subtype": "init", "mcp_servers": servers, "skills": skills},
            *({"type": "attachment", "path": path} for path in loaded),
            {"type": "result", "subtype": "success", "is_error": False, "result": "ok"}]


def test_main_a_leaf_session_loads_no_skills_connectors_memory_or_user_claude_md_but_logs_in_and_reads_the_repos_claude_md_1705(
        tmp_path, monkeypatch, capfd):
    import json
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    home = pathlib.Path(os.environ["HOME"])
    launches = []

    def launch(argv, *args, **kwargs):
        stream = "".join(json.dumps(r) + "\n" for r in _stream_of_what_the_real_claude_loads(argv, home, work))
        return _FakeLeaf(launches, argv, stream=stream.encode(), **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)

    code = run_leaf.main(["prompt.txt", "--permission-mode", "bypassPermissions"])
    records = [json.loads(line) for line in capfd.readouterr().out.splitlines() if line.startswith("{")]

    init = next(r for r in records if r.get("subtype") == "init")
    assert (code, init["skills"], init["mcp_servers"],
            [r["path"] for r in records if r["type"] == "attachment"],
            [r["is_error"] for r in records if r["type"] == "result"]) == (
        0, [], [], [str(work / "CLAUDE.md")], [False])


def test_main_a_leaf_asked_for_the_five_minute_cache_ttl_reports_five_minute_writes_and_no_one_hour_writes_1707(
        tmp_path, monkeypatch, capfd):
    import json
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    monkeypatch.delenv("FORCE_PROMPT_CACHING_5M", raising=False)
    _write_prompt(work, "do the step\n")
    launches = []

    def launch(argv, *args, **kwargs):
        five = kwargs["env"].get("FORCE_PROMPT_CACHING_5M") == "1"
        cache = {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0}
        cache["ephemeral_5m_input_tokens" if five else "ephemeral_1h_input_tokens"] = 1000
        record = {"type": "assistant", "message": {"usage": {"cache_creation": cache}}}
        return _FakeLeaf(launches, argv, stream=(json.dumps(record) + "\n").encode(), **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)

    code = run_leaf.main(["prompt.txt"])
    records = [json.loads(line) for line in capfd.readouterr().out.splitlines() if line.startswith("{")]

    cache = records[0]["message"]["usage"]["cache_creation"]
    assert (code, cache["ephemeral_5m_input_tokens"] > 0, cache["ephemeral_1h_input_tokens"]) == (0, True, 0)


def test_main_reads_the_prompt_from_a_relative_file_or_stdin_as_bytes_and_refuses_a_missing_file_or_a_directory_with_2(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch, "sub", "adir")
    (work / "sub" / "p.txt").write_bytes(b"line one\nline two\n\n\n")
    (work / "raw.txt").write_bytes(b"a\x00b\xff\xfec\n\n")
    stdin_file = tmp_path / "stdin"
    stdin_file.write_bytes(b"from stdin\n\n")

    saved_stdin = os.dup(0)
    stdin_fd = os.open(stdin_file, os.O_RDONLY)
    os.dup2(stdin_fd, 0)
    os.close(stdin_fd)
    monkeypatch.setattr(sys, "stdin", open(stdin_file, encoding="utf-8"))
    answers = []
    try:
        for prompt_arg in ("sub/p.txt", "raw.txt", "-", "nope.txt", "adir"):
            launches = []
            monkeypatch.setattr(subprocess, "Popen",
                                lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))
            try:
                code = run_leaf.main([prompt_arg])
            except Exception as error:
                code = type(error).__name__
            out = capfd.readouterr().out
            prompts = [os.fsencode(argv[2]) for argv in launches]
            answers.append((prompt_arg, code, prompts) if prompts
                           else (prompt_arg, code, out, sorted(tmp.iterdir())))
    finally:
        os.dup2(saved_stdin, 0)
        os.close(saved_stdin)

    assert answers == [
        ("sub/p.txt", 0, [b"line one\nline two"]),
        ("raw.txt", 0, [b"ab\xff\xfec"]),
        ("-", 0, [b"from stdin"]),
        ("nope.txt", 2, "", []),
        ("adir", 2, "", []),
    ]


def test_main_when_the_prompt_file_is_a_directory_returns_2_launches_nothing_and_names_it_on_stderr(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch, "adir")
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))

    code = run_leaf.main(["adir"])
    err = capfd.readouterr().err

    assert (code, launches, err) == (2, [], "run-leaf.sh: adir: Is a directory\n")


def test_main_when_the_prompt_file_is_empty_or_only_nul_bytes_and_newlines_returns_2_launches_nothing_and_says_the_prompt_is_empty_2137(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))

    answers = []
    for content in (b"", b"\0\n\0\n\n"):
        (work / "prompt.txt").write_bytes(content)
        code = run_leaf.main(["prompt.txt"])
        answers.append((code, "empty" in capfd.readouterr().err))

    assert (answers, launches) == ([(2, True), (2, True)], [])


def _as_extract_result_sh_prints(stream):
    extract_result = importlib.import_module("veri.extract_result")
    stdin = io.TextIOWrapper(io.BytesIO(stream), encoding=sys.__stdin__.encoding,
                             errors=sys.__stdin__.errors)
    stdout = io.TextIOWrapper(io.BytesIO(), encoding=sys.__stdout__.encoding,
                              errors=sys.__stdout__.errors, newline="\n")
    saved = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = stdin, stdout
    try:
        extract_result.main([])
    except UnicodeDecodeError:
        pass
    finally:
        sys.stdin, sys.stdout = saved
    stdout.flush()
    return stdout.buffer.getvalue()


def test_main_writes_after_the_leaf_ends_a_newline_then_the_extraction_the_stream_twice_with_no_result_record_and_a_non_utf8_byte_as_extract_result_sh_prints_it(
        tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    with_result = (b'{"type":"assistant","message":{"content":[]}}\n'
                   b'{"type":"result","subtype":"success","result":"done"}\n')
    without_result = b'{"type":"system","subtype":"init"}\nplain line\n'
    non_utf8 = b'{"type":"system","subtype":"init"}\nraw \xff\xfe byte\n'
    printed = _as_extract_result_sh_prints(non_utf8)

    outs = []
    for stream in (with_result, without_result, non_utf8):
        monkeypatch.setattr(subprocess, "Popen",
                            lambda argv, *args, stream=stream, **kwargs:
                            _FakeLeaf([], argv, stream=stream, **kwargs))
        try:
            run_leaf.main(["prompt.txt"])
        except UnicodeDecodeError:
            pass
        outs.append(capfdbinary.readouterr().out)

    assert outs == [
        with_result + b"\n" + b"done\n",
        without_result + b"\n" + without_result,
        non_utf8 + b"\n" + printed,
    ]


def test_main_writes_each_chunk_of_the_leafs_stdout_to_stdout_and_the_stream_temp_file_before_the_next_chunk_is_read(
        tmp_path, monkeypatch):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    first = b'{"type":"system","subtype":"init"}\n'
    second = b'{"type":"result","subtype":"success","result":"done"}\n'
    leaf_read, leaf_write = os.pipe()

    class _ChunkedLeaf(_FakeLeaf):
        def __init__(self, argv, *args, **kwargs):
            self.stdout = open(leaf_read, "rb", buffering=0)
            self.returncode = 0
            self.pid = 0

    monkeypatch.setattr(subprocess, "Popen", _ChunkedLeaf)

    def next_stdout_chunk():
        ready, _, _ = select.select([out_read], [], [], 5)
        return os.read(out_read, 65536) if ready else b"<nothing on stdout>"

    def a_stream_file_holds(expected):
        deadline = time.monotonic() + 5
        while expected not in [path.read_bytes() for path in sorted(tmp.iterdir())]:
            if time.monotonic() > deadline:
                return False
            time.sleep(0.01)
        return True

    out_read, out_write = os.pipe()
    saved_stdout = os.dup(1)
    os.dup2(out_write, 1)
    results = []
    leaf = threading.Thread(target=lambda: results.append(run_leaf.main(["prompt.txt"])))
    observed = []
    try:
        leaf.start()
        os.write(leaf_write, first)
        observed.append((next_stdout_chunk(), a_stream_file_holds(first)))
        os.write(leaf_write, second)
        observed.append((next_stdout_chunk(), a_stream_file_holds(first + second)))
    finally:
        os.close(leaf_write)
        leaf.join()
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)
        os.close(out_write)
    rest = b""
    while chunk := os.read(out_read, 65536):
        rest += chunk
    os.close(out_read)

    assert (observed, results, rest) == (
        [(first, True), (second, True)], [0], b"\n" + b"done\n")


def test_main_returns_the_leafs_status_when_it_is_0_to_3_else_2_and_for_a_leaf_that_cannot_start_prints_its_own_line_then_the_newline_and_returns_2(
        tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")

    def answer():
        try:
            code = run_leaf.main(["prompt.txt"])
        except Exception as error:
            code = type(error).__name__
        captured = capfdbinary.readouterr()
        return code, captured.out, captured.err

    def ending_with(returncode):
        def launch(argv, *args, **kwargs):
            leaf = _FakeLeaf([], argv, **kwargs)
            leaf.returncode = returncode
            return leaf
        return launch

    statuses = []
    for returncode in (0, 1, 2, 3, 7, -9):
        monkeypatch.setattr(subprocess, "Popen", ending_with(returncode))
        statuses.append(answer()[0])

    unstartable = []
    for error in (FileNotFoundError(2, "No such file or directory"),
                  PermissionError(13, "Permission denied"),
                  OSError(7, "Argument list too long")):
        def refuse(argv, *args, error=error, **kwargs):
            raise error
        monkeypatch.setattr(subprocess, "Popen", refuse)
        code, out, err = answer()
        unstartable.append((code, out, err.count(b"\n"), err.endswith(b"\n"), len(err) > 1))

    assert (statuses, unstartable) == (
        [0, 1, 2, 3, 2, 2],
        [(2, b"\n", 1, True, True)] * 3)


def test_main_when_copying_a_regular_gitconfig_into_the_leafs_temp_file_fails_returns_2_launches_nothing_and_leaves_no_temp_file(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    (tmp_path / "home" / ".gitconfig").write_text("[user]\n\tname = operator\n")
    made = []
    real_mkstemp = tempfile.mkstemp

    def mkstemp_with_a_directory_at_the_second_path(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        made.append(path)
        if len(made) == 2:
            os.remove(path)
            os.mkdir(path)
        return fd, path

    monkeypatch.setattr(tempfile, "mkstemp", mkstemp_with_a_directory_at_the_second_path)
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))

    try:
        code = run_leaf.main(["prompt.txt"])
    except Exception as error:
        code = type(error).__name__
    capfd.readouterr()

    left = sorted(path for path in tmp.rglob("*") if not path.is_dir())
    assert (code, launches, left) == (2, [], [])


def test_main_when_a_gitconfig_that_was_a_regular_file_cannot_be_read_as_one_returns_2_launches_nothing_and_leaves_neither_temp_file(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    gitconfig = tmp_path / "home" / ".gitconfig"
    gitconfig.write_text("[user]\n\tname = operator\n")
    real_isfile = os.path.isfile

    def isfile_then_the_gitconfig_becomes_a_directory(path):
        answer = real_isfile(path)
        if os.fspath(path) == str(gitconfig) and answer:
            gitconfig.unlink()
            gitconfig.mkdir()
        return answer

    monkeypatch.setattr(os.path, "isfile", isfile_then_the_gitconfig_becomes_a_directory)
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))

    try:
        code = run_leaf.main(["prompt.txt"])
    except Exception as error:
        code = type(error).__name__
    capfd.readouterr()

    assert (code, launches, sorted(tmp.iterdir())) == (2, [], [])


def test_main_when_copying_the_gitconfig_into_the_leafs_temp_git_config_raises_oserror_returns_2_launches_nothing_leaves_no_temp_file_and_names_it_on_stderr(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    (tmp_path / "home" / ".gitconfig").write_text("[user]\n\tname = operator\n")
    made = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        made.append(path)
        return fd, path

    def copyfile_out_of_space(*args, **kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(tempfile, "mkstemp", recording_mkstemp)
    monkeypatch.setattr(shutil, "copyfile", copyfile_out_of_space)
    launches = []
    monkeypatch.setattr(subprocess, "Popen",
                        lambda argv, *args, **kwargs: _FakeLeaf(launches, argv, **kwargs))

    try:
        code = run_leaf.main(["prompt.txt"])
    except Exception as error:
        code = type(error).__name__
    err = capfd.readouterr().err

    assert (code, launches, sorted(tmp.iterdir()), err) == (
        2, [], [], f"run-leaf.sh: {made[1]}: No space left on device\n")


def test_main_when_the_stream_temp_file_vanishes_during_the_leafs_run_returns_2_and_names_it_on_stderr(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    made = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        made.append(path)
        return fd, path

    def launch_then_lose_the_stream(argv, *args, **kwargs):
        os.remove(made[0])
        return _FakeLeaf([], argv, **kwargs)

    monkeypatch.setattr(tempfile, "mkstemp", recording_mkstemp)
    monkeypatch.setattr(subprocess, "Popen", launch_then_lose_the_stream)

    try:
        code = run_leaf.main(["prompt.txt"])
    except Exception as error:
        code = type(error).__name__
    err = capfd.readouterr().err

    assert (code, err) == (2, f"run-leaf.sh: {made[0]}: No such file or directory\n")


def test_main_makes_the_stream_then_the_git_config_temp_file_in_tmpdir_copies_the_gitconfig_into_it_launches_with_git_config_global_on_it_and_removes_both(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    home = tmp_path / "home"
    operator_config = tmp_path / "operator.gitconfig"
    operator_config.write_text("[user]\n\tname = operator\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "caller.gitconfig"))
    made = []
    real_mkstemp = tempfile.mkstemp

    def recording_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        made.append(path)
        return fd, path

    monkeypatch.setattr(tempfile, "mkstemp", recording_mkstemp)
    seen = []

    def launch(argv, *args, remove_stream=False, **kwargs):
        env = kwargs.get("env") or dict(os.environ)
        config = env.get("GIT_CONFIG_GLOBAL")
        seen.append((config == (made[1] if len(made) == 2 else None),
                     [os.path.exists(path) for path in made],
                     pathlib.Path(config).read_text() if config and os.path.isfile(config) else None))
        if remove_stream:
            os.remove(made[0])
        return _FakeLeaf([], argv, **kwargs)

    def refuse(argv, *args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory")

    answers = []
    for tmpdir, gitconfig, launcher in (
            (str(tmp), "symlink", launch),
            (str(tmp), None, launch),
            (None, None, launch),
            ("", None, launch),
            (str(tmp), None, refuse),
            (str(tmp), None, lambda argv, *a, **k: launch(argv, *a, remove_stream=True, **k))):
        made.clear()
        seen.clear()
        if tmpdir is None:
            monkeypatch.delenv("TMPDIR", raising=False)
        else:
            monkeypatch.setenv("TMPDIR", tmpdir)
        if (home / ".gitconfig").is_symlink():
            (home / ".gitconfig").unlink()
        if gitconfig:
            (home / ".gitconfig").symlink_to(operator_config)
        monkeypatch.setattr(subprocess, "Popen", launcher)
        try:
            code = run_leaf.main(["prompt.txt"])
        except Exception as error:
            code = type(error).__name__
        capfd.readouterr()
        answers.append((code, [os.path.dirname(path) for path in made], list(seen),
                        [os.path.exists(path) for path in made]))

    copied = "[user]\n\tname = operator\n"
    assert answers == [
        (0, [str(tmp)] * 2, [(True, [True, True], copied)], [False, False]),
        (0, [str(tmp)] * 2, [(True, [True, True], "")], [False, False]),
        (0, ["/tmp"] * 2, [(True, [True, True], "")], [False, False]),
        (0, ["/tmp"] * 2, [(True, [True, True], "")], [False, False]),
        (2, [str(tmp)] * 2, [], [False, False]),
        (2, [str(tmp)] * 2, [(True, [True, True], "")], [False, False]),
    ]


def test_main_strips_the_launched_environment_through_veri_session_env_so_a_name_added_to_its_session_vars_is_absent_from_the_leafs_environment(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
    monkeypatch.setenv("VERI_PLANTED_621", "from-the-conductor")
    monkeypatch.setenv("VERI_KEPT_621", "kept")
    for name in ("veri.session_env", "session_env"):
        session_env = importlib.import_module(name)
        monkeypatch.setattr(session_env, "SESSION_VARS", (*session_env.SESSION_VARS, "VERI_PLANTED_621"))
    seen = []

    def launch(argv, *args, **kwargs):
        env = kwargs.get("env") or dict(os.environ)
        seen.append((env.get("VERI_PLANTED_621"), env.get("VERI_KEPT_621")))
        return _FakeLeaf([], argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)
    code = run_leaf.main(["prompt.txt"])
    capfd.readouterr()

    assert (code, seen) == (0, [(None, "kept")])


def test_main_reads_claude_bin_and_veri_leaf_model_before_the_strip_sets_git_config_global_after_it_and_drops_the_shims_locale_guard_only_when_its_marker_is_set(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    session_id = "sess-1071-id"
    session_tmp = tmp_path / f"tmp-{session_id}"
    session_tmp.mkdir()
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
    monkeypatch.delenv("PYTHONCOERCECLOCALE", raising=False)
    monkeypatch.delenv("VERI_SHIM_SET_COERCE", raising=False)
    seen = []

    def launch(argv, *args, **kwargs):
        env = kwargs.get("env") or dict(os.environ)
        seen.append((argv[0], argv[argv.index("--model") + 1] if "--model" in argv else None,
                     env.get("GIT_CONFIG_GLOBAL") is not None,
                     env.get("PYTHONCOERCECLOCALE"), env.get("VERI_SHIM_SET_COERCE")))
        return _FakeLeaf([], argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)
    answers = []
    for settings in (
            {"CLAUDE_CODE_SESSION_ID": session_id, "TMPDIR": str(session_tmp),
             "CLAUDE_BIN": f"/stub/{session_id}/claude", "VERI_LEAF_MODEL": f"model-{session_id}"},
            {"PYTHONCOERCECLOCALE": "0", "VERI_SHIM_SET_COERCE": "1"},
            {"PYTHONCOERCECLOCALE": "1"}):
        with monkeypatch.context() as run:
            for name, value in settings.items():
                run.setenv(name, value)
            seen.clear()
            code = run_leaf.main(["prompt.txt"])
            capfd.readouterr()
            answers.append((code, list(seen)))

    assert answers == [
        (0, [(f"/stub/{session_id}/claude", f"model-{session_id}", True, None, None)]),
        (0, [("claude", None, True, None, None)]),
        (0, [("claude", None, True, "1", None)]),
    ]


_RUN_MAIN = """
import signal, sys
sys.path[:0] = sys.argv[1:3]
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
import veri.run_leaf
sys.exit(veri.run_leaf.main(sys.argv[3:]))
"""


@pytest.mark.process("SIGTERM reaching a real process group of a stub claude")
def test_main_launches_the_leaf_in_its_callers_process_group_with_sigpipe_and_sigxfsz_as_handed_and_on_sigterm_removes_both_temp_files(
        tmp_path, monkeypatch):
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    report = tmp_path / "report"
    stub = tmp_path / "claude"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"trap -p PIPE XFSZ > {shlex.quote(str(report))}\n"
        f"exec {shlex.quote(sys.executable)} -c "
        "'import os, sys, time; open(sys.argv[1], \"a\").write(\"pgid %d pid %d\\n\" % (os.getpgid(0), os.getpid())); "
        "print(\"{}\", flush=True); time.sleep(30)' "
        f"{shlex.quote(str(report))}\n")
    stub.chmod(0o755)
    monkeypatch.setenv("CLAUDE_BIN", str(stub))

    runner = subprocess.Popen(
        [sys.executable, "-c", _RUN_MAIN, str(SCRIPTS), str(SCRIPTS / "veri"), "prompt.txt"],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        start_new_session=True)
    leaf_pid = None
    try:
        ready, _, _ = select.select([runner.stdout], [], [], 10)
        first = runner.stdout.readline() if ready else b""
        lines = report.read_text().splitlines()
        leaf_pid = int(lines[-1].split()[3])
        os.killpg(runner.pid, signal.SIGTERM)
        runner.wait(timeout=10)
    finally:
        for pid in (runner.pid if runner.poll() is None else None, leaf_pid):
            if pid:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        runner.stdout.close()
        runner.wait()

    assert (first, lines, sorted(path.name for path in tmp.iterdir())) == (
        b"{}\n", ["trap -- '' SIGXFSZ", f"pgid {runner.pid} pid {leaf_pid}"], [])


_RESULT_STREAM = (b'{"type":"system","subtype":"init","session_id":"x"}\n'
                  b'{"type":"assistant","message":{"content":[{"type":"text","text":"VERDICT: PASS"}]}}\n'
                  b'{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}\n')


def _run_over(run_leaf, monkeypatch, capfdbinary, stream=_RESULT_STREAM, returncode=0):
    def launch(argv, *args, **kwargs):
        leaf = _FakeLeaf([], argv, stream=stream, **kwargs)
        leaf.returncode = returncode
        return leaf
    monkeypatch.setattr(subprocess, "Popen", launch)
    code = run_leaf.main(["prompt.txt"])
    return code, capfdbinary.readouterr().out


def test_main_returns_extracted_result_text(tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Verify the test for issue 3.")

    code, out = _run_over(run_leaf, monkeypatch, capfdbinary)

    assert (code, out.endswith(b"\nVERDICT: PASS\n")) == (0, True)


def test_main_streams_raw_events_for_heartbeat(tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Verify the test for issue 3.")

    code, out = _run_over(run_leaf, monkeypatch, capfdbinary)

    assert (code, out.startswith(_RESULT_STREAM)) == (0, True)


def test_main_propagates_leaf_exit_status(tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Verify the test for issue 3.")

    code, _ = _run_over(run_leaf, monkeypatch, capfdbinary, returncode=1)

    assert code == 1


def test_main_maps_a_foreign_leaf_exit_status_to_2(tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Verify the test for issue 3.")

    code, _ = _run_over(run_leaf, monkeypatch, capfdbinary, returncode=7)

    assert code == 2


def test_main_does_not_own_a_tdd_log(tmp_path, monkeypatch, capfdbinary):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Verify the test for issue 3.")

    code, _ = _run_over(run_leaf, monkeypatch, capfdbinary)

    assert (code, (work / ".tdd").exists()) == (0, False)


_SESSION_VARS_621 = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_HOST_SESSION_ID",
                     "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_PID",
                     "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_ENTRYPOINT")


def _cli_launch(run_cli, monkeypatch, tmp_path, env=None, unset=(), returncode=0,
                stream=_RESULT_STREAM):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
    for name in (*_SESSION_VARS_621, "CLAUDE_AUTO_BACKGROUND_TASKS",
                 "CLAUDE_CODE_REMOTE_SESSION_ID"):
        monkeypatch.delenv(name, raising=False)
    for name in unset:
        monkeypatch.delenv(name, raising=False)
    seen = []

    def launch(argv, *args, **kwargs):
        seen.append(dict(kwargs.get("env") or os.environ))
        leaf = _FakeLeaf([], argv, stream=stream, **kwargs)
        leaf.returncode = returncode
        return leaf

    monkeypatch.setattr(subprocess, "Popen", launch)
    code, out, err = run_cli(run_leaf, ["prompt.txt"], env=env, cwd=work)
    return code, out, err, seen


def test_cli_starts_claude_without_the_conductor_sessions_variables(
        tmp_path, monkeypatch, run_cli):
    env = {name: "from-the-conductor" for name in _SESSION_VARS_621}

    code, _, _, seen = _cli_launch(run_cli, monkeypatch, tmp_path, env=env)

    assert (code, len(seen), [n for n in _SESSION_VARS_621 if n in seen[0]]) == (0, 1, [])


def test_cli_starts_claude_without_claude_auto_background_tasks(tmp_path, monkeypatch, run_cli):
    code, _, _, seen = _cli_launch(run_cli, monkeypatch, tmp_path,
                                   env={"CLAUDE_AUTO_BACKGROUND_TASKS": "true"})

    assert (code, len(seen), "CLAUDE_AUTO_BACKGROUND_TASKS" in seen[0]) == (0, 1, False)


def test_cli_a_non_numeric_veri_timeout_exits_2_before_claude_with_one_stderr_line_naming_it_and_no_traceback_1939(
        tmp_path, monkeypatch, run_cli):
    code, _, err, seen = _cli_launch(run_cli, monkeypatch, tmp_path,
                                     env={"VERI_TIMEOUT": "abc"})

    assert (code, len(seen), err.count("\n"), "Traceback" in err) == (2, 0, 1, False)
    assert "VERI_TIMEOUT" in err, err


def test_cli_still_passes_veri_test_cmd_and_git_config_global_through_to_claude(
        tmp_path, monkeypatch, run_cli):
    code, _, _, seen = _cli_launch(run_cli, monkeypatch, tmp_path,
                                   env={"VERI_TEST_CMD": "make unit"})

    assert (code, len(seen), seen[0].get("VERI_TEST_CMD"),
            bool(seen[0].get("GIT_CONFIG_GLOBAL"))) == (0, 1, "make unit", True)


def test_cli_with_no_session_variable_set_exits_with_the_stubs_code_and_prints_the_same_stdout(
        tmp_path, monkeypatch, run_cli):
    want_out = _RESULT_STREAM.decode() + "\nVERDICT: PASS\n"
    answers = []
    for returncode in (0, 1, 2, 3, 7):
        scratch = tmp_path / f"c{returncode}"
        scratch.mkdir()
        code, out, err, _ = _cli_launch(run_cli, monkeypatch, scratch, returncode=returncode)
        answers.append((code, out == want_out, err))

    assert answers == [(0, True, ""), (1, True, ""), (2, True, ""), (3, True, ""), (2, True, "")]


def test_cli_with_the_session_id_unset_or_empty_strips_nothing_beyond_session_vars(
        tmp_path, monkeypatch, run_cli):
    kept = []
    for how in ("unset", "empty"):
        scratch = tmp_path / how
        scratch.mkdir()
        env = {"VERI_TEST_CMD": "make unit", "VERI_FAKE_CARRIER": "x-unrelated-y"}
        if how == "empty":
            env["CLAUDE_CODE_SESSION_ID"] = ""
        _, _, _, seen = _cli_launch(run_cli, monkeypatch, scratch, env=env)
        kept.append((seen[0].get("VERI_TEST_CMD"), seen[0].get("VERI_FAKE_CARRIER")))

    assert kept == [("make unit", "x-unrelated-y")] * 2


def test_cli_with_the_session_id_set_still_passes_veri_test_cmd_and_run_leafs_git_config_global_through(
        tmp_path, monkeypatch, run_cli):
    code, _, _, seen = _cli_launch(
        run_cli, monkeypatch, tmp_path,
        env={"CLAUDE_CODE_SESSION_ID": "sess-933-fake", "VERI_TEST_CMD": "make unit",
             "GIT_CONFIG_GLOBAL": "/from/the/caller"})
    config = seen[0].get("GIT_CONFIG_GLOBAL")

    assert (code, seen[0].get("VERI_TEST_CMD"), bool(config), config != "/from/the/caller") == (
        0, "make unit", True, True)


def test_cli_strips_a_variable_whose_value_contains_the_session_id_and_the_id_itself(
        tmp_path, monkeypatch, run_cli):
    code, _, _, seen = _cli_launch(
        run_cli, monkeypatch, tmp_path,
        env={"CLAUDE_CODE_SESSION_ID": "sess-933-fake", "FAKE_CARRIER": "x-sess-933-fake-y"})

    assert (code, [n for n in ("CLAUDE_CODE_SESSION_ID", "FAKE_CARRIER") if n in seen[0]]) == (0, [])


def test_cli_starts_claude_without_claude_code_remote_session_id_whose_value_need_not_contain_the_session_id(
        tmp_path, monkeypatch, run_cli):
    code, _, _, seen = _cli_launch(
        run_cli, monkeypatch, tmp_path,
        env={"CLAUDE_CODE_SESSION_ID": "sess-966-fake",
             "CLAUDE_CODE_REMOTE_SESSION_ID": "remote-unrelated-value"})

    assert (code, "CLAUDE_CODE_REMOTE_SESSION_ID" in seen[0]) == (0, False)


def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_reads_its_relative_prompt_and_prints_and_exits_as_in_place(
        tmp_path, monkeypatch, run_cli):
    import importlib.util
    importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "the prompt in the other working directory")
    (tmp_path / "skill").symlink_to(SCRIPTS.parent)
    launches = []

    def launch(argv, *args, **kwargs):
        leaf = _FakeLeaf(launches, argv, stream=_RESULT_STREAM, **kwargs)
        leaf.returncode = 3
        return leaf
    monkeypatch.setattr(subprocess, "Popen", launch)

    answers = {}
    for how, path in (("inplace", SCRIPTS / "veri" / "run_leaf.py"),
                      ("linked", tmp_path / "skill" / "scripts" / "veri" / "run_leaf.py")):
        spec = importlib.util.spec_from_file_location(f"run_leaf_{how}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        answers[how] = run_cli(module, ["prompt.txt"], cwd=work)

    assert ([argv[2] for argv in launches], answers["linked"] == answers["inplace"],
            answers["linked"][0]) == (["the prompt in the other working directory"] * 2, True, 3)


@pytest.mark.process("a real stub claude inheriting the signal dispositions its launcher was handed")
def test_cli_hands_claude_sigpipe_and_sigxfsz_as_its_caller_had_them_at_default_when_default_ignored_when_ignored(
        tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    stub = tmp_path / "claude"
    stub.write_text("#!/usr/bin/env bash\n"
                    'trap -p PIPE XFSZ > "$DISP_OUT"\n'
                    "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"ok\"}'\n")
    stub.chmod(0o755)
    monkeypatch.setenv("CLAUDE_BIN", str(stub))
    saved = {name: signal.getsignal(name) for name in (signal.SIGPIPE, signal.SIGXFSZ)}
    seen = {}
    try:
        for caller, shim in (("default", " PIPE XFSZ"), ("ignored", "")):
            for name in saved:
                signal.signal(name, signal.SIG_IGN)
            out = tmp_path / f"disp-{caller}"
            code, _, _ = run_cli(run_leaf, ["prompt.txt"], env={
                "DISP_OUT": str(out), "VERI_SHIM_DEFAULT_SIGNALS": shim})
            seen[caller] = (code, out.read_text())
    finally:
        for name, handler in saved.items():
            signal.signal(name, handler)

    assert seen == {"default": (0, ""),
                    "ignored": (0, "trap -- '' SIGPIPE\ntrap -- '' SIGXFSZ\n")}


_EXEC_WITH_DISPOSITION = """
import os, signal, sys
for name in ("SIGPIPE", "SIGXFSZ"):
    signal.signal(getattr(signal, name), getattr(signal, sys.argv[1]))
os.execv(sys.argv[2], sys.argv[2:])
"""


@pytest.mark.process("run-leaf.sh exec'd by a real caller holding SIGPIPE and SIGXFSZ default or ignored, deriving what a real stub claude inherits")
def test_cli_run_leaf_sh_hands_claude_sigpipe_and_sigxfsz_as_its_caller_had_them_at_default_when_default_ignored_when_ignored(
        tmp_path, monkeypatch, run_cli):
    work = _prompt_workspace(tmp_path, monkeypatch, "Verify the test for issue 3.")
    stub = _executable(tmp_path / "claude", "#!/usr/bin/env bash\n"
                       'trap -p PIPE XFSZ > "$DISP_OUT"\n' + _OK_RESULT_LINE)
    seen = {}
    for handed in ("SIG_DFL", "SIG_IGN"):
        out = tmp_path / f"disp-{handed}"

        class _Caller:
            @staticmethod
            def main(argv):
                return subprocess.run(
                    [sys.executable, "-c", _EXEC_WITH_DISPOSITION, handed,
                     str(SCRIPTS / "run-leaf.sh"), *argv],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL).returncode

        code, _, _ = run_cli(_Caller, ["prompt.txt"], cwd=work,
                             env={"CLAUDE_BIN": str(stub), "DISP_OUT": str(out)})
        seen[handed] = (code, out.read_text() if out.exists() else None)

    assert seen == {"SIG_DFL": (0, ""),
                    "SIG_IGN": (0, "trap -- '' SIGPIPE\ntrap -- '' SIGXFSZ\n")}


@pytest.mark.process("a real python3 started by a stub claude importing a module mutated and reverted in one mtime second")
def test_cli_under_a_leaf_a_python_module_mutated_and_reverted_at_the_same_whole_second_mtime_and_size_is_re_read_from_source(
        tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    pyc = tmp_path / "pyc"
    pyc.mkdir()
    (pyc / "mod.py").write_text("ANSWER = 1\n")
    os.utime(pyc / "mod.py", (1672531200, 1672531200))
    stub = tmp_path / "claude"
    py = shlex.quote(sys.executable)
    stub.write_text(
        "#!/bin/sh\n"
        'cd "$MOD_DIR" || exit 2\n'
        "same_second='import os, sys; open(\"mod.py\", \"w\").write(sys.argv[1]); "
        "os.utime(\"mod.py\", (1700000100, 1700000100))'\n"
        f"{py} -c 'import mod; print(mod.ANSWER)' > before\n"
        f"{py} -c \"$same_second\" 'ANSWER = 2\n'\n"
        f"{py} -c 'import mod; print(mod.ANSWER)' > mutated\n"
        f"{py} -c \"$same_second\" 'ANSWER = 1\n'\n"
        f"{py} -c 'import mod; print(mod.ANSWER)' > after\n"
        "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"ok\"}'\n")
    stub.chmod(0o755)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)

    code, _, _ = run_cli(run_leaf, ["prompt.txt"],
                         env={"CLAUDE_BIN": str(stub), "MOD_DIR": str(pyc)})

    assert (code, [(pyc / name).read_text().strip() for name in ("before", "mutated", "after")]) == (
        0, ["1", "2", "1"])


def test_cli_hands_the_leaf_pythondontwritebytecode_1_whether_the_caller_left_it_unset_set_it_to_0_or_set_it_empty(
        tmp_path, monkeypatch, run_cli):
    handed = []
    for caller in ("unset", "0", "empty"):
        scratch = tmp_path / caller
        scratch.mkdir()
        if caller == "unset":
            _, _, _, seen = _cli_launch(run_cli, monkeypatch, scratch, unset=("PYTHONDONTWRITEBYTECODE",))
        else:
            _, _, _, seen = _cli_launch(run_cli, monkeypatch, scratch,
                                        env={"PYTHONDONTWRITEBYTECODE": "0" if caller == "0" else ""})
        handed.append(seen[0].get("PYTHONDONTWRITEBYTECODE"))

    assert handed == ["1", "1", "1"]


@pytest.mark.process("a real python3 started by a stub claude importing from a tree")
def test_cli_a_python_process_under_a_leaf_writes_no_pyc_into_the_tree_it_imports_from(
        tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    tree = tmp_path / "tree"
    (tree / "pkg").mkdir(parents=True)
    (tree / "mod.py").write_text("ANSWER = 1\n")
    (tree / "pkg" / "__init__.py").write_text("")
    (tree / "pkg" / "sub.py").write_text("ANSWER = 2\n")
    stub = tmp_path / "claude"
    stub.write_text(
        "#!/bin/sh\n"
        'cd "$MOD_DIR" || exit 2\n'
        f"{shlex.quote(sys.executable)} -c 'import mod, pkg.sub; print(mod.ANSWER + pkg.sub.ANSWER)' > ../answer\n"
        "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"ok\"}'\n")
    stub.chmod(0o755)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)

    code, _, _ = run_cli(run_leaf, ["prompt.txt"],
                         env={"CLAUDE_BIN": str(stub), "MOD_DIR": str(tree)})

    assert (code, (tmp_path / "answer").read_text().strip(), sorted(tree.rglob("*.pyc"))) == (0, "3", [])


_OK_RESULT_LINE = "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"ok\"}'\n"
_RULE_PHRASES = ("signal only processes you started", "by the pid you recorded")


def _executable(path, text):
    path.write_text(text)
    path.chmod(0o755)
    return path


def _leaf_stub(tmp_path, body):
    return _executable(tmp_path / "claude", "#!/bin/sh\n" + body + _OK_RESULT_LINE)


@pytest.mark.process("a real stub claude running pkill and killall through the leaf-guard scripts on its PATH")
def test_cli_refuses_a_leafs_pkill_and_killall_before_they_signal_anything_naming_the_rule(
        tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    tools = tmp_path / "tools"
    tools.mkdir()
    for tool in ("pkill", "killall"):
        _executable(tools / tool, f'#!/bin/sh\nprintf "%s\\n" "$*" > "{tmp_path}/{tool}-ran"\n')
    stub = _leaf_stub(tmp_path,
                      "pkill -n -f 'exp-sleep 60' > \"$SIG_DIR/pkill-out\" 2>&1\n"
                      "killall exp-sleep > \"$SIG_DIR/killall-out\" 2>&1\n")
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")

    code, _, _ = run_cli(run_leaf, ["prompt.txt"],
                         env={"CLAUDE_BIN": str(stub), "SIG_DIR": str(tmp_path)})

    problems = []
    for tool in ("pkill", "killall"):
        if (tmp_path / f"{tool}-ran").exists():
            problems.append(f"{tool} reached the signalling tool")
        said = (tmp_path / f"{tool}-out").read_text().lower()
        problems += [f"{tool} printed no {phrase!r}: {said!r}"
                     for phrase in _RULE_PHRASES if phrase not in said]
    assert (code, problems) == (0, [])


@pytest.mark.process("a real stub claude running kill $(pgrep ...) and a script running pgrep -g through the leaf-guard scripts")
def test_cli_refuses_a_leafs_kill_of_a_pgrep_substitution_naming_the_rule_while_a_script_the_leaf_runs_still_reaches_pgrep_g(
        tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    tools = tmp_path / "tools"
    tools.mkdir()
    _executable(tools / "pgrep", f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{tmp_path}/pgrep-ran"\n')
    _executable(tmp_path / "suite.sh",
                f'#!/bin/sh\npgrep -g 0\nprintf "%s\\n" "$?" > "{tmp_path}/suite-exit"\n')
    stub = _leaf_stub(tmp_path,
                      "{ kill $(pgrep -f 'exp-sleep 60'); } > \"$PG_DIR/kill-out\" 2>&1\n"
                      "\"$PG_DIR/suite.sh\"\n")
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")

    code, _, _ = run_cli(run_leaf, ["prompt.txt"],
                         env={"CLAUDE_BIN": str(stub), "PG_DIR": str(tmp_path)})

    ran = (tmp_path / "pgrep-ran").read_text().splitlines() if (tmp_path / "pgrep-ran").exists() else []
    said = (tmp_path / "kill-out").read_text().lower()
    assert (code, [line for line in ran if "-f exp-sleep 60" in line],
            [phrase for phrase in _RULE_PHRASES if phrase not in said],
            "-g 0" in ran, (tmp_path / "suite-exit").read_text().strip()) == (0, [], [], True, "0")


@pytest.mark.process("a real stub claude killing a real sleep it started and recorded the pid of")
def test_cli_a_leaf_can_still_kill_a_pid_it_started_and_recorded(tmp_path, monkeypatch, run_cli):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "do the step\n")
    stub = _leaf_stub(tmp_path,
                      "bash -c 'sleep 30 & pid=$!\n"
                      "env kill \"$pid\" 2> \"$OWN_DIR/kill-err\"; status=$?\n"
                      "printf \"%s\\n\" \"$status\" > \"$OWN_DIR/kill-exit\"\n"
                      "[ \"$status\" = 0 ] || /bin/kill \"$pid\"\n"
                      "wait \"$pid\"; printf \"%s\\n\" \"$?\" > \"$OWN_DIR/wait-exit\"'\n")

    code, _, _ = run_cli(run_leaf, ["prompt.txt"],
                         env={"CLAUDE_BIN": str(stub), "OWN_DIR": str(tmp_path)})

    assert (code, [(tmp_path / name).read_text().strip() for name in ("kill-exit", "wait-exit")]) == (
        0, ["0", "143"])


def _prompt_workspace(tmp_path, monkeypatch, prompt):
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, prompt)
    return work


def _cli_argv(run_cli, monkeypatch, tmp_path, prompt_arg, extra=(), stdin=""):
    run_leaf = importlib.import_module("veri.run_leaf")
    work = _prompt_workspace(tmp_path, monkeypatch, "Verify the test for issue 3.")
    launches = []

    def launch(argv, *args, **kwargs):
        return _FakeLeaf(launches, argv, stream=_RESULT_STREAM, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)

    class _BytesStdin:
        @staticmethod
        def main(argv):
            sys.stdin = io.TextIOWrapper(io.BytesIO(stdin.encode()))
            return run_leaf.main(argv)

    code, out, _ = run_cli(_BytesStdin, [prompt_arg, *extra], cwd=work)
    return code, out, launches


def test_cli_passes_the_prompt_to_claude_via_dash_p_in_stream_json(tmp_path, monkeypatch, run_cli):
    code, out, launches = _cli_argv(run_cli, monkeypatch, tmp_path, "prompt.txt")

    assert (code, out.endswith("\nVERDICT: PASS\n"), [a[:6] for a in launches], len(launches)) == (
        0, True, [["claude", "-p", "Verify the test for issue 3.",
                   "--output-format", "stream-json", "--verbose"]], 1)


@pytest.mark.process("the run-leaf.sh entry point handing its arguments to a real stub claude")
def test_cli_passes_extra_arguments_through_to_claude(tmp_path, monkeypatch, run_cli):
    work = _prompt_workspace(tmp_path, monkeypatch, "Verify the test for issue 3.")
    stub = _leaf_stub(tmp_path, 'printf "%s\\n" "$@" > "$ARGV_OUT"\n')

    class _EntryPoint:
        @staticmethod
        def main(argv):
            return subprocess.run([str(SCRIPTS / "run-leaf.sh"), *argv], stdin=subprocess.DEVNULL).returncode

    code, _, _ = run_cli(_EntryPoint, ["prompt.txt", "--allowed-tools", "Read,Bash"], cwd=work,
                         env={"CLAUDE_BIN": str(stub), "ARGV_OUT": str(tmp_path / "argv")})

    assert (code, (tmp_path / "argv").read_text().splitlines()[-2:]) == (
        0, ["--allowed-tools", "Read,Bash"])


def test_cli_reads_the_prompt_from_stdin_on_dash(tmp_path, monkeypatch, run_cli):
    code, _, launches = _cli_argv(run_cli, monkeypatch, tmp_path, "-", stdin="piped prompt body")

    assert (code, [argv[2] for argv in launches]) == (0, ["piped prompt body"])


def _run_with_operator_gitconfig(tmp_path, monkeypatch, run_cli, gitconfig, stub_body):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, _ = _workspace(tmp_path, monkeypatch)
    _write_prompt(work, "Write the failing test for issue 276.")
    home = tmp_path / "home"
    (home / ".gitconfig").write_bytes(gitconfig)
    stub = _executable(tmp_path / "claude", "#!/bin/sh\n" + stub_body +
        "printf '%s\\n' '{\"type\":\"system\",\"subtype\":\"init\",\"session_id\":\"x\"}'\n"
        "printf '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"%s\"}\\n' \"$note\"\n")
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)

    code, out, _ = run_cli(run_leaf, ["prompt.txt"], cwd=work, env={
        "CLAUDE_BIN": str(stub), "XDG_CONFIG_HOME": str(home / ".config")})
    return (home / ".gitconfig").read_bytes(), code, out


@pytest.mark.process("a real git run by a stub claude writing and reading the leaf's private global config")
def test_cli_a_leafs_git_config_global_write_leaves_the_operators_global_config_byte_identical_and_the_leaf_reads_it_back(
        tmp_path, monkeypatch, run_cli):
    before = b"[user]\n\tname = Operator\n"

    after, code, out = _run_with_operator_gitconfig(tmp_path, monkeypatch, run_cli, before,
        "git config --global veri.probe wrote-it 2>/dev/null || true\n"
        "readback=\"$(git config --global --get veri.probe 2>/dev/null)\" || readback='<unset>'\n"
        "note=\"read-back: $readback\"\n")

    assert (after, code, "read-back: wrote-it" in out) == (before, 0, True)


@pytest.mark.process("a real git run by a stub claude reading the leaf's private global config")
def test_cli_a_leafs_private_global_git_config_starts_as_a_copy_of_the_operators_so_a_key_there_is_visible_to_the_leaf(
        tmp_path, monkeypatch, run_cli):
    before = b"[user]\n\tname = Operator\n[credential]\n\thelper = veri-test-helper\n"

    after, code, out = _run_with_operator_gitconfig(tmp_path, monkeypatch, run_cli, before,
        "seen=\"$(git config --global --get credential.helper 2>/dev/null)\" || seen='<unset>'\n"
        "note=\"sees: $seen\"\n")

    assert (after, code, "sees: veri-test-helper" in out) == (before, 0, True)
