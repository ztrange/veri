"""In-process cases for veri/profile.py, the module profile.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def profile():
    return importlib.import_module("veri.profile")


def fake_processes(monkeypatch):
    """subprocess.run recording each command, its program by basename: a traced bash that
    writes no trace line, and a sort that hands its input back."""
    calls = []

    def fake_run(args, **kwargs):
        program = os.path.basename(str(args[0]))
        calls.append([program] + [str(a) for a in args[1:]])
        if program == "bash":
            return subprocess.CompletedProcess(args, 0, "", "")
        if program == "sort":
            text = kwargs.get("input") or ""
            if isinstance(text, bytes):
                text = text.decode()
            return subprocess.CompletedProcess(args, 0, text, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_refuses_a_bad_threshold_answers_nothing_for_no_suite_and_refuses_a_suite_with_no_counter(tmp_path, monkeypatch, capsys, profile):
    suite = tmp_path / "a.test.sh"
    suite.write_text("pass=0\n")

    calls = fake_processes(monkeypatch)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "abc")
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got 'abc'\n")

    monkeypatch.delenv("VERI_PROFILE_THRESHOLD")
    code = profile.main([])
    captured = capsys.readouterr()
    assert calls == [["sort", "-rn"]]
    assert (code, captured.out) == (0, "")

    del calls[:]
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls[0][0] == "bash" and calls[0][-1] == str(suite)
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: %s: no pass=/fail= increment in its trace\n" % suite)
