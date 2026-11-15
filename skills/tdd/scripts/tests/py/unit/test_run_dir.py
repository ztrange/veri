"""In-process cases for veri/run_dir.py, the one spelling of a path inside a run's .tdd/ directory."""
import importlib


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
