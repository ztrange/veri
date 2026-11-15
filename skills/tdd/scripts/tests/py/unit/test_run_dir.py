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


def git_says(monkeypatch, fake_processes, tmp_path, code=0, out="", error=None):
    """Fake the one `git worktree list --porcelain` call; returns the fake, whose seen holds the argv/kwargs it was made with."""
    monkeypatch.chdir(tmp_path)
    return fake_processes.answers({"git ": error if error else (code, out, "")})


def test_main_tree_is_the_first_worktree_git_lists_as_a_str(monkeypatch, fake_processes, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    seen = git_says(monkeypatch, fake_processes, tmp_path, out=PORCELAIN)

    assert run_dir.main_tree() == "/repo"
    assert seen.argvs[0] == ["git", "worktree", "list", "--porcelain"]


def test_main_tree_takes_a_first_line_without_the_worktree_prefix_as_the_tree(monkeypatch, fake_processes, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, fake_processes, tmp_path, out="/repo\n")

    assert run_dir.main_tree() == "/repo"


def test_main_tree_asks_git_from_the_given_directory(monkeypatch, fake_processes, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    seen = git_says(monkeypatch, fake_processes, tmp_path, out=PORCELAIN)

    run_dir.main_tree("/repo/.tdd/wt/42")

    assert seen.seen[0][1]["cwd"] == "/repo/.tdd/wt/42"


@pytest.mark.parametrize("answer", [
    {"error": FileNotFoundError("git")},
    {"error": NotADirectoryError("/nope")},
    {"code": 128, "out": ""},
    {"code": 1, "out": PORCELAIN},
    {"code": 0, "out": ""},
], ids=["no-git", "bad-cwd", "not-a-repo", "failed-with-output", "empty"])
def test_main_tree_raises_no_main_tree_when_git_gives_no_answer(monkeypatch, fake_processes, tmp_path, answer):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, fake_processes, tmp_path, **answer)

    with pytest.raises(run_dir.NoMainTree):
        run_dir.main_tree()


@pytest.mark.parametrize("missing", ["", None, "/nowhere"], ids=["empty", "none", "path"])
@pytest.mark.parametrize("answer", [
    {"error": FileNotFoundError("git")},
    {"code": 128, "out": ""},
    {"code": 0, "out": ""},
], ids=["no-git", "not-a-repo", "empty"])
def test_main_tree_returns_the_missing_value_the_caller_gave_instead_of_raising(monkeypatch, fake_processes, tmp_path, answer, missing):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, fake_processes, tmp_path, **answer)

    assert run_dir.main_tree(missing=missing) is missing


def test_main_tree_ignores_missing_when_git_names_a_tree(monkeypatch, fake_processes, tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    git_says(monkeypatch, fake_processes, tmp_path, code=0, out=PORCELAIN)

    assert run_dir.main_tree(missing="") == "/repo"


def lay_out(tmp_path, pointer, commondir="../..", admin="main/.git/worktrees/linked"):
    """A main tree with a `.git` directory and a linked tree whose `.git` file says `gitdir: <pointer>`."""
    (tmp_path / "main" / ".git").mkdir(parents=True)
    (tmp_path / admin).mkdir(parents=True)
    (tmp_path / admin / "commondir").write_text(commondir + "\n")
    (tmp_path / "linked" / "src" / "deep").mkdir(parents=True)
    (tmp_path / "linked" / ".git").write_text("gitdir: %s\n" % pointer)


def test_main_tree_from_files_in_a_plain_clone_is_the_directory_holding_the_git_directory_from_any_depth(tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    (tmp_path / ".git").mkdir()
    (tmp_path / "a" / "b").mkdir(parents=True)

    assert [run_dir.main_tree_from_files(tmp_path), run_dir.main_tree_from_files(tmp_path / "a" / "b")] == [
        str(tmp_path), str(tmp_path)]


def test_main_tree_from_files_in_a_linked_worktree_follows_the_gitdirs_commondir_to_the_main_tree(tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    lay_out(tmp_path, str(tmp_path / "main/.git/worktrees/linked"))

    assert run_dir.main_tree_from_files(tmp_path / "linked") == str(tmp_path / "main")


def test_main_tree_from_files_called_from_a_subdirectory_of_a_linked_worktree_answers_the_main_tree(tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    lay_out(tmp_path, str(tmp_path / "main/.git/worktrees/linked"))

    assert run_dir.main_tree_from_files(tmp_path / "linked" / "src" / "deep") == str(tmp_path / "main")


def test_main_tree_from_files_resolves_a_relative_gitdir_against_the_directory_holding_the_git_file(tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    lay_out(tmp_path, "../main/.git/worktrees/linked")

    assert run_dir.main_tree_from_files(tmp_path / "linked" / "src") == str(tmp_path / "main")


def test_main_tree_from_files_with_no_repository_above_start_answers_start_itself(tmp_path):
    run_dir = importlib.import_module("veri.run_dir")
    (tmp_path / "x").mkdir()

    assert run_dir.main_tree_from_files(tmp_path / "x") == str(tmp_path / "x")
