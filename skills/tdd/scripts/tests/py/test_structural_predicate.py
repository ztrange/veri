"""In-process cases for veri/structural_predicate.py, the module structural-predicate.sh is a shim over."""
import importlib
import io
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

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
