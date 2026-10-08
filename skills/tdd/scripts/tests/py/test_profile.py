"""In-process cases for veri/profile.py, the module profile.sh is a shim over."""
import importlib
import os
import subprocess

import pytest


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


def test_main_runs_each_suite_under_a_traced_bash_and_every_line_through_one_sort(tmp_path, monkeypatch, capsys, profile):
    import tempfile

    traces = {"a.test.sh": "++10.000000 2 x=1\n++11.000000 3 x=2\n++12.000000 4 pass=1\n",
              "b.test.sh": "++20.000000 2 pass=1\n"}
    for suite in traces:
        (tmp_path / suite).write_text("pass=0\n")
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    monkeypatch.delenv("BASH_XTRACEFD", raising=False)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    devnull = os.stat("/dev/null")

    def is_devnull(handle):
        if handle == subprocess.DEVNULL:
            return True
        fd = handle if isinstance(handle, int) and handle >= 0 else getattr(handle, "fileno", lambda: -1)()
        if fd < 0:
            return False
        st = os.fstat(fd)
        return (st.st_dev, st.st_ino) == (devnull.st_dev, devnull.st_ino)

    def fake(sort_status):
        seen = {"calls": [], "env": [], "devnull": [], "trace": [], "sort_input": []}

        def fake_run(args, **kwargs):
            program = os.path.basename(str(args[0]))
            seen["calls"].append([program] + [str(a) for a in args[1:]])
            if program == "bash":
                env = kwargs.get("env")
                seen["env"].append((os.environ if env is None else env).get("BASH_XTRACEFD"))
                seen["devnull"].append([is_devnull(kwargs.get(k)) for k in ("stdin", "stdout", "stderr")])
                inherited = 9 in kwargs.get("pass_fds", ()) or kwargs.get("close_fds") is False
                if inherited:
                    st = os.fstat(9)
                    held = [os.stat(scratch / name).st_ino for name in os.listdir(scratch)]
                    seen["trace"].append((st.st_size, held == [st.st_ino]))
                    os.write(9, traces[str(args[-1])].encode())
                else:
                    seen["trace"].append(None)
                return subprocess.CompletedProcess(args, 1 if args[-1] == "a.test.sh" else 0, None, None)
            if program == "sort":
                text = kwargs.get("input") or ""
                seen["sort_input"].append(text.decode() if isinstance(text, bytes) else text)
                out = "printed as it is\n"
                return subprocess.CompletedProcess(args, sort_status, out.encode() if isinstance(text, bytes) else out, None)
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        return seen

    traced = 'PS4=\'+${EPOCHREALTIME} ${LINENO} \'; set -x; . "$0"'
    seen = fake(0)
    code = profile.main(["a.test.sh", "b.test.sh"])
    captured = capsys.readouterr()
    assert seen["calls"] == [["bash", "-c", traced, "a.test.sh"], ["bash", "-c", traced, "b.test.sh"], ["sort", "-rn"]]
    assert seen["env"] == ["9", "9"]
    assert seen["devnull"] == [[True, True, True], [True, True, True]]
    assert seen["trace"] == [(0, True), (0, True)]
    assert sorted(seen["sort_input"][0].splitlines()) == [
        "0.000000 b.test.sh case 1 L2-2", "2.000000 a.test.sh case 1 L2-4"]
    assert (code, captured.out) == (0, "printed as it is\n")
    assert os.listdir(scratch) == []

    for status, answer in ((3, 3), (1, 1), (5, 2), (141, 2)):
        seen = fake(status)
        code = profile.main(["a.test.sh", "b.test.sh"])
        captured = capsys.readouterr()
        assert (status, code, captured.out) == (status, answer, "printed as it is\n")
        assert os.listdir(scratch) == []


def test_main_reads_only_double_plus_lines_and_cuts_a_case_where_a_three_field_counter_rises_above_its_last_value(tmp_path, monkeypatch, capsys, profile):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "grammar.test.sh").write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    fake_processes(monkeypatch, trace=(
        "++ 2 x=0\n"
        "+10.000000 3 pass=1\n"
        "++10.000000 4 x=1\n"
        "+++10.500000 5 pass=9\n"
        "++11.000000 6 pass=7\n"
        "++12.000000 7 pass=3\n"
        "++13.000000 8 pass=5 extra\n"
        "++14.000000 9 pass=4\n"))
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    code = profile.main(["sub/grammar.test.sh"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (
        0, "1.000000 sub/grammar.test.sh case 1 L2-6\n3.000000 sub/grammar.test.sh case 2 L7-9\n")


def test_main_ends_the_run_at_a_suite_with_no_counter_still_sorting_the_lines_before_it(tmp_path, monkeypatch, capsys, profile):
    traces = {"a.test.sh": "++10.000000 2 x=1\n++12.000000 3 pass=1\n",
              "none.test.sh": "++20.000000 2 x=1\n",
              "c.test.sh": "++30.000000 2 pass=1\n"}
    for suite in traces:
        (tmp_path / suite).write_text("pass=0\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_PROFILE_THRESHOLD", "0")
    calls = []

    def fake_run(args, **kwargs):
        program = os.path.basename(str(args[0]))
        calls.append([program, str(args[-1])])
        if program == "bash":
            if 9 in kwargs.get("pass_fds", ()):
                os.write(9, traces.get(str(args[-1]), "").encode())
            return subprocess.CompletedProcess(args, 0, "", "")
        if program == "sort":
            text = kwargs.get("input") or ""
            return subprocess.CompletedProcess(args, 0, text.decode() if isinstance(text, bytes) else text, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    code = profile.main(["a.test.sh", "none.test.sh", "c.test.sh"])
    captured = capsys.readouterr()
    assert calls == [["bash", "a.test.sh"], ["bash", "none.test.sh"], ["sort", "-rn"]]
    assert (code, captured.out, captured.err) == (
        2, "2.000000 a.test.sh case 1 L2-3\n",
        "profile.sh: none.test.sh: no pass=/fail= increment in its trace\n")

    del calls[:]
    code = profile.main(["missing.test.sh"])
    captured = capsys.readouterr()
    assert calls == [["bash", "missing.test.sh"], ["sort", "-rn"]]
    assert (code, captured.out, captured.err) == (
        2, "", "profile.sh: missing.test.sh: no pass=/fail= increment in its trace\n")
