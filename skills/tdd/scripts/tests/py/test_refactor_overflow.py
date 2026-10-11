"""In-process cases for veri/refactor_overflow.py, the module refactor-overflow.sh is a shim over."""
import importlib
import os
import subprocess
import sys

import pytest

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


def write_owed(tmp_path, candidates):
    owed = tmp_path / "owed.md"
    owed.write_text("### a step\n" + "".join(f"- {c}\n" for c in candidates))
    return str(owed)


def fake_gh(monkeypatch, code=0, out="https://github.com/o/r/issues/9\n", err=None):
    """Only gh is faked, and any other process is refused. Returns gh's argv lists, in order."""
    calls = []

    def run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] != "gh":
            raise AssertionError(f"started a process: {args}")
        calls.append(args[1:])
        if err is not None and not (kwargs.get("capture_output") or kwargs.get("stderr") is not None):
            sys.stderr.write(err)
        return subprocess.CompletedProcess(args, code, out if code == 0 else "", None)

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def issue(n, body):
    return ["api", "repos/{owner}/{repo}/issues", "-f", f"title=Refactor owed by #{n}",
            "-f", f"body={body}", "-q", ".html_url"]


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


def test_main_files_the_skipped_file_s_candidates_when_list_exits_3_issue_777(
        monkeypatch, capsys, tmp_path, refactor_overflow):
    owed = write_owed(tmp_path, [])
    (tmp_path / "skipped.md").write_text("a skipped candidate\nanother skipped\n")
    calls = fake_gh(monkeypatch)

    code = refactor_overflow.main(["7", owed, "0", str(tmp_path / "skipped.md")])

    captured = capsys.readouterr()
    assert calls == [issue(7, BODY_HEAD + "- a skipped candidate\n- another skipped")]
    assert (code, captured.out) == (0, "https://github.com/o/r/issues/9\n")


@pytest.mark.parametrize("skipped, list_code", [("a skipped candidate\n", 1), (None, 4)])
def test_main_returns_any_other_structural_lines_code_as_its_own_and_files_nothing(
        monkeypatch, capsys, tmp_path, refactor_overflow, skipped, list_code):
    owed = write_owed(tmp_path, ["first", "second"])
    argv = ["7", owed, "0"]
    if skipped is not None:
        (tmp_path / "skipped.md").write_text(skipped)
        argv.append(str(tmp_path / "skipped.md"))
    asked = []

    def structural_lines(file):
        asked.append(file)
        return list_code, ["first", "second"]

    monkeypatch.setattr(refactor_overflow, "structural_lines", structural_lines)
    calls = fake_gh(monkeypatch)

    code = refactor_overflow.main(argv)

    captured = capsys.readouterr()
    assert (asked, calls) == ([owed], [])
    assert (code, captured.out, captured.err) == (list_code, "", "")


def test_cli_files_nothing_and_exits_3_when_every_unreached_candidate_in_the_owed_file_is_test_only(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-663-refactor-owed.md"
    owed.write_text("### first step\n"
                    "- test-only | fold the suite's two fixture writers into one helper\n"
                    "- test-only | hoist the stub directory into the harness\n")
    calls = fake_processes(lambda line, **kwargs: (0, "https://github.com/o/r/issues/9\n", ""))

    result = run_cli(refactor_overflow, ["663", str(owed), "0"])

    assert (result, calls) == ((3, "", ""), [])


URL = "https://github.com/o/r/issues/9\n"
FOLD = "fold verify.sh's two mktemp calls into one helper"
HOIST = "hoist the ledger path into one variable"
SPLIT = "split the verdict parser out of run-leaf.sh"


def owed_504(directory):
    owed = directory / "issue-504-refactor-owed.md"
    owed.write_text(f"### first step\n- {FOLD}\n- {HOIST}\n### second step\n- {HOIST}\n- {SPLIT}\n")
    return owed


def filing(n, body):
    return ["gh " + " ".join(issue(n, body))]


def gh_files(line, **kwargs):
    return 0, URL, ""


def test_cli_files_one_issue_naming_the_parent_listing_every_candidate_after_the_first_reached_and_prints_its_url(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert calls == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")


@pytest.mark.parametrize("argv, expected", [
    (lambda d, owed: ["504", str(d / "no-such-file.md"), "0"], (3, "", "")),
    (lambda d, owed: ["504", str(d / "headed-only.md"), "0"], (3, "", "")),
    (lambda d, owed: ["504", owed, "3"], (3, "", "")),
    (lambda d, owed: ["504", owed], (2, "", USAGE)),
    (lambda d, owed: ["504", owed, "two"], (2, "", USAGE)),
    (lambda d, owed: ["five-oh-four", owed, "1"], (2, "", USAGE)),
    (lambda d, owed: ["504", "", "1"], (2, "", USAGE)),
    (lambda d, owed: [], (2, "", USAGE)),
    (lambda d, owed: ["504", owed, "1", str(d / "no-such-skipped-file")],
     lambda d: (2, "", f"refactor-overflow: no such skipped file: {d / 'no-such-skipped-file'}\n")),
])
def test_cli_files_nothing_exiting_3_with_no_candidate_unreached_and_2_with_its_usage_or_skipped_file_line_on_a_bad_argument(
        tmp_path, refactor_overflow, run_cli, fake_processes, argv, expected):
    owed = str(owed_504(tmp_path))
    (tmp_path / "headed-only.md").write_text("### first step\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, argv(tmp_path, owed), cwd=tmp_path)

    assert (result, calls) == (expected(tmp_path) if callable(expected) else expected, [])


@pytest.mark.parametrize("reached", ["1.5", "-1", "abc", "", " 7", "7x", "0x10"])
def test_cli_refuses_a_reached_that_is_not_a_non_negative_whole_number_with_exit_2_naming_reached_issue_776(
        tmp_path, refactor_overflow, run_cli, fake_processes, reached):
    owed = owed_504(tmp_path)
    calls = fake_processes(gh_files)

    code, out, err = run_cli(refactor_overflow, ["504", str(owed), reached], cwd=tmp_path)

    assert (code, out, calls) == (2, "", [])
    assert "<reached>" in err


def test_cli_files_a_two_class_owed_file_s_one_unreached_structural_candidate_as_before_test_only_existed(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-505-refactor-owed.md"
    owed.write_text(f"### first step\n- {FOLD}\n- {HOIST}\n### second step\n- {HOIST}\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["505", str(owed), "1"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert calls == filing(505, f"Structural candidates #505's closing pass could not reach:\n\n- {FOLD}")


def test_cli_sends_no_label_makes_no_call_on_the_parent_and_writes_no_file_into_the_repository(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    owed_504(repo / ".tdd")

    def snapshot():
        return sorted((str(p.relative_to(repo)), p.read_bytes()) for p in repo.rglob("*") if p.is_file())

    before = snapshot()
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["504", ".tdd/issue-504-refactor-owed.md", "1"], cwd=repo)

    assert result == (0, URL, "")
    assert calls == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")
    assert snapshot() == before


@pytest.mark.parametrize("reached, listed", [("1", f"- {HOIST}\n- {FOLD}\n- {SPLIT}"), ("3", f"- {HOIST}")])
def test_cli_files_the_skipped_file_s_candidates_beside_the_unreached_and_even_when_every_candidate_was_reached_issue_691(
        tmp_path, refactor_overflow, run_cli, fake_processes, reached, listed):
    owed = owed_504(tmp_path)
    skipped = tmp_path / "issue-504-structural-skipped"
    skipped.write_text(f"{HOIST}\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["504", str(owed), reached, str(skipped)], cwd=tmp_path)

    assert result == (0, URL, "")
    assert calls == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n{listed}")
