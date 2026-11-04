"""In-process cases for veri/suite_flakes.py, the module suite-flakes.sh is a shim over."""
import importlib


def test_2957_suite_flakes_with_no_argument_prints_a_usage_line_naming_the_script_and_exits_2(run_cli):
    suite_flakes = importlib.import_module("veri.suite_flakes")

    code, out, err = run_cli(suite_flakes, [])

    assert (code, out, "suite-flakes.sh" in err) == (2, "", True)


def test_2957_suite_flakes_with_a_run_directory_lacking_an_event_log_exits_2_naming_that_directory(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    run_dir = tmp_path / "12"
    run_dir.mkdir()

    code, out, err = run_cli(suite_flakes, [str(run_dir)])

    assert (code, out, str(run_dir) in err) == (2, "", True)


def test_2957_suite_flakes_with_each_cleared_file_in_one_run_only_prints_nothing_and_exits_3(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    run_dirs = []
    for number, name in (("12", "scripts/a.test.mjs"), ("19", "scripts/b.test.mjs")):
        run_dir = tmp_path / number
        (run_dir / ".tdd").mkdir(parents=True)
        (run_dir / ".tdd" / "events.jsonl").write_text(
            '{"event": "suite-flake", "files": "' + name + '"}\n')
        run_dirs.append(str(run_dir))

    code, out, err = run_cli(suite_flakes, run_dirs)

    assert (code, out) == (3, "")


def test_2957_suite_flakes_lists_a_file_cleared_in_two_runs_with_ascending_run_numbers_and_not_one_cleared_once(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    run_dirs = []
    for number, name in (("19", "scripts/a.test.mjs,scripts/b.test.mjs"), ("12", "scripts/a.test.mjs")):
        run_dir = tmp_path / number
        (run_dir / ".tdd").mkdir(parents=True)
        (run_dir / ".tdd" / "events.jsonl").write_text(
            '{"event": "suite-flake", "files": "' + name + '"}\n')
        run_dirs.append(str(run_dir))

    code, out, err = run_cli(suite_flakes, run_dirs)

    assert (code, out) == (0, "scripts/a.test.mjs: 12, 19\n")


def test_2957_suite_flakes_counts_a_file_named_by_two_events_in_one_run_once_and_exits_3(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    run_dir = tmp_path / "12"
    (run_dir / ".tdd").mkdir(parents=True)
    (run_dir / ".tdd" / "events.jsonl").write_text(
        '{"event": "suite-flake", "files": "scripts/a.test.mjs"}\n'
        '{"event": "suite-flake", "files": "scripts/a.test.mjs"}\n')

    code, out, err = run_cli(suite_flakes, [str(run_dir)])

    assert (code, out) == (3, "")


def test_2957_suite_flakes_counts_each_file_of_a_comma_list_so_one_named_second_is_listed_with_both_runs(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    run_dirs = []
    for number, name in (("19", "scripts/b.test.mjs,scripts/a.test.mjs"), ("12", "scripts/a.test.mjs")):
        run_dir = tmp_path / number
        (run_dir / ".tdd").mkdir(parents=True)
        (run_dir / ".tdd" / "events.jsonl").write_text(
            '{"event": "suite-flake", "files": "' + name + '"}\n')
        run_dirs.append(str(run_dir))

    code, out, err = run_cli(suite_flakes, run_dirs)

    assert (code, out) == (0, "scripts/a.test.mjs: 12, 19\n")


def test_2957_suite_flakes_skips_non_object_lines_and_other_events_with_files_so_a_file_only_they_name_is_not_listed(run_cli, tmp_path):
    suite_flakes = importlib.import_module("veri.suite_flakes")
    skipped = tmp_path / "12"
    (skipped / ".tdd").mkdir(parents=True)
    (skipped / ".tdd" / "events.jsonl").write_text(
        'not json at all\n'
        '["scripts/a.test.mjs"]\n'
        '{"event": "other", "files": "scripts/a.test.mjs"}\n')
    cleared = tmp_path / "19"
    (cleared / ".tdd").mkdir(parents=True)
    (cleared / ".tdd" / "events.jsonl").write_text(
        '{"event": "suite-flake", "files": "scripts/a.test.mjs"}\n')

    code, out, err = run_cli(suite_flakes, [str(skipped), str(cleared)])

    assert (code, out) == (3, "")
