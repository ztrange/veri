"""Cases for veri/case_history.py that need a real repository: the fakes in unit/test_case_history.py pin
the argv, these pin that git answers the way the module reads it."""
import importlib
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout.strip()


@pytest.mark.process("git")
def test_the_queries_answer_over_a_repository_of_three_commits(tmp_path, monkeypatch):
    case_history = importlib.import_module("veri.case_history")
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    suite, ledger = repo / "test_x.py", repo / ".tdd" / "issue-7.md"
    ledger.write_text("- [ ] one\n- [ ] two\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "plan: scope")
    plan = git(repo, "rev-parse", "HEAD")
    suite.write_text("def test_one():\n    assert 1\n")
    ledger.write_text("- [x] one\n- [ ] two\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "feat: one")
    first = git(repo, "rev-parse", "HEAD")
    suite.write_text("def test_one():\n    assert 1\n\n\ndef test_two():\n    assert 2\n")
    ledger.write_text("- [x] one\n- [x] two\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "refactor: two")
    second = git(repo, "rev-parse", "HEAD")
    suite.write_text("def test_three():\n    assert 3\n")
    monkeypatch.chdir(repo)

    assert (
        case_history.toplevel() == str(repo.resolve()),
        case_history.has_rev("HEAD~1"), case_history.has_rev("HEAD~9"),
        case_history.current_branch(),
        sorted(case_history.cases_at("HEAD", "test_x.py")), case_history.cases_at("HEAD~2", "test_x.py"),
        case_history.revisions("test_x.py"), case_history.revisions("test_x.py", since=first),
        case_history.subject(second), case_history.first_revision_with("one", ".tdd/issue-7.md") == plan,
        case_history.changed_test_files(),
        case_history.step_commits("two", "7"), case_history.commit_of("HEAD"),
    ) == (
        True, True, False, "main",
        ["test_one", "test_two"], {},
        [second, first], [second],
        "refactor: two\n", True,
        ["test_x.py"],
        {second}, second,
    )
