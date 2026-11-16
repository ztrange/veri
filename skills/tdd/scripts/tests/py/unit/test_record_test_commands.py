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


@pytest.mark.parametrize("argv", [[], ["make unit"], ["", "make test"], ["make unit", ""], ["make unit", "", "."]])
def test_a_missing_or_empty_command_is_exit_2_naming_the_usage_before_any_process_starts(
        record, run_cli, fake_processes, argv):
    fake = fake_processes.answers({})

    code, out, err = run_cli(record, argv)

    assert (code, out, fake.calls) == (2, "", [])
    assert record.USAGE in err


def test_a_repo_root_outside_a_git_repository_is_exit_2_saying_so_with_nothing_written(
        record, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers({"git rev-parse": (128, "", "fatal: not a git repository\n")})

    code, out, err = run_cli(record, ["make unit", "make test", str(tmp_path)])

    assert (code, out) == (2, "")
    assert "not a git repository" in err
    assert [call.split()[1] for call in fake.calls] == ["rev-parse"]
