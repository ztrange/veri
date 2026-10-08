"""In-process cases for veri/refactor_overflow.py, the module refactor-overflow.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

from conftest import SCRIPTS

USAGE = "refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>\n"


@pytest.fixture
def refactor_overflow():
    return importlib.import_module("veri.refactor_overflow")


def refuse_processes(monkeypatch):
    """subprocess.run and subprocess.Popen recording each command, its program by basename, and starting none."""
    calls = []

    def record(args, *rest, **kwargs):
        calls.append(" ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]]))
        raise AssertionError(f"started a process: {calls[-1]}")

    monkeypatch.setattr(subprocess, "run", record)
    monkeypatch.setattr(subprocess, "Popen", record)
    return calls


@pytest.mark.parametrize("argv, expected_err", [
    (lambda d: [], USAGE),
    (lambda d: ["", str(d / "owed.md"), "0"], USAGE),
    (lambda d: ["two", str(d / "owed.md"), "0"], USAGE),
    (lambda d: ["-1", str(d / "owed.md"), "0"], USAGE),
    (lambda d: ["7", str(d / "owed.md")], USAGE),
    (lambda d: ["7", str(d / "owed.md"), ""], USAGE),
    (lambda d: ["7", str(d / "owed.md"), "two"], USAGE),
    (lambda d: ["7", str(d / "owed.md"), "-1"], USAGE),
    (lambda d: ["7", "", "0"], USAGE),
    (lambda d: ["7", "", "0", str(d / "skipped.md"), "extra"], USAGE),
    (lambda d: ["7", str(d / "owed.md"), "0", str(d / "missing.md")],
     lambda d: f"refactor-overflow: no such skipped file: {d / 'missing.md'}\n"),
    (lambda d: ["7", str(d / "owed.md"), "0", "/dev/null"],
     lambda d: "refactor-overflow: no such skipped file: /dev/null\n"),
    (lambda d: ["7", str(d / "owed.md"), "0", str(d / "missing.md"), "extra", "more"],
     lambda d: f"refactor-overflow: no such skipped file: {d / 'missing.md'}\n"),
])
def test_main_refuses_a_bad_argument_with_exit_2_its_stderr_line_and_no_process(
        monkeypatch, capsys, tmp_path, refactor_overflow, argv, expected_err):
    (tmp_path / "owed.md").write_text("### structural\n- a candidate\n")
    (tmp_path / "skipped.md").write_text("a skipped candidate\n")
    calls = refuse_processes(monkeypatch)
    expected = expected_err(tmp_path) if callable(expected_err) else expected_err

    code = refactor_overflow.main(argv(tmp_path))

    captured = capsys.readouterr()
    assert calls == []
    assert (code, captured.out, captured.err) == (2, "", expected)


@pytest.mark.parametrize("n", ["504", "007"])
def test_main_files_the_unreached_list_lines_through_gh_and_prints_its_url(
        monkeypatch, capsys, tmp_path, refactor_overflow, n):
    owed = str(tmp_path / "owed.md")
    cwd = os.getcwd()
    calls = []

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        calls.append((args, kwargs.get("cwd"), os.getcwd()))
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, "https://github.com/o/r/issues/9\n\n", "")
        return subprocess.CompletedProcess(args, 0, "- [ ] first\n- [ ] second\n- [ ] third\n", "")

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    code = refactor_overflow.main([n, owed, "1"])

    captured = capsys.readouterr()
    assert [c[0][1:] for c in calls] == [
        ["list", owed],
        ["api", "repos/{owner}/{repo}/issues",
         "-f", f"title=Refactor owed by #{n}",
         "-f", f"body=Structural candidates #{n}'s closing pass could not reach:\n\n"
               "- - [ ] second\n- - [ ] third",
         "-q", ".html_url"],
    ]
    assert pathlib.Path(calls[0][0][0]).resolve() == SCRIPTS / "refactor-owed.sh"
    assert calls[1][0][0] == "gh"
    assert [(c[1], c[2]) for c in calls] == [(None, cwd), (None, cwd)]
    assert os.getcwd() == cwd
    assert (code, captured.out) == (0, "https://github.com/o/r/issues/9\n")


BODY_HEAD = "body=Structural candidates #7's closing pass could not reach:\n\n"


@pytest.mark.parametrize("skipped, listed, reached, expected_code, expected_body", [
    ("skipped one\n\nskipped one\n", (0, "first\nsecond\n\nsecond\nthird\n\n\n"), "1", 0,
     "- skipped one\n- \n- skipped one\n- second\n- \n- second\n- third"),
    ("skipped one\n\nskipped two", (0, "first\nsecond\n"), "1", 0,
     "- skipped one\n- \n- skipped twosecond"),
    ("skipped one\n\n\n", (0, "first\n"), "1", 0, "- skipped one"),
    (None, (0, "first\nsecond\n"), "2", 3, None),
    (None, (0, "first\n\n\n"), "1", 3, None),
    ("", (0, "first\n"), "1", 3, None),
    ("a skipped candidate\n", (3, ""), "0", 0, "- a skipped candidate"),
    ("a skipped candidate\n", (1, "first\nsecond\n"), "0", 1, None),
    (None, (4, "first\nsecond\n"), "0", 4, None),
])
def test_main_builds_the_unreached_text_from_the_skipped_file_then_the_list_lines_after_reached(
        monkeypatch, capsys, tmp_path, refactor_overflow,
        skipped, listed, reached, expected_code, expected_body):
    owed = str(tmp_path / "owed.md")
    argv = ["7", owed, reached]
    if skipped is not None:
        (tmp_path / "skipped.md").write_text(skipped)
        argv.append(str(tmp_path / "skipped.md"))
    calls = []

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        calls.append(args[1:])
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, "https://github.com/o/r/issues/9\n", "")
        return subprocess.CompletedProcess(args, listed[0], listed[1], "")

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    code = refactor_overflow.main(argv)

    captured = capsys.readouterr()
    expected_calls = [["list", owed]]
    if expected_body is not None:
        expected_calls.append(["api", "repos/{owner}/{repo}/issues",
                               "-f", "title=Refactor owed by #7",
                               "-f", BODY_HEAD + expected_body,
                               "-q", ".html_url"])
    assert calls == expected_calls
    expected_out = "https://github.com/o/r/issues/9\n" if expected_code == 0 else ""
    assert (code, captured.out) == (expected_code, expected_out)


@pytest.mark.parametrize("list_code, expected_code", [(0, 0), (3, 3), (1, 1)])
def test_main_lets_what_list_writes_to_stderr_through_to_the_callers_stderr_on_every_exit(
        monkeypatch, capsys, tmp_path, refactor_overflow, list_code, expected_code):
    owed = str(tmp_path / "owed.md")
    list_err = "refactor-owed: a warning\n"

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, "https://github.com/o/r/issues/9\n", "")
        if kwargs.get("capture_output") or kwargs.get("stderr") is not None:
            return subprocess.CompletedProcess(args, list_code, "first\nsecond\n", list_err)
        sys.stderr.write(list_err)
        return subprocess.CompletedProcess(args, list_code, "first\nsecond\n", None)

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    code = refactor_overflow.main(["7", owed, "1"])

    captured = capsys.readouterr()
    assert (code, captured.err) == (expected_code, list_err)


@pytest.mark.parametrize("gh_code", [0, 1])
def test_main_lets_what_gh_writes_to_stderr_through_to_the_callers_stderr_on_every_exit(
        monkeypatch, capsys, tmp_path, refactor_overflow, gh_code):
    owed = str(tmp_path / "owed.md")
    gh_err = "gh: a warning\n"

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] != "gh":
            return subprocess.CompletedProcess(args, 0, "first\nsecond\n", None)
        out = "https://github.com/o/r/issues/9\n" if gh_code == 0 else ""
        if kwargs.get("capture_output") or kwargs.get("stderr") is not None:
            return subprocess.CompletedProcess(args, gh_code, out, gh_err)
        sys.stderr.write(gh_err)
        return subprocess.CompletedProcess(args, gh_code, out, None)

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    refactor_overflow.main(["7", owed, "1"])

    assert capsys.readouterr().err == gh_err


TEN_LINES = "".join(f"l{i}\n" for i in range(1, 11))


@pytest.mark.parametrize("reached, gh_code, expected_code, expected_out, expected_body", [
    ("1", 1, 2, "", "- l2\n- l3\n- l4\n- l5\n- l6\n- l7\n- l8\n- l9\n- l10"),
    ("1", 4, 2, "", "- l2\n- l3\n- l4\n- l5\n- l6\n- l7\n- l8\n- l9\n- l10"),
    ("010", 0, 3, "", None),
    ("08", 0, 0, "https://github.com/o/r/issues/9\n", "- l9\n- l10"),
    ("18446744073709551615", 0, 3, "", None),
    ("99999999999999999999", 0, 3, "", None),
    ("9223372036854775808", 0, 3, "", None),
])
def test_main_returns_gh_s_own_failing_code_and_reads_reached_with_leading_zeros_as_decimal_issue_776(
        monkeypatch, capsys, tmp_path, refactor_overflow,
        reached, gh_code, expected_code, expected_out, expected_body):
    owed = str(tmp_path / "owed.md")
    gh_calls = []

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] == "gh":
            gh_calls.append(args[1:])
            out = "https://github.com/o/r/issues/9\n" if gh_code == 0 else ""
            return subprocess.CompletedProcess(args, gh_code, out, None)
        return subprocess.CompletedProcess(args, 0, TEN_LINES, None)

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    code = refactor_overflow.main(["7", owed, reached])

    captured = capsys.readouterr()
    expected_gh = [] if expected_body is None else [
        ["api", "repos/{owner}/{repo}/issues", "-f", "title=Refactor owed by #7",
         "-f", BODY_HEAD + expected_body, "-q", ".html_url"]]
    assert gh_calls == expected_gh
    assert (code, captured.out) == (expected_code, expected_out)


def test_main_files_the_skipped_file_s_candidates_when_list_exits_3_issue_777(
        monkeypatch, capsys, tmp_path, refactor_overflow):
    owed = str(tmp_path / "owed.md")
    (tmp_path / "skipped.md").write_text("a skipped candidate\nanother skipped\n")
    calls = []

    def fake_run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        calls.append(args[1:])
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, "https://github.com/o/r/issues/9\n", "")
        return subprocess.CompletedProcess(args, 3, "", "")

    def refuse_popen(args, *rest, **kwargs):
        raise AssertionError(f"started a process through Popen: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", refuse_popen)

    code = refactor_overflow.main(["7", owed, "0", str(tmp_path / "skipped.md")])

    captured = capsys.readouterr()
    assert calls == [["list", owed],
                     ["api", "repos/{owner}/{repo}/issues",
                      "-f", "title=Refactor owed by #7",
                      "-f", BODY_HEAD + "- a skipped candidate\n- another skipped",
                      "-q", ".html_url"]]
    assert (code, captured.out) == (0, "https://github.com/o/r/issues/9\n")
