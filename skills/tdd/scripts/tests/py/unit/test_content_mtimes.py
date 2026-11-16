"""In-process cases for veri/content_mtimes.py, which stamps each tracked file's mtime from its blob id."""
import importlib
import os

import pytest


@pytest.fixture
def content_mtimes():
    return importlib.import_module("veri.content_mtimes")


def test_run_outside_a_git_working_tree_exits_2_with_one_stderr_line_and_changes_no_file_3922(
        content_mtimes, run_cli, fake_processes, tmp_path):
    fake_processes.answers({"git": (128, "", "fatal: not a git repository (or any of the parent directories): .git\n")})
    kept = tmp_path / "kept.py"
    kept.write_text("x = 1\n")
    os.utime(kept, (1500000000, 1500000000))

    code, out, err = run_cli(content_mtimes, [], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), os.stat(kept).st_mtime) == (2, "", 1, 1500000000), err
