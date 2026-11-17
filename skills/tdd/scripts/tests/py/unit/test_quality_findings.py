"""test-quality.sh record (veri/quality_findings.py): the develop-test-quality leaf's FINDING: lines, recorded (#4119)."""
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
    path = worktree / ".tdd" / "issue-7-test-quality.md"
    return code, err, path.read_text() if path.exists() else None


def test_record_writes_each_finding_in_report_order_and_exits_0(run_cli, test_quality, worktree):
    report = ("I read both cases.\n"
              "FINDING: weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic, not the adder\n"
              "  FINDING: redundant | tests/test_alpha.py::TestGroup::test_inner | asserts nothing at all\n")

    assert record(run_cli, test_quality, worktree, report) == (0, "", (
        "weak-assertion | tests/test_alpha.py::test_adds | asserts arithmetic, not the adder\n"
        "redundant | tests/test_alpha.py::TestGroup::test_inner | asserts nothing at all\n"))


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
    previous = worktree / ".tdd" / "issue-7-test-quality.md"
    previous.write_text("an earlier record\n")

    code, err, written = record(run_cli, test_quality, worktree, report)

    assert (code, reason in err, written) == (2, True, "an earlier record\n")


def test_record_refuses_a_missing_verb_or_issue_number_with_exit_2(run_cli, test_quality, worktree):
    answers = [run_cli(test_quality, argv, stdin="FINDING: none\n", cwd=str(worktree))[0]
               for argv in ([], ["record"], ["record", "x"], ["list", "7"])]

    assert (answers, (worktree / ".tdd" / "issue-7-test-quality.md").exists()) == ([2, 2, 2, 2], False)
