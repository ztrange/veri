"""In-process cases for veri/run_leaf.py, the module run-leaf.sh is a shim over."""
import importlib
import io
import os
import pathlib
import select
import subprocess
import sys
import tempfile
import threading
import time

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
    (work / "prompt.txt").write_text("do the step\n")
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
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
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
    (work / "prompt.txt").write_text("do the step\n")
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
    (work / "prompt.txt").write_text("do the step\n")

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


def test_main_when_copying_a_regular_gitconfig_into_the_leafs_temp_file_fails_returns_1_launches_nothing_and_leaves_no_temp_file(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
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
    assert (code, launches, left) == (1, [], [])


def test_main_when_a_gitconfig_that_was_a_regular_file_cannot_be_read_as_one_returns_1_launches_nothing_and_leaves_neither_temp_file(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
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

    assert (code, launches, sorted(tmp.iterdir())) == (1, [], [])


def test_main_makes_the_stream_then_the_git_config_temp_file_in_tmpdir_copies_the_gitconfig_into_it_launches_with_git_config_global_on_it_and_removes_both(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
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
        (1, [str(tmp)] * 2, [(True, [True, True], "")], [False, False]),
    ]


def test_main_strips_the_launched_environment_through_veri_session_env_so_a_name_added_to_its_session_vars_is_absent_from_the_leafs_environment(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
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


def test_main_strips_after_git_config_global_is_set_and_before_claude_bin_and_veri_leaf_model_are_read_and_drops_the_shims_locale_guard_only_when_its_marker_is_set(
        tmp_path, monkeypatch, capfd):
    run_leaf = importlib.import_module("veri.run_leaf")
    work, tmp = _workspace(tmp_path, monkeypatch)
    (work / "prompt.txt").write_text("do the step\n")
    session_id = "sess-1071-id"
    session_tmp = tmp_path / f"tmp-{session_id}"
    session_tmp.mkdir()
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
    monkeypatch.delenv("PYTHONCOERCECLOCALE", raising=False)
    monkeypatch.delenv("VERI_SHIM_SET_COERCE", raising=False)
    seen = []

    def launch(argv, *args, **kwargs):
        env = kwargs.get("env") or dict(os.environ)
        seen.append((argv[0], "--model" in argv, env.get("GIT_CONFIG_GLOBAL") is not None,
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
        (0, [("claude", False, False, None, None)]),
        (0, [("claude", False, True, None, None)]),
        (0, [("claude", False, True, "1", None)]),
    ]
