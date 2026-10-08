"""In-process cases for veri/structural_predicate.py, the module structural-predicate.sh is a shim over."""
import importlib
import io
import os
import subprocess
import sys

import pytest

USAGE = "usage: structural-predicate.sh <record>\n"


@pytest.fixture
def structural_predicate():
    return importlib.import_module("veri.structural_predicate")


def fake_stdin(monkeypatch, data):
    stdin = io.TextIOWrapper(io.BytesIO(data))
    monkeypatch.setattr(sys, "stdin", stdin)
    return stdin


def spy_subprocess(monkeypatch):
    started = []

    def refuse(*args, **kwargs):
        started.append(args)
        raise AssertionError("started a subprocess: %r" % (args,))

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, refuse)
    return started


def test_main_refuses_a_missing_or_empty_record_with_its_usage_reading_no_stdin_and_starting_no_subprocess(
    monkeypatch, capsys, tmp_path, structural_predicate
):
    monkeypatch.chdir(tmp_path)
    started = spy_subprocess(monkeypatch)
    report = b"PREDICATE: false\n"
    for argv in ([], [""], ["", "record"]):
        stdin = fake_stdin(monkeypatch, report)
        code = structural_predicate.main(argv)
        assert (argv, code, capsys.readouterr()) == (argv, 2, ("", USAGE))
        assert stdin.buffer.read() == report
    assert started == []
    assert list(tmp_path.iterdir()) == []


def test_main_reads_the_last_terminated_predicate_line_and_refuses_a_report_without_one(
    monkeypatch, capsys, tmp_path, structural_predicate
):
    monkeypatch.chdir(tmp_path)
    started = spy_subprocess(monkeypatch)
    monkeypatch.setenv("predicate", "false")
    missing = "structural-predicate.sh: the report carries no PREDICATE: line\n"
    for report in (
        b"no line here\n",
        b"text\nPREDICATE: false",
        b"  PREDICATE: false\n",
        b"PREDICATES: false\n",
    ):
        fake_stdin(monkeypatch, report)
        code = structural_predicate.main(["record"])
        assert (report, code, capsys.readouterr()) == (report, 2, ("", missing))
    assert started == []
    assert list(tmp_path.iterdir()) == []

    ran = []

    def run(args, *rest, **kwargs):
        ran.append(args)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", run)
    fake_stdin(monkeypatch, b"PREDICATE: first\nPREDICATE: tr\0ue\r\n")
    code = structural_predicate.main(["record"])
    assert (code, capsys.readouterr().out, ran) == (1, "", [["bash", "-c", "true\r"]])
    assert list(tmp_path.iterdir()) == []


def test_main_skips_a_none_value_and_runs_its_near_misses_as_commands(
    monkeypatch, capsys, tmp_path, structural_predicate
):
    monkeypatch.chdir(tmp_path)
    ran = []

    def run(args, *rest, **kwargs):
        ran.append(args)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", run)
    for value in ("NONE", "NONE no structural change", "NONE—why", "NONE: why"):
        fake_stdin(monkeypatch, ("PREDICATE: %s\n" % value).encode())
        code = structural_predicate.main(["record"])
        assert (value, code, capsys.readouterr(), ran) == (value, 3, ("", ""), [])
    assert list(tmp_path.iterdir()) == []

    for value in ("NONE-x", "NONE\tx", "none", "NONEX"):
        ran.clear()
        fake_stdin(monkeypatch, ("PREDICATE: %s\n" % value).encode())
        code = structural_predicate.main(["record"])
        assert (value, code, ran) == (value, 1, [["bash", "-c", value]])
    assert list(tmp_path.iterdir()) == []


def test_main_runs_the_predicate_through_bash_and_writes_the_record_only_on_a_non_zero_run(
    monkeypatch, capsys, tmp_path, structural_predicate
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("predicate", "leaked")
    monkeypatch.setenv("VERI_KEPT", "kept")
    record = tmp_path / "record"
    runs = []
    answer = []

    def run(args, *rest, **kwargs):
        env = kwargs.get("env")
        env = dict(os.environ if env is None else env)
        runs.append(
            (
                args,
                rest,
                kwargs.get("stdin"),
                kwargs.get("stdout"),
                kwargs.get("stderr"),
                kwargs.get("cwd"),
                os.path.realpath(os.getcwd()),
                "predicate" in env,
                env.get("VERI_KEPT"),
                kwargs.get("timeout"),
            )
        )
        if isinstance(answer[0], BaseException):
            raise answer[0]
        return subprocess.CompletedProcess(args, answer[0])

    def call(value):
        return (
            ["bash", "-c", value],
            (),
            subprocess.DEVNULL,
            subprocess.DEVNULL,
            subprocess.DEVNULL,
            None,
            os.path.realpath(tmp_path),
            False,
            "kept",
            None,
        )

    monkeypatch.setattr(subprocess, "run", run)
    for report, value in (
        (b"PREDICATE: true\n", "true"),
        (b"PREDICATE:\n", ""),
        (b"PREDICATE: \n", ""),
    ):
        runs.clear()
        answer[:] = [0]
        fake_stdin(monkeypatch, report)
        code = structural_predicate.main(["record"])
        assert (report, code, capsys.readouterr().out, runs, record.exists()) == (
            report, 1, "", [call(value)], False
        )

    for status in (1, 127, FileNotFoundError("bash"), PermissionError("bash")):
        runs.clear()
        answer[:] = [status]
        record.write_bytes(b"an older and much longer record\n")
        fake_stdin(monkeypatch, b"PREDICATE: test -e caf\xc3\xa9\n")
        code = structural_predicate.main(["record"])
        value = b"test -e caf\xc3\xa9".decode("utf-8", "surrogateescape")
        assert (repr(status), code, capsys.readouterr().out, runs, record.read_bytes()) == (
            repr(status), 0, "", [call(value)], b"test -e caf\xc3\xa9\n"
        )

    answer[:] = [1]
    fake_stdin(monkeypatch, b"PREDICATE: false\n")
    code = structural_predicate.main(["missing/record"])
    captured = capsys.readouterr()
    assert (code, captured.out, "missing/record" in captured.err) == (1, "", True)
    assert not (tmp_path / "missing").exists()
