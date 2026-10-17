"""In-process cases for veri/refactor_overflow.py, the module refactor-overflow.sh is a shim over."""
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
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


NO_OPEN_ISSUES = "[]"


def is_lookup(line):
    """The open-issue lookup: a REST read of the issues route, as opposed to the filing's title= write."""
    return line.startswith("gh api repos/{owner}/{repo}/issues") and "title=" not in line and "state=open" in line


def filed(calls):
    return [c for c in calls if not is_lookup(c)]


def fake_gh(monkeypatch, code=0, out="https://github.com/o/r/issues/9\n", err=None):
    """Only gh is faked, and any other process is refused. Returns gh's argv lists, in order."""
    calls = []

    def run(args, *rest, **kwargs):
        args = [str(a) for a in args]
        if args[0] != "gh":
            raise AssertionError(f"started a process: {args}")
        if is_lookup(" ".join(args)):
            return subprocess.CompletedProcess(args, 0, NO_OPEN_ISSUES, "")
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
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["663", str(owed), "0"])

    assert (result, filed(calls)) == ((3, "", ""), [])


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
    if is_lookup(line):
        return 0, NO_OPEN_ISSUES, ""
    return 0, URL, ""


def test_cli_files_one_issue_naming_the_parent_listing_every_candidate_after_the_first_reached_and_prints_its_url(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")


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

    assert (result, filed(calls)) == (expected(tmp_path) if callable(expected) else expected, [])


@pytest.mark.parametrize("reached", ["1.5", "-1", "abc", "", " 7", "7x", "0x10"])
def test_cli_refuses_a_reached_that_is_not_a_non_negative_whole_number_with_exit_2_naming_reached_issue_776(
        tmp_path, refactor_overflow, run_cli, fake_processes, reached):
    owed = owed_504(tmp_path)
    calls = fake_processes(gh_files)

    code, out, err = run_cli(refactor_overflow, ["504", str(owed), reached], cwd=tmp_path)

    assert (code, out, filed(calls)) == (2, "", [])
    assert "<reached>" in err


def test_cli_files_a_two_class_owed_file_s_one_unreached_structural_candidate_as_before_test_only_existed(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-505-refactor-owed.md"
    owed.write_text(f"### first step\n- {FOLD}\n- {HOIST}\n### second step\n- {HOIST}\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["505", str(owed), "1"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(505, f"Structural candidates #505's closing pass could not reach:\n\n- {FOLD}")


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
    assert filed(calls) == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")
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
    assert filed(calls) == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n{listed}")


MKTEMP = "extract the five copies of the mktemp dance across the skill"
REMOVE = "remove gh(), issue() and the subprocess import from coverage_blocker.py"
HTTP_422 = "gh: HTTP 422: Validation Failed\n"


@pytest.mark.parametrize("gh_code", [1, 3, 5])
def test_cli_exits_2_with_nothing_on_stdout_and_lets_gh_s_stderr_through_when_gh_fails_while_filing_issue_775(
        tmp_path, refactor_overflow, run_cli, fake_processes, gh_code):
    owed = owed_504(tmp_path)

    def gh_fails(line, **kwargs):
        if is_lookup(line):
            return 0, NO_OPEN_ISSUES, ""
        os.write(2, HTTP_422.encode())
        return gh_code, "", None

    calls = fake_processes(gh_fails)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    assert result == (2, "", HTTP_422)
    assert filed(calls) == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")


def test_cli_run_from_another_working_directory_runs_gh_in_the_caller_s_working_directory(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    cwds = []

    def gh_records_its_cwd(line, **kwargs):
        cwds.append(kwargs.get("cwd") or os.getcwd())
        return gh_files(line, **kwargs)

    calls = fake_processes(gh_records_its_cwd)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=elsewhere)

    assert result == (0, URL, "")
    assert filed(calls) == filing(504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")
    assert cwds == [str(elsewhere)] * 2


@pytest.mark.process("refactor-overflow.sh run through a symlink to the skill directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_files_through_gh_there(
        tmp_path):
    owed = owed_504(tmp_path)
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\npwd -P > "$EXP_GH_PWD"\nprintf \'%s\\n\' "$@" > "$EXP_GH_ARGS"\n'
                  f'echo "{URL.rstrip()}"\n')
    gh.chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}",
               EXP_GH_PWD=str(tmp_path / "gh-pwd"), EXP_GH_ARGS=str(tmp_path / "gh-args"))

    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "refactor-overflow.sh"), "504", str(owed), "1"],
                         cwd=elsewhere, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, URL, "")
    assert (tmp_path / "gh-args").read_text() == "\n".join(issue(
        504, f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}")) + "\n"
    assert (tmp_path / "gh-pwd").read_text() == f"{elsewhere.resolve()}\n"


def test_cli_files_one_refactor_owed_issue_whose_body_lists_the_transform_over_an_owed_file_holding_only_an_out_of_scope_candidate_issue_992(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-992-refactor-owed.md"
    owed.write_text(f"### first step\n- out-of-scope | {MKTEMP}\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["992", str(owed), "0"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(992, f"Out-of-scope transforms #992's closing pass did not attempt:\n\n- {MKTEMP}")


def test_cli_files_a_body_carrying_only_the_out_of_scope_heading_when_only_out_of_scope_transforms_are_owed_issue_1035(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-1035-refactor-owed.md"
    owed.write_text(f"### first step\n- out-of-scope | {MKTEMP}\n")
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["1035", str(owed), "0"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(1035, f"Out-of-scope transforms #1035's closing pass did not attempt:\n\n- {MKTEMP}")


def test_cli_files_no_out_of_scope_candidate_the_owed_file_records_as_applied_and_still_files_an_unapplied_one_issue_1058(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = tmp_path / "issue-1058-refactor-owed.md"
    owed.write_text(f"### fourth step\n- out-of-scope | {REMOVE}\napplied | 1b4ed26 | out-of-scope | {REMOVE}\n")
    calls = fake_processes(gh_files)

    assert (run_cli(refactor_overflow, ["1058", str(owed), "0"], cwd=tmp_path), filed(calls)) == ((3, "", ""), [])

    with owed.open("a") as f:
        f.write(f"### fifth step\n- out-of-scope | {MKTEMP}\n")

    result = run_cli(refactor_overflow, ["1058", str(owed), "0"], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(1058, f"Out-of-scope transforms #1058's closing pass did not attempt:\n\n- {MKTEMP}")


@pytest.mark.parametrize("owed_text, reached, body", [
    (f"### first step\n- {HOIST}\n- out-of-scope | {MKTEMP}\n", "0",
     f"Structural candidates #1035's closing pass could not reach:\n\n- {HOIST}\n\n"
     f"Out-of-scope transforms #1035's closing pass did not attempt:\n\n- {MKTEMP}"),
    (f"### first step\n- {HOIST}\n- {SPLIT}\n", "1",
     f"Structural candidates #1035's closing pass could not reach:\n\n- {SPLIT}"),
])
def test_cli_files_a_headed_list_per_kind_owed_under_the_unchanged_title_issue_1035(
        tmp_path, refactor_overflow, run_cli, fake_processes, owed_text, reached, body):
    owed = tmp_path / "issue-1035-refactor-owed.md"
    owed.write_text(owed_text)
    calls = fake_processes(gh_files)

    result = run_cli(refactor_overflow, ["1035", str(owed), reached], cwd=tmp_path)

    assert result == (0, URL, "")
    assert filed(calls) == filing(1035, body)


def test_cli_comments_the_unlisted_candidates_on_the_open_refactor_owed_issue_and_files_none_issue_1609(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    existing = "https://github.com/o/r/issues/42"
    open_issues = json.dumps([
        {"number": 7, "title": "Refactor owed by #50", "html_url": "https://github.com/o/r/issues/7", "body": ""},
        {"number": 42, "title": "Refactor owed by #504", "html_url": existing,
         "body": f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}"}])

    def gh(line, **kwargs):
        if is_lookup(line):
            return 0, open_issues, ""
        return 0, "https://github.com/o/r/issues/43\n", ""

    calls = fake_processes(gh)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    commented = [c for c in calls if "issues/42/comments" in c]
    assert result == (0, existing + "\n", "")
    assert [c for c in calls if "title=" in c] == []
    assert len(commented) == 1 and SPLIT in commented[0] and FOLD not in commented[0]


def test_cli_files_no_issue_and_posts_no_comment_when_the_open_refactor_owed_issue_already_lists_every_candidate_issue_1609(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    existing = "https://github.com/o/r/issues/42"
    open_issues = json.dumps([
        {"number": 42, "title": "Refactor owed by #504", "html_url": existing,
         "body": f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}"}])

    def gh(line, **kwargs):
        if is_lookup(line):
            return 0, open_issues, ""
        return 0, "https://github.com/o/r/issues/43\n", ""

    calls = fake_processes(gh)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    assert result == (0, existing + "\n", "")
    assert filed(calls) == []


def test_cli_finds_the_open_refactor_owed_issue_beyond_the_first_page_of_open_issues_and_files_none_issue_1609(
        tmp_path, refactor_overflow, run_cli, fake_processes):
    owed = owed_504(tmp_path)
    existing = "https://github.com/o/r/issues/142"
    first_page = [{"number": i, "title": f"Unrelated #{i}", "html_url": f"https://github.com/o/r/issues/{i}", "body": ""}
                  for i in range(1, 101)]
    second_page = [{"number": 142, "title": "Refactor owed by #504", "html_url": existing,
                    "body": f"Structural candidates #504's closing pass could not reach:\n\n- {FOLD}\n- {SPLIT}"}]

    def gh(line, **kwargs):
        if is_lookup(line):
            page = re.search(r"[?&]page=(\d+)", line)
            pages = {None: first_page, "1": first_page, "2": second_page}
            return 0, json.dumps(pages.get(page and page.group(1), [])), ""
        return 0, "https://github.com/o/r/issues/143\n", ""

    calls = fake_processes(gh)

    result = run_cli(refactor_overflow, ["504", str(owed), "1"], cwd=tmp_path)

    assert result == (0, existing + "\n", "")
    assert [c for c in calls if "title=" in c] == []
