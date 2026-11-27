"""In-process cases for veri/covering_tests.py, which parses a red report's `COVERING_TESTS:` line, and for
red-half.sh's stop on a `HOLDS` report naming those ids (PRD 044.2, D7, D8, RD115)."""
import importlib

import pytest
from test_red_half import BRANCH_BASE, LEDGER, STEP, Fake

TRACKED = "tests/test_b.py\n"
HOLDS = ("TEST_PATH:\nTARGET_TEST:\nAGAINST_UNMODIFIED: HOLDS\nCOVERING_TESTS: tests/test_b.py::test_two\n"
         "WHY: already covered\n")


@pytest.fixture
def red(monkeypatch, run_cli, tmp_path):
    """red(report) runs red-half for issue 12 from the main tree on <report> as develop-red's, `git ls-files` listing
    TRACKED; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    red_half = importlib.import_module("veri.red_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    for name, text in (("issue-12-branch-base", BRANCH_BASE + "\n"),
                       ("issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                       ("issue-12.md", LEDGER % STEP), ("issue-12-spec.md", "# spec\n"), ("develop-red.out", "{}\n")):
        (wt / ".tdd" / name).write_text(text)

    def go(report):
        fake = Fake({("git", "ls-files"): (0, TRACKED)}, report=report)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(red_half, ["12"], cwd=str(tmp_path))
        return code, out, err, fake

    return go


def test_red_half_on_a_holds_report_naming_one_tracked_id_stops_at_red_2_with_exit_1_naming_the_id(red):
    code, out, err, fake = red(HOLDS)

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 COVERING_TESTS: tests/test_b.py::test_two")
    assert "verdict-red" not in fake.launched()


def test_red_half_on_a_holds_report_whose_covering_tests_line_holds_no_id_exits_2(red):
    code, out, err, fake = red(HOLDS.replace(" tests/test_b.py::test_two", ""))

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 COVERING_TESTS: holds no id")
    assert "verdict-red" not in fake.launched()
