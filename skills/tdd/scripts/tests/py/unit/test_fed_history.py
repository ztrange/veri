"""The fed_history fixture: case_history answered from a table of named revisions (PRD 017.5, R26, R27)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


LEDGER = ".tdd/issue-7.md"
ONE = "def test_one():\n    assert 1\n"
TWO = "def test_two():\n    assert 2\n"
SUITE, GONE = "tests/test_a.py", "tests/test_gone.py"  # names, not literals, in calls: a literal suite path reads as a nested run


def test_fed_history_answers_every_case_history_query_tests_frozen_makes_from_its_table_of_named_revisions(
        tmp_path, fed_history, tests_frozen):
    fed_history(("base", "start", {"tests/test_a.py": ONE, "src/a.py": "x = 1\n",
                                   LEDGER: "# Plan for #7\n\n- [ ] step one\n- [ ] step two\n"}),
                ("red", "red: test_two", {"tests/test_a.py": ONE + "\n\n" + TWO}),
                ("green", "green: step one", {"src/a.py": "x = 2\n",
                                              LEDGER: "# Plan for #7\n\n- [x] step one\n- [ ] step two\n"}),
                ("later", "red: step two", {"src/a.py": "x = 3\n"}),
                root=tmp_path, branch="tdd/7-thing")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(ONE)
    (tmp_path / "tests" / "test_b.py").write_text(TWO)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 4\n")
    history = tests_frozen.case_history

    answers = {
        "toplevel": history.toplevel(),
        "has_rev": [history.has_rev(rev) for rev in ("HEAD", "HEAD~1", "base", "HEAD~4", "nowhere")],
        "current_branch": history.current_branch(),
        "text_at": [history.text_at("HEAD~3", SUITE, quiet=True), history.text_at("red", "gone.py")],
        "cases_at": [sorted(history.cases_at(rev, SUITE)) for rev in ("base", "HEAD")],
        "cases_at absent": history.cases_at("HEAD", GONE),
        "revisions": [history.revisions(SUITE), history.revisions("src/a.py", since="red")],
        "first_revision_with": [history.first_revision_with("test_two", SUITE),
                                history.first_revision_with("never", SUITE)],
        "changed_test_files": history.changed_test_files(),
        "commit_of": history.commit_of("HEAD~2"),
        "step_commits": [sorted(history.step_commits("step one", "7")), sorted(history.step_commits("step two", "7"))],
    }

    assert answers == {
        "toplevel": str(tmp_path),
        "has_rev": [True, True, True, False, False],
        "current_branch": "tdd/7-thing",
        "text_at": [ONE, ""],
        "cases_at": [["test_one"], ["test_one", "test_two"]],
        "cases_at absent": {},
        "revisions": [["red", "base"], ["later", "green"]],
        "first_revision_with": ["red", ""],
        "changed_test_files": ["tests/test_a.py", "tests/test_b.py"],
        "commit_of": "red",
        "step_commits": [["green", "red"], ["later"]],
    }
