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


def test_main_refuses_a_missing_or_empty_record_with_its_usage_reading_no_stdin_and_starting_no_subprocess(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({})
    report = b"PREDICATE: false\n"
    for argv in ([], [""], ["", "record"]):
        stdin = fake_stdin(monkeypatch, report)
        code = structural_predicate.main(argv)
        assert (argv, code, capsys.readouterr()) == (argv, 2, ("", USAGE))
        assert stdin.buffer.read() == report
    assert fake.calls == []
    assert list(tmp_path.iterdir()) == []


def test_main_reads_the_last_terminated_predicate_line_and_refuses_a_report_without_one(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({})
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
    assert fake.calls == []
    assert list(tmp_path.iterdir()) == []

    fake = fake_processes.answers({"bash": (0, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: first\nPREDICATE: tr\0ue\r\n")
    code = structural_predicate.main(["record"])
    assert (code, capsys.readouterr().out, fake.argvs) == (1, "", [["bash", "-c", "true\r"]])
    assert list(tmp_path.iterdir()) == []


def test_main_skips_a_none_value_and_runs_its_near_misses_as_commands(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (0, "", "")})
    for value in ("NONE", "NONE no structural change", "NONE—why", "NONE: why"):
        fake_stdin(monkeypatch, ("PREDICATE: %s\n" % value).encode())
        code = structural_predicate.main(["record"])
        assert (value, code, capsys.readouterr(), fake.argvs) == (value, 3, ("", ""), [])
    assert list(tmp_path.iterdir()) == []

    for value in ("NONE-x", "NONE\tx", "none", "NONEX"):
        fake.seen.clear()
        fake_stdin(monkeypatch, ("PREDICATE: %s\n" % value).encode())
        code = structural_predicate.main(["record"])
        assert (value, code, fake.argvs) == (value, 1, [["bash", "-c", value]])
    assert list(tmp_path.iterdir()) == []


def test_main_runs_the_predicate_through_bash_and_writes_the_record_only_on_a_non_zero_run(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("predicate", "leaked")
    monkeypatch.setenv("VERI_KEPT", "kept")
    record = tmp_path / "record"
    runs = []
    answer = []

    def observe(line, **kwargs):
        env = kwargs.get("env")
        env = dict(os.environ if env is None else env)
        runs.append(
            (
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
        return (answer[0], "", "")

    fake = fake_processes.answers({"bash": observe})

    def observed():
        return [(argv, rest) + seen for argv, rest, seen in zip(fake.argvs, fake.rests, runs)]

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

    for report, value in (
        (b"PREDICATE: true\n", "true"),
        (b"PREDICATE:\n", ""),
        (b"PREDICATE: \n", ""),
    ):
        runs.clear()
        fake.seen.clear()
        fake.rests.clear()
        answer[:] = [0]
        fake_stdin(monkeypatch, report)
        code = structural_predicate.main(["record"])
        assert (report, code, capsys.readouterr().out, observed(), record.exists()) == (
            report, 1, "", [call(value)], False
        )

    for status in (1, 127, FileNotFoundError("bash"), PermissionError("bash")):
        runs.clear()
        fake.seen.clear()
        fake.rests.clear()
        answer[:] = [status]
        record.write_bytes(b"an older and much longer record\n")
        fake_stdin(monkeypatch, b"PREDICATE: test -e caf\xc3\xa9\n")
        code = structural_predicate.main(["record"])
        value = b"test -e caf\xc3\xa9".decode("utf-8", "surrogateescape")
        assert (repr(status), code, capsys.readouterr().out, observed(), record.read_bytes()) == (
            repr(status), 0, "", [call(value)], b"test -e caf\xc3\xa9\n"
        )

    answer[:] = [1]
    fake_stdin(monkeypatch, b"PREDICATE: false\n")
    code = structural_predicate.main(["missing/record"])
    captured = capsys.readouterr()
    assert (code, captured.out, "missing/record" in captured.err) == (1, "", True)
    assert not (tmp_path / "missing").exists()


def test_main_2881_blank_lines_after_a_single_line_predicate_do_not_make_it_multi_line(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (1, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: false\n\n\n\n")
    code = structural_predicate.main(["record"])
    assert (code, capsys.readouterr(), fake.argvs) == (0, ("", ""), [["bash", "-c", "false"]])
    assert (tmp_path / "record").read_bytes() == b"false\n"


def test_main_2881_a_whitespace_only_line_after_the_predicate_line_is_judged_like_a_single_line_reply(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (1, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: false\n   \t\n")
    code = structural_predicate.main(["record"])
    assert (code, capsys.readouterr(), fake.argvs) == (0, ("", ""), [["bash", "-c", "false"]])
    assert (tmp_path / "record").read_bytes() == b"false\n"


def test_main_2881_a_heredoc_predicate_exits_2_naming_the_multi_line_predicate_running_nothing_and_writing_no_record(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (0, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: python3 - <<'PY'\nimport sys\nsys.exit(1)\nPY\n")
    code = structural_predicate.main(["record"])
    captured = capsys.readouterr()
    assert (code, captured.out, "multi-line" in captured.err.lower(), fake.argvs) == (2, "", True, [])
    assert list(tmp_path.iterdir()) == []


def test_main_2881_a_trailing_backslash_continuation_predicate_exits_2_naming_the_multi_line_predicate_running_nothing_and_writing_no_record(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (0, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: grep -q foo \\\nfile.txt\n")
    code = structural_predicate.main(["record"])
    captured = capsys.readouterr()
    assert (code, captured.out, "multi-line" in captured.err.lower(), fake.argvs) == (2, "", True, [])
    assert list(tmp_path.iterdir()) == []


def test_main_2881_plain_prose_after_the_predicate_line_exits_2_naming_the_multi_line_predicate_running_nothing_and_writing_no_record(
    monkeypatch, capsys, tmp_path, structural_predicate, fake_processes
):
    monkeypatch.chdir(tmp_path)
    fake = fake_processes.answers({"bash": (0, "", "")})
    fake_stdin(monkeypatch, b"PREDICATE: test -e marker\nThis is why I chose it.\n")
    code = structural_predicate.main(["record"])
    captured = capsys.readouterr()
    assert (code, captured.out, "multi-line" in captured.err.lower(), fake.argvs) == (2, "", True, [])
    assert list(tmp_path.iterdir()) == []
