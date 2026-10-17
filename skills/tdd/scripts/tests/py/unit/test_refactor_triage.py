"""In-process cases for veri/refactor_triage.py, the module refactor-triage.sh is a shim over."""
import importlib
import io
import re
import sys

import pytest

from conftest import SCRIPTS


@pytest.fixture
def refactor_triage():
    return importlib.import_module("veri.refactor_triage")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_prints_structural_candidates_exits_3_with_none_left_and_refuses_a_report_with_exit_2_and_its_diagnostic(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: structural | x\n",
            b"CANDIDATES: cosmetic | x\n",
            b"CANDIDATES: none\n",
            b"",
            b"CANDIDATES: cosmic | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        b"CANDIDATES: structural | x\n": (0, b"x\n", b""),
        b"CANDIDATES: cosmetic | x\n": (3, b"", b""),
        b"CANDIDATES: none\n": (3, b"", b""),
        b"": (2, b"", b"refactor-triage: the report has no CANDIDATES: line\n"),
        b"CANDIDATES: cosmic | x\n": (
            2, b"",
            b"refactor-triage: candidate line has no class, or one that is not structural, cosmetic, test-only or out-of-scope: "
            b"CANDIDATES: cosmic | x\n"),
    }


def test_main_reads_a_test_only_candidate_as_its_own_class_exiting_3_alone_printing_only_the_structural_beside_it_and_refusing_a_capitalised_class(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b'RESULT: applied "inline the single-use variable", suite green\n'
            b"CANDIDATES: test-only | fold the three mktemp fixtures into one helper\n",
            b"CANDIDATES: test-only | x\nCANDIDATES: structural | y\n",
            b"CANDIDATES: Test-only | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, capsysbinary.readouterr().out)

    assert results == {
        b'RESULT: applied "inline the single-use variable", suite green\n'
        b"CANDIDATES: test-only | fold the three mktemp fixtures into one helper\n": (3, b""),
        b"CANDIDATES: test-only | x\nCANDIDATES: structural | y\n": (0, b"y\n"),
        b"CANDIDATES: Test-only | x\n": (2, b""),
    }


def test_main_reads_an_out_of_scope_candidate_and_never_prints_it_exiting_3_alone_printing_only_the_structural_beside_it_in_either_order_and_refusing_a_capitalised_class(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: out-of-scope | x\n",
            b"CANDIDATES: out-of-scope | x\nCANDIDATES: structural | y\n",
            b"CANDIDATES: structural | y\nCANDIDATES: out-of-scope | x\n",
            b"CANDIDATES: Out-of-scope | x\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert results == {
        b"CANDIDATES: out-of-scope | x\n": (3, b"", b""),
        b"CANDIDATES: out-of-scope | x\nCANDIDATES: structural | y\n": (0, b"y\n", b""),
        b"CANDIDATES: structural | y\nCANDIDATES: out-of-scope | x\n": (0, b"y\n", b""),
        b"CANDIDATES: Out-of-scope | x\n": (
            2, b"",
            b"refactor-triage: candidate line has no class, or one that is not structural, cosmetic, test-only or out-of-scope: "
            b"CANDIDATES: Out-of-scope | x\n"),
    }


def test_main_reads_and_writes_bytes_keeping_a_last_line_without_newline_dropping_nul_passing_non_utf8_through_reading_no_break_space_as_not_whitespace_under_any_locale_and_ignoring_argv(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: structural | a",
            b"CANDIDATES: structural | a\0b\n",
            b"CANDIDATES: structural | \377\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())
    for env in ({}, {"LC_ALL": "en_US.UTF-8"}, {"LC_CTYPE": "en_US.UTF-8"}, {"LANG": "en_US.UTF-8"}):
        for name in ("LC_ALL", "LC_CTYPE", "LANG"):
            monkeypatch.delenv(name, raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        fake_stdin(monkeypatch, b"CANDIDATES:\xc2\xa0structural | a\n")
        code = refactor_triage.main([])
        results[tuple(env.items())] = (code, capsysbinary.readouterr().out)
    fake_stdin(monkeypatch, b"CANDIDATES: structural | x\n")
    code = refactor_triage.main(["foo", "bar"])
    results["argv"] = (code, *capsysbinary.readouterr())

    assert results == {
        b"CANDIDATES: structural | a": (0, b"a\n", b""),
        b"CANDIDATES: structural | a\0b\n": (0, b"ab\n", b""),
        b"CANDIDATES: structural | \377\n": (0, b"\377\n", b""),
        (): (2, b""),
        (("LC_ALL", "en_US.UTF-8"),): (2, b""),
        (("LC_CTYPE", "en_US.UTF-8"),): (2, b""),
        (("LANG", "en_US.UTF-8"),): (2, b""),
        "argv": (0, b"x\n", b""),
    }


def test_main_reads_the_class_with_optional_whitespace_around_it_and_the_bar_matched_exactly_and_case_sensitively_and_counts_only_a_line_starting_candidates(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES:none\n",
            b"CANDIDATES: none \r\n",
            b"CANDIDATES:\tstructural\t|\tx\n",
            b"CANDIDATES: structural\v| x\n",
            b"CANDIDATES: Structural | x\n",
            b"CANDIDATES: None\n",
            b"CANDIDATES:\n",
            b"CANDIDATES: none | x\n",
            b"CANDIDATES: test-only\n",
            b"CANDIDATES: out-of-scope\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, capsysbinary.readouterr().out)
    for report in (b" CANDIDATES: structural | a\n", b"candidates: structural | a\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert results == {
        b"CANDIDATES:none\n": (3, b""),
        b"CANDIDATES: none \r\n": (3, b""),
        b"CANDIDATES:\tstructural\t|\tx\n": (0, b"x\n"),
        b"CANDIDATES: structural\v| x\n": (0, b"x\n"),
        b"CANDIDATES: Structural | x\n": (2, b""),
        b"CANDIDATES: None\n": (2, b""),
        b"CANDIDATES:\n": (2, b""),
        b"CANDIDATES: none | x\n": (2, b""),
        b"CANDIDATES: test-only\n": (2, b""),
        b"CANDIDATES: out-of-scope\n": (2, b""),
        b" CANDIDATES: structural | a\n": (2, b"", b"refactor-triage: the report has no CANDIDATES: line\n"),
        b"candidates: structural | a\n": (2, b"", b"refactor-triage: the report has no CANDIDATES: line\n"),
    }


def test_main_prints_the_transform_after_the_first_bar_keeping_trailing_whitespace_and_cr_printing_duplicates_and_empty_transforms_and_stops_at_the_first_refused_line(
        monkeypatch, capsysbinary, refactor_triage):
    results = {}
    for report in (
            b"CANDIDATES: structural |  x  \n",
            b"CANDIDATES: structural | a | b\n",
            b"CANDIDATES: structural | x\r\n",
            b"CANDIDATES: structural |\n",
            b"CANDIDATES: structural | x\nCANDIDATES: structural | y\nCANDIDATES: structural | x\n",
            b"CANDIDATES: none\nCANDIDATES: structural | x\n",
            b"CANDIDATES: structural | x\nCANDIDATES: cosmic | y\r\nCANDIDATES: structural | z\n"):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        results[report] = (code, *capsysbinary.readouterr())

    assert results == {
        b"CANDIDATES: structural |  x  \n": (0, b"x  \n", b""),
        b"CANDIDATES: structural | a | b\n": (0, b"a | b\n", b""),
        b"CANDIDATES: structural | x\r\n": (0, b"x\r\n", b""),
        b"CANDIDATES: structural |\n": (
            2, b"", b"refactor-triage: structural candidate line names no transform: CANDIDATES: structural |\n"),
        b"CANDIDATES: structural | x\nCANDIDATES: structural | y\nCANDIDATES: structural | x\n": (
            0, b"x\ny\nx\n", b""),
        b"CANDIDATES: none\nCANDIDATES: structural | x\n": (0, b"x\n", b""),
        b"CANDIDATES: structural | x\nCANDIDATES: cosmic | y\r\nCANDIDATES: structural | z\n": (
            2, b"",
            b"refactor-triage: candidate line has no class, or one that is not structural, cosmetic, test-only or out-of-scope: "
            b"CANDIDATES: cosmic | y\r\n"),
    }


def test_main_lets_an_unexpected_failure_escape_as_an_exception_with_stdin_or_stdout_closed(
        monkeypatch, capsysbinary, refactor_triage):
    monkeypatch.setattr(sys, "stdin", None)
    with pytest.raises(Exception):
        refactor_triage.main([])
    fake_stdin(monkeypatch, b"CANDIDATES: structural | x\n")
    monkeypatch.setattr(sys, "stdout", None)
    with pytest.raises(Exception):
        refactor_triage.main([])


def test_main_answers_the_six_contract_cases_of_refactor_triage_test_sh_in_process(
        monkeypatch, capsysbinary, refactor_triage):
    def run(report):
        fake_stdin(monkeypatch, report)
        code = refactor_triage.main([])
        return (code, *capsysbinary.readouterr())

    structural = (b'RESULT: applied "fold verify.sh\'s two prompt paths into one", suite green\n'
                  b"FLAGS: none\n"
                  b"CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper\n"
                  b"CANDIDATES: cosmetic | reflow the header comment to ninety columns\n"
                  b"CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds\n")
    code, out, _ = run(structural)
    assert (code, out) == (
        0, b"fold verify.sh's two mktemp calls into one helper\n"
           b"rename $tmp to $prompt_file, which is what it holds\n")

    applied = b'RESULT: applied "inline the single-use $phase_label variable", suite green\nFLAGS: none\n'
    for report in (
            b'RESULT: applied "extract the two mktemp calls into one helper", suite green\nFLAGS: none\n'
            b"CANDIDATES: cosmetic | reflow the header comment to ninety columns\n"
            b"CANDIDATES: cosmetic | re-cite SKILL.md's Refactor entry by section, not line\n",
            applied + b"CANDIDATES: none\n"):
        assert run(report)[0] == 3

    extracted = b'RESULT: applied "extract the two mktemp calls into one helper", suite green\nFLAGS: none\n'
    for report in (
            extracted + b"CANDIDATES: fold verify.sh's two prompt paths into one\n",
            extracted + b"CANDIDATES: cosmic | reflow the header comment to ninety columns\n",
            applied):
        code, out, err = run(report)
        assert (code, out) == (2, b"")
        assert err != b""

    assert run(applied
               + b"CANDIDATES: test-only | fold the suite's three mktemp fixtures into one helper\n"
               + b"CANDIDATES: test-only | rename the suite's $out to $stdout_file\n")[0] == 3
    code, out, _ = run(applied
                       + b"CANDIDATES: test-only | fold the suite's three mktemp fixtures into one helper\n"
                       + b"CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper\n")
    assert (code, out) == (0, b"fold verify.sh's two mktemp calls into one helper\n")

    new_steps = (b"NEW_STEP: the parser accepts a second header field\n"
                 b"NEW_STEP: the parser rejects a header field it has no name for\n")
    for report in (
            b'RESULT: applied "inline the single-use $phase_label variable", suite green\n'
            b"CANDIDATES: structural | fold the two mktemp calls into one helper\n",
            b'RESULT: applied "inline the single-use $phase_label variable", suite green\nCANDIDATES: none\n',
            b'RESULT: applied "inline the single-use $phase_label variable", suite green\n'):
        assert run(report + new_steps)[0] == run(report)[0]

    code, out, _ = run(b'RESULT: applied "inline the single-use variable", suite green\nFLAGS: none\n'
                       b"CANDIDATES: out-of-scope | extract the shared mktemp helper across scripts "
                       b"outside this issue's files\n")
    assert (code, out) == (3, b"")


def test_main_refuses_a_structural_candidate_with_nothing_after_the_bar_with_exit_2_a_diagnostic_and_nothing_on_stdout_820(
        monkeypatch, capsysbinary, refactor_triage):
    fake_stdin(monkeypatch, b"CANDIDATES: structural |\n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err != b""


def test_main_refuses_a_structural_candidate_with_only_whitespace_after_the_bar_with_exit_2_a_diagnostic_and_nothing_on_stdout_820(
        monkeypatch, capsysbinary, refactor_triage):
    fake_stdin(monkeypatch, b"CANDIDATES: structural |  \t \n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err != b""


def test_main_refuses_an_unknown_class_with_a_diagnostic_naming_all_four_accepted_classes_and_ending_with_the_line_1035(
        monkeypatch, capsysbinary, refactor_triage):
    line = b"CANDIDATES: cosmic | x"
    fake_stdin(monkeypatch, line + b"\n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err.startswith(b"refactor-triage: ")
    assert err.endswith(b": " + line + b"\n")
    named = err[:-len(line + b"\n")]
    assert [cls for cls in (b"structural", b"cosmetic", b"test-only", b"out-of-scope") if cls not in named] == []


def test_main_refuses_a_cosmetic_candidate_with_nothing_after_the_bar_with_exit_2_and_a_diagnostic_naming_the_line_1035(
        monkeypatch, capsysbinary, refactor_triage):
    line = b"CANDIDATES: cosmetic |"
    fake_stdin(monkeypatch, line + b"\n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err.startswith(b"refactor-triage: ")
    assert err.endswith(b": " + line + b"\n")


def test_main_refuses_a_test_only_candidate_with_nothing_after_the_bar_with_exit_2_and_a_diagnostic_naming_the_line_1035(
        monkeypatch, capsysbinary, refactor_triage):
    line = b"CANDIDATES: test-only |"
    fake_stdin(monkeypatch, line + b"\n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err.startswith(b"refactor-triage: ")
    assert err.endswith(b": " + line + b"\n")


def test_main_refuses_an_out_of_scope_candidate_with_nothing_after_the_bar_with_exit_2_and_a_diagnostic_naming_the_line_1035(
        monkeypatch, capsysbinary, refactor_triage):
    line = b"CANDIDATES: out-of-scope |"
    fake_stdin(monkeypatch, line + b"\n")
    code = refactor_triage.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out) == (2, b"")
    assert err.startswith(b"refactor-triage: ")
    assert err.endswith(b": " + line + b"\n")


SKILL_MD = SCRIPTS.parent / "SKILL.md"
SKILL_NAME = "skills/tdd/SKILL.md"


def refactor_loop_lines():
    inside, kept = False, []
    for line in SKILL_MD.read_bytes().split(b"\n"):
        if not inside:
            inside = line.startswith(b"#### Refactor loop")
            continue
        if line.startswith(b"#"):
            break
        kept.append(line.replace(b"*", b"").replace(b"`", b"").lower())
    if kept and kept[-1] == b"":
        kept.pop()
    return kept


def line_of(lines, pattern):
    for number, line in enumerate(lines, 1):
        if re.search(pattern, line):
            return number
    return None


def test_skill_md_refactor_loop_calls_refactor_triage_sh_on_each_committed_transform_and_stops_on_exit_3_and_exit_2():
    lines = refactor_loop_lines()
    problems = []
    if not b"".join(lines).strip():
        problems.append(f"{SKILL_NAME} has no '#### Refactor loop' section to read")
    else:
        triage_at = line_of(lines, rb"refactor-triage\.sh")
        commit_at = line_of(lines, rb'git commit -m "refactor:')
        if triage_at is None:
            problems.append(f"{SKILL_NAME}'s refactor loop never names refactor-triage.sh")
        elif commit_at is None:
            problems.append(f"{SKILL_NAME}'s refactor loop no longer commits the transform")
        elif triage_at < commit_at:
            problems.append(f"{SKILL_NAME}'s refactor loop calls refactor-triage.sh (line {triage_at}) "
                            f"before it commits the transform (line {commit_at})")
        flat = b" ".join(lines) + b" "
        windows = re.findall(rb"refactor-triage\.sh.{0,250}", flat)
        if not any(re.search(rb"(exits? 3.{0,120}stop|stop.{0,120}exits? 3)", w) for w in windows):
            problems.append(f"{SKILL_NAME}'s refactor loop never says exit 3 stops it")
        if not any(re.search(rb"(exits? 2.{0,160}narrat|narrat.{0,160}exits? 2)", w) for w in windows):
            problems.append(f"{SKILL_NAME}'s refactor loop never says exit 2 is narrated")
    assert problems == []


def test_skill_md_refactor_comment_names_which_of_the_three_stop_conditions_ended_the_loop_and_files_the_leftovers_by_class():
    narration, inside = [], False
    for line in refactor_loop_lines():
        if not inside and b"###" in line and b"refactor" in line:
            inside = True
        if inside and re.match(rb"^ *- pass:", line):
            break
        if inside:
            narration.append(line)
    text = b" ".join(narration) + b" "
    problems = []
    if not text.strip():
        problems.append(f"{SKILL_NAME}'s refactor loop names no ### comment to post")
    else:
        if b"nothing left to tidy" not in text:
            problems.append("the comment never says the loop ran dry: nothing left to tidy")
        if b"budget" not in text:
            problems.append("the comment never names the budget")
        if not re.search(rb"(no|nothing|none)[ a-z]{0,14}structural|only cosmetic|refactor-triage", text):
            problems.append("the comment never names the third stop condition")
        if b"cosmetic" not in text:
            problems.append("the comment never mentions cosmetic leftovers")
        if not re.search(rb"separat|apart|split|by class|per class|each class|own list|own line|own heading|own group",
                         text):
            problems.append("the comment never keeps structural leftovers apart from cosmetic ones")
    assert problems == []
