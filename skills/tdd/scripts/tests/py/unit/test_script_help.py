"""In-process cases for veri/script_help.py, the module script-help.sh is a shim over."""
import importlib
import pathlib

import pytest


@pytest.fixture
def script_help():
    return importlib.import_module("veri.script_help")


def test_main_with_no_argument_exits_2_printing_the_usage_line_script_help_sh(run_cli, script_help):
    code, out, err = run_cli(script_help, [])

    assert (code, out, err) == (2, "", "usage: script-help.sh <name>\n")


def test_main_with_a_name_that_has_no_entry_in_scripts_md_exits_3_printing_nothing_on_stdout(run_cli, script_help):
    code, out, err = run_cli(script_help, ["no-such-script.sh"])

    assert (code, out) == (3, "")


def test_main_with_a_name_prints_exactly_that_scripts_entry_and_exits_0(run_cli, script_help):
    catalogue = (pathlib.Path(__file__).resolve().parents[3] / ".." / "SCRIPTS.md").resolve()
    lines = catalogue.read_text().splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.startswith("- `$S/pin-recheck.sh"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i][:1] not in (" ", "\n") or lines[i] == ""), len(lines))
    expected = "".join(lines[start:end]).rstrip("\n") + "\n"

    code, out, err = run_cli(script_help, ["pin-recheck.sh"])

    assert (code, out) == (0, expected)


def test_main_with_the_name_of_the_last_entry_in_scripts_md_prints_that_entry_in_full_and_exits_0(run_cli, script_help):
    catalogue = (pathlib.Path(__file__).resolve().parents[3] / ".." / "SCRIPTS.md").resolve()
    lines = catalogue.read_text().splitlines(keepends=True)
    start = max(i for i, line in enumerate(lines) if line.startswith("- `$S/"))
    name = lines[start].removeprefix("- `$S/").split()[0].rstrip("`")
    expected = "".join(lines[start:]).rstrip("\n") + "\n"

    code, out, err = run_cli(script_help, [name])

    assert (code, out) == (0, expected)


def test_main_with_only_a_prefix_of_a_catalogued_script_name_exits_3_printing_nothing_on_stdout(run_cli, script_help):
    code, out, err = run_cli(script_help, ["pin-recheck"])

    assert (code, out) == (3, "")
