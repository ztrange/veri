"""In-process cases for veri/near_duplicates.py, the module near-duplicates.sh is a shim over."""
import importlib

import pytest

USAGE = "usage: near-duplicates.sh <commit>\n"


@pytest.fixture
def near_duplicates():
    return importlib.import_module("veri.near_duplicates")


def test_main_with_no_commit_returns_2_with_the_usage_line_on_stderr(capsys, near_duplicates, fake_processes):
    fake_processes()

    code = near_duplicates.main([])
    captured = capsys.readouterr()

    assert (code, captured.out) == (2, "")
    assert captured.err.endswith(USAGE)


def test_main_with_an_unresolvable_commit_returns_2_with_the_usage_line_on_stderr(
        monkeypatch, tmp_path, capsys, near_duplicates, fake_processes):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers({"git rev-parse --verify --quiet": (1, "", "")}, default=(0, "", ""))

    code = near_duplicates.main(["deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"])
    captured = capsys.readouterr()

    assert (code, captured.out) == (2, "")
    assert captured.err.endswith(USAGE)
