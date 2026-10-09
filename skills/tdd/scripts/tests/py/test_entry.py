"""In-process cases for veri/entry.py, the one __main__ entry point every ported module calls."""
import errno
import importlib
import importlib.util
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.fixture
def entry():
    return importlib.import_module("veri.entry")


def test_run_exits_with_the_code_main_returns_and_lets_a_raised_system_exit_through_unchanged_1150(entry):
    for code in (0, 1, 2, 3):
        seen = []

        def returns(argv, _code=code):
            seen.append(argv)
            return _code

        with pytest.raises(SystemExit) as exited:
            entry.run(returns, ["--flag", "value"])
        assert (exited.value.code, seen) == (code, [["--flag", "value"]])

    def raises(argv):
        raise SystemExit(7)

    with pytest.raises(SystemExit) as exited:
        entry.run(raises, [])
    assert exited.value.code == 7


def test_run_turns_an_exception_escaping_main_into_exit_2_and_one_stderr_line_named_for_the_shim_1150(tmp_path, capsys):
    source = tmp_path / "render_leaf_log.py"
    source.write_text(
        "from veri import entry\n"
        "\n"
        "\n"
        "def main(argv):\n"
        "    raise ValueError('first line\\nsecond line')\n"
        "\n"
        "\n"
        "def go(argv):\n"
        "    entry.run(main, argv)\n"
    )
    spec = importlib.util.spec_from_file_location("render_leaf_log", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(SystemExit) as exited:
        module.go([])
    out, err = capsys.readouterr()
    lines = err.splitlines()

    assert exited.value.code == 2
    assert len(lines) == 1, err
    assert lines[0].startswith("render-leaf-log.sh: ValueError: first line"), err
    assert "second line" in lines[0], err
    assert "Traceback" not in err


def test_run_flushes_stdout_inside_its_guard_so_a_failed_write_exits_2_with_one_stderr_line_1150(entry, monkeypatch, capsys):
    class FullStdout:
        def write(self, text):
            return len(text)

        def flush(self):
            raise OSError(errno.ENOSPC, "No space left on device")

    def main(argv):
        sys.stdout.write("an answer\n")
        return 0

    monkeypatch.setattr(sys, "stdout", FullStdout())
    with pytest.raises(SystemExit) as exited:
        entry.run(main, [])
    monkeypatch.undo()
    out, err = capsys.readouterr()
    lines = err.splitlines()

    assert exited.value.code == 2
    assert len(lines) == 1, err
    assert lines[0].startswith("test-entry.sh: OSError: "), err
    assert "No space left on device" in lines[0], err
    assert "Traceback" not in err


def test_run_turns_a_broken_pipe_on_stdout_into_exit_141_with_nothing_on_stdout_or_stderr_1150(entry, monkeypatch, capsys):
    class ClosedPipe:
        def write(self, text):
            return len(text)

        def flush(self):
            raise BrokenPipeError(errno.EPIPE, "Broken pipe")

    def main(argv):
        sys.stdout.write("an answer\n")
        return 0

    monkeypatch.setattr(sys, "stdout", ClosedPipe())
    with pytest.raises(SystemExit) as exited:
        entry.run(main, [])
    monkeypatch.undo()
    out, err = capsys.readouterr()

    assert exited.value.code == 141
    assert (out, err) == ("", "")


def test_run_leaves_nothing_for_shutdown_to_flush_so_a_real_closed_pipe_still_exits_141_with_an_empty_stderr_1150():
    program = (
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "from veri import entry\n"
        "def main(argv):\n"
        "    sys.stdout.write('an answer\\n')\n"
        "    return 0\n"
        "entry.run(main, [])\n"
    )
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        run = subprocess.run([sys.executable, "-c", program], stdin=subprocess.DEVNULL, stdout=write_end,
                             stderr=subprocess.PIPE, timeout=10)
    finally:
        os.close(write_end)

    assert (run.returncode, run.stderr.decode()) == (141, "")
