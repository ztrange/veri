"""In-process cases for veri/run_dir.py, the one spelling of a path inside a run's .tdd/ directory."""
import importlib


def test_run_file_names_a_plain_file_and_a_glob_inside_the_runs_tdd_directory():
    run_dir = importlib.import_module("veri.run_dir")

    assert [run_dir.run_file("/repo/.tdd/wt/42", "events.jsonl"),
            run_dir.run_file("/repo/.tdd/wt/42", "*.conductor.out")] == [
        "/repo/.tdd/wt/42/.tdd/events.jsonl",
        "/repo/.tdd/wt/42/.tdd/*.conductor.out",
    ]
