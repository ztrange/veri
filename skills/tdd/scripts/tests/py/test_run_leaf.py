"""In-process cases for veri/run_leaf.py, the module run-leaf.sh is a shim over."""
import importlib
import io
import os
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def test_main_without_a_prompt_argument_refuses_with_the_usage_line_before_any_temp_file_or_launch(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp):
        path.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
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
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp):
        path.mkdir()
    (work / "prompt.txt").write_text("do the step\n")
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
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
        launched.append((launches, [want]))

    assert [got for got, _ in launched] == [want for _, want in launched]


def test_main_reads_the_prompt_from_a_relative_file_or_stdin_as_bytes_and_refuses_a_missing_file_or_a_directory_with_1(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp, work / "sub", work / "adir"):
        path.mkdir()
    (work / "sub" / "p.txt").write_bytes(b"line one\nline two\n\n\n")
    (work / "raw.txt").write_bytes(b"a\x00b\xff\xfec\n\n")
    stdin_file = tmp_path / "stdin"
    stdin_file.write_bytes(b"from stdin\n\n")
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    monkeypatch.delenv("CLAUDE_BIN", raising=False)
    monkeypatch.delenv("VERI_LEAF_MODEL", raising=False)

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
        ("nope.txt", 1, "", []),
        ("adir", 1, "", []),
    ]


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
    work, home, tmp = (tmp_path / name for name in ("work", "home", "tmp"))
    for path in (work, home, tmp):
        path.mkdir()
    (work / "prompt.txt").write_text("do the step\n")
    monkeypatch.chdir(work)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("TMPDIR", str(tmp))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    monkeypatch.delenv("CLAUDE_BIN", raising=False)
    monkeypatch.delenv("VERI_LEAF_MODEL", raising=False)
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
