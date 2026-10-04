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


def fake_processes(monkeypatch, trace=""):
    """subprocess.run recording each command, its program by basename: a traced bash that
    writes `trace` to the fd 9 it is handed, and a sort that hands its input back."""
    calls = []

    def fake_run(args, **kwargs):
        program = os.path.basename(str(args[0]))
        calls.append([program] + [str(a) for a in args[1:]])
        if program == "bash":
            if trace and 9 in kwargs.get("pass_fds", ()):
                os.write(9, trace.encode())
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


@pytest.mark.parametrize("threshold", ["1.", ".5", "1e3", " 1"])
def test_main_refuses_a_threshold_that_is_not_digits_with_an_optional_fraction(threshold, tmp_path, monkeypatch, capsys, profile):
    suite = tmp_path / "a.test.sh"
    suite.write_text("pass=0\n")
    calls = fake_processes(monkeypatch)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", threshold)
    code = profile.main([str(suite)])
    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got '%s'\n" % threshold)


def test_main_prints_each_case_as_secs_suite_case_n_and_its_line_range(tmp_path, monkeypatch, capsys, profile):
    (tmp_path / "format.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    fake_processes(monkeypatch, trace=(
        "++10.000000 2 pass=0\n"
        "++10.000000 2 fail=0\n"
        "++10.000000 3 EPOCHREALTIME=10.000000\n"
        "++10.000000 4 pass=1\n"
        "++10.000000 5 EPOCHREALTIME=11.000000\n"
        "++11.000000 6 x=1\n"
        "++11.000000 7 EPOCHREALTIME=13.000000\n"
        "++13.000000 8 pass=2\n"))
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    code = profile.main(["format.test.sh"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (
        0, "0.000000 format.test.sh case 1 L2-4\n3.000000 format.test.sh case 2 L5-8\n")


def test_main_prints_a_case_when_its_seconds_reach_the_threshold_default_1(tmp_path, monkeypatch, capsys, profile):
    def trace(*secs):
        lines, stamp = [], 10.0
        for n, d in enumerate(secs, 1):
            lines.append("++%.6f %d x=%d\n" % (stamp, 2 * n, n))
            stamp += d
            lines.append("++%.6f %d pass=%d\n" % (stamp, 2 * n + 1, n))
        return "".join(lines)

    def printed(threshold):
        monkeypatch.setenv("VERI_PROFILE_THRESHOLD", threshold)
        code = profile.main(["t.test.sh"])
        out = capsys.readouterr().out
        ordered = sorted(out.splitlines(), key=lambda line: float(line.split()[0]), reverse=True)
        return code, [int(line.split()[3]) for line in ordered]

    (tmp_path / "t.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)

    fake_processes(monkeypatch, trace=trace(1.0, 0.9))
    assert printed("") == (0, [1])

    fake_processes(monkeypatch, trace=trace(0.25, 2.0, 5.0, 3.0))
    assert printed("0") == (0, [3, 4, 2, 1])
    assert printed("1") == (0, [3, 4, 2])
    assert printed("2.5") == (0, [3, 4])
    assert printed("4") == (0, [3])
