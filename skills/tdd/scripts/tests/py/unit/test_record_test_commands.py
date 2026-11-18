"""Cases for record-test-commands.sh's CLAUDE.md rewrite and its refusals, in-process."""
import importlib

import pytest


@pytest.fixture
def record():
    return importlib.import_module("veri.record_test_commands")


def test_an_existing_tier_line_is_replaced_where_it_stands_keeping_what_precedes_its_marker_and_every_other_line(record):
    text = (b"# Project\n"
            b"Write `veri: fast tests:` lines here.\n"
            b"veri: fast tests:\n"
            b"- veri: fast tests: `old fast`\n"
            b"between\r\n"
            b"veri: all tests: old all\n"
            b"tail")

    assert record.recorded(text, b"make unit", b"make test") == (
        b"# Project\n"
        b"Write `veri: fast tests:` lines here.\n"
        b"veri: fast tests:\n"
        b"- veri: fast tests: make unit\n"
        b"between\r\n"
        b"veri: all tests: make test\n"
        b"tail")


def test_a_crlf_claude_md_gets_its_tier_lines_with_crlf_endings_backticked_so_the_detector_reads_them_back_exactly(record):
    text = b"# P\r\nveri: fast tests: old\r\nend\r\n"

    new = record.recorded(text, b"make unit", b"make test")

    assert new == b"# P\r\nveri: fast tests: `make unit`\r\nend\r\nveri: all tests: `make test`\r\n"
    assert (record.declared(new, record.FAST), record.declared(new, record.ALL)) == (b"make unit", b"make test")


def test_an_existing_one_test_file_line_is_replaced_where_it_stands_and_every_other_line_is_unchanged(record):
    text = b"# P\nveri: one test file: `old \"$1\"`\nmid\nveri: fast tests: f\nveri: all tests: a\nend\n"

    assert record.recorded(text, b"f", b"a", b'pytest -q "$1"') == (
        b"# P\nveri: one test file: pytest -q \"$1\"\nmid\nveri: fast tests: f\nveri: all tests: a\nend\n")


def test_without_one_file_no_one_test_file_line_is_added_and_an_existing_one_is_left_unchanged(record):
    bare = b"# P\n"
    held = b"# P\nveri: one test file: `old \"$1\"`\n"

    assert (record.recorded(bare, b"f", b"a"), record.recorded(held, b"f", b"a")) == (
        b"# P\nveri: fast tests: f\nveri: all tests: a\n",
        b"# P\nveri: one test file: `old \"$1\"`\nveri: fast tests: f\nveri: all tests: a\n")


def test_issue_4335_a_quiet_command_is_written_to_the_quiet_test_files_line_where_it_stands_else_appended(record):
    held = b"# P\nveri: quiet test files: `old -q`\nmid\nveri: fast tests: f\nveri: all tests: a\nend\n"
    bare = b"# P\n"

    assert (record.recorded(held, b"f", b"a", quiet=b"pytest -q --no-header -rf"),
            record.recorded(bare, b"f", b"a", quiet=b"npx jest --silent")) == (
        b"# P\nveri: quiet test files: pytest -q --no-header -rf\nmid\nveri: fast tests: f\nveri: all tests: a\nend\n",
        b"# P\nveri: fast tests: f\nveri: all tests: a\nveri: quiet test files: npx jest --silent\n")


@pytest.mark.parametrize("argv",[[], ["make unit"], ["", "make test"], ["make unit", ""], ["make unit", "", "."]])
def test_a_missing_or_empty_command_is_exit_2_naming_the_usage_before_any_process_starts(
        record, run_cli, fake_processes, argv):
    fake = fake_processes.answers({})

    code, out, err = run_cli(record, argv)

    assert (code, out, fake.calls) == (2, "", [])
    assert record.USAGE in err


@pytest.mark.parametrize("argv", [["--one-file", "", "make unit", "make test"], ["--one-file"]])
def test_an_empty_or_missing_one_file_command_is_exit_2_naming_the_usage_before_any_process_starts(
        record, run_cli, fake_processes, argv):
    fake = fake_processes.answers({})

    code, out, err = run_cli(record, argv)

    assert (code, out, fake.calls) == (2, "", [])
    assert record.USAGE in err


@pytest.mark.parametrize("one", ["make test", "pytest $10", "echo '$1'x", "pytest x$1"])
def test_a_one_file_command_without_the_file_placeholder_is_exit_2_before_any_process_starts(
        record, run_cli, fake_processes, one):
    fake = fake_processes.answers({})

    code, out, err = run_cli(record, ["--one-file", one, "make unit", "make test"])

    assert (code, out, fake.calls) == (2, "", [])
    assert '"$1"' in err


def test_a_repo_root_outside_a_git_repository_is_exit_2_saying_so_with_nothing_written(
        record, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers({"git rev-parse": (128, "", "fatal: not a git repository\n")})

    code, out, err = run_cli(record, ["make unit", "make test", str(tmp_path)])

    assert (code, out) == (2, "")
    assert "not a git repository" in err
    assert [call.split()[1] for call in fake.calls] == ["rev-parse"]
