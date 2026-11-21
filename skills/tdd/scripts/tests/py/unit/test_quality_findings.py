"""test-quality.sh record (veri/quality_findings.py): the develop-test-quality leaf's FINDING: lines, recorded (#4119)."""
import fnmatch
import importlib

import pytest

ALPHA = "def test_adds():\n    assert 1 + 1 == 2\n\n\nclass TestGroup:\n    def test_inner(self):\n        assert True\n"


@pytest.fixture
def test_quality():
    return importlib.import_module("veri.quality_findings")


@pytest.fixture
def worktree(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text(ALPHA)
    return tmp_path


def record(run_cli, test_quality, worktree, report):
    code, out, err = run_cli(test_quality, ["record", "7"], stdin=report, cwd=str(worktree))
    path = worktree / ".tdd" / "issue-7-test-quality"
    return code, err, path.read_text() if path.exists() else None


def test_record_writes_each_finding_in_report_order_and_exits_0(run_cli, test_quality, worktree):
    report = ("I read both cases.\n"
              "FINDING: weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic, not the adder\n"
              "  FINDING: redundant | tests/test_alpha.py::TestGroup::test_inner | asserts nothing at all\n")

    assert record(run_cli, test_quality, worktree, report) == (0, "", (
        "weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic, not the adder\n"
        "redundant | tests/test_alpha.py::TestGroup::test_inner | asserts nothing at all\n"))


def test_the_record_is_named_so_the_installed_ignore_rule_never_readmits_it(run_cli, test_quality, worktree):
    record(run_cli, test_quality, worktree, "FINDING: none\n")

    assert [p.name for p in (worktree / ".tdd").iterdir() if fnmatch.fnmatch(p.name, "issue-*.md")] == []


def test_record_exits_3_on_finding_none_writing_the_file_with_no_finding(run_cli, test_quality, worktree):
    assert record(run_cli, test_quality, worktree, "all good\nFINDING: none\n") == (3, "", "")


@pytest.mark.parametrize("report, reason", [
    ("FINDING: weak-assertion | tests/test_alpha.py | no case named\n", "names no <file>::<case>"),
    ("FINDING: redundant | tests/test_alpha.py::test_gone | gone\n", "does not define"),
    ("FINDING: redundant | tests/test_missing.py::test_adds | gone\n", "does not define"),
    ("FINDING: flaky | tests/test_alpha.py::test_adds | an unknown kind\n", "not one of"),
    ("FINDING: weak-assertion | tests/test_alpha.py::test_adds\n", "names no <file>::<case>"),
    ("I found nothing to say.\n", "no FINDING: line"),
])
def test_record_exits_2_writing_nothing_on_a_line_it_cannot_record(run_cli, test_quality, worktree, report, reason):
    previous = worktree / ".tdd" / "issue-7-test-quality"
    previous.write_text("an earlier record\n")

    code, err, written = record(run_cli, test_quality, worktree, report)

    assert (code, reason in err, written) == (2, True, "an earlier record\n")


def test_record_writes_the_valid_findings_and_names_one_naming_a_non_test_helper_on_stderr_4534(
        run_cli, test_quality, worktree):
    (worktree / "tests" / "test_alpha.py").write_text(ALPHA + "\n\ndef first_stages():\n    return []\n")
    report = ("FINDING: weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic only\n"
              "FINDING: redundant | tests/test_alpha.py::first_stages | a helper, not a case\n")

    code, err, written = record(run_cli, test_quality, worktree, report)

    assert (code, "tests/test_alpha.py::first_stages" in err, written) == (
        0, True, "weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic only\n")


@pytest.mark.parametrize("bad, named", [
    ("FINDING: redundant | tests/test_alpha.py | no case named\n", "names no <file>::<case>"),
    ("FINDING: flaky | tests/test_alpha.py::test_inner | an unknown kind\n", "not one of"),
])
def test_record_writes_the_valid_finding_and_skips_a_malformed_or_unknown_kind_line_beside_it_4534(
        run_cli, test_quality, worktree, bad, named):
    report = ("FINDING: weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic only\n" + bad)

    code, err, written = record(run_cli, test_quality, worktree, report)

    assert (code, "finding skipped" in err, named in err, written) == (
        0, True, True, "weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic only\n")


def test_record_exits_2_writing_nothing_when_every_finding_of_the_report_is_refused_4534(
        run_cli, test_quality, worktree):
    previous = worktree / ".tdd" / "issue-7-test-quality"
    previous.write_text("an earlier record\n")
    report = ("FINDING: weak-assertion | tests/test_alpha.py::first_stages | a helper, not a case\n"
              "FINDING: redundant | tests/test_alpha.py::test_gone | gone\n")

    code, err, written = record(run_cli, test_quality, worktree, report)

    assert (code, "nothing recorded" in err, written) == (2, True, "an earlier record\n")


def test_record_refuses_a_missing_verb_or_issue_number_with_exit_2(run_cli, test_quality, worktree):
    answers = [run_cli(test_quality, argv, stdin="FINDING: none\n", cwd=str(worktree))[0]
               for argv in ([], ["record"], ["record", "x"], ["list", "7"])]

    assert (answers, (worktree / ".tdd" / "issue-7-test-quality").exists()) == ([2, 2, 2, 2], False)


LEDGER = ("# Plan\n\n"
          "- [x] the adder adds ⟦criterion 1⟧\n"
          "- [x] the adder carries ⟦criterion 2⟧ ⟂ refactor pending\n"
          "- [ ] the adder overflows ⟦criterion 3⟧\n")


@pytest.mark.parametrize("ledger, answer", [
    (LEDGER, (0, "the adder carries ⟦criterion 2⟧\n")),
    (LEDGER.replace("- [x] the adder carries", "- [ ] the adder carries"), (0, "the adder adds ⟦criterion 1⟧\n")),
    (LEDGER.replace("⟦criterion 2⟧", "⟦criterion 2⟧ ⟦criterion 3⟧"), (3, "")),
    (LEDGER.replace("[x]", "[ ]"), (3, "")),
])
def test_anchor_prints_the_last_done_step_add_ledger_step_accepts_or_exits_3(run_cli, test_quality, worktree,
                                                                            ledger, answer):
    (worktree / ".tdd" / "issue-7.md").write_text(ledger)

    assert run_cli(test_quality, ["anchor", ".tdd/issue-7.md"], cwd=str(worktree))[:2] == answer


def test_anchor_exits_2_on_an_unreadable_ledger(run_cli, test_quality, worktree):
    assert run_cli(test_quality, ["anchor", ".tdd/issue-8.md"], cwd=str(worktree))[0] == 2


def test_files_prints_the_test_files_the_range_names_that_still_exist_and_exits_0(run_cli, test_quality, worktree,
                                                                                  fake_processes):
    (worktree / "src").mkdir()
    (worktree / "src" / "adder.py").write_text("def add(a, b):\n    return a + b\n")
    fake = fake_processes.answers(
        {"git diff --name-only": (0, "src/adder.py\ntests/test_alpha.py\ntests/test_gone.py\n", "")})

    code, out, err = run_cli(test_quality, ["files", "abc1234"], cwd=str(worktree))

    assert (code, out, err, fake.calls) == (0, "tests/test_alpha.py\n", "", ["git diff --name-only abc1234..HEAD"])


def test_files_exits_3_when_the_range_names_no_test_file_and_2_when_git_cannot_answer(run_cli, test_quality, worktree,
                                                                                      fake_processes):
    fake_processes.answers({"git diff --name-only": [(0, "src/adder.py\n", ""), (128, "", "fatal: bad revision\n")]})

    answers = [run_cli(test_quality, ["files", "abc1234"], cwd=str(worktree))[:2] for _ in range(2)]

    assert answers == [(3, ""), (2, "")]
