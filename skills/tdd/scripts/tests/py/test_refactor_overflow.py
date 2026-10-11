"""In-process cases for veri/refactor_overflow.py, the module refactor-overflow.sh is a shim over."""
import importlib
import os
import subprocess
import sys

import pytest

USAGE = "refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>\n"


REAL_RUN = subprocess.run


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


def write_owed(tmp_path, candidates):
    owed = tmp_path / "owed.md"
    owed.write_text("### a step\n" + "".join(f"- {c}\n" for c in candidates))
    return str(owed)


def fake_gh(monkeypatch, code=0, out="https://github.com/o/r/issues/9\n", err=None):
    """Only gh is faked; refactor-owed.sh runs for real. Returns gh's argv lists, in order."""
    calls = []

    def run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] != "gh":
            return REAL_RUN(args, *rest, **kwargs)
        calls.append(args[1:])
        if err is not None and not (kwargs.get("capture_output") or kwargs.get("stderr") is not None):
            sys.stderr.write(err)
        return subprocess.CompletedProcess(args, code, out if code == 0 else "", None)

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def issue(n, body):
    return ["api", "repos/{owner}/{repo}/issues", "-f", f"title=Refactor owed by #{n}",
            "-f", f"body={body}", "-q", ".html_url"]


@pytest.mark.process("refactor-owed.sh list, run as the sibling process")
@pytest.mark.parametrize("n", ["504", "007"])
def test_main_files_the_unreached_list_lines_through_gh_and_prints_its_url(
        monkeypatch, capsys, tmp_path, refactor_overflow, n):
    owed = write_owed(tmp_path, ["- [ ] first", "- [ ] second", "- [ ] third"])
    cwd = os.getcwd()
    calls = fake_gh(monkeypatch, out="https://github.com/o/r/issues/9\n\n")

    code = refactor_overflow.main([n, owed, "1"])

    captured = capsys.readouterr()
    assert calls == [issue(n, f"Structural candidates #{n}'s closing pass could not reach:\n\n"
                              "- - [ ] second\n- - [ ] third")]
    assert os.getcwd() == cwd
    assert (code, captured.out) == (0, "https://github.com/o/r/issues/9\n")


BODY_HEAD = "Structural candidates #7's closing pass could not reach:\n\n"


@pytest.mark.process("refactor-owed.sh list, run as the sibling process")
@pytest.mark.parametrize("skipped, listed, reached, expected_code, expected_body", [
    ("skipped one\n\nskipped one\n", ["first", "second", "third"], "1", 0,
     "- skipped one\n- \n- skipped one\n- second\n- third"),
    ("skipped one\n\nskipped two", ["first", "second"], "1", 0,
     "- skipped one\n- \n- skipped twosecond"),
    ("skipped one\n\n\n", ["first"], "1", 0, "- skipped one"),
    (None, ["first", "second"], "2", 3, None),
    (None, ["first"], "1", 3, None),
    ("", ["first"], "1", 3, None),
    ("a skipped candidate\n", [], "0", 0, "- a skipped candidate"),
    (None, [], "0", 3, None),
])
def test_main_builds_the_unreached_text_from_the_skipped_file_then_the_list_lines_after_reached(
        monkeypatch, capsys, tmp_path, refactor_overflow,
        skipped, listed, reached, expected_code, expected_body):
    owed = write_owed(tmp_path, listed)
    argv = ["7", owed, reached]
    if skipped is not None:
        (tmp_path / "skipped.md").write_text(skipped)
        argv.append(str(tmp_path / "skipped.md"))
    calls = fake_gh(monkeypatch)

    code = refactor_overflow.main(argv)

    captured = capsys.readouterr()
    assert calls == ([] if expected_body is None else [issue(7, BODY_HEAD + expected_body)])
    expected_out = "https://github.com/o/r/issues/9\n" if expected_code == 0 else ""
    assert (code, captured.out) == (expected_code, expected_out)


@pytest.mark.process("refactor-owed.sh list, run as the sibling process")
@pytest.mark.parametrize("gh_code, expected_code", [(0, 0), (1, 2)])
def test_main_lets_what_gh_writes_to_stderr_through_to_the_callers_stderr_on_every_exit(
        monkeypatch, capsys, tmp_path, refactor_overflow, gh_code, expected_code):
    owed = write_owed(tmp_path, ["first", "second"])
    gh_err = "gh: a warning\n"
    fake_gh(monkeypatch, code=gh_code, err=gh_err)

    code = refactor_overflow.main(["7", owed, "1"])

    captured = capsys.readouterr()
    assert (code, captured.err) == (expected_code, gh_err)


TEN = [f"l{i}" for i in range(1, 11)]


@pytest.mark.process("refactor-owed.sh list, run as the sibling process")
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
    owed = write_owed(tmp_path, TEN)
    gh_calls = fake_gh(monkeypatch, code=gh_code)

    code = refactor_overflow.main(["7", owed, reached])

    captured = capsys.readouterr()
    expected_gh = [] if expected_body is None else [issue(7, BODY_HEAD + expected_body)]
    assert gh_calls == expected_gh
    assert (code, captured.out) == (expected_code, expected_out)


@pytest.mark.process("refactor-owed.sh list, run as the sibling process")
def test_main_files_the_skipped_file_s_candidates_when_list_exits_3_issue_777(
        monkeypatch, capsys, tmp_path, refactor_overflow):
    owed = write_owed(tmp_path, [])
    (tmp_path / "skipped.md").write_text("a skipped candidate\nanother skipped\n")
    calls = fake_gh(monkeypatch)

    code = refactor_overflow.main(["7", owed, "0", str(tmp_path / "skipped.md")])

    captured = capsys.readouterr()
    assert calls == [issue(7, BODY_HEAD + "- a skipped candidate\n- another skipped")]
    assert (code, captured.out) == (0, "https://github.com/o/r/issues/9\n")
