"""In-process cases for veri/run_dir.py, the one spelling of a path inside a run's .tdd/ directory."""
import importlib

import pytest


def test_run_file_names_a_plain_file_and_a_glob_inside_the_runs_tdd_directory():
    run_dir = importlib.import_module("veri.run_dir")

    assert [run_dir.run_file("/repo/.tdd/wt/42", "events.jsonl"),
            run_dir.run_file("/repo/.tdd/wt/42", "*.conductor.out")] == [
        "/repo/.tdd/wt/42/.tdd/events.jsonl",
        "/repo/.tdd/wt/42/.tdd/*.conductor.out",
    ]


def test_main_tree_paths_name_the_tdd_directory_the_runs_directory_and_one_run():
    run_dir = importlib.import_module("veri.run_dir")

    assert [run_dir.main_file("/repo", "merge.lock"),
            run_dir.worktrees("/repo"),
            run_dir.worktree("/repo", 42),
            run_dir.worktree("/repo", "42")] == [
        "/repo/.tdd/merge.lock",
        "/repo/.tdd/wt",
        "/repo/.tdd/wt/42",
        "/repo/.tdd/wt/42",
    ]


def test_issue_file_names_a_per_issue_file_of_a_run_and_the_ledger_is_its_md_form():
    run_dir = importlib.import_module("veri.run_dir")

    assert [run_dir.issue_file("/repo/.tdd/wt/7", 7),
            run_dir.issue_file("/repo/.tdd/wt/7", "7", "-skill-commit"),
            run_dir.issue_file("/repo/.tdd/wt/7", 7, "-spec.md"),
            run_dir.ledger("/repo/.tdd/wt/7", 7)] == [
        "/repo/.tdd/wt/7/.tdd/issue-7",
        "/repo/.tdd/wt/7/.tdd/issue-7-skill-commit",
        "/repo/.tdd/wt/7/.tdd/issue-7-spec.md",
        "/repo/.tdd/wt/7/.tdd/issue-7.md",
    ]


PORCELAIN = "worktree /repo\nHEAD abc\nbranch refs/heads/main\n\nworktree /repo/.tdd/wt/42\nHEAD def\n"


def git_says(monkeypatch, tmp_path, code=0, out="", error=None):
    """Fake the one `git worktree list --porcelain` call; returns the argv/kwargs it was made with."""
    import subprocess
    seen = []
    monkeypatch.chdir(tmp_path)

    def run(args, **kwargs):
        seen.append((list(args), kwargs))
        if error:
            raise error
        return subprocess.CompletedProcess(args, code, out, "")

    monkeypatch.setattr(subprocess, "run", run)
    return seen


def test_main_tree_is_the_first_worktree_git_lists_as_a_str(monkeypatch, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    seen = git_says(monkeypatch, tmp_path, out=PORCELAIN)

    assert run_dir.main_tree() == "/repo"
    assert seen[0][0] == ["git", "worktree", "list", "--porcelain"]


def test_main_tree_takes_a_first_line_without_the_worktree_prefix_as_the_tree(monkeypatch, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, tmp_path, out="/repo\n")

    assert run_dir.main_tree() == "/repo"


def test_main_tree_asks_git_from_the_given_directory(monkeypatch, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    seen = git_says(monkeypatch, tmp_path, out=PORCELAIN)

    run_dir.main_tree("/repo/.tdd/wt/42")

    assert seen[0][1]["cwd"] == "/repo/.tdd/wt/42"


@pytest.mark.parametrize("answer", [
    {"error": FileNotFoundError("git")},
    {"error": NotADirectoryError("/nope")},
    {"code": 128, "out": ""},
    {"code": 1, "out": PORCELAIN},
    {"code": 0, "out": ""},
], ids=["no-git", "bad-cwd", "not-a-repo", "failed-with-output", "empty"])
def test_main_tree_raises_no_main_tree_when_git_gives_no_answer(monkeypatch, tmp_path, answer):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, tmp_path, **answer)

    with pytest.raises(run_dir.NoMainTree):
        run_dir.main_tree()


@pytest.mark.parametrize("missing", ["", None, "/nowhere"], ids=["empty", "none", "path"])
@pytest.mark.parametrize("answer", [
    {"error": FileNotFoundError("git")},
    {"code": 128, "out": ""},
    {"code": 0, "out": ""},
], ids=["no-git", "not-a-repo", "empty"])
def test_main_tree_returns_the_missing_value_the_caller_gave_instead_of_raising(monkeypatch, tmp_path, answer, missing):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, tmp_path, **answer)

    assert run_dir.main_tree(missing=missing) is missing


def test_main_tree_ignores_missing_when_git_names_a_tree(monkeypatch, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, tmp_path, code=0, out=PORCELAIN)

    assert run_dir.main_tree(missing="") == "/repo"
