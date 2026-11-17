"""Cases for veri/fused.py that start a real process: run_script's stdin and its file redirections."""
import importlib

import pytest


@pytest.mark.process("a real sh whose stdout and stderr fused.run_script sends to files")
def test_run_script_sends_stdout_and_stderr_to_the_named_files_and_returns_them_empty(tmp_path):
    fused = importlib.import_module("veri.fused")

    got = fused.run_script("/bin/sh", "-c", "echo out; echo err >&2; exit 4", cwd=str(tmp_path), out="o.txt",
                           err="e.txt")

    assert got == (4, "", "")
    assert ((tmp_path / "o.txt").read_text(), (tmp_path / "e.txt").read_text()) == ("out\n", "err\n")


@pytest.mark.process("a real sh reading the stdin fused.run_script feeds it")
def test_run_script_feeds_stdin_and_captures_what_is_not_redirected(tmp_path):
    fused = importlib.import_module("veri.fused")

    assert fused.run_script("/bin/sh", "-c", "wc -l | tr -d ' '; echo e >&2", stdin="a\nb\n",
                            cwd=str(tmp_path)) == (0, "2\n", "e\n")
