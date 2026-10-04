"""In-process cases for veri/refactor_overflow.py, the module refactor-overflow.sh is a shim over."""
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
    ("a skipped candidate\n", (3, ""), "0", 3, None),
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
